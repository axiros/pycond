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
        """

        ## Parsing
        pycond parses the condition expressions according to a set of constraints given to the parser in the `tokenizer` function.
        The result of the tokenizer is given to the builder.


        ## Building
        After parsing the builder is assembling a nested set of operator functions, combined via combining operators.
        The functions are partials, i.e. not yet evaluated but information about the necessary keys is already
        available:

        """

        def f1():
            from pycond import parse_cond

            f, meta = parse_cond('foo eq bar')
            assert meta['keys'] == ['foo']

        """

        ## Evaluation

        The result of the builder is a 'pycondition', which can be run many times against a varying state of the system.
        How state is evaluated is customizable at build and run time.

        ### Default Lookup
        The default is to get lookup keys within expressions from an initially empty `State` dict within the module.

        """

        def f2():
            from pycond import pycond, State as S

            f = pycond('foo eq bar')
            assert f() == False
            S['foo'] = 'bar'
            assert f() == True

        """

        (`pycond` is a shortcut for `parse_cond`, when meta infos are not required).


        ### Custom Lookup & Value Passing

        """

        def f3():
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

        """
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

        """

        def f4():
            from pycond import pycond as p, State as S

            S.update({'foo': 1, 'bar': 'a', 'baz': []})
            assert p('[ foo and bar and not baz]')() == True

        """

        #### Condition Operators

        All boolean [standardlib operators](https://docs.python.org/2/library/operator.html) are available by default:

        """

        def f4_1():
            from pytest_to_md import html_table as tbl  # just a table gen.
            from pycond import get_ops

            for k in 'nr', 'str':
                s = 'Default supported ' + k + ' operators...(click to extend)'
                print(tbl(get_ops()[k], k + ' operator', 'alias', summary=s))

        """

        ##### Using Symbolic Operators

        By default pycond uses text style operators.

        - `ops_use_symbolic` switches processwide to symbolic style only.
        - `ops_use_both` switches processwide to both notations allowed.

        """

        def f4_2():
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

        """

        > Operator namespace(s) should be assigned at process start, they are global.


        ##### Extending Condition Operators

        """

        def f5():
            import time
            from pycond import pycond as p, OPS

            OPS['maybe'] = lambda a, b: int(time.time()) % 2

            assert p('a maybe b')() in (True, False)  # valid expression now.

        """

        #### Negation `not`

        Negates the result of the condition operator:

        """

        from pycond import pycond, State as S

        def f6():
            S['foo'] = 'abc'
            assert pycond('foo eq abc')() == True
            assert pycond('foo not eq abc')() == False

        """

        #### Reversal `rev`

        Reverses the arguments before calling the operator
        """

        def f7():

            S['foo'] = 'abc'
            assert pycond('foo contains a')() == True
            assert pycond('foo rev contains abc')() == True

        """

        > `rev` and `not` can be combined in any order.

        ##### Wrapping Condition Operators

        ##### Global Wrapping
        You may globally wrap all evaluation time condition operations through a custom function:


        """

        def f8():
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

        """

        You may compose such wrappers via repeated application of the `run_all_ops_thru` API function.

        ##### Condition Local Wrapping

        This is done through the `ops_thru` parameter as shown:

        """

        def f9():
            import pycond as pc

            def myhk(f_op, a, b):
                return True

            pc.State['a'] = 1
            f = pc.pycond('a eq 2')
            assert f() == False
            f = pc.pycond('a eq 2', ops_thru=myhk)
            assert f() == True

        """

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

        """

        def f9_1():
            import pycond as pc

            pc.State['a'] = 42
            assert pc.pycond('a.eq.42', sep='.')() == True

        """
        > sep can be a any single character including binary.

        Bracket characters do not need to be separated, the tokenizer will do:

        """

        def f10():
            import pycond as pc

            # equal:
            assert (
                pc.pycond('[[a eq 42] and b]')()
                == pc.pycond('[ [ a eq 42 ] and b ]')()
            )

        """
        > The condition functions themselves do not evaluate equal - those
        > had been assembled two times.

        #### Apostrophes

        By putting strings into Apostrophes you can tell the tokenizer to not further inspect them, e.g. for the seperator:

        """

        def f11():
            import pycond as pc

            pc.State['a'] = 'Hello World'

            assert pc.pycond('a eq "Hello World"')() == True

        """



        #### Escaping

        Tell the tokenizer to not interpret the next character:

        """

        def f12():
            import pycond as pc

            pc.State['b'] = 'Hello World'
            assert pc.pycond('b eq Hello\ World')() == True

        """


        ## Building

        ### Autoconv: Casting of values into python simple types

        Expression string values are automatically cast into bools and numbers via the public `pycond.py_type` function.

        This can be prevented by setting the `autoconv` parameter to `False` or by using Apostrophes:

        """

        def f13():
            import pycond as pc

            pc.State['a'] = '42'
            assert pc.pycond('a eq 42')() == False
            # compared as string now
            assert pc.pycond('a eq "42"')() == True
            # compared as string now
            assert pc.pycond('a eq 42', autoconv=False)() == True

        """

        If you do not want to provide a custom lookup function (where you can do what you want)
        but want to have looked up keys autoconverted then use:

        """

        def f14():
            import pycond as pc

            for id in '1', 1:
                pc.State['id'] = id
                assert pc.pycond('id lt 42', autoconv_lookups=True)

        ptm.md_from_source_code()
        ptm.write_readme(with_source_ref=True)
