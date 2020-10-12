---

author: gk
version: 2020.10.10

---


# pycond: Lightweight Declarative Condition Expressions

[![Build Status](https://travis-ci.org/axiros/pycond.svg?branch=master)](https://travis-ci.org/axiros/pycond) [![codecov](https://codecov.io/gh/axiros/pycond/branch/master/graph/badge.svg)](https://codecov.io/gh/axiros/pycond)[![PyPI    version][pypisvg]][pypi] [![][blacksvg]][black]

[blacksvg]: https://img.shields.io/badge/code%20style-black-000000.svg
[black]: https://github.com/ambv/black
[pypisvg]: https://img.shields.io/pypi/v/pycond.svg
[pypi]: https://badge.fury.io/py/pycond

<!-- badges: http://thomas-cokelaer.info/blog/2014/08/1013/ -->


<!-- TOC -->

# Table Of Contents

- <a name="toc1"></a>[What](#what)
- <a name="toc2"></a>[Why](#why)
    - <a name="toc3"></a>[Alternatives](#alternatives)
- <a name="toc4"></a>[Mechanics](#mechanics)
    - <a name="toc5"></a>[Parsing](#parsing)
    - <a name="toc6"></a>[Building](#building)
    - <a name="toc7"></a>[Structured Conditions](#structured-conditions)
- <a name="toc8"></a>[Evaluation](#evaluation)
    - <a name="toc9"></a>[Default Lookup](#default-lookup)
    - <a name="toc10"></a>[Passing State](#passing-state)
        - <a name="toc11"></a>[Deep Lookup / Nested State / Lists](#deep-lookup-nested-state-lists)
    - <a name="toc12"></a>[Prefixed Data](#prefixed-data)
    - <a name="toc13"></a>[Custom Lookup And Value Passing](#custom-lookup-and-value-passing)
    - <a name="toc14"></a>[Lazy Evaluation](#lazy-evaluation)
- <a name="toc15"></a>[Details](#details)
    - <a name="toc16"></a>[Debugging Lookups](#debugging-lookups)
    - <a name="toc17"></a>[Enabling/Disabling of Branches](#enabling-disabling-of-branches)
    - <a name="toc18"></a>[Building Conditions From Text](#building-conditions-from-text)
        - <a name="toc19"></a>[Grammar](#grammar)
        - <a name="toc20"></a>[Atomic Conditions](#atomic-conditions)
    - <a name="toc21"></a>[Condition Operators](#condition-operators)
        - <a name="toc22"></a>[Using Symbolic Operators](#using-symbolic-operators)
        - <a name="toc23"></a>[Extending Condition Operators](#extending-condition-operators)
        - <a name="toc24"></a>[Negation `not`](#negation-not)
        - <a name="toc25"></a>[Reversal `rev`](#reversal-rev)
        - <a name="toc26"></a>[Wrapping Condition Operators](#wrapping-condition-operators)
            - <a name="toc27"></a>[Global Wrapping](#global-wrapping)
            - <a name="toc28"></a>[Condition Local Wrapping](#condition-local-wrapping)
    - <a name="toc29"></a>[Combining Operations](#combining-operations)
        - <a name="toc30"></a>[Nesting](#nesting)
    - <a name="toc31"></a>[Tokenizing Details](#tokenizing-details)
        - <a name="toc32"></a>[Functioning](#functioning)
        - <a name="toc33"></a>[Separator `sep`](#separator-sep)
        - <a name="toc34"></a>[Apostrophes](#apostrophes)
        - <a name="toc35"></a>[Escaping](#escaping)
        - <a name="toc36"></a>[Building](#building)
        - <a name="toc37"></a>[Autoconv: Casting of values into python simple types](#autoconv-casting-of-values-into-python-simple-types)
    - <a name="toc38"></a>[Context On Demand](#context-on-demand)
- <a name="toc39"></a>[Lookup Providers](#lookup-providers)
    - <a name="toc40"></a>[Accepted Signatures](#accepted-signatures)
    - <a name="toc41"></a>[Parametrized Lookup Functions](#parametrized-lookup-functions)
    - <a name="toc42"></a>[Namespace](#namespace)
    - <a name="toc43"></a>[Caching](#caching)
    - <a name="toc44"></a>[Extensions](#extensions)
- <a name="toc45"></a>[Named Conditions: Qualification](#named-conditions-qualification)
    - <a name="toc46"></a>[Options](#options)
    - <a name="toc47"></a>[Partial Evaluation](#partial-evaluation)
- <a name="toc48"></a>[Streaming Data](#streaming-data)
    - <a name="toc49"></a>[Filtering](#filtering)
    - <a name="toc50"></a>[Streaming Classification](#streaming-classification)
        - <a name="toc51"></a>[Selective Classification](#selective-classification)
            - <a name="toc52"></a>[Treating of Booleans (Conditions, Not Names)](#treating-of-booleans-conditions-not-names)
    - <a name="toc53"></a>[Asyncronous Operations](#asyncronous-operations)
        - <a name="toc54"></a>[Asyncronous Filter](#asyncronous-filter)

<!-- TOC -->


# <a href="#toc1">What</a>

You have a bunch of data, possibly streaming...

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

> In real life performance is often **better** then using imperative code, due to
`pycond's` [lazy evaluation](#context-on-demand-and-lazy-evaluation) feature. 

# <a href="#toc2">Why</a>

When the developer can decide upon the filters to apply on data he'll certainly
use Python's excellent expressive possibilities directly, e.g. as shown above
through list comprehensions.   
But what if the filtering conditions are based on decisions outside of the program's
control? I.e. from an end user, hitting the program via the network, in a somehow serialized form, which is rarely directly evaluatable Python.

This is the main use case for this module.  

## <a href="#toc3">Alternatives</a>

But why yet another tool for such a standard job?  

There is a list of great tools and frameworks where condition parsing is a (small) part of them, e.g. [pyke](http://pyke.sourceforge.net/) or [durable](https://pypi.python.org/pypi/durable_rules) and many in the django world or from SQL statement parsers.


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


`3.` Performance: Good enough to have "pyconditions" used within [stream filters](https://github.com/ReactiveX/RxPY).
With the current feature set we are sometimes a factor 2-3 worse but (due to lazy eval) often better,
compared with handcrafted list comprehensions.


# <a href="#toc4">Mechanics</a>

<!-- md_links_for: github -->
<!-- autogen tutorial -->

## <a href="#toc5">Parsing</a>
pycond parses the condition expressions according to a set of constraints given to the parser in the `tokenizer` function.
The result of the tokenizer is given to the builder.
  


```python
import pycond as pc

cond = '[a eq b and [c lt 42 or foo eq bar]]'
cond = pc.to_struct(pc.tokenize(cond, sep=' ', brkts='[]'))
print(cond)
return cond
```
Output:

```
[['a', 'eq', 'b', 'and', ['c', 'lt', '42', 'or', 'foo', 'eq', 'bar']]]
```


## <a href="#toc6">Building</a>
After parsing the builder is assembling a nested set of operator functions, combined via combining operators.
The functions are partials, i.e. not yet evaluated but information about the necessary keys is already
available:
  


```python
f, meta = pc.parse_cond('foo eq bar')
assert meta['keys'] == ['foo']
```

## <a href="#toc7">Structured Conditions</a>

Other processes may deliver condition structures via serializable formats (e.g. json).
If you hand such already tokenized constructs to pycond, then the tokenizer is bypassed:
  


```python
cond = [['a', 'eq', 'b'], 'or', ['c', 'in', ['foo', 'bar']]]
assert pc.pycond(cond)(state={'a': 'b'}) == True
# json support is built in:
cond_as_json = json.dumps(cond)
assert pc.pycond(cond_as_json)(state={'a': 'b'}) == True
```

# <a href="#toc8">Evaluation</a>

The result of the builder is a 'pycondition', which can be run many times against varying state of the system.
How state is evaluated is customizable at build and run time.

## <a href="#toc9">Default Lookup</a>

The default is to get lookup keys within expressions from an initially empty `State` dict within the module - which is *not* thread safe, i.e. not to be used in async or non cooperative multitasking environments.
  


```python
f = pc.pycond('foo eq bar')
assert f() == False
pc.State['foo'] = 'bar'  # not thread safe!
assert f() == True
```


(`pycond` is a shortcut for `parse_cond`, when meta infos are not required).

## <a href="#toc10">Passing State</a>

Use the state argument at evaluation:  


```python
assert pc.pycond('a gt 2')(state={'a': 42}) == True
assert pc.pycond('a gt 2')(state={'a': -2}) == False
```

### <a href="#toc11">Deep Lookup / Nested State / Lists</a>

You may supply a path seperator for diving into nested structures like so:  


```python
m = {'a': {'b': [{'c': 1}]}}
assert pc.pycond('a.b.0.c', deep='.')(state=m) == True
assert pc.pycond('a.b.1.c', deep='.')(state=m) == False
assert pc.pycond('a.b.0.c eq 1', deep='.')(state=m) == True
# convencience argument for string conditions:
assert pc.pycond('deep: a.b.0.c')(state=m) == True

# This is how you express deep access via structured conditions:
assert pc.pycond([('a', 'b', 0, 'c'), 'eq', 1])(state=m) == True

# Since tuples are not transferrable in json, we also allow deep paths as list:
# We apply heuristics to exclude expressions or conditions:
c = [[['a', 'b', 0, 'c'], 'eq', 1], 'and', 'a']
f, nfos = pc.parse_cond(c)
# sorting order for keys: tuples at end, sorted by len, rest default py sorted:
assert f(state=m) == True and nfos['keys'] == ['a', ('a', 'b', 0, 'c')]
print(nfos)
```
Output:

```
{'keys': ['a', ('a', 'b', 0, 'c')]}
```

## <a href="#toc12">Prefixed Data</a>

When data is passed through processing pipelines, it often is passed with headers. So it may be useful to pass a global prefix to access the payload like so:
  


```python
m = {'payload': {'b': [{'c': 1}], 'id': 123}}
assert pc.pycond('b.0.c', deep='.', prefix='payload')(state=m) == True
```


## <a href="#toc13">Custom Lookup And Value Passing</a>

You can supply your own function for value acquisition.

- Signature: See example.
- Returns: The value for the key from the current state plus the
  compare value for the operator function.  


```python
# must return a (key, value) tuple:
model = {'eve': {'last_host': 'somehost'}}

def my_lu(k, v, req, user, model=model):
    print('user check. locals:', dict(locals()))
    return (model.get(user) or {}).get(k), req[v]

f = pc.pycond('last_host eq host', lookup=my_lu)

req = {'host': 'somehost'}
assert f(req=req, user='joe') == False
assert f(req=req, user='eve') == True
```
Output:

```
user check. locals: {'k': 'last_host', 'v': 'host', 'req': {'host': 'somehost'}, 'user': 'joe', 'model': {'eve': {'last_host': 'somehost'}}}
user check. locals: {'k': 'last_host', 'v': 'host', 'req': {'host': 'somehost'}, 'user': 'eve', 'model': {'eve': {'last_host': 'somehost'}}}
```

> as you can see in the example, the state parameter is just a convention
for `pyconds'` [default lookup function][pycond.py#185].

## <a href="#toc14">Lazy Evaluation</a>

This is avoiding unnecessary calculations in many cases:

When an evaluation branch contains an "and" or "and_not" combinator, then
at runtime we evaluate the first expression - and stop if it is already
False.
Same when first expression is True, followed by "or" or "or_not".

That way expensive deep branch evaluations are omitted or, when
the lookup is done lazy, the values won't be even fetched:
  


```python
evaluated = []

def myget(key, val, cfg, state=None, **kw):
    evaluated.append(key)
    return pc.state_get(key, val, cfg, state, **kw)

f = pc.pycond('[a eq b] or foo eq bar and baz eq bar', lookup=myget)
assert f(state={'foo': 42}) == False
# the value for "baz" is not even fetched and the whole (possibly
# deep) branch after the last and is ignored:
assert evaluated == ['a', 'foo']
print(evaluated)
evaluated.clear()

f = pc.pycond('[[a eq b] or foo eq bar] and baz eq bar', lookup=myget)
assert f(state={'a': 'b', 'baz': 'bar'}) == True
# the value for "baz" is not even fetched and the whole (possibly
# deep) branch after the last and is ignored:
assert evaluated == ['a', 'baz']
print(evaluated)
```
Output:

```
['a', 'foo']
['a', 'baz']
```

Remember that all keys occurring in a condition (which may be provided by the user at runtime) are returned by the condition parser. Means that building of evaluation contexts [can be done](#context-on-demand-and-lazy-evaluation), based on the data actually needed and not more.

# <a href="#toc15">Details</a>

## <a href="#toc16">Debugging Lookups</a>

pycond provides a key getter which prints out every lookup.  


```python
f = pc.pycond('[[a eq b] or foo eq bar] or [baz eq bar]', lookup=pc.dbg_get)
assert f(state={'foo': 'bar'}) == True
```
Output:

```
Lookup: a b -> None
Lookup: foo bar -> bar
```

## <a href="#toc17">Enabling/Disabling of Branches</a>

Insert booleans like shown:  


```python
f = pc.pycond(['foo', 'and', ['bar', 'eq', 1]])
assert f(state={'foo': 1}) == False
f = pc.pycond(['foo', 'and', [True, 'or', ['bar', 'eq', 1]]])
assert f(state={'foo': 1}) == True
```

## <a href="#toc18">Building Conditions From Text</a>

Condition functions are created internally from structured expressions -
but those are [hard to type](#lazy-dynamic-context-assembly),
involving many apostropies.

The text based condition syntax is intended for situations when end users
type them into text boxes directly.

### <a href="#toc19">Grammar</a>

Combine atomic conditions with boolean operators and nesting brackets like:

```
[  <atom1> <and|or|and not|...> <atom2> ] <and|or...> [ [ <atom3> ....
```

### <a href="#toc20">Atomic Conditions</a>

```
[not] <lookup_key> [ [rev] [not] <condition operator (co)> <value> ]
```
- When just `lookup_key` is given, then `co` is set to the `truthy` function:
```python
def truthy(key, val=None):
    return operatur.truth(k)
```

so such an expression is valid and True:
  


```python
pc.State.update({'foo': 1, 'bar': 'a', 'baz': []})
assert pc.pycond('[ foo and bar and not baz]')() == True
```

- When `not lookup_key` is given, then `co` is set to the `falsy`
  function:
  


```python
m = {'x': 'y', 'falsy_val': {}}
# normal way
assert pc.pycond(['foo', 'eq', None])(state=m) == True
# using "not" as prefix:
assert pc.pycond('not foo')(state=m) == True
assert pc.pycond(['not', 'foo'])(state=m) == True
assert pc.pycond('not falsy_val')(state=m) == True
assert pc.pycond('x and not foo')(state=m) == True
assert pc.pycond('y and not falsy_val')(state=m) == False
```

## <a href="#toc21">Condition Operators</a>

All boolean [standardlib operators](https://docs.python.org/2/library/operator.html)
are available by default:
  


```python
from pytest2md import html_table as tbl  # just a table gen.
from pycond import get_ops

for k in 'nr', 'str':
    s = 'Default supported ' + k + ' operators...(click to extend)'
    print(tbl(get_ops()[k], [k + ' operator', 'alias'], summary=s))
```


<details><summary>Default supported nr operators...(click to extend)</summary>

<table>
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




<details><summary>Default supported str operators...(click to extend)</summary>

<table>
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




### <a href="#toc22">Using Symbolic Operators</a>

By default pycond uses text style operators.

- `ops_use_symbolic` switches processwide to symbolic style only.
- `ops_use_symbolic_and_txt` switches processwide to both notations allowed.
  


```python
pc.ops_use_symbolic()
pc.State['foo'] = 'bar'
assert pc.pycond('foo == bar')() == True
try:
    # this raises now, text ops not known anymore:
    pc.pycond('foo eq bar')
except:
    pc.ops_use_symbolic_and_txt(allow_single_eq=True)
    assert pc.pycond('foo = bar')() == True
    assert pc.pycond('foo == bar')() == True
    assert pc.pycond('foo eq bar')() == True
    assert pc.pycond('foo != baz')() == True
```


> Operator namespace(s) should be assigned at process start, they are global.

### <a href="#toc23">Extending Condition Operators</a>
  


```python
pc.OPS['maybe'] = lambda a, b: int(time.time()) % 2
# valid expression now:
assert pc.pycond('a maybe b')() in (True, False)
```


### <a href="#toc24">Negation `not`</a>

Negates the result of the condition operator:
  


```python
pc.State['foo'] = 'abc'
assert pc.pycond('foo eq abc')() == True
assert pc.pycond('foo not eq abc')() == False
```


### <a href="#toc25">Reversal `rev`</a>

Reverses the arguments before calling the operator  


```python
pc.State['foo'] = 'abc'
assert pc.pycond('foo contains a')() == True
assert pc.pycond('foo rev contains abc')() == True
```


> `rev` and `not` can be combined in any order.

### <a href="#toc26">Wrapping Condition Operators</a>

#### <a href="#toc27">Global Wrapping</a>
You may globally wrap all evaluation time condition operations through a custom function:
  


```python
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
pc.ops_use_symbolic_and_txt()
```


You may compose such wrappers via repeated application of the `run_all_ops_thru` API function.

#### <a href="#toc28">Condition Local Wrapping</a>

This is done through the `ops_thru` parameter as shown:
  


```python
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

## <a href="#toc29">Combining Operations</a>

You can combine single conditions with

- `and`
- `and not`
- `or`
- `or not`
- `xor` by default.

The combining functions are stored in `pycond.COMB_OPS` dict and may be extended.

> Do not use spaces for the names of combining operators. The user may use them but they are replaced at before tokenizing time, like `and not` -> `and_not`.

### <a href="#toc30">Nesting</a>

Combined conditions may be arbitrarily nested using brackets "[" and "]".

> Via the `brkts` config parameter you may change those to other separators at build time.

## <a href="#toc31">Tokenizing Details</a>

> Brackets as strings in this flat list form, e.g. `['[', 'a', 'and' 'b', ']'...]`

### <a href="#toc32">Functioning</a>

The tokenizers job is to take apart expression strings for the builder.

### <a href="#toc33">Separator `sep`</a>

Separates the different parts of an expression. Default is ' '.
  


```python
pc.State['a'] = 42
assert pc.pycond('a.eq.42', sep='.')() == True
```

> sep can be a any single character including binary.

Bracket characters do not need to be separated, the tokenizer will do:
  


```python
# equal:
assert (
    pc.pycond('[[a eq 42] and b]')() == pc.pycond('[ [ a eq 42 ] and b ]')()
)
```

> The condition functions themselves do not evaluate equal - those
> had been assembled two times.

### <a href="#toc34">Apostrophes</a>

By putting strings into Apostrophes you can tell the tokenizer to not further inspect them, e.g. for the seperator:
  


```python
pc.State['a'] = 'Hello World'
assert pc.pycond('a eq "Hello World"')() == True
```


### <a href="#toc35">Escaping</a>

Tell the tokenizer to not interpret the next character:
  


```python
pc.State['b'] = 'Hello World'
assert pc.pycond('b eq Hello\ World')() == True
```


### <a href="#toc36">Building</a>

### <a href="#toc37">Autoconv: Casting of values into python simple types</a>

Expression string values are automatically cast into bools and numbers via the public `pycond.py_type` function.

This can be prevented by setting the `autoconv` parameter to `False` or by using Apostrophes:
  


```python
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
for id in '1', 1:
    pc.State['id'] = id
    assert pc.pycond('id lt 42', autoconv_lookups=True)
```


## <a href="#toc38">Context On Demand</a>

Often the conditions are in user space, applied on data streams under
the developer's control only at development time.

The end user might pick only a few keys from many offered within an API.

pycond's `ctx_builder` allows to only calculate those keys at runtime,
the user decided to base conditions upon:
At condition build time hand over a namespace for *all* functions which
are available to build the ctx.

`pycon` will return a context builder function for you, calling only those functions
which the condition actually requires.
  


```python
pc.ops_use_symbolic_and_txt(allow_single_eq=True)

# Condition the end user configured, e.g. at program run time:
cond = [
    ['group_type', 'in', ['lab', 'first1k', 'friendly', 'auto']],
    'and',
    [
        [
            [
                [['cur_q', '<', 0.5], 'and', ['delta_q', '>=', 0.15],],
                'and',
                ['dt_last_enforce', '>', 28800],
            ],
            'and',
            ['cur_hour', 'in', [3, 4, 5]],
        ],
        'or',
        [
            [
                [['cur_q', '<', 0.5], 'and', ['delta_q', '>=', 0.15],],
                'and',
                ['dt_last_enforce', '>', 28800],
            ],
            'and',
            ['clients', '=', 0],
        ],
    ],
]

# Getters for API keys offered to the user, involving potentially
# expensive to fetch context delivery functions:
# Signature must provide minimum a positional for the current
# state:
class ApiCtxFuncs:
    def expensive_but_not_needed_here(ctx):
        raise Exception("Won't run with cond. from above")

    def cur_q(ctx):
        print('Calculating cur_q')
        return 0.1

    def cur_hour(ctx):
        print('Calculating cur_hour')
        return 4

    def dt_last_enforce(ctx):
        print('Calculating dt_last_enforce')
        return 10000000

    def delta_q(ctx):
        print('Calculating (expensive) delta_q')
        time.sleep(0.1)
        return 1

    def clients(ctx):
        print('Calculating clients')
        return 0

if sys.version_info[0] < 3:
    # we don't think it is a good idea to make the getter API stateful:
    p2m.convert_to_staticmethods(ApiCtxFuncs)

f, nfos = pc.parse_cond(cond, ctx_provider=ApiCtxFuncs)

# now we create (incomplete) data..
data1 = {'group_type': 'xxx'}, False
data2 = {'group_type': 'lab'}, True

# this key stores a context builder function, calculating the complete data:
make_ctx = nfos['complete_ctx']

t0 = time.time()
for event, expected in data1, data2:
    assert f(state=make_ctx(event)) == expected

print('Calc.Time (delta_q was called twice):', round(time.time() - t0, 4)),
return cond, ApiCtxFuncs
```
Output:

```
Calculating clients
Calculating cur_hour
Calculating cur_q
Calculating (expensive) delta_q
Calculating dt_last_enforce
Calculating clients
Calculating cur_hour
Calculating cur_q
Calculating (expensive) delta_q
Calculating dt_last_enforce
Calc.Time (delta_q was called twice): 0.2007
```


# <a href="#toc39">Lookup Providers</a>

ContextBuilders are interesting but we can do better.

We still calculated values for keys which might (dependent on the data) be not needed in dead ends of a lazily evaluated condition.

Lets avoid calculating these values, remembering the [custom lookup function](#custom-lookup-and-value-passing) feature.

This is where lookup providers come in, providing namespaces for functions to be called conditionally.

Pycond [treats the condition keys as function names][pycond.py#491] within that namespace and calls them, when needed.

## <a href="#toc40">Accepted Signatures</a>

Lookup provider functions may have the following signatures:
  


```python
class F:
    # simple data passing
    def f1(data):
        """simple return a value being compared, getting passed the state/data"""
        return data['a']

    # simple, with ctx
    def f2(data, **kw):
        """
        simple return a value being compared, getting passed the state/data
        All context information within kw, compare value not modifiable
        """
        return data['b']

    # full pycond compliant signature,
    def f3(key, val, cfg, data, **kw):
        """
        full pycond signature.
        val is the value as defined by the condition, and which you could return modified
        kw holds the cache, cfg holds the setup
        v has to be returned:
        """
        return data['c'], 100  # not 45!

    # applied al
    def f4(*a, **kw):
        """
        Full variant (always when varargs are involved)
        """
        return a[3]['d'], 'foo'

_ = 'and'
f = pc.pycond(
    [
        [':f1', 'eq', 42],
        _,
        [':f2', 'eq', 43, _, ':f3', 'eq', 45],
        _,
        [':f4', 'eq', 'foo'],
    ],
    lookup_provider=F,
)
assert f(state={'a': 42, 'b': 43, 'c': 100, 'd': 'foo'}) == True
```

## <a href="#toc41">Parametrized Lookup Functions</a>

Via the 'params' parameter you may supply keyword args to lookup functions:  


```python
class F:
    def hello(k, v, cfg, data, count, **kw):
        return data['foo'] == count, 0

m = pc.pycond(
    [':hello'], lookup_provider=F, params={'hello': {'count': 2}}
)(state={'foo': 2})
assert m == True
```


## <a href="#toc42">Namespace</a>

- Lookup functions can be found in nested class hirarchies or dicts. Separator is colon (':')
- As shown above, if they are flat within a toplevel class or dict you should still prefix with ':', to get build time exception (MissingLookupFunction) when not present
- You can switch that behaviour off per condition build as config arg, as shown below
- You can switch that behaviour off globally via `pc.prefixed_lookup_funcs = False`

Warning: This is a breaking API change with pre-20200610 versions, where the prefix was not required to find functions in, back then, only flat namespaces. Use the global switch after import to get the old behaviour.
  


```python
class F:
    a = lambda data: data['foo']

    class inner:
        b = lambda data: data['bar']

m = {'c': {'d': {'func': lambda data: data['baz']}}}

# for the inner lookup the first prefix may be omitted:
_ = 'and'
cond = [
    [':a', 'eq', 'foo1'],
    _,
    ['inner:b', 'eq', 'bar1'],
    _,
    ['c:d', 'eq', 'baz1',],
]
c = pc.pycond(cond, lookup_provider=F, lookup_provider_dict=m)
assert c(state={'foo': 'foo1', 'bar': 'bar1', 'baz': 'baz1'}) == True

# Prefix checking on / off:
try:
    pc.pycond([':xx', 'and', cond])
    i = 9 / 0  # above will raise this:
except pc.MissingLookupFunction:
    pass
try:
    pc.pycond([':xx', 'and', cond], prefixed_lookup_funcs=False)
    i = 9 / 0  # above will raise this:
except pc.MissingLookupFunction:
    pass
cond[0] = 'a'  # remove prefix, will still be found
c = pc.pycond(
    ['xx', 'or', cond],
    lookup_provider=F,
    lookup_provider_dict=m,
    prefixed_lookup_funcs=False,
)
assert c(state={'foo': 'foo1', 'bar': 'bar1', 'baz': 'baz1'}) == True
```

You can switch that prefix needs off - and pycond will then check the state for key presence:
  


```python
# we let pycond generate the lookup function (we use the simple signature type):
f = pc.pycond(
    cond, lookup_provider=ApiCtxFuncs, prefixed_lookup_funcs=False
)
# Same events as above:
data1 = {'group_type': 'xxx'}, False
data2 = {'group_type': 'lab'}, True

t0 = time.time()
for event, expected in data1, data2:
    # we will lookup only once:
    assert f(state=event) == expected

print(
    'Calc.Time (delta_q was called just once):', round(time.time() - t0, 4),
)

# The deep switch keeps working:
cond2 = [cond, 'or', ['a-0-b', 'eq', 42]]
f = pc.pycond(
    cond2,
    lookup_provider=ApiCtxFuncs,
    deep='-',
    prefixed_lookup_funcs=False,
)
data2[0]['a'] = [{'b': 42}]
print('sample:', data2[0])
assert f(state=data2[0]) == True
```
Output:

```
Calculating cur_q
Calculating (expensive) delta_q
Calculating dt_last_enforce
Calculating cur_hour
Calc.Time (delta_q was called just once): 0.1004
sample: {'group_type': 'lab', 'a': [{'b': 42}]}
Calculating cur_q
Calculating (expensive) delta_q
Calculating dt_last_enforce
Calculating cur_hour
```


The output demonstrates that we did not even call the value provider functions for the dead branches of the condition.

NOTE: Instead of providing a class tree you may also provide a dict of functions as `lookup_provider_dict` argument, see `qualify` examples below.

## <a href="#toc43">Caching</a>

Note: Currently you cannot override these defaults. Drop an issue if you need to.

- Builtin state lookups: Not cached
- Custom `lookup` functions: Not cached (you can implement caching within those functions)
- Lookup provider return values: Cached, i.e. called only once, per data set
- Named condition sets (see below): Cached

## <a href="#toc44">Extensions</a>

We deliver a few lookup function [extensions][pycond.py#590]

- for time checks
- for os.environ checks (re-evaluated at runtime)
  


```python
from datetime import datetime as dt
from os import environ as env

this_sec = dt.now().second
this_utc_hour = dt.utcnow().hour
f = pc.pycond(
    [
        ['env:foo', 'eq', 'bar'],
        'and',
        # not breaking the build when the sec just jumps:
        ['dt:second', 'in', [this_sec, this_sec + 1, 0]],
        'and',
        ['utc:hour', 'eq', this_utc_hour],
    ]
)
env['foo'] = 'bar'
assert f(state={'a': 1}) == True
```



# <a href="#toc45">Named Conditions: Qualification</a>

Instead of just delivering booleans, pycond can be used to determine a whole set of
information about data declaratively, like so:  


```python
# We accept different forms of delivery.
# The first full text is restricted to simple flat dicts only:
for c in [
    'one: a gt 10, two: a gt 10 or foo eq bar',
    {'one': 'a gt 10', 'two': 'a gt 10 or foo eq bar'},
    {
        'one': ['a', 'gt', 10],
        'two': ['a', 'gt', 10, 'or', 'foo', 'eq', 'bar'],
    },
]:
    f = pc.qualify(c)
    r = f({'foo': 'bar', 'a': 0})
    assert r == {'one': False, 'two': True}
```


We may refer to results of other named conditions and also can pass named condition sets as lists instead of dicts:  


```python
def run(q):
    print('Running', q)

    class F:
        def custom(data):
            return data.get('a')

    f = pc.qualify(q, lookup_provider=F)

    assert f({'a': 'b'}) == {
        'first': True,
        'listed': [False, False],
        'thrd': True,
        'zero': True,
        'last': True,
    }
    res = f({'c': 'foo', 'x': 1})
    assert res == {
        'first': False,
        'listed': [False, True],
        'thrd': False,
        'zero': True,
        'last': True,
    }

q = {
    'thrd': ['k', 'or', ':first'],
    'listed': [['foo'], ['c', 'eq', 'foo']],
    'zero': [['x', 'eq', 1], 'or', ':thrd'],
    'first': [':custom', 'eq', 'b'],
    'last': True,  # you might want to do this to always get at least one matcher, e.g. for data streaming
}
# as list of conditions:
run(q)

# as dict:
q = dict([[k, v] for k, v in q.items()])
run(q)
```
Output:

```
Running {'thrd': ['k', 'or', ':first'], 'listed': [['foo'], ['c', 'eq', 'foo']], 'zero': [['x', 'eq', 1], 'or', ':thrd'], 'first': [':custom', 'eq', 'b'], 'last': True}
Running {'thrd': ['k', 'or', ':first'], 'listed': [['foo'], ['c', 'eq', 'foo']], 'zero': [['x', 'eq', 1], 'or', ':thrd'], 'first': [':custom', 'eq', 'b'], 'last': True}
```

WARNING: For performance reasons there is no built in circular reference check. You'll run into python's built in recursion checker!

## <a href="#toc46">Options</a>

- into: Put the matched named conditions into the original data
- prefix: Work from a prefix nested in the root
- add_cached: Return also the data from function result cache

Here a few variants to parametrize behaviour, by example:  


```python
conds = {
    0: ['foo'],
    1: ['bar'],
    2: ['func'],
    3: ['n'],
    'n': ['bar'],
}

class F:
    def func(*a, **kw):
        return True, 0

q = lambda d, **kw: pc.qualify(
    conds, lookup_provider=F, prefixed_lookup_funcs=False, **kw
)(d)

m = q({'bar': 1})
assert m == {0: False, 1: True, 2: True, 3: True, 'n': True}

# return data, with matched conds in:
m = q({'bar': 1}, into='conds')
assert m == {
    'bar': 1,
    'conds': {0: False, 1: True, 2: True, 3: True, 'n': True},
}

msg = lambda: {'bar': 1, 'pl': {'a': 1}}

# add_cached == True -> it's put into the cond results:
m = q(msg(), into='conds', add_cached=True)
assert m == {
    'bar': 1,
    'conds': {0: False, 1: True, 2: True, 3: True, 'n': True, 'func': True},
    'pl': {'a': 1},
}

m = q(msg(), into='conds', add_cached='pl')
assert m == {
    'bar': 1,
    'conds': {0: False, 1: True, 2: True, 3: True, 'n': True},
    # n had been put into the cache, was not evaled twice:
    'pl': {'a': 1, 'func': True, 'n': True},
}

m = q({'bar': 1}, add_cached='pl')
assert m == {0: False, 1: True, 2: True, 3: True, 'n': True, 'func': True}

# prefix -> Nr 1, bar,  should NOT be True, since not in pl now:
m = q(msg(), prefix='pl', into='conds', add_cached='pl',)
assert m == {
    'bar': 1,
    'conds': {0: False, 1: False, 2: True, 3: False, 'n': False},
    'pl': {'a': 1, 'func': True, 'n': False},
}
```



## <a href="#toc47">Partial Evaluation</a>

If you either supply a key called 'root' OR supply it as argument to `qualify`, pycond will only evaluate named conditions required to calculate the root key:
  


```python
called = []

def expensive_func(k, v, cfg, data, **kw):
    called.append(data)
    return 1, v

def xx(k, v, cfg, data, **kw):
    called.append(data)
    return data.get('a'), v

funcs = {'exp': {'func': expensive_func}, 'xx': {'func': xx}}
q = {
    'root': ['foo', 'and', ':bar'],
    'bar': [['somecond'], 'or', [[':exp', 'eq', 1], 'and', ':baz'],],
    'x': [':xx'],
    'baz': [':exp', 'lt', 10],
}
qualifier = pc.qualify(q, lookup_provider_dict=funcs, add_cached=True)

d = {'foo': 1}
r = qualifier(d)

# root, bar, baz had been calculated, not x
assert r == {'root': True, 'bar': True, 'baz': True, 'exp': 1}
# expensive_func result, which was cached, is also returned.
# expensive_func only called once allthough result evaluated for bar and baz:
assert len(called) == 1

called.clear()
f = pc.qualify(q, lookup_provider_dict=funcs, root='x', add_cached=True)
assert f({'a': 1}) == {'x': True, 'xx': 1}
assert f({'b': 1}) == {'x': False, 'xx': None}
assert called == [{'a': 1}, {'b': 1}]
```

This means pycond can be used as a lightweight declarative function dispatching framework.
  

# <a href="#toc48">Streaming Data</a>

Since version 20200601 and Python 3.x versions, pycond can deliver [ReactiveX](https://github.com/ReactiveX/RxPY) compliant stream operators.

Lets first set up a test data stream, by defining a function `rx_setup` like so:
  


```python
# simply `import rx as Rx and rx = rx.operators`:
# import pycond as pc, like always:
Rx, rx, GS = pc.import_rx('GS')

def push_through(*test_pipe, items=4):
    """
    Function which takes a set of operators and runs an 'rx.interval' stream, until count items are through
    """

    # stream sink result holder plus a stream completer:
    l, compl = [], rx.take(items)
    l.clear()  # clear any previous results

    def next_(x):
        # simply remember what went through in a list:
        l.append(x)

    def err(*a):
        # should never happen:
        print('exception', a)

    stream = Rx.interval(0.01)  # numbers, each on its own thread

    # turns the ints into dicts: {'i': 1}, then {'i': 2} and so on:
    # (we start from 1, the first 0 we filter out)
    stream = stream.pipe(
        rx.filter(lambda i: i > 0), rx.map(lambda i: {'i': i})
    )

    # defines the stream through the tested operators:
    test_pipe = test_pipe + (compl,)
    s = stream.pipe(*test_pipe)

    # runs the stream:
    d = s.subscribe(
        on_error=err,
        on_next=next_,
        on_completed=lambda: l.append('completed'),
    )

    # blocks until completed:
    while not (l and l[-1] == 'completed'):
        time.sleep(0.001)
    l.pop()  # removes completed indicator

    return l  # returns all processed messages

return Rx, rx, push_through
```

Lets test the setup by having some messages streamed through:
  


```python
Rx, rx, push_through = rx_setup()
# test test setup:
r = push_through(items=3)
assert r == [{'i': 1}, {'i': 2}, {'i': 3}]
```

-> test setup works.

## <a href="#toc49">Filtering</a>

This is the most simple operation: A simple stream filter.
  


```python
Rx, rx, push_through = rx_setup()

# ask pycond for a stream filter based on a condition:
pcfilter = partial(pc.rxop, ['i', 'mod', 2])

r = push_through(pcfilter())
odds = [{'i': 1}, {'i': 3}, {'i': 5}, {'i': 7}]
assert r == odds

# try the stream filter with message headered data:
pl = 'payload'
r = push_through(rx.map(lambda i: {pl: i}), pcfilter(prefix=pl))
print('Full messages passed:', r)
r = [m[pl] for m in r]
assert len(r) == 4
assert r == odds
```
Output:

```
Full messages passed: [{'payload': {'i': 1}}, {'payload': {'i': 3}}, {'payload': {'i': 5}}, {'payload': {'i': 7}}]
```

## <a href="#toc50">Streaming Classification</a>

Using named condition dicts we can classify data, i.e. tag it, in order to process subsequently:
  


```python
Rx, rx, push_through = rx_setup()

# generate a set of classifiers:
conds = [['i', 'mod', i] for i in range(2, 4)]

def run(offs=0):

    # and get a classifying operator from pycond, adding the results in place, at key 'mod':
    r = push_through(pc.rxop(conds, into='mod'))
    i, j = 0 + offs, 1 + offs
    assert r == [
        {'i': 1, 'mod': {i: 1, j: 1}},
        {'i': 2, 'mod': {i: 0, j: 2}},
        {'i': 3, 'mod': {i: 1, j: 0}},
        {'i': 4, 'mod': {i: 0, j: 1}},
    ]

# this will automatically number the classifiers, from 0:
run()

# we can also provide the names of the classifiers by passing a dict:
# here we pass 2 and 3 as those names:
conds = dict([(i, ['i', 'mod', i]) for i in range(2, 4)])
run(2)
```

Normally the data has headers, so thats a good place to keep the classification tags.

### <a href="#toc51">Selective Classification</a>

We fall back to an alternative condition evaluation (which could be a function call) *only* when a previous condition evaluation returns something falsy - by providing a *root condition*.
When it evaluated, possibly requiring evaluation of other conditions, we return:  


```python
Rx, rx, push_through = rx_setup()

# using the list style:
conds = [[i, [['i', 'mod', i], 'or', ':alt']] for i in range(2, 4)]
conds.append(['alt', ['i', 'gt', 1]])

# provide the root condition. Only when it evals falsy, the named "alt" condiction will be evaluated:
r = push_through(pc.rxop(conds, into='mod', root=2, add_cached=True))

assert r == [
    # evaluation of alt was not required:
    {'i': 1, 'mod': {2: True}},
    # evaluation of alt was required:
    {'i': 2, 'mod': {2: True, 'alt': True}},
    {'i': 3, 'mod': {2: True}},
    {'i': 4, 'mod': {2: True, 'alt': True}},
]
```

#### <a href="#toc52">Treating of Booleans (Conditions, Not Names)</a>

For the special case of booleans in a condition list we do not treat them as names.  


```python
# 2 unnamed conditions -> keys will be positional
qs = pc.qualify([True, False])
res = qs({'a': 1})
assert res == {0: True, 1: False}  # and not {True: False}
# 2 named conds
qs = pc.qualify([[1, ['a', 'eq', 1]], [2, ['b', 'eq', 42]]])
res = qs({'a': 1})
assert res == {1: True, 2: False}
```

## <a href="#toc53">Asyncronous Operations</a>

WARNING: Early Version. Only for the gevent platform.

Selective classification allows to call condition functions only when other criteria are met.
That makes it possible to read e.g. from a database only when data is really required - and not always, "just in case".

pycond allows to define, that blocking operations should be run *async* within the stream, possibly giving up order.

### <a href="#toc54">Asyncronous Filter</a>

First a simple filter, which gives up order but does not block:
  


```python
Rx, rx, push_through = rx_setup()

class F:
    def check(k, v, cfg, data, t0=[], **kw):
        # will be on different thread:
        i, pointer = data['i'], ''
        if not t0:
            t0.append(now())
        if i == 1:
            # ints are fired at 0.01, i.e. the 1 will land 4 after 1:
            time.sleep(0.048)
            pointer = '   <----- not in order, blocked'
        # demonstrate that item 1 is not blocking anything - just order is disturbed:
        print('item %s: %.3fs %s' % (i, now() - t0[0], pointer))
        return i % 2, v

# have the operator built for us - with a single condition filter:
rxop = pc.rxop([':check'], into='mod', lookup_provider=F, asyn=['check'],)
r = push_through(rxop, items=5)
assert [m['i'] for m in r] == [3, 5, 1, 7, 9]
```
Output:

```
item 2: 0.011s 
item 3: 0.022s 
item 4: 0.033s 
item 5: 0.044s 
item 1: 0.048s    <----- not in order, blocked
item 6: 0.055s 
item 7: 0.065s 
item 8: 0.076s 
item 9: 0.087s
```

Finally asyncronous classification, i.e. evaluation of multiple conditions:
  


```python
_thn = lambda msg, data: print('thread:', cur_thread().name, msg, data)

# push_through just runs a stream of {'i': <nr>} through a given operator:
Rx, rx, push_through = rx_setup()

# Defining a simple 'set' of classifiers, here as list, with one single key: 42:
conds = [
    [
        42,
        [
            ['i', 'lt', 100],
            'and',
            [[':odd', 'eq', 1], 'or', ['i', 'eq', 2]],
            'and_not',
            [':blocking', 'eq', 3],
        ],
    ]
]

class F:
    """
    Namespace for condition lookup functions.
    You may also pass a dict (lookup_provider_dict)

    We provide the functions for 'odd' and 'blocking'.
    """

    def odd(k, v, cfg, data, **kw):
        # just print the threadname.
        # will go up, interval stream has each nr on its own thread:
        _thn('odd', data)
        # fullfill condition only for odd numbers
        # -> even nrs won't even run func 'blocking':
        return data['i'] % 2, v

    def blocking(k, v, cfg, data, **kw):
        i = data['i']
        # will be on different thread:
        _thn('blocking', data)
        if i == 1:
            # two others will "overtake the i=1 item,
            # since the interval stream is firing every 0.01 secs:
            time.sleep(0.028)
        elif i == 2:
            # Exceptions, incl. timeouts, will simply be forwarded to cfg['err_handler']
            # i.e. also timeout mgmt have to be done here, in the custom functions themselves.

            # Rationale for not providing a timeout monitoring within pycond itself:
            # Async ops are done with libs, which ship with their own timeout params.
            # No need to re-invent / overlay with our own monitoring of that.

            # In the err handler, then further arrangements can be done.
            raise TimeoutError('ups')
        elif i == 5:
            1 / 0
        return data['i'], v

errors = []

def handle_err(item, cfg, ctx, exc, t=errors, **kw):
    # args are: [item, cfg]
    if 'ups' in str(exc):
        assert item['i'] == 2
        assert exc.__class__ == TimeoutError
        t.append(item)
    else:
        assert item['i'] == 5
        assert exc.__class__ == ZeroDivisionError
        t.append(item)

# have the operator built for us:
rxop = pc.rxop(
    conds,
    into='mod',
    lookup_provider=F,
    err_handler=handle_err,
    asyn=['blocking'],
)
r = push_through(rxop, items=5)
assert [m['i'] for m in r] == [3, 1, 4, 6, 7]
assert [m['mod'][42] for m in r] == [False, True, False, False, True]
# item 2 caused a timeout:
assert [t['i'] for t in errors] == [2, 5]
```
Output:

```
thread: Thread-10054 odd {'i': 1}
thread: DummyThread-10056 blocking {'i': 1}
thread: Thread-10055 odd {'i': 2}
thread: DummyThread-10058 blocking {'i': 2}
thread: Thread-10057 odd {'i': 3}
thread: DummyThread-10060 blocking {'i': 3}
thread: Thread-10059 odd {'i': 4}
thread: Thread-10061 odd {'i': 5}
thread: DummyThread-10063 blocking {'i': 5}
thread: Thread-10062 odd {'i': 6}
thread: Thread-10064 odd {'i': 7}
thread: DummyThread-10066 blocking {'i': 7}
```


*Auto generated by [pytest2md](https://github.com/axiros/pytest2md), running [./tests/test_tutorial.py](./tests/test_tutorial.py)

<!-- autogen tutorial -->


<!-- autogenlinks -->
[pycond.py#185]: https://github.com/axiros/pycond/blob/26816201b5fec9889f3cdc82da1dd6aa3743f456/pycond.py#L185
[pycond.py#491]: https://github.com/axiros/pycond/blob/26816201b5fec9889f3cdc82da1dd6aa3743f456/pycond.py#L491
[pycond.py#590]: https://github.com/axiros/pycond/blob/26816201b5fec9889f3cdc82da1dd6aa3743f456/pycond.py#L590