---

author: gk
version: 20200529

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
    - <a name="toc12"></a>[Custom Lookup And Value Passing](#custom-lookup-and-value-passing)
    - <a name="toc13"></a>[Lazy Evaluation](#lazy-evaluation)
- <a name="toc14"></a>[Details](#details)
    - <a name="toc15"></a>[Debugging Lookups](#debugging-lookups)
    - <a name="toc16"></a>[Building Conditions From Text](#building-conditions-from-text)
        - <a name="toc17"></a>[Grammar](#grammar)
        - <a name="toc18"></a>[Atomic Conditions](#atomic-conditions)
    - <a name="toc19"></a>[Condition Operators](#condition-operators)
        - <a name="toc20"></a>[Using Symbolic Operators](#using-symbolic-operators)
        - <a name="toc21"></a>[Extending Condition Operators](#extending-condition-operators)
        - <a name="toc22"></a>[Negation `not`](#negation-not)
        - <a name="toc23"></a>[Reversal `rev`](#reversal-rev)
        - <a name="toc24"></a>[Wrapping Condition Operators](#wrapping-condition-operators)
            - <a name="toc25"></a>[Global Wrapping](#global-wrapping)
            - <a name="toc26"></a>[Condition Local Wrapping](#condition-local-wrapping)
    - <a name="toc27"></a>[Combining Operations](#combining-operations)
        - <a name="toc28"></a>[Nesting](#nesting)
    - <a name="toc29"></a>[Tokenizing Details](#tokenizing-details)
        - <a name="toc30"></a>[Functioning](#functioning)
        - <a name="toc31"></a>[Separator `sep`](#separator-sep)
        - <a name="toc32"></a>[Apostrophes](#apostrophes)
        - <a name="toc33"></a>[Escaping](#escaping)
        - <a name="toc34"></a>[Building](#building)
        - <a name="toc35"></a>[Autoconv: Casting of values into python simple types](#autoconv-casting-of-values-into-python-simple-types)
- <a name="toc36"></a>[Context On Demand And Lazy Evaluation](#context-on-demand-and-lazy-evaluation)

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
`pycond's` [lazy evaluation](#lazy-evaluation) feature. 

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
```

# <a href="#toc8">Evaluation</a>

The result of the builder is a 'pycondition', which can be run many times against varying state of the system.
How state is evaluated is customizable at build and run time.

## <a href="#toc9">Default Lookup</a>

The default is to get lookup keys within expressions from an initially empty `State` dict within the module - which is *not* thread safe, i.e. not to be used in async  or non cooperative multitasking environments.
  


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
{'keys': ['a', ('a', 'b', 0, 'c')], 'foo': 'bar1'}
```


## <a href="#toc12">Custom Lookup And Value Passing</a>

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
for `pyconds'` [title: default lookup function,fmatch=pycond.py,lmatch:def state_get
function.

## <a href="#toc13">Lazy Evaluation</a>

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

# <a href="#toc14">Details</a>

## <a href="#toc15">Debugging Lookups</a>

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

## <a href="#toc16">Building Conditions From Text</a>

Condition functions are created internally from structured expressions -
but those are [hard to type](#lazy-dynamic-context-assembly),
involving many apostropies.

The text based condition syntax is intended for situations when end users
type them into text boxes directly.

### <a href="#toc17">Grammar</a>

Combine atomic conditions with boolean operators and nesting brackets like:

```
[  <atom1> <and|or|and not|...> <atom2> ] <and|or...> [ [ <atom3> ....
```

### <a href="#toc18">Atomic Conditions</a>

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

## <a href="#toc19">Condition Operators</a>

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




### <a href="#toc20">Using Symbolic Operators</a>

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


### <a href="#toc21">Extending Condition Operators</a>
  


```python
pc.OPS['maybe'] = lambda a, b: int(time.time()) % 2
# valid expression now:
assert pc.pycond('a maybe b')() in (True, False)
```


### <a href="#toc22">Negation `not`</a>

Negates the result of the condition operator:
  


```python
pc.State['foo'] = 'abc'
assert pc.pycond('foo eq abc')() == True
assert pc.pycond('foo not eq abc')() == False
```


### <a href="#toc23">Reversal `rev`</a>

Reverses the arguments before calling the operator  


```python
pc.State['foo'] = 'abc'
assert pc.pycond('foo contains a')() == True
assert pc.pycond('foo rev contains abc')() == True
```


> `rev` and `not` can be combined in any order.

### <a href="#toc24">Wrapping Condition Operators</a>

#### <a href="#toc25">Global Wrapping</a>
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

#### <a href="#toc26">Condition Local Wrapping</a>

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


## <a href="#toc27">Combining Operations</a>

You can combine single conditions with

- `and`
- `and not`
- `or`
- `or not`
- `xor` by default.

The combining functions are stored in `pycond.COMB_OPS` dict and may be extended.

> Do not use spaces for the names of combining operators. The user may use them but they are replaced at before tokenizing time, like `and not` -> `and_not`.

### <a href="#toc28">Nesting</a>

Combined conditions may be arbitrarily nested using brackets "[" and "]".

> Via the `brkts` config parameter you may change those to other separators at build time.


## <a href="#toc29">Tokenizing Details</a>


> Brackets as strings in this flat list form, e.g. `['[', 'a', 'and' 'b', ']'...]`

### <a href="#toc30">Functioning</a>

The tokenizers job is to take apart expression strings for the builder.

### <a href="#toc31">Separator `sep`</a>

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

### <a href="#toc32">Apostrophes</a>

By putting strings into Apostrophes you can tell the tokenizer to not further inspect them, e.g. for the seperator:
  


```python
pc.State['a'] = 'Hello World'
assert pc.pycond('a eq "Hello World"')() == True
```




### <a href="#toc33">Escaping</a>

Tell the tokenizer to not interpret the next character:
  


```python
pc.State['b'] = 'Hello World'
assert pc.pycond('b eq Hello\ World')() == True
```



### <a href="#toc34">Building</a>

### <a href="#toc35">Autoconv: Casting of values into python simple types</a>

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


# <a href="#toc36">Context On Demand And Lazy Evaluation</a>

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

    def group_type(ctx):
        raise Exception("Won't run since contained in example data")

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
Calc.Time (delta_q was called twice): 0.2006
```


But we can do better - we still calculated values for keys which might be
only needed in dead ends of a lazily evaluated condition.

Lets avoid calculating these values, remembering the
[custom lookup function](#custom-lookup-and-value-passing) feature.


> pycond does generate such a custom lookup function readily for you,
> if you pass a getter namespace as `lookup_provider`:
  


```python
# we add a deep condition and let pycond generate the lookup function:
f = pc.pycond(cond, lookup_provider=ApiCtxFuncs)

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
f = pc.pycond(cond2, lookup_provider=ApiCtxFuncs, deep='-')
data2[0]['a'] = [{'b': 42}]
assert f(state=data2[0]) == True
```
Output:

```
Calculating cur_q
Calculating (expensive) delta_q
Calculating dt_last_enforce
Calculating cur_hour
Calc.Time (delta_q was called just once): 0.1003
```

The output demonstrates that we did not even call the value provider functions for the dead branches of the condition.  


*Auto generated by [pytest2md](https://github.com/axiros/pytest2md), running [./tests/test_tutorial.py](./tests/test_tutorial.py)

<!-- autogen tutorial -->