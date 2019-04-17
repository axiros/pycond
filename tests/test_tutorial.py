"""
Creates Readme
"""
import pytest_to_md as ptm
import pytest, json, os, time
from functools import partial
from uuid import uuid4
import json

# py2.7 compat:
breakpoint = ptm.breakpoint

here, fn = ptm.setup(__file__, fn_target_md='../README.md')

# parametrizing the shell run results:
run = partial(ptm.bash_run, no_cmd_path=True)
md = ptm.md


class Test1:
    def test_mechanics(self):
        def f1():
            from pycond import parse_cond

            f, meta = parse_cond('foo eq bar')
            assert meta['keys'] == ['foo']

        def f2():
            from pycond import pycond, State as S

            f = pycond('foo eq bar')
            assert f() == False
            S['foo'] = 'bar'
            assert f() == True

        t = """

        ## Parsing
        pycond parses the condition expressions according to a set of constraints given to the parser in the `tokenizer` function.
        The result of the tokenizer is given to the builder.


        ## Building
        After parsing the builder is assembling a nested set of operator functions, combined via combining operators.
        The functions are partials, i.e. not yet evaluated but information about the necessary keys is already
        available:

        pyrun: f1

        ## Evaluation

        The result of the builder is a 'pycondition', which can be run many times against a varying state of the system.
        How state is evaluated is customizable at build and run time.

        ### Default Lookup
        The default is to get lookup keys within expressions from an initially empty `State` dict within the module.

        pyrun: f2

        (`pycond` is a shortcut for `parse_cond`, when meta infos are not required).

        """
        md(t)

        def f3():
            from pycond import pycond

            # must return a (key, value) tuple:
            model = {'joe': {'last_host': 'somehost'}}

            def my_lu(k, v, req, user, model=model):
                print('user check', user, k, v)
                return (model.get(user) or {}).get(k), req[v]

            f = pycond('last_host eq host', lookup=my_lu)

            req = {'host': 'somehost'}
            f(req=req, user='joe')  # True
            f(req=req, user='sally')  # False

        t = """

        ### Custom Lookup & Value Passing

        pyrun: f3
        """
        md(t)
        t = """
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

        so such an expression is valid `[ foo and bar and not baz]` and True e.g. for `S={'foo': 1, 'bar': 'a', 'baz': []}`

        #### Condition Operators

        All boolean [standardlib operators](https://docs.python.org/2/library/operator.html) are available by default.

        ##### Extending Condition Operators

        ```python
        from pycond import OPS
        OPS['maybe'] = lambda a, b: random.choice((True, False))

        'a maybe b' # valid expression now.
        ```

        > This way you can have math symbols instead operator names, e.g.:

        ```
        OPS['='] = OPS['eq']
        OPS['<='] = OPS['le']
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

        ##### Wrapping Condition Operators

        ##### Global Wrapping
        You may globally wrap all evaluation time condition operations through a custom function:

        ```python
        def hk(f_op, a, b, l=l):
            l.append((getattr(f_op, '__name__', ''), a, b))
            return f_op(a, b)

        pycon.run_all_ops_thru(hk) # globally wrap the operators

        S.update({'a': 1, 'b': 2, 'c': 3})
        f = pycond('a gt 0 and b lt 3 and not c gt 4')
        assert l == []
        f()
        expected_log = [  ('gt', 1, 0.0)
                        , ('lt', 2, 3.0)
                        , ('gt', 3, 4.0)]
        assert l == expected_log
        ```
        You may compose such wrappers via repeated application of the `run_all_ops_thru` API function.

        ##### Condition Local Wrapping

        This is done through the `ops_thru` parameter as shown:
        ```python
        def myhk(f_op, a, b):
            return True
        S['a'] = 1
        f = pycond('a eq 2')
        assert f() == False
        f = pycond('a eq 2', ops_thru=myhk)
        assert f() == True
        ```

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
        py_cond('a.eq.42', sep='.')
        ```
        > sep can be a any single character including binary.

        Bracket characters do not need to be separated, the tokenizer will do:

        ```
        # equal:
        py_cond('[[a eq 42] and b]')
        py_cond('[ [ a eq 42 ] and b ]')
        ```

        #### Apostrophes

        By putting strings into Apostrophes you can tell the tokenizer to not further inspect them, e.g. for the seperator:

        ```
        py_cond('a eq "Hello World"')
        ```



        #### Escaping

        Tell the tokenizer to not interpret the next character:

        ```
        py_cond('a eq Hello\ World')
        ```


        ## Building

        ### Autoconv: Casting of values into python simple types

        Expression string values are automatically cast into bools and numbers via the public `pycond.py_type` function.

        This can be prevented by setting the `autoconv` parameter to `False` or by using Apostrophes:

        ```
        py_cond('a eq "42"') # compared as string now
        py_cond('a eq 42', autoconv=False) # compared as string now
        ```

        If you do not want to provide a custom lookup function (where you can do what you want) but want to have looked up keys autoconverted then use:

        ```
        py_cond('id lt 42', autoconv_lookups=True) # True if S['id'] in ('1', 1, ...)
        ```
        """

    def test_insert_tutorial_into_readme(self):
        """addd the new version of the rendered tutorial into the main readme"""
        ptm.write_readme()
