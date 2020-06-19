"""
Creates The Tutorial Using pytest2md
"""

# we use gevent
import gevent

from gevent import monkey

try:
    monkey.patch_all()
except Exception as ex:
    os.environ['P2MSKIP'] = 'rx_async'

import pytest, json, os, time
import pytest2md as p2m  # this is our markdown tutorial generation tool
import pycond as pc  # the tested module:

from functools import partial
from uuid import uuid4
import time
import json
import sys
from threading import current_thread as cur_thread


# py2.7 compat:

p2m = p2m.P2M(__file__, fn_target_md='README.md')

# parametrizing the shell run results (not required here):
# run = partial(p2m.bash_run, no_cmd_path=True)
now = time.time

if sys.version_info[0] < 3:
    # no support:
    os.environ['P2MSKIP'] = 'rx_'


class Test1:
    def test_mechanics(self):
        """
        ## Parsing
        pycond parses the condition expressions according to a set of constraints given to the parser in the `tokenizer` function.
        The result of the tokenizer is given to the builder.

        """

        def f0():
            import pycond as pc

            cond = '[a eq b and [c lt 42 or foo eq bar]]'
            cond = pc.to_struct(pc.tokenize(cond, sep=' ', brkts='[]'))
            print(cond)
            return cond

        assert isinstance(f0(), list) and isinstance(f0()[0], list)
        """

        ## Building
        After parsing the builder is assembling a nested set of operator functions, combined via combining operators.
        The functions are partials, i.e. not yet evaluated but information about the necessary keys is already
        available:

        """

        def f1():
            f, meta = pc.parse_cond('foo eq bar')
            assert meta['keys'] == ['foo']

        """
        ## Structured Conditions

        Other processes may deliver condition structures via serializable formats (e.g. json).
        If you hand such already tokenized constructs to pycond, then the tokenizer is bypassed:

        """

        def f1_1():
            cond = [['a', 'eq', 'b'], 'or', ['c', 'in', ['foo', 'bar']]]
            assert pc.pycond(cond)(state={'a': 'b'}) == True
            # json support is built in:
            cond_as_json = json.dumps(cond)
            assert pc.pycond(cond_as_json)(state={'a': 'b'}) == True

        """
        # Evaluation

        The result of the builder is a 'pycondition', which can be run many times against varying state of the system.
        How state is evaluated is customizable at build and run time.

        ## Default Lookup

        The default is to get lookup keys within expressions from an initially empty `State` dict within the module - which is *not* thread safe, i.e. not to be used in async or non cooperative multitasking environments.

        """

        def f2():
            f = pc.pycond('foo eq bar')
            assert f() == False
            pc.State['foo'] = 'bar'  # not thread safe!
            assert f() == True

        """

        (`pycond` is a shortcut for `parse_cond`, when meta infos are not required).

        ## Passing State

        Use the state argument at evaluation:
        """

        def f2_1():
            assert pc.pycond('a gt 2')(state={'a': 42}) == True
            assert pc.pycond('a gt 2')(state={'a': -2}) == False

        """
        ### Deep Lookup / Nested State / Lists

        You may supply a path seperator for diving into nested structures like so:
        """

        def f2_2():
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

        """
        ## Prefixed Data

        When data is passed through processing pipelines, it often is passed with headers. So it may be useful to pass a global prefix to access the payload like so:

        """

        def f_21():
            m = {'payload': {'b': [{'c': 1}], 'id': 123}}
            assert pc.pycond('b.0.c', deep='.', prefix='payload')(state=m) == True

        """

        ## Custom Lookup And Value Passing

        You can supply your own function for value acquisition.

        - Signature: See example.
        - Returns: The value for the key from the current state plus the
          compare value for the operator function.
        """

        def f3():
            # must return a (key, value) tuple:
            model = {'eve': {'last_host': 'somehost'}}

            def my_lu(k, v, req, user, model=model):
                print('user check. locals:', dict(locals()))
                return (model.get(user) or {}).get(k), req[v]

            f = pc.pycond('last_host eq host', lookup=my_lu)

            req = {'host': 'somehost'}
            assert f(req=req, user='joe') == False
            assert f(req=req, user='eve') == True

        """
        > as you can see in the example, the state parameter is just a convention
        for `pyconds'` [title: default lookup function,fmatch:pycond.py,lmatch:def state_get]<SRC>.

        ## Lazy Evaluation

        This is avoiding unnecessary calculations in many cases:

        When an evaluation branch contains an "and" or "and_not" combinator, then
        at runtime we evaluate the first expression - and stop if it is already
        False.
        Same when first expression is True, followed by "or" or "or_not".

        That way expensive deep branch evaluations are omitted or, when
        the lookup is done lazy, the values won't be even fetched:

        """

        def f3_1():
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

        """
        Remember that all keys occurring in a condition (which may be provided by the user at runtime) are returned by the condition parser. Means that building of evaluation contexts [can be done](#context-on-demand-and-lazy-evaluation), based on the data actually needed and not more.

        # Details

        ## Debugging Lookups

        pycond provides a key getter which prints out every lookup.
        """

        def f3_2():
            f = pc.pycond('[[a eq b] or foo eq bar] or [baz eq bar]', lookup=pc.dbg_get)
            assert f(state={'foo': 'bar'}) == True

        """
        ## Enabling/Disabling of Branches

        Insert booleans like shown:
        """

        def f3_21():
            f = pc.pycond(['foo', 'and', ['bar', 'eq', 1]])
            assert f(state={'foo': 1}) == False
            f = pc.pycond(['foo', 'and', [True, 'or', ['bar', 'eq', 1]]])
            assert f(state={'foo': 1}) == True

        """
        ## Building Conditions From Text

        Condition functions are created internally from structured expressions -
        but those are [hard to type](#lazy-dynamic-context-assembly),
        involving many apostropies.

        The text based condition syntax is intended for situations when end users
        type them into text boxes directly.

        ### Grammar

        Combine atomic conditions with boolean operators and nesting brackets like:

        ```
        [  <atom1> <and|or|and not|...> <atom2> ] <and|or...> [ [ <atom3> ....
        ```

        ### Atomic Conditions

        ```
        [not] <lookup_key> [ [rev] [not] <condition operator (co)> <value> ]
        ```
        - When just `lookup_key` is given, then `co` is set to the `truthy` function:
        ```python
        def truthy(key, val=None):
            return operatur.truth(k)
        ```

        so such an expression is valid and True:

        """

        def f4():
            pc.State.update({'foo': 1, 'bar': 'a', 'baz': []})
            assert pc.pycond('[ foo and bar and not baz]')() == True

        """
        - When `not lookup_key` is given, then `co` is set to the `falsy`
          function:

        """

        def f4_11():
            m = {'x': 'y', 'falsy_val': {}}
            # normal way
            assert pc.pycond(['foo', 'eq', None])(state=m) == True
            # using "not" as prefix:
            assert pc.pycond('not foo')(state=m) == True
            assert pc.pycond(['not', 'foo'])(state=m) == True
            assert pc.pycond('not falsy_val')(state=m) == True
            assert pc.pycond('x and not foo')(state=m) == True
            assert pc.pycond('y and not falsy_val')(state=m) == False

        """
        ## Condition Operators

        All boolean [standardlib operators](https://docs.python.org/2/library/operator.html)
        are available by default:

        """

        def f4_1():
            from pytest2md import html_table as tbl  # just a table gen.
            from pycond import get_ops

            for k in 'nr', 'str':
                s = 'Default supported ' + k + ' operators...(click to extend)'
                print(tbl(get_ops()[k], [k + ' operator', 'alias'], summary=s))

        """

        ### Using Symbolic Operators

        By default pycond uses text style operators.

        - `ops_use_symbolic` switches processwide to symbolic style only.
        - `ops_use_symbolic_and_txt` switches processwide to both notations allowed.

        """

        def f4_2():
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

        """

        > Operator namespace(s) should be assigned at process start, they are global.

        ### Extending Condition Operators

        """

        def f5():
            pc.OPS['maybe'] = lambda a, b: int(time.time()) % 2
            # valid expression now:
            assert pc.pycond('a maybe b')() in (True, False)

        """

        ### Negation `not`

        Negates the result of the condition operator:

        """

        def f6():
            pc.State['foo'] = 'abc'
            assert pc.pycond('foo eq abc')() == True
            assert pc.pycond('foo not eq abc')() == False

        """

        ### Reversal `rev`

        Reverses the arguments before calling the operator
        """

        def f7():

            pc.State['foo'] = 'abc'
            assert pc.pycond('foo contains a')() == True
            assert pc.pycond('foo rev contains abc')() == True

        """

        > `rev` and `not` can be combined in any order.

        ### Wrapping Condition Operators

        #### Global Wrapping
        You may globally wrap all evaluation time condition operations through a custom function:

        """

        def f8():
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

        """

        You may compose such wrappers via repeated application of the `run_all_ops_thru` API function.

        #### Condition Local Wrapping

        This is done through the `ops_thru` parameter as shown:

        """

        def f9():
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

        ## Combining Operations

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

        ## Tokenizing Details

        > Brackets as strings in this flat list form, e.g. `['[', 'a', 'and' 'b', ']'...]`

        ### Functioning

        The tokenizers job is to take apart expression strings for the builder.

        ### Separator `sep`

        Separates the different parts of an expression. Default is ' '.

        """

        def f9_1():
            pc.State['a'] = 42
            assert pc.pycond('a.eq.42', sep='.')() == True

        """
        > sep can be a any single character including binary.

        Bracket characters do not need to be separated, the tokenizer will do:

        """

        def f10():
            # equal:
            assert (
                pc.pycond('[[a eq 42] and b]')() == pc.pycond('[ [ a eq 42 ] and b ]')()
            )

        """
        > The condition functions themselves do not evaluate equal - those
        > had been assembled two times.

        ### Apostrophes

        By putting strings into Apostrophes you can tell the tokenizer to not further inspect them, e.g. for the seperator:

        """

        def f11():
            pc.State['a'] = 'Hello World'
            assert pc.pycond('a eq "Hello World"')() == True

        """

        ### Escaping

        Tell the tokenizer to not interpret the next character:

        """

        def f12():
            pc.State['b'] = 'Hello World'
            assert pc.pycond('b eq Hello\ World')() == True

        """

        ### Building

        ### Autoconv: Casting of values into python simple types

        Expression string values are automatically cast into bools and numbers via the public `pycond.py_type` function.

        This can be prevented by setting the `autoconv` parameter to `False` or by using Apostrophes:

        """

        def f13():
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
            for id in '1', 1:
                pc.State['id'] = id
                assert pc.pycond('id lt 42', autoconv_lookups=True)

        """

        ## Context On Demand

        Often the conditions are in user space, applied on data streams under
        the developer's control only at development time.

        The end user might pick only a few keys from many offered within an API.

        pycond's `ctx_builder` allows to only calculate those keys at runtime,
        the user decided to base conditions upon:
        At condition build time hand over a namespace for *all* functions which
        are available to build the ctx.

        `pycon` will return a context builder function for you, calling only those functions
        which the condition actually requires.

        """

        def f15_1():
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

        cond, ApiCtxFuncs = f15_1()
        """

        # Lookup Providers

        ContextBuilders are interesting but we can do better.

        We still calculated values for keys which might (dependent on the data) be not needed in dead ends of a lazily evaluated condition.

        Lets avoid calculating these values, remembering the [custom lookup function](#custom-lookup-and-value-passing) feature.

        This is where lookup providers come in, providing namespaces for functions to be called conditionally.

        Pycond [title: treats the condition keys as function names,fmatch:pycond.py,lmatch:def f_from_lookup_provider]<SRC> within that namespace and calls them, when needed.

        ## Accepted Signatures

        Lookup provider functions may have the following signatures:

        """

        def f15_11():
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

                # full pycond compliant signature
                def f3(key, val, cfg, data, **kw):
                    """
                    full pycond signature.
                    val is the value as defined by the condition, and which you could return modified
                    kw holds the cache, cfg holds the setup
                    """
                    return data['c'], 100  # not 45!

            _ = 'and'
            f = pc.pycond(
                [[':f1', 'eq', 42], _, [':f2', 'eq', 43, _, ':f3', 'eq', 45]],
                lookup_provider=F,
            )
            assert f(state={'a': 42, 'b': 43, 'c': 100}) == True

        """

        ## Namespace

        - Lookup functions can be found in nested class hirarchies or dicts. Separator is colon (':')
        - As shown above, if they are flat within a toplevel class or dict you should still prefix with ':', to get build time exception (MissingLookupFunction) when not present
        - You can switch that behaviour off per condition build as config arg, as shown below
        - You can switch that behaviour off globally via `pc.prefixed_lookup_funcs = False`

        Warning: This is a breaking API change with pre-20200610 versions, where the prefix was not required to find functions in, back then, only flat namespaces. Use the global switch after import to get the old behaviour.
        
        """

        def f15_15():
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

        """
        You can switch that prefix needs off - and pycond will then check the state for key presence:

        """

        def f15_2():
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

        from pytest2md import html_table as tbl  # just a table gen.

        """
        The output demonstrates that we did not even call the value provider functions for the dead branches of the condition.

        NOTE: Instead of providing a class tree you may also provide a dict of functions as `lookup_provider_dict` argument, see `qualify` examples below.

        ## Caching

        Note: Currently you cannot override these defaults. Drop an issue if you need to.

        - Builtin state lookups: Not cached
        - Custom `lookup` functions: Not cached (you can implement caching within those functions)
        - Lookup provider return values: Cached, i.e. called only once, per data set
        - Named condition sets (see below): Cached

        ## Extensions

        We deliver a few lookup function [title: extensions,fmatch:pycond.py,lmatch:class Extensions]<SRC>

        - for time checks
        - for os.environ checks (re-evaluated at runtime)

        """

        def f16_1():
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

        """


        # Named Conditions: Qualification

        Instead of just delivering booleans, pycond can be used to determine a whole set of
        information about data declaratively, like so:
        """

        def f20_1():
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

        """

        We may refer to results of other named conditions and also can pass named condition sets as lists instead of dicts:
        """

        def f20_3():
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

        """
        WARNING: For performance reasons there is no built in circular reference check. You'll run into python's built in recursion checker!

        ## Options

        - into: Put the matched named conditions into the original data
        - prefix: Work from a prefix nested in the root
        - add_cached: Return also the data from function result cache

        Here a few variants to parametrize behaviour, by example:
        """

        def f20_31():

            conds = {0: ['foo'], 1: ['bar'], 2: ['func']}

            class F:
                def func(*a, **kw):
                    return True

            q = lambda d, **kw: pc.qualify(
                conds, lookup_provider=F, prefixed_lookup_funcs=False, **kw
            )(d)

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

        """


        ## Partial Evaluation

        If you either supply a key called 'root' OR supply it as argument to `qualify`, pycond will only evaluate named conditions required to calculate the root key:

        """

        def f20_4():
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

        """
        This means pycond can be used as a lightweight declarative function dispatching framework.

        """

        """
        # Streaming Data

        Since version 20200601 and Python 3.x versions, pycond can deliver [ReactiveX](https://github.com/ReactiveX/RxPY) compliant stream operators.

        Lets first set up a test data stream, by defining a function `rx_setup` like so:

        """

        def rx_setup():
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

        """
        Lets test the setup by having some messages streamed through:

        """

        def rx_1():
            Rx, rx, push_through = rx_setup()
            # test test setup:
            r = push_through(items=3)
            assert r == [{'i': 1}, {'i': 2}, {'i': 3}]

        """
        -> test setup works.

        ## Filtering

        This is the most simple operation: A simple stream filter.

        """

        def rx_filter():
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

        """
        ## Streaming Classification

        Using named condition dicts we can classify data, i.e. tag it, in order to process subsequently:

        """

        def rx_classifier():
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

        """
        Normally the data has headers, so thats a good place to keep the classification tags.

        ### Selective Classification

        We fall back to an alternative condition evaluation (which could be a function call) *only* when a previous condition evaluation returns something falsy - by providing a *root condition*.
        When it evaluated, possibly requiring evaluation of other conditions, we return:
        """

        def rx_class_sel():
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

        """
        ## Asyncronous Operations

        WARNING: Early Version. Only for the gevent platform.

        Selective classification allows to call condition functions only when other criteria are met.
        That makes it possible to read e.g. from a database only when data is really required - and not always, "just in case".

        pycond allows to define, that blocking operations should be run *async* within the stream, possibly giving up order.

        ### Asyncronous Filter

        First a simple filter, which gives up order but does not block:

        """

        def rx_async_filter():
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

        """
        Finally asyncronous classification, i.e. evaluation of multiple conditions:

        """

        def rx_async():
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

        ## Data Filtering
        p2m.md_from_source_code()
        p2m.write_markdown(with_source_ref=True, make_toc=True)
