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

... and you need to filter. For now lets say we have them already as list of dicts.

You can do it imperatively:

```python

or you have this module assemble a condition function from a declaration like:

```python

and then apply as often as you need, against varying state / facts / models (...):

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

## Evaluation

The result of the builder is a 'pycondition', which can be run many times against a varying state of the system.
How state is evaluated is customizable at build and run time.

### Default Lookup
The default is to get lookup keys within expressions from an initially empty `State` dict within the module.

```python

(`pycond` is a shortcut for `parse_cond`, when meta infos are not required).


### Custom Lookup & Value Passing

```python
Output:
```user check joe last_host host
## Building Conditions

### Grammar

Combine atomic conditions with boolean operators and nesting brackets like:

```

### Atomic Conditions

```
When just `lookup_key` given then `co` is set to the `truthy` function:

```python

so such an expression is valid and True:

```python

#### Condition Operators

All boolean [standardlib operators](https://docs.python.org/2/library/operator.html) are available by default:

```python


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

> Operator namespace(s) should be assigned at process start, they are global.


##### Extending Condition Operators

```python

#### Negation `not`

Negates the result of the condition operator:

```python

#### Reversal `rev`

Reverses the arguments before calling the operator
```python

> `rev` and `not` can be combined in any order.

##### Wrapping Condition Operators

##### Global Wrapping
You may globally wrap all evaluation time condition operations through a custom function:


```python

You may compose such wrappers via repeated application of the `run_all_ops_thru` API function.

##### Condition Local Wrapping

This is done through the `ops_thru` parameter as shown:

```python

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
> sep can be a any single character including binary.

Bracket characters do not need to be separated, the tokenizer will do:

```python
> The condition functions themselves do not evaluate equal - those
> had been assembled two times.

#### Apostrophes

By putting strings into Apostrophes you can tell the tokenizer to not further inspect them, e.g. for the seperator:

```python



#### Escaping

Tell the tokenizer to not interpret the next character:

```python


## Building

### Autoconv: Casting of values into python simple types

Expression string values are automatically cast into bools and numbers via the public `pycond.py_type` function.

This can be prevented by setting the `autoconv` parameter to `False` or by using Apostrophes:

```python

If you do not want to provide a custom lookup function (where you can do what you want)
but want to have looked up keys autoconverted then use:

```python

*Auto generated by [pytest_to_md](https://github.com/axiros/pytest_to_md), running [test_tutorial.py][test_tutorial.py]*

<!-- autogen tutorial -->


<!-- autogenlinks -->
[test_tutorial.py]: https://github.com/axiros/pycond/blob/4c980d656098c545666ebe5dd740d4535669b207/tests/test_tutorial.py