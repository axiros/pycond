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
from pycond import parse_cond
cond = 'email contains .de and gender eq Male or last_name eq Scott'
is_foo = parse_cond(cond)
```

and then apply as often as you need, against varying state / facts / models (...):

```
foo_users = [ u for u in users if is_foo(state=u) ]
```
with roughly the same performance (factor 2-3) than the handcrafted python.

# Why

When the developer can decide upon the filters to apply on data he'll certainly
use Python's excellent expressive possibilities directly, e.g. as shown above
through list comprehensions.   
But what if the filtering conditions are based on decisions outside of the program's
control? I.e. from an end user, hitting the program via the network, in a somehow serialized form, which is rarely directly evaluatable Python.

This is the main use case for this module.  

But why yet another tool for such a standard job?  

There is a massive list of great tools and frameworks where condition parsing is a (small) part of them, e.g. [pyke](http://pyke.sourceforge.net/) or [durable](https://pypi.python.org/pypi/durable_rules) and many in the django world or from SQL statement parsers.

## pycond Reasons to exist

`1.` I just needed a very **slim** tool for only the parsing into functions - but this pretty transparent and customizable

pycond allows to customize
- the list of condition operators
- the list of combination operators
- the general behavior of condition operators via global or condition local wrappers
- their names
- the tokenizer
- the value lookup function

and ships as zero dependency single module.

All evaluation is done via [partials](https://stackoverflow.com/a/3252425/4583360) and not lambdas, i.e. operations can be introspected and debugged very simply, through breakpoints or custom logging operator or lookup wrappers.

`2.` Simplicity of the grammar: Easy to type directly, readable by non
programmers but also synthesisable from structured data, e.g. from a web framework.


`3.` Performance: Good enough to have "pyconditions" used within [stream filters](https://github.com/ReactiveX/RxPY). With the current feature set we are (only) a factor 2-3 slower, compared to handcrafted list comprehensions.


# Mechanics

<!-- md_links_for: github -->
<!-- autogen tutorial -->

## Parsing
pycond parses the condition expressions according to a set of constraints given to the parser in the `tokenizer` function.
The result of the tokenizer is given to the builder.


## Building
After parsing the builder is assembling a nested set of operator functions, combined via combining operators.
The functions are partials, i.e. not yet evaluated but information about the necessary keys is already
available:

```python

from pycond import parse_cond

f, meta = parse_cond('foo eq bar')
assert meta['keys'] == ['foo']
```

## Evaluation

The result of the builder is a 'pycondition', which can be run many times against a varying state of the system.
How state is evaluated is customizable at build and run time.

### Default Lookup
The default is to get lookup keys within expressions from an initially empty `State` dict within the module.

```python

from pycond import pycond, State as S

f = pycond('foo eq bar')
assert f() == False
S['foo'] = 'bar'
assert f() == True
```

(`pycond` is a shortcut for `parse_cond`, when meta infos are not required).


### Custom Lookup & Value Passing

```python

from pycond import pycond

# must return a (key, value) tuple:
model = {'eve': {'last_host': 'somehost'}}

def my_lu(k, v, req, user, model=model):
    print('user check', user, k, v)
    return (model.get(user) or {}).get(k), req[v]

f = pycond('last_host eq host', lookup=my_lu)

req = {'host': 'somehost'}
assert f(req=req, user='joe') == False
assert f(req=req, user='eve') == True
```
Output:
```user check joe last_host host
user check eve last_host host

```
## Building Conditions

### Grammar

Combine atomic conditions with boolean operators and nesting brackets like:

```
[  <atom1> <and|or|and not|...> <atom2> ] <and|or...> [ [ <atom3> ....
```

### Atomic Conditions

```
<lookup_key> [ [rev] [not] <condition operator (co)> <value> ]
```
When just `lookup_key` given then `co` is set to the `truthy` function:

```python
def truthy(key, val=None):
    return operatur.truth(k)
```

so such an expression is valid and True:

```python

from pycond import pycond as p, State as S

S.update({'foo': 1, 'bar': 'a', 'baz': []})
assert p('[ foo and bar and not baz]')() == True
```

#### Condition Operators

All boolean [standardlib operators](https://docs.python.org/2/library/operator.html) are available by default:

```python

from pytest_to_md import md_table  # just a markdown formatter
from pycond import get_ops

for k in 'nr', 'str':
    print(md_table(get_ops()[k], 'operator', 'alias'))
```


 | operator | alias | 
 | _ | _ | 
 | add | + | 
 | and_ | & | 
 | eq | == | 
 | floordiv | // | 
 | ge | >= | 
 | gt | > | 
 | iadd | += | 
 | iand | &= | 
 | ifloordiv | //= | 
 | ilshift | <<= | 
 | imod | %= | 
 | imul | *= | 
 | ior | |= | 
 | ipow | **= | 
 | irshift | >>= | 
 | is_ | is | 
 | is_not | is | 
 | isub | -= | 
 | itruediv | /= | 
 | ixor | ^= | 
 | le | <= | 
 | lshift | << | 
 | lt | < | 
 | mod | % | 
 | mul | * | 
 | ne | != | 
 | or_ | | | 
 | pow | ** | 
 | rshift | >> | 
 | sub | - | 
 | truediv | / | 
 | xor | ^ | 
 | itemgetter |  | 
 | length_hint |  | 



 | operator | alias | 
 | _ | _ | 
 | attrgetter |  | 
 | concat | + | 
 | contains |  | 
 | countOf |  | 
 | iconcat | += | 
 | indexOf |  | 
 | methodcaller |  | 



##### Extending Condition Operators

```python

import time
from pycond import pycond as p, OPS

OPS['maybe'] = lambda a, b: int(time.time()) % 2

assert p('a maybe b')() in (True, False)  # valid expression now.
```
<!-- autogen tutorial -->
