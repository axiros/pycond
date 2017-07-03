# pycond

[![Build Status](https://travis-ci.org/axiros/pycond.svg?branch=master)](https://travis-ci.org/axiros/pycond)


Lightweight condition expression parsing and building of evaluation functions.

# What

You have a bunch of data...

```csv
id,first_name,last_name,email,gender,ip_address
1,Rufe,Morstatt,rmorstatt0@newsvine.de,Male,216.70.69.120
2,Kaela,Scott,scott@opera.com,Female,73.248.145.44,2
(...)
```

... and you need to filter. For now lets say we have them already as list of dicts.

You can do it imperatively:

```python
foo_users = [ u for u in users
              if ([u['gender'] == 'Male' or u['last_name'] == 'Scott') and
                  '@' in u['email']) ]
```

or you have this module assemble a condition function from a declaration like:

```python
from py_cond import pycond
cond = 'email contains .de and gender eq Male or last_name eq Scott'
is_foo = pycond(cond)
```

and then apply as often as you need, against varying state / facts / models (...):

```
foo_users = [ u for u in users if is_foo(state=u) ]
```
with roughly the same performance (factor 2-3) than the handcrafted python.

# Why

There is a massive list of great tools and frameworks where condition parsing is a (small) part of them, e.g. [pyke](http://pyke.sourceforge.net/) or [durable](https://pypi.python.org/pypi/durable_rules) and many in the django world or from SQL statement parsers.

I just needed a very slim tool for only the parsing into functions - but this pretty customizable.

pycond allows to customize
- the list of condition operators
- the list of combination operators
- the general behavior of condition operators via global or condition local wrappers
- their names
- the tokenizer
- the value lookup function

and ships as zero dependency single module.

All evaluation is done via [partials](https://stackoverflow.com/a/3252425/4583360) and not lambdas, i.e. operations can be introspected and debugged very simple.

Performance is good enough to have "pyconditions" used within [stream filters](https://github.com/ReactiveX/RxPY).


# Mechanics

## Parsing
pycond parses the condition expressions according to a set of constraints given to the parser in the `tokenizer` function.
The result of the tokenizer is given to the builder.

## Building
After parsing the builder is assembling a nested set of operator functions, combined via combining operators.
The functions are partials, i.e. not yet evaluated.

## Evaluation

The result of the builder is a 'pycondition', which can be run many times against a varying state of the system.
How state is evaluated is customizable at build and run time.

### Default Lookup
The default is to get lookup keys within expressions from an initially empty `State` dict within the module.

```python
from pycond import pycond, State as S

pycond('foo eq bar')  # False
S['foo'] = 'bar'
pycond('foo eq bar')  # True
```

### Custom Lookup & Value Passing

```python
# must return a (key, value) tuple:
model = {'joe': {'last_host': 'somehost'}}
def my_lu(k, v, req, user, model=model):
     log('user check', user, k, v)
     return ( model.get(user) or {} ).get(k), req[v]
f = pycond('last_host eq host', lookup=my_lu)

req = {'host': 'somehost'}
f(req=req, user='joe')    # True
f(req=req, user='sally')  # False
```




## Building Conditions

### Grammar

Combine atomic conditions with boolean operators and nesting brackets like:

[  <atom1> <and|or|and not|...> <atom2> ] <and|or...> [ [ <atom3> ....

### Atomic Conditions

```
<lookup_key> [ [rev] [not] <condition operator (co)> <value> ]
```
When just `lookup_key` given then `co` is set to the `truthy` function:

```python
def truthy(key, val=None):
    return True if key else False
```

so such an expression is valid `[ foo and bar and not baz]` and True e.g. for `S={'foo': 1, 'bar': 'a', 'baz': []}`

#### Condition Operators

All boolean [standardlib operators](https://docs.python.org/2/library/operator.html) are available by default.

##### Extending Condition Operators

```python
from pycond import OPS
OPS['maybe'] = lambda a, b: random.choice((True, False))

'a maybe b' # valid expression now.
```


#### Negation `not`

Negates the result of the condition operator:

```python
S['foo'] = 'abc'; pycond('foo eq abc')()            # True
S['foo'] = 'abc'; pycond('foo not eq abc')()        # False
```




#### Reversal `rev`

Reverses the arguments before calling the operator

```python
S['foo'] = 'abc'; pycond('foo contains a')()        # True
S['foo'] = 'a'  ; pycond('foo rev contains abc')()  # True
```

> `rev` and `not` can be combined in any order.


### Combining Operations

You can combine single conditions with
- `and`
- `and not`
- `or`
- `or not`
- `xor` by default.

The combining functions are stored in `pycond.COMB_OPS` dict and may be extended.

> Do not use spaces for the names of combining operators. The user may use them but they are replaced at before tokenizing time, like `and not` -> `and_not`.

### Nesting

Combined conditions may be arbitrarily nested using brackets "[" and "]".

> Via the `brkts` config parameter you may change those to other separators at build time.
