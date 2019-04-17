# pycond


[![Build Status](https://travis-ci.org/axiros/pycond.svg?branch=master)](https://travis-ci.org/axiros/pycond)


Lightweight condition expression parsing and building of evaluation functions.

- [What](#what)
- [Why](#why)
    - [pycond Reasons to exist](#pycond-reasons-to-exist)
- [Mechanics](#mechanics)
    - [Parsing](#parsing)
    - [Building](#building)
    - [Evaluation](#evaluation)
        - [Default Lookup](#default-lookup)
        - [Custom Lookup & Value Passing](#custom-lookup-value-passing)
    - [Building Conditions](#building-conditions)
        - [Grammar](#grammar)
        - [Atomic Conditions](#atomic-conditions)
            - [Condition Operators](#condition-operators)
                - [Using Symbolic Operators](#using-symbolic-operators)
                - [Extending Condition Operators](#extending-condition-operators)
            - [Negation `not`](#negation-not)
            - [Reversal `rev`](#reversal-rev)
                - [Wrapping Condition Operators](#wrapping-condition-operators)
                - [Global Wrapping](#global-wrapping)
                - [Condition Local Wrapping](#condition-local-wrapping)
        - [Combining Operations](#combining-operations)
        - [Nesting](#nesting)
    - [Tokenizing](#tokenizing)
        - [Bypassing](#bypassing)
        - [Functioning](#functioning)
            - [Separator `sep`](#separator-sep)
            - [Apostrophes](#apostrophes)
            - [Escaping](#escaping)
    - [Building](#building)
        - [Autoconv: Casting of values into python simple types](#autoconv-casting-of-values-into-python-simple-types)


# What

You have a bunch of data...

```csv
1,Rufe,Morstatt,rmorstatt0@newsvine.de,Male,216.70.69.120
2,Kaela,Scott,scott@opera.com,Female,73.248.145.44,2
(...)
```

... and you need to filter. For now lets say we have them already as list of dicts.

You can do it imperatively:

```python
              if ([u['gender'] == 'Male' or u['last_name'] == 'Scott') and
                  '@' in u['email']) ]
```

or you have this module assemble a condition function from a declaration like:

```python
cond = 'email contains .de and gender eq Male or last_name eq Scott'
is_foo = parse_cond(cond)
```

and then apply as often as you need, against varying state / facts / models (...):

```
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

```
## Building Conditions

### Grammar

Combine atomic conditions with boolean operators and nesting brackets like:

```
```

### Atomic Conditions

```
```
When just `lookup_key` given then `co` is set to the `truthy` function:

```python
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
from pytest_to_md import html_table as tbl  # just a table gen.
from pycond import get_ops

for k in 'nr', 'str':
    s = 'Default supported ' + k + ' operators...(click to extend)'
    print(tbl(get_ops()[k], k + ' operator', 'alias', summary=s))
```


<details>
        <summary>Default supported nr operators...(click to extend)</summary>
<tr><td>nr operator</td><td>alias</td></tr>
<tr><td>add</td><td>+</td></tr>
<tr><td>and_</td><td>&</td></tr>
<tr><td>eq</td><td>==</td></tr>
<tr><td>floordiv</td><td>//</td></tr>
<tr><td>ge</td><td>>=</td></tr>
<tr><td>gt</td><td>></td></tr>
<tr><td>iadd</td><td>+=</td></tr>
<tr><td>iand</td><td>&=</td></tr>
<tr><td>ifloordiv</td><td>//=</td></tr>
<tr><td>ilshift</td><td><<=</td></tr>
<tr><td>imod</td><td>%=</td></tr>
<tr><td>imul</td><td>*=</td></tr>
<tr><td>ior</td><td>|=</td></tr>
<tr><td>ipow</td><td>**=</td></tr>
<tr><td>irshift</td><td>>>=</td></tr>
<tr><td>is_</td><td>is</td></tr>
<tr><td>is_not</td><td>is</td></tr>
<tr><td>isub</td><td>-=</td></tr>
<tr><td>itruediv</td><td>/=</td></tr>
<tr><td>ixor</td><td>^=</td></tr>
<tr><td>le</td><td><=</td></tr>
<tr><td>lshift</td><td><<</td></tr>
<tr><td>lt</td><td><</td></tr>
<tr><td>mod</td><td>%</td></tr>
<tr><td>mul</td><td>*</td></tr>
<tr><td>ne</td><td>!=</td></tr>
<tr><td>or_</td><td>|</td></tr>
<tr><td>pow</td><td>**</td></tr>
<tr><td>rshift</td><td>>></td></tr>
<tr><td>sub</td><td>-</td></tr>
<tr><td>truediv</td><td>/</td></tr>
<tr><td>xor</td><td>^</td></tr>
<tr><td>itemgetter</td><td></td></tr>
<tr><td>length_hint</td><td></td></tr>
</table>
        </details>



<details>
        <summary>Default supported str operators...(click to extend)</summary>
<tr><td>str operator</td><td>alias</td></tr>
<tr><td>attrgetter</td><td></td></tr>
<tr><td>concat</td><td>+</td></tr>
<tr><td>contains</td><td></td></tr>
<tr><td>countOf</td><td></td></tr>
<tr><td>iconcat</td><td>+=</td></tr>
<tr><td>indexOf</td><td></td></tr>
<tr><td>methodcaller</td><td></td></tr>
</table>
        </details>


##### Using Symbolic Operators

By default pycond uses text style operators.

- `ops_use_symbolic` switches processwide to symbolic style only.
- `ops_use_both` switches processwide to both notations allowed.

```python
import pycond as pc

pc.ops_use_symbolic()
pc.State['foo'] = 'bar'
assert pc.pycond('foo == bar')() == True
try:
    # this raises now, text ops not known anymore:
    pc.pycond('foo eq bar')
except:
    pc.ops_use_both()
    assert pc.pycond('foo eq bar')() == True
    assert pc.pycond('foo != baz')() == True
```

> Operator namespace(s) should be assigned at process start, they are global.


##### Extending Condition Operators

```python
import time
from pycond import pycond as p, OPS

OPS['maybe'] = lambda a, b: int(time.time()) % 2

assert p('a maybe b')() in (True, False)  # valid expression now.
```

#### Negation `not`

Negates the result of the condition operator:

```python
S['foo'] = 'abc'
assert pycond('foo eq abc')() == True
assert pycond('foo not eq abc')() == False
```

#### Reversal `rev`

Reverses the arguments before calling the operator
```python

S['foo'] = 'abc'
assert pycond('foo contains a')() == True
assert pycond('foo rev contains abc')() == True
```

> `rev` and `not` can be combined in any order.

##### Wrapping Condition Operators

##### Global Wrapping
You may globally wrap all evaluation time condition operations through a custom function:


```python
import pycond as pc

l = []

def hk(f_op, a, b, l=l):
    l.append((getattr(f_op, '__name__', ''), a, b))
    return f_op(a, b)

pc.run_all_ops_thru(hk)  # globally wrap the operators

pc.State.update({'a': 1, 'b': 2, 'c': 3})
f = pc.pycond('a gt 0 and b lt 3 and not c gt 4')
assert l == []
f()
expected_log = [('gt', 1, 0.0), ('lt', 2, 3.0), ('gt', 3, 4.0)]
assert l == expected_log
pc.ops_use_both()
```

You may compose such wrappers via repeated application of the `run_all_ops_thru` API function.

##### Condition Local Wrapping

This is done through the `ops_thru` parameter as shown:

```python
import pycond as pc

def myhk(f_op, a, b):
    return True

pc.State['a'] = 1
f = pc.pycond('a eq 2')
assert f() == False
f = pc.pycond('a eq 2', ops_thru=myhk)
assert f() == True
```

> Using `ops_thru` is a good way to debug unexpected results, since you
> can add breakpoints or loggers there.


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


## Tokenizing

### Bypassing

You can bypass the tokenizer by passing an already tokenized list to pycond, e.g. `pycond(['a', 'eq', 42])`.

> Brackets as strings in this flat list form, e.g. `['[', 'a', 'and' 'b', ']'...]`

### Functioning

The tokenizers job is to take apart expression strings for the builder.

#### Separator `sep`

Separates the different parts of an expression. Default is ' '.

```python
import pycond as pc

pc.State['a'] = 42
assert pc.pycond('a.eq.42', sep='.')() == True
```
> sep can be a any single character including binary.

Bracket characters do not need to be separated, the tokenizer will do:

```python
import pycond as pc

# equal:
assert (
    pc.pycond('[[a eq 42] and b]')()
    == pc.pycond('[ [ a eq 42 ] and b ]')()
)
```
> The condition functions themselves do not evaluate equal - those
> had been assembled two times.

#### Apostrophes

By putting strings into Apostrophes you can tell the tokenizer to not further inspect them, e.g. for the seperator:

```python
import pycond as pc

pc.State['a'] = 'Hello World'

assert pc.pycond('a eq "Hello World"')() == True
```



#### Escaping

Tell the tokenizer to not interpret the next character:

```python
import pycond as pc

pc.State['b'] = 'Hello World'
assert pc.pycond('b eq Hello\ World')() == True
```


## Building

### Autoconv: Casting of values into python simple types

Expression string values are automatically cast into bools and numbers via the public `pycond.py_type` function.

This can be prevented by setting the `autoconv` parameter to `False` or by using Apostrophes:

```python
import pycond as pc

pc.State['a'] = '42'
assert pc.pycond('a eq 42')() == False
# compared as string now
assert pc.pycond('a eq "42"')() == True
# compared as string now
assert pc.pycond('a eq 42', autoconv=False)() == True
```

If you do not want to provide a custom lookup function (where you can do what you want)
but want to have looked up keys autoconverted then use:

```python
import pycond as pc

for id in '1', 1:
    pc.State['id'] = id
    assert pc.pycond('id lt 42', autoconv_lookups=True)
```

*Auto generated by [pytest_to_md](https://github.com/axiros/pytest_to_md), running [test_tutorial.py][test_tutorial.py]*

<!-- autogen tutorial -->


<!-- autogenlinks -->
[test_tutorial.py]: https://github.com/axiros/pycond/blob/e7a0f2aff2c970c7c5dd3282e80d667cc26fad81/tests/test_tutorial.py