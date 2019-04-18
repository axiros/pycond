# pycond: Lightweight Declarative Condition Expressions

[![Build Status](https://travis-ci.org/axiros/pycond.svg?branch=master)](https://travis-ci.org/axiros/pycond) [![codecov](https://codecov.io/gh/axiros/pycond/branch/master/graph/badge.svg)](https://codecov.io/gh/axiros/pycond)[![PyPI    version][pypisvg]][pypi] [![][blacksvg]][black]

[blacksvg]: https://img.shields.io/badge/code%20style-black-000000.svg
[black]: https://github.com/ambv/black
[pypisvg]: https://img.shields.io/pypi/v/pycond.svg
[pypi]: https://badge.fury.io/py/pycond

<!-- badges: http://thomas-cokelaer.info/blog/2014/08/1013/ -->


<hr/>
# Table Of Contents

- <a name="toc1"></a>[TODO](#todo)
<hr/>
# Table Of Contents

- <a name="toc2"></a>[What](#what)
<hr/>
# Table Of Contents

- <a name="toc3"></a>[Why](#why)
<hr/>
# Table Of Contents

    - <a name="toc4"></a>[Alternatives](#alternatives)
<hr/>
# Table Of Contents

- <a name="toc5"></a>[Mechanics](#mechanics)
<hr/>
# Table Of Contents

    - <a name="toc6"></a>[Parsing](#parsing)
<hr/>
# Table Of Contents

    - <a name="toc7"></a>[Building](#building)
<hr/>
# Table Of Contents

    - <a name="toc8"></a>[Structured Conditions](#structured-conditions)
<hr/>
# Table Of Contents

    - <a name="toc9"></a>[Evaluation](#evaluation)
<hr/>
# Table Of Contents

    - <a name="toc10"></a>[Default Lookup](#default-lookup)
<hr/>
# Table Of Contents

    - <a name="toc11"></a>[Passing Custom State](#passing-custom-state)
<hr/>
# Table Of Contents

    - <a name="toc12"></a>[Custom Lookup And Value Passing](#custom-lookup-and-value-passing)
<hr/>
# Table Of Contents

    - <a name="toc13"></a>[Lazy Evaluation](#lazy-evaluation)
<hr/>
# Table Of Contents

    - <a name="toc14"></a>[Building Conditions From Text](#building-conditions-from-text)
<hr/>
# Table Of Contents

        - <a name="toc15"></a>[Grammar](#grammar)
<hr/>
# Table Of Contents

        - <a name="toc16"></a>[Atomic Conditions](#atomic-conditions)
<hr/>
# Table Of Contents

    - <a name="toc17"></a>[Condition Operators](#condition-operators)
<hr/>
# Table Of Contents

        - <a name="toc18"></a>[Using Symbolic Operators](#using-symbolic-operators)
<hr/>
# Table Of Contents

        - <a name="toc19"></a>[Extending Condition Operators](#extending-condition-operators)
<hr/>
# Table Of Contents

        - <a name="toc20"></a>[Negation `not`](#negation-not)
<hr/>
# Table Of Contents

        - <a name="toc21"></a>[Reversal `rev`](#reversal-rev)
<hr/>
# Table Of Contents

        - <a name="toc22"></a>[Wrapping Condition Operators](#wrapping-condition-operators)
<hr/>
# Table Of Contents

            - <a name="toc23"></a>[Global Wrapping](#global-wrapping)
<hr/>
# Table Of Contents

            - <a name="toc24"></a>[Condition Local Wrapping](#condition-local-wrapping)
<hr/>
# Table Of Contents

    - <a name="toc25"></a>[Combining Operations](#combining-operations)
<hr/>
# Table Of Contents

        - <a name="toc26"></a>[Nesting](#nesting)
<hr/>
# Table Of Contents

    - <a name="toc27"></a>[Tokenizing Details](#tokenizing-details)
<hr/>
# Table Of Contents

        - <a name="toc28"></a>[Functioning](#functioning)
<hr/>
# Table Of Contents

        - <a name="toc29"></a>[Separator `sep`](#separator-sep)
<hr/>
# Table Of Contents

        - <a name="toc30"></a>[Apostrophes](#apostrophes)
<hr/>
# Table Of Contents

        - <a name="toc31"></a>[Escaping](#escaping)
<hr/>
# Table Of Contents

        - <a name="toc32"></a>[Building](#building)
<hr/>
# Table Of Contents

        - <a name="toc33"></a>[Autoconv: Casting of values into python simple types](#autoconv-casting-of-values-into-python-simple-types)
<hr/>
# Table Of Contents

- <a name="toc34"></a>[Context On Demand And Lazy Evaluation](#context-on-demand-and-lazy-evaluation)
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

# <a href="#toc1">TODO</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

- `safe_eval` option, wrapping atomic eval
<hr/>
# Table Of Contents

- lazy
<hr/>
# Table Of Contents

- single_eq
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

# <a href="#toc2">What</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

You have a bunch of data...
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```csv
<hr/>
# Table Of Contents

id,first_name,last_name,email,gender,ip_address
<hr/>
# Table Of Contents

1,Rufe,Morstatt,rmorstatt0@newsvine.de,Male,216.70.69.120
<hr/>
# Table Of Contents

2,Kaela,Scott,scott@opera.com,Female,73.248.145.44,2
<hr/>
# Table Of Contents

(...)
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

... and you need to filter. For now lets say we have them already as list of dicts.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

You can do it imperatively:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents

foo_users = [ u for u in users
<hr/>
# Table Of Contents

              if ([u['gender'] == 'Male' or u['last_name'] == 'Scott') and
<hr/>
# Table Of Contents

                  '@' in u['email']) ]
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

or you have this module assemble a condition function from a declaration like:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents

from pycond import parse_cond
<hr/>
# Table Of Contents

cond = 'email contains .de and gender eq Male or last_name eq Scott'
<hr/>
# Table Of Contents

is_foo = parse_cond(cond)
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

and then apply as often as you need, against varying state / facts / models (...):
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

foo_users = [ u for u in users if is_foo(state=u) ]
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

with roughly the same performance (factor 2-3) than the handcrafted python.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

> In real life performance is often **better** then using imperative code, due to
<hr/>
# Table Of Contents

`pycond's` [lazy evaluation](#lazy-evaluation) feature. 
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

# <a href="#toc3">Why</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

When the developer can decide upon the filters to apply on data he'll certainly
<hr/>
# Table Of Contents

use Python's excellent expressive possibilities directly, e.g. as shown above
<hr/>
# Table Of Contents

through list comprehensions.   
<hr/>
# Table Of Contents

But what if the filtering conditions are based on decisions outside of the program's
<hr/>
# Table Of Contents

control? I.e. from an end user, hitting the program via the network, in a somehow serialized form, which is rarely directly evaluatable Python.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

This is the main use case for this module.  
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

## <a href="#toc4">Alternatives</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

But why yet another tool for such a standard job?  
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

There is a list of great tools and frameworks where condition parsing is a (small) part of them, e.g. [pyke](http://pyke.sourceforge.net/) or [durable](https://pypi.python.org/pypi/durable_rules) and many in the django world or from SQL statement parsers.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

`1.` I just needed a very **slim** tool for only the parsing into functions - but this pretty transparent and customizable
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pycond allows to customize
<hr/>
# Table Of Contents

- the list of condition operators
<hr/>
# Table Of Contents

- the list of combination operators
<hr/>
# Table Of Contents

- the general behavior of condition operators via global or condition local wrappers
<hr/>
# Table Of Contents

- their names
<hr/>
# Table Of Contents

- the tokenizer
<hr/>
# Table Of Contents

- the value lookup function
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

and ships as zero dependency single module.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

All evaluation is done via [partials](https://stackoverflow.com/a/3252425/4583360) and not lambdas, i.e. operations can be introspected and debugged very simply, through breakpoints or custom logging operator or lookup wrappers.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

`2.` Simplicity of the grammar: Easy to type directly, readable by non
<hr/>
# Table Of Contents

programmers but also synthesisable from structured data, e.g. from a web framework.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

`3.` Performance: Good enough to have "pyconditions" used within [stream filters](https://github.com/ReactiveX/RxPY).
<hr/>
# Table Of Contents

With the current feature set we are sometimes a factor 2-3 worse but (due to lazy eval) often better,
<hr/>
# Table Of Contents

compared with handcrafted list comprehensions.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

# <a href="#toc5">Mechanics</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

<!-- md_links_for: github -->
<hr/>
# Table Of Contents

<!-- autogen tutorial -->
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

## <a href="#toc6">Parsing</a>
<hr/>
# Table Of Contents

pycond parses the condition expressions according to a set of constraints given to the parser in the `tokenizer` function.
<hr/>
# Table Of Contents

The result of the tokenizer is given to the builder.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

import pycond as pc
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

cond = '[a eq b and [c lt 42 or foo eq bar]]'
<hr/>
# Table Of Contents

cond = pc.to_struct(pc.tokenize(cond, sep=' ', brkts='[]'))
<hr/>
# Table Of Contents

print(cond)
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

Output:
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

[['a', 'eq', 'b', 'and', ['c', 'lt', '42', 'or', 'foo', 'eq', 'bar']]]
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

## <a href="#toc7">Building</a>
<hr/>
# Table Of Contents

After parsing the builder is assembling a nested set of operator functions, combined via combining operators.
<hr/>
# Table Of Contents

The functions are partials, i.e. not yet evaluated but information about the necessary keys is already
<hr/>
# Table Of Contents

available:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

f, meta = pc.parse_cond('foo eq bar')
<hr/>
# Table Of Contents

assert meta['keys'] == ['foo']
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

## <a href="#toc8">Structured Conditions</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Other processes may deliver condition structures via serializable formats (e.g. json).
<hr/>
# Table Of Contents

If you hand such already tokenized constructs to pycond, then the tokenizer is bypassed:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

cond = [['a', 'eq', 'b'], 'or', ['c', 'in', ['foo', 'bar']]]
<hr/>
# Table Of Contents

assert pc.pycond(cond)(state={'a': 'b'}) == True
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

## <a href="#toc9">Evaluation</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

The result of the builder is a 'pycondition', which can be run many times against a varying state of the system.
<hr/>
# Table Of Contents

How state is evaluated is customizable at build and run time.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

## <a href="#toc10">Default Lookup</a>
<hr/>
# Table Of Contents

The default is to get lookup keys within expressions from an initially empty `State` dict within the module.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

f = pc.pycond('foo eq bar')
<hr/>
# Table Of Contents

assert f() == False
<hr/>
# Table Of Contents

pc.State['foo'] = 'bar'
<hr/>
# Table Of Contents

assert f() == True
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

(`pycond` is a shortcut for `parse_cond`, when meta infos are not required).
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

## <a href="#toc11">Passing Custom State</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Use the state argument at evaluation:
<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

assert pc.pycond('a gt 2')(state={'a': 42}) == True
<hr/>
# Table Of Contents

assert pc.pycond('a gt 2')(state={'a': -2}) == False
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

## <a href="#toc12">Custom Lookup And Value Passing</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

You can supply your own function for value acquisition.
<hr/>
# Table Of Contents

- Signature: See example.
<hr/>
# Table Of Contents

- Returns: The value for the key from the current state plus the
<hr/>
# Table Of Contents

  compare value for the operator function.
<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

# must return a (key, value) tuple:
<hr/>
# Table Of Contents

model = {'eve': {'last_host': 'somehost'}}
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

def my_lu(k, v, req, user, model=model):
<hr/>
# Table Of Contents

    print('user check. locals:', dict(locals()))
<hr/>
# Table Of Contents

    return (model.get(user) or {}).get(k), req[v]
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

f = pc.pycond('last_host eq host', lookup=my_lu)
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

req = {'host': 'somehost'}
<hr/>
# Table Of Contents

assert f(req=req, user='joe') == False
<hr/>
# Table Of Contents

assert f(req=req, user='eve') == True
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

Output:
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

user check. locals: {'k': 'last_host', 'v': 'host', 'req': {'host': 'somehost'}, 'user': 'joe', 'model': {'eve': {'last_host': 'somehost'}}}
<hr/>
# Table Of Contents

user check. locals: {'k': 'last_host', 'v': 'host', 'req': {'host': 'somehost'}, 'user': 'eve', 'model': {'eve': {'last_host': 'somehost'}}}
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

> as you can see in the example, the state parameter is just a convention
<hr/>
# Table Of Contents

for `pyconds'` [title: default lookup function,fmatch=pycond.py,lmatch:def state_get
<hr/>
# Table Of Contents

function.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

## <a href="#toc13">Lazy Evaluation</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

This is avoiding unnecessary calculations in many cases:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

When an evaluation branch contains an "and" or "and_not" combinator, then
<hr/>
# Table Of Contents

at runtime we evaluate the first expression - and stop if it is already
<hr/>
# Table Of Contents

False. That way expensive deep branch evaluations are omitted or, when
<hr/>
# Table Of Contents

the lookup is done lazy, the values won't be even fetched:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

evaluated = []
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

def myget(key, val, cfg, state=None, **kw):
<hr/>
# Table Of Contents

    evaluated.append(key)
<hr/>
# Table Of Contents

    # lets say we are false - always:
<hr/>
# Table Of Contents

    return False, True
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

f = pc.pycond(
<hr/>
# Table Of Contents

    '[a eq b] or foo eq bar and baz eq bar', lookup=myget
<hr/>
# Table Of Contents

)
<hr/>
# Table Of Contents

f()
<hr/>
# Table Of Contents

# the value for "baz" is not even fetched and the whole (possibly
<hr/>
# Table Of Contents

# deep) branch after the last and is ignored:
<hr/>
# Table Of Contents

assert evaluated == ['a', 'foo']
<hr/>
# Table Of Contents

print(evaluated)
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

Output:
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

['a', 'foo']
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

## <a href="#toc14">Building Conditions From Text</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Condition functions are created internally from structured expressions -
<hr/>
# Table Of Contents

but those are [hard to type](#lazy-dynamic-context-assembly),
<hr/>
# Table Of Contents

involving many apostropies.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

The text based condition syntax is intended for situations when end users
<hr/>
# Table Of Contents

type them into text boxes directly.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc15">Grammar</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Combine atomic conditions with boolean operators and nesting brackets like:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

[  <atom1> <and|or|and not|...> <atom2> ] <and|or...> [ [ <atom3> ....
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc16">Atomic Conditions</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

<lookup_key> [ [rev] [not] <condition operator (co)> <value> ]
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

When just `lookup_key` is given, then `co` is set to the `truthy` function:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents

def truthy(key, val=None):
<hr/>
# Table Of Contents

    return operatur.truth(k)
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

so such an expression is valid and True:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.State.update({'foo': 1, 'bar': 'a', 'baz': []})
<hr/>
# Table Of Contents

assert pc.pycond('[ foo and bar and not baz]')() == True
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

## <a href="#toc17">Condition Operators</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

All boolean [standardlib operators](https://docs.python.org/2/library/operator.html)
<hr/>
# Table Of Contents

are available by default:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

from pytest2md import html_table as tbl  # just a table gen.
<hr/>
# Table Of Contents

from pycond import get_ops
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

for k in 'nr', 'str':
<hr/>
# Table Of Contents

    s = 'Default supported ' + k + ' operators...(click to extend)'
<hr/>
# Table Of Contents

    print(tbl(get_ops()[k], [k + ' operator', 'alias'], summary=s))
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

<details>
<hr/>
# Table Of Contents

        <summary>Default supported nr operators...(click to extend)</summary>
<hr/>
# Table Of Contents

        <table>
<hr/>
# Table Of Contents

<tr><td>nr operator</td><td>alias</td></tr>
<hr/>
# Table Of Contents

<tr><td>add</td><td>+</td></tr>
<hr/>
# Table Of Contents

<tr><td>and_</td><td>&</td></tr>
<hr/>
# Table Of Contents

<tr><td>eq</td><td>==</td></tr>
<hr/>
# Table Of Contents

<tr><td>floordiv</td><td>//</td></tr>
<hr/>
# Table Of Contents

<tr><td>ge</td><td>>=</td></tr>
<hr/>
# Table Of Contents

<tr><td>gt</td><td>></td></tr>
<hr/>
# Table Of Contents

<tr><td>iadd</td><td>+=</td></tr>
<hr/>
# Table Of Contents

<tr><td>iand</td><td>&=</td></tr>
<hr/>
# Table Of Contents

<tr><td>ifloordiv</td><td>//=</td></tr>
<hr/>
# Table Of Contents

<tr><td>ilshift</td><td><<=</td></tr>
<hr/>
# Table Of Contents

<tr><td>imod</td><td>%=</td></tr>
<hr/>
# Table Of Contents

<tr><td>imul</td><td>*=</td></tr>
<hr/>
# Table Of Contents

<tr><td>ior</td><td>|=</td></tr>
<hr/>
# Table Of Contents

<tr><td>ipow</td><td>**=</td></tr>
<hr/>
# Table Of Contents

<tr><td>irshift</td><td>>>=</td></tr>
<hr/>
# Table Of Contents

<tr><td>is_</td><td>is</td></tr>
<hr/>
# Table Of Contents

<tr><td>is_not</td><td>is</td></tr>
<hr/>
# Table Of Contents

<tr><td>isub</td><td>-=</td></tr>
<hr/>
# Table Of Contents

<tr><td>itruediv</td><td>/=</td></tr>
<hr/>
# Table Of Contents

<tr><td>ixor</td><td>^=</td></tr>
<hr/>
# Table Of Contents

<tr><td>le</td><td><=</td></tr>
<hr/>
# Table Of Contents

<tr><td>lshift</td><td><<</td></tr>
<hr/>
# Table Of Contents

<tr><td>lt</td><td><</td></tr>
<hr/>
# Table Of Contents

<tr><td>mod</td><td>%</td></tr>
<hr/>
# Table Of Contents

<tr><td>mul</td><td>*</td></tr>
<hr/>
# Table Of Contents

<tr><td>ne</td><td>!=</td></tr>
<hr/>
# Table Of Contents

<tr><td>or_</td><td>|</td></tr>
<hr/>
# Table Of Contents

<tr><td>pow</td><td>**</td></tr>
<hr/>
# Table Of Contents

<tr><td>rshift</td><td>>></td></tr>
<hr/>
# Table Of Contents

<tr><td>sub</td><td>-</td></tr>
<hr/>
# Table Of Contents

<tr><td>truediv</td><td>/</td></tr>
<hr/>
# Table Of Contents

<tr><td>xor</td><td>^</td></tr>
<hr/>
# Table Of Contents

<tr><td>itemgetter</td><td></td></tr>
<hr/>
# Table Of Contents

<tr><td>length_hint</td><td></td></tr>
<hr/>
# Table Of Contents

</table>
<hr/>
# Table Of Contents

        </details>
<hr/>
# Table Of Contents

        
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

<details>
<hr/>
# Table Of Contents

        <summary>Default supported str operators...(click to extend)</summary>
<hr/>
# Table Of Contents

        <table>
<hr/>
# Table Of Contents

<tr><td>str operator</td><td>alias</td></tr>
<hr/>
# Table Of Contents

<tr><td>attrgetter</td><td></td></tr>
<hr/>
# Table Of Contents

<tr><td>concat</td><td>+</td></tr>
<hr/>
# Table Of Contents

<tr><td>contains</td><td></td></tr>
<hr/>
# Table Of Contents

<tr><td>countOf</td><td></td></tr>
<hr/>
# Table Of Contents

<tr><td>iconcat</td><td>+=</td></tr>
<hr/>
# Table Of Contents

<tr><td>indexOf</td><td></td></tr>
<hr/>
# Table Of Contents

<tr><td>methodcaller</td><td></td></tr>
<hr/>
# Table Of Contents

</table>
<hr/>
# Table Of Contents

        </details>
<hr/>
# Table Of Contents

        
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc18">Using Symbolic Operators</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

By default pycond uses text style operators.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

- `ops_use_symbolic` switches processwide to symbolic style only.
<hr/>
# Table Of Contents

- `ops_use_symbolic_and_txt` switches processwide to both notations allowed.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.ops_use_symbolic()
<hr/>
# Table Of Contents

pc.State['foo'] = 'bar'
<hr/>
# Table Of Contents

assert pc.pycond('foo == bar')() == True
<hr/>
# Table Of Contents

try:
<hr/>
# Table Of Contents

    # this raises now, text ops not known anymore:
<hr/>
# Table Of Contents

    pc.pycond('foo eq bar')
<hr/>
# Table Of Contents

except:
<hr/>
# Table Of Contents

    pc.ops_use_symbolic_and_txt(allow_single_eq=True)
<hr/>
# Table Of Contents

    assert pc.pycond('foo = bar')() == True
<hr/>
# Table Of Contents

    assert pc.pycond('foo == bar')() == True
<hr/>
# Table Of Contents

    assert pc.pycond('foo eq bar')() == True
<hr/>
# Table Of Contents

    assert pc.pycond('foo != baz')() == True
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

> Operator namespace(s) should be assigned at process start, they are global.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc19">Extending Condition Operators</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.OPS['maybe'] = lambda a, b: int(time.time()) % 2
<hr/>
# Table Of Contents

# valid expression now:
<hr/>
# Table Of Contents

assert pc.pycond('a maybe b')() in (True, False)
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc20">Negation `not`</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Negates the result of the condition operator:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.State['foo'] = 'abc'
<hr/>
# Table Of Contents

assert pc.pycond('foo eq abc')() == True
<hr/>
# Table Of Contents

assert pc.pycond('foo not eq abc')() == False
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc21">Reversal `rev`</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Reverses the arguments before calling the operator
<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.State['foo'] = 'abc'
<hr/>
# Table Of Contents

assert pc.pycond('foo contains a')() == True
<hr/>
# Table Of Contents

assert pc.pycond('foo rev contains abc')() == True
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

> `rev` and `not` can be combined in any order.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc22">Wrapping Condition Operators</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

#### <a href="#toc23">Global Wrapping</a>
<hr/>
# Table Of Contents

You may globally wrap all evaluation time condition operations through a custom function:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

l = []
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

def hk(f_op, a, b, l=l):
<hr/>
# Table Of Contents

    l.append((getattr(f_op, '__name__', ''), a, b))
<hr/>
# Table Of Contents

    return f_op(a, b)
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.run_all_ops_thru(hk)  # globally wrap the operators
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.State.update({'a': 1, 'b': 2, 'c': 3})
<hr/>
# Table Of Contents

f = pc.pycond('a gt 0 and b lt 3 and not c gt 4')
<hr/>
# Table Of Contents

assert l == []
<hr/>
# Table Of Contents

f()
<hr/>
# Table Of Contents

expected_log = [('gt', 1, 0.0), ('lt', 2, 3.0), ('gt', 3, 4.0)]
<hr/>
# Table Of Contents

assert l == expected_log
<hr/>
# Table Of Contents

pc.ops_use_symbolic_and_txt()
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

You may compose such wrappers via repeated application of the `run_all_ops_thru` API function.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

#### <a href="#toc24">Condition Local Wrapping</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

This is done through the `ops_thru` parameter as shown:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

def myhk(f_op, a, b):
<hr/>
# Table Of Contents

    return True
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.State['a'] = 1
<hr/>
# Table Of Contents

f = pc.pycond('a eq 2')
<hr/>
# Table Of Contents

assert f() == False
<hr/>
# Table Of Contents

f = pc.pycond('a eq 2', ops_thru=myhk)
<hr/>
# Table Of Contents

assert f() == True
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

> Using `ops_thru` is a good way to debug unexpected results, since you
<hr/>
# Table Of Contents

> can add breakpoints or loggers there.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

## <a href="#toc25">Combining Operations</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

You can combine single conditions with
<hr/>
# Table Of Contents

- `and`
<hr/>
# Table Of Contents

- `and not`
<hr/>
# Table Of Contents

- `or`
<hr/>
# Table Of Contents

- `or not`
<hr/>
# Table Of Contents

- `xor` by default.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

The combining functions are stored in `pycond.COMB_OPS` dict and may be extended.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

> Do not use spaces for the names of combining operators. The user may use them but they are replaced at before tokenizing time, like `and not` -> `and_not`.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc26">Nesting</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Combined conditions may be arbitrarily nested using brackets "[" and "]".
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

> Via the `brkts` config parameter you may change those to other separators at build time.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

## <a href="#toc27">Tokenizing Details</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

> Brackets as strings in this flat list form, e.g. `['[', 'a', 'and' 'b', ']'...]`
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc28">Functioning</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

The tokenizers job is to take apart expression strings for the builder.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc29">Separator `sep`</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Separates the different parts of an expression. Default is ' '.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.State['a'] = 42
<hr/>
# Table Of Contents

assert pc.pycond('a.eq.42', sep='.')() == True
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

> sep can be a any single character including binary.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Bracket characters do not need to be separated, the tokenizer will do:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

# equal:
<hr/>
# Table Of Contents

assert (
<hr/>
# Table Of Contents

    pc.pycond('[[a eq 42] and b]')()
<hr/>
# Table Of Contents

    == pc.pycond('[ [ a eq 42 ] and b ]')()
<hr/>
# Table Of Contents

)
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

> The condition functions themselves do not evaluate equal - those
<hr/>
# Table Of Contents

> had been assembled two times.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc30">Apostrophes</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

By putting strings into Apostrophes you can tell the tokenizer to not further inspect them, e.g. for the seperator:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.State['a'] = 'Hello World'
<hr/>
# Table Of Contents

assert pc.pycond('a eq "Hello World"')() == True
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc31">Escaping</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Tell the tokenizer to not interpret the next character:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.State['b'] = 'Hello World'
<hr/>
# Table Of Contents

assert pc.pycond('b eq Hello\ World')() == True
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc32">Building</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

### <a href="#toc33">Autoconv: Casting of values into python simple types</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Expression string values are automatically cast into bools and numbers via the public `pycond.py_type` function.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

This can be prevented by setting the `autoconv` parameter to `False` or by using Apostrophes:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.State['a'] = '42'
<hr/>
# Table Of Contents

assert pc.pycond('a eq 42')() == False
<hr/>
# Table Of Contents

# compared as string now
<hr/>
# Table Of Contents

assert pc.pycond('a eq "42"')() == True
<hr/>
# Table Of Contents

# compared as string now
<hr/>
# Table Of Contents

assert pc.pycond('a eq 42', autoconv=False)() == True
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

If you do not want to provide a custom lookup function (where you can do what you want)
<hr/>
# Table Of Contents

but want to have looked up keys autoconverted then use:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

for id in '1', 1:
<hr/>
# Table Of Contents

    pc.State['id'] = id
<hr/>
# Table Of Contents

    assert pc.pycond('id lt 42', autoconv_lookups=True)
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

# <a href="#toc34">Context On Demand And Lazy Evaluation</a>
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Often the conditions are in user space, applied on data streams under
<hr/>
# Table Of Contents

the developer's control only at development time.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

The end user might pick only a few keys from many offered within an API.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pycond's `ctx_builder` allows to only calculate those keys at runtime,
<hr/>
# Table Of Contents

the user decided to base conditions upon:
<hr/>
# Table Of Contents

At condition build time hand over a namespace for *all* functions which
<hr/>
# Table Of Contents

are available to build the ctx.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

`pycon` will return a context builder function for you, calling only those functions
<hr/>
# Table Of Contents

which the condition actually requires.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

pc.ops_use_symbolic_and_txt(allow_single_eq=True)
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

# Condition the end user configured, e.g. at program run time:
<hr/>
# Table Of Contents

cond = [
<hr/>
# Table Of Contents

    ['group_type', 'in', ['lab', 'first1k', 'friendly', 'auto']],
<hr/>
# Table Of Contents

    'and',
<hr/>
# Table Of Contents

    [
<hr/>
# Table Of Contents

        [
<hr/>
# Table Of Contents

            [
<hr/>
# Table Of Contents

                [
<hr/>
# Table Of Contents

                    ['cur_q', '<', 0.5],
<hr/>
# Table Of Contents

                    'and',
<hr/>
# Table Of Contents

                    ['delta_q', '>=', 0.15],
<hr/>
# Table Of Contents

                ],
<hr/>
# Table Of Contents

                'and',
<hr/>
# Table Of Contents

                ['dt_last_enforce', '>', 28800],
<hr/>
# Table Of Contents

            ],
<hr/>
# Table Of Contents

            'and',
<hr/>
# Table Of Contents

            ['cur_hour', 'in', [3, 4, 5]],
<hr/>
# Table Of Contents

        ],
<hr/>
# Table Of Contents

        'or',
<hr/>
# Table Of Contents

        [
<hr/>
# Table Of Contents

            [
<hr/>
# Table Of Contents

                [
<hr/>
# Table Of Contents

                    ['cur_q', '<', 0.5],
<hr/>
# Table Of Contents

                    'and',
<hr/>
# Table Of Contents

                    ['delta_q', '>=', 0.15],
<hr/>
# Table Of Contents

                ],
<hr/>
# Table Of Contents

                'and',
<hr/>
# Table Of Contents

                ['dt_last_enforce', '>', 28800],
<hr/>
# Table Of Contents

            ],
<hr/>
# Table Of Contents

            'and',
<hr/>
# Table Of Contents

            ['clients', '=', 0],
<hr/>
# Table Of Contents

        ],
<hr/>
# Table Of Contents

    ],
<hr/>
# Table Of Contents

]
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

# Getters for API keys offered to the user, involving potentially
<hr/>
# Table Of Contents

# expensive to fetch context delivery functions:
<hr/>
# Table Of Contents

# Signature must provide minimum a positional for the current
<hr/>
# Table Of Contents

# state:
<hr/>
# Table Of Contents

class ApiCtxFuncs:
<hr/>
# Table Of Contents

    def expensive_but_not_needed_here(ctx):
<hr/>
# Table Of Contents

        raise Exception("Won't run with cond. from above")
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

    def group_type(ctx):
<hr/>
# Table Of Contents

        raise Exception(
<hr/>
# Table Of Contents

            "Won't run since contained in example data"
<hr/>
# Table Of Contents

        )
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

    def cur_q(ctx):
<hr/>
# Table Of Contents

        print('Calculating cur_q')
<hr/>
# Table Of Contents

        return 0.1
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

    def cur_hour(ctx):
<hr/>
# Table Of Contents

        print('Calculating cur_hour')
<hr/>
# Table Of Contents

        return 4
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

    def dt_last_enforce(ctx):
<hr/>
# Table Of Contents

        print('Calculating dt_last_enforce')
<hr/>
# Table Of Contents

        return 10000000
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

    def delta_q(ctx):
<hr/>
# Table Of Contents

        print('Calculating (expensive) delta_q')
<hr/>
# Table Of Contents

        time.sleep(0.1)
<hr/>
# Table Of Contents

        return 1
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

    def clients(ctx):
<hr/>
# Table Of Contents

        print('Calculating clients')
<hr/>
# Table Of Contents

        return 0
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

if sys.version_info[0] < 3:
<hr/>
# Table Of Contents

    # we don't think it is a good idea to make the getter API stateful:
<hr/>
# Table Of Contents

    p2m.convert_to_staticmethods(ApiCtxFuncs)
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

f, nfos = pc.parse_cond(cond, ctx_provider=ApiCtxFuncs)
<hr/>
# Table Of Contents

# this key stores the context builder function
<hr/>
# Table Of Contents

make_ctx = nfos['complete_ctx']
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

# now we get (incomplete) data..
<hr/>
# Table Of Contents

data1 = {'group_type': 'xxx'}, False
<hr/>
# Table Of Contents

data2 = {'group_type': 'lab'}, True
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

t0 = time.time()
<hr/>
# Table Of Contents

for event, expected in data1, data2:
<hr/>
# Table Of Contents

    assert pc.pycond(cond)(state=make_ctx(event)) == expected
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

print('Calc.Time', round(time.time() - t0, 4))
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

Output:
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

Calculating clients
<hr/>
# Table Of Contents

Calculating cur_hour
<hr/>
# Table Of Contents

Calculating cur_q
<hr/>
# Table Of Contents

Calculating (expensive) delta_q
<hr/>
# Table Of Contents

Calculating dt_last_enforce
<hr/>
# Table Of Contents

Calculating clients
<hr/>
# Table Of Contents

Calculating cur_hour
<hr/>
# Table Of Contents

Calculating cur_q
<hr/>
# Table Of Contents

Calculating (expensive) delta_q
<hr/>
# Table Of Contents

Calculating dt_last_enforce
<hr/>
# Table Of Contents

Calc.Time 0.2017
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

But we can do better - we still calculated values for keys which might be
<hr/>
# Table Of Contents

only needed in dead ends of a lazily evaluated condition.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

Lets avoid calculating these values, remembering the
<hr/>
# Table Of Contents

[custom lookup function](#custom-lookup-and-value-passing) feature.
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

> pycond does generate such a custom lookup function readily for you,
<hr/>
# Table Of Contents

> if you pass a getter namespace as `lookup_provider`:
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```python
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

# we let pycond generate the lookup function now:
<hr/>
# Table Of Contents

f = pc.pycond(cond, lookup_provider=ApiCtxFuncs)
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

# Same events as above:
<hr/>
# Table Of Contents

data1 = {'group_type': 'xxx'}, False
<hr/>
# Table Of Contents

data2 = {'group_type': 'lab'}, True
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

t0 = time.time()
<hr/>
# Table Of Contents

for event, expected in data1, data2:
<hr/>
# Table Of Contents

    # we will lookup only once:
<hr/>
# Table Of Contents

    assert f(state=event) == expected
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

print(
<hr/>
# Table Of Contents

    'Calc.Time (only one expensive calculation):',
<hr/>
# Table Of Contents

    round(time.time() - t0, 4),
<hr/>
# Table Of Contents

)
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

Output:
<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents

Calculating cur_q
<hr/>
# Table Of Contents

Calculating (expensive) delta_q
<hr/>
# Table Of Contents

Calculating dt_last_enforce
<hr/>
# Table Of Contents

Calculating cur_hour
<hr/>
# Table Of Contents

Calculating clients
<hr/>
# Table Of Contents

Calc.Time (only one expensive calculation): 0.1018
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

```
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

*Auto generated by [pytest2md](https://github.com/axiros/pytest2md), running [test_tutorial.py][test_tutorial.py]*
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

<!-- autogen tutorial -->
<hr/>
# Table Of Contents


<hr/>
# Table Of Contents


<hr/>
# Table Of Contents

<!-- autogenlinks -->
<hr/>
# Table Of Contents

[test_tutorial.py]: https://github.com/axiros/pycond/blob/82ec05de454f10c8c6074997b35923e2f23d9a0c/tests/test_tutorial.py