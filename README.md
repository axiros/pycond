---

author: gk
version: 20200613

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
- <a name="toc38"></a>[Context On Demand And Lazy Evaluation](#context-on-demand-and-lazy-evaluation)
    - <a name="toc39"></a>[Caching](#caching)
    - <a name="toc40"></a>[Named Conditions: Qualification](#named-conditions-qualification)
            - <a name="toc41"></a>[Options](#options)
        - <a name="toc42"></a>[Partial Evaluation](#partial-evaluation)
- <a name="toc43"></a>[Streaming Data](#streaming-data)
    - <a name="toc44"></a>[Filtering](#filtering)
    - <a name="toc45"></a>[Streaming Classification](#streaming-classification)
        - <a name="toc46"></a>[Selective Classification](#selective-classification)
    - <a name="toc47"></a>[Asyncronous Operations](#asyncronous-operations)
        - <a name="toc48"></a>[Asyncronous Filter](#asyncronous-filter)

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
  

Skipped: f0


## <a href="#toc6">Building</a>
After parsing the builder is assembling a nested set of operator functions, combined via combining operators.
The functions are partials, i.e. not yet evaluated but information about the necessary keys is already
available:
  

Skipped: f1

## <a href="#toc7">Structured Conditions</a>

Other processes may deliver condition structures via serializable formats (e.g. json).
If you hand such already tokenized constructs to pycond, then the tokenizer is bypassed:
  

Skipped: f1_1

# <a href="#toc8">Evaluation</a>

The result of the builder is a 'pycondition', which can be run many times against varying state of the system.
How state is evaluated is customizable at build and run time.

## <a href="#toc9">Default Lookup</a>

The default is to get lookup keys within expressions from an initially empty `State` dict within the module - which is *not* thread safe, i.e. not to be used in async or non cooperative multitasking environments.
  

Skipped: f2


(`pycond` is a shortcut for `parse_cond`, when meta infos are not required).

## <a href="#toc10">Passing State</a>

Use the state argument at evaluation:  

Skipped: f2_1

### <a href="#toc11">Deep Lookup / Nested State / Lists</a>

You may supply a path seperator for diving into nested structures like so:  

Skipped: f2_2

## <a href="#toc12">Prefixed Data</a>

When data is passed through processing pipelines, it often is passed with headers. So it may be useful to pass a global prefix to access the payload like so:
  

Skipped: f_21


## <a href="#toc13">Custom Lookup And Value Passing</a>

You can supply your own function for value acquisition.

- Signature: See example.
- Returns: The value for the key from the current state plus the
  compare value for the operator function.  

Skipped: f3

> as you can see in the example, the state parameter is just a convention
for `pyconds'` [default lookup function][pycond.py#186].

## <a href="#toc14">Lazy Evaluation</a>

This is avoiding unnecessary calculations in many cases:

When an evaluation branch contains an "and" or "and_not" combinator, then
at runtime we evaluate the first expression - and stop if it is already
False.
Same when first expression is True, followed by "or" or "or_not".

That way expensive deep branch evaluations are omitted or, when
the lookup is done lazy, the values won't be even fetched:
  

Skipped: f3_1

Remember that all keys occurring in a condition (which may be provided by the user at runtime) are returned by the condition parser. Means that building of evaluation contexts [can be done](#context-on-demand-and-lazy-evaluation), based on the data actually needed and not more.

# <a href="#toc15">Details</a>

## <a href="#toc16">Debugging Lookups</a>

pycond provides a key getter which prints out every lookup.  

Skipped: f3_2

## <a href="#toc17">Enabling/Disabling of Branches</a>

Insert booleans like shown:  

Skipped: f3_21

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
  

Skipped: f4

- When `not lookup_key` is given, then `co` is set to the `falsy`
  function:
  

Skipped: f4_11

## <a href="#toc21">Condition Operators</a>

All boolean [standardlib operators](https://docs.python.org/2/library/operator.html)
are available by default:
  

Skipped: f4_1


### <a href="#toc22">Using Symbolic Operators</a>

By default pycond uses text style operators.

- `ops_use_symbolic` switches processwide to symbolic style only.
- `ops_use_symbolic_and_txt` switches processwide to both notations allowed.
  

Skipped: f4_2


> Operator namespace(s) should be assigned at process start, they are global.

### <a href="#toc23">Extending Condition Operators</a>
  

Skipped: f5


### <a href="#toc24">Negation `not`</a>

Negates the result of the condition operator:
  

Skipped: f6


### <a href="#toc25">Reversal `rev`</a>

Reverses the arguments before calling the operator  

Skipped: f7


> `rev` and `not` can be combined in any order.

### <a href="#toc26">Wrapping Condition Operators</a>

#### <a href="#toc27">Global Wrapping</a>
You may globally wrap all evaluation time condition operations through a custom function:
  

Skipped: f8


You may compose such wrappers via repeated application of the `run_all_ops_thru` API function.

#### <a href="#toc28">Condition Local Wrapping</a>

This is done through the `ops_thru` parameter as shown:
  

Skipped: f9


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
  

Skipped: f9_1

> sep can be a any single character including binary.

Bracket characters do not need to be separated, the tokenizer will do:
  

Skipped: f10

> The condition functions themselves do not evaluate equal - those
> had been assembled two times.

### <a href="#toc34">Apostrophes</a>

By putting strings into Apostrophes you can tell the tokenizer to not further inspect them, e.g. for the seperator:
  

Skipped: f11


### <a href="#toc35">Escaping</a>

Tell the tokenizer to not interpret the next character:
  

Skipped: f12


### <a href="#toc36">Building</a>

### <a href="#toc37">Autoconv: Casting of values into python simple types</a>

Expression string values are automatically cast into bools and numbers via the public `pycond.py_type` function.

This can be prevented by setting the `autoconv` parameter to `False` or by using Apostrophes:
  

Skipped: f13


If you do not want to provide a custom lookup function (where you can do what you want)
but want to have looked up keys autoconverted then use:
  

Skipped: f14


# <a href="#toc38">Context On Demand And Lazy Evaluation</a>

Often the conditions are in user space, applied on data streams under
the developer's control only at development time.

The end user might pick only a few keys from many offered within an API.

pycond's `ctx_builder` allows to only calculate those keys at runtime,
the user decided to base conditions upon:
At condition build time hand over a namespace for *all* functions which
are available to build the ctx.

`pycon` will return a context builder function for you, calling only those functions
which the condition actually requires.
  

Skipped: f15_1


But we can do better - we still calculated values for keys which might be
only needed in dead ends of a lazily evaluated condition.

Lets avoid calculating these values, remembering the
[custom lookup function](#custom-lookup-and-value-passing) feature.

> pycond does generate such a custom lookup function readily for you,
> if you pass a getter namespace as `lookup_provider`.

Pycond then [treats the condition keys as function names][pycond.py#595] within that namespace and calls them, when needed, with the usual signature, except the key:
  

Skipped: f15_2


The output demonstrates that we did not even call the value provider functions for the dead branches of the condition.

NOTE: Instead of providing a class tree you may also provide a dict of functions as `lookup_provider_dict` argument, see `qualify` examples below.

## <a href="#toc39">Caching</a>

Note: Currently you cannot override these defaults. Drop an issue if you need to.

- Builtin state lookups: Not cached
- Custom `lookup` functions: Not cached (you can implment caching within those functions)
- Lookup provider return values: Cached, i.e. called only once
- Named conditions (see below): Cached

## <a href="#toc40">Named Conditions: Qualification</a>

Instead of just delivering booleans, pycond can be used to qualify a whole set of
information about data, like so:  

Skipped: f20_1


We may refer to results of other named conditions and also can pass named condition sets as lists instead of dicts:  


```python
def run(q):
    print('Running', q)
    f = pc.qualify(q)

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
    'thrd': ['k', 'or', 'first'],
    'listed': [['foo'], ['c', 'eq', 'foo']],
    'zero': [['x', 'eq', 1], 'or', 'thrd'],
    'first': ['a', 'eq', 'b'],
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
Running {'thrd': ['k', 'or', 'first'], 'listed': [['foo'], ['c', 'eq', 'foo']], 'zero': [['x', 'eq', 1], 'or', 'thrd'], 'first': ['a', 'eq', 'b'], 'last': True}
Running {'thrd': ['k', 'or', 'first'], 'listed': [['foo'], ['c', 'eq', 'foo']], 'zero': [['x', 'eq', 1], 'or', 'thrd'], 'first': ['a', 'eq', 'b'], 'last': True}
```

WARNING: For performance reasons there is no built in circular reference check. You'll run into python's built in recursion checker!

#### <a href="#toc41">Options</a>

- into: Put the matched named conditions into the original data
- prefix: Work from a prefix nested in the root
- add_cached: Return also the data from function result cache

Here a few variants to parametrize behaviour, by example:  


```python
conds = {0: ['foo'], 1: ['bar'], 2: ['func']}

class F:
    def func(*a, **kw):
        return True, 0

q = lambda d, **kw: pc.qualify(conds, lookup_provider=F, **kw)(d)

m = q({'bar': 1})
assert m == {0: False, 1: True, 2: True}

# return data, with matched conds in:
m = q({'bar': 1}, into='conds')
assert m == {'bar': 1, 'conds': {0: False, 1: True, 2: True}}

msg = lambda: {'bar': 1, 'pl': {'a': 1}}

# add_cached == True -> it's put into the cond results:
m = q(msg(), into='conds', add_cached=True)
assert m == {
    'bar': 1,
    'conds': {0: False, 1: True, 2: True, 'func': True},
    'pl': {'a': 1},
}

m = q(msg(), into='conds', add_cached='pl')
assert m == {
    'bar': 1,
    'conds': {0: False, 1: True, 2: True},
    'pl': {'a': 1, 'func': True},
}

m = q({'bar': 1}, add_cached='pl')
assert m == {0: False, 1: True, 2: True, 'func': True}

# prefix -> bar won't be True, not in pl now:
m = q(msg(), prefix='pl', into='conds', add_cached='pl',)
assert m == {
    'bar': 1,
    'conds': {0: False, 1: False, 2: True},
    'pl': {'a': 1, 'func': True},
}
```



### <a href="#toc42">Partial Evaluation</a>

If you either supply a key called 'root' OR supply it as argument to `qualify`, pycond will only evaluate named conditions required to calculate the root key:
  

Skipped: f20_4

This means pycond can be used as a lightweight declarative function dispatching framework.
  

# <a href="#toc43">Streaming Data</a>

Since version 20200601 and Python 3.x versions, pycond can deliver [ReactiveX](https://github.com/ReactiveX/RxPY) compliant stream operators.

Lets first set up a test data stream, by defining a function `rx_setup` like so:
  

Skipped: rx_setup

Lets test the setup by having some messages streamed through:
  

Skipped: rx_1

-> test setup works.

## <a href="#toc44">Filtering</a>

This is the most simple operation: A simple stream filter.
  

Skipped: rx_filter

## <a href="#toc45">Streaming Classification</a>

Using named condition dicts we can classify data, i.e. tag it, in order to process subsequently:
  

Skipped: rx_classifier

Normally the data has headers, so thats a good place to keep the classification tags.

### <a href="#toc46">Selective Classification</a>

We fall back to an alternative condition evaluation (which could be a function call) *only* when a previous condition evaluation returns something falsy - by providing a *root condition*.
When it evaluated, possibly requiring evaluation of other conditions, we return:  

Skipped: rx_class_sel

## <a href="#toc47">Asyncronous Operations</a>

WARNING: Early Version. Only for the gevent platform.

Selective classification allows to call condition functions only when other criteria are met.
That makes it possible to read e.g. from a database only when data is really required - and not always, "just in case".

pycond allows to define, that blocking operations should be run *async* within the stream, possibly giving up order.

### <a href="#toc48">Asyncronous Filter</a>

First a simple filter, which gives up order but does not block:
  

Skipped: rx_async_filter

Finally asyncronous classification, i.e. evaluation of multiple conditions:
  

Skipped: rx_async


*Auto generated by [pytest2md](https://github.com/axiros/pytest2md), running [./tests/test_tutorial.py](./tests/test_tutorial.py)

<!-- autogen tutorial -->


<!-- autogenlinks -->
[pycond.py#186]: https://github.com/axiros/pycond/blob/938c9c1324b8510876ac6692485f47480884e9e7/pycond.py#L186
[pycond.py#595]: https://github.com/axiros/pycond/blob/938c9c1324b8510876ac6692485f47480884e9e7/pycond.py#L595