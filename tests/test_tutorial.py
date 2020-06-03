"""
Creates The Tutorial Using pytest2md
"""
import pytest, json, os, time
import pytest2md as p2m  # this is our markdown tutorial generation tool
import pycond as pc  # the tested module:

from functools import partial
from uuid import uuid4
import time
import json
import sys


# py2.7 compat:

p2m = p2m.P2M(__file__, fn_target_md='README.md')

# parametrizing the shell run results (not required here):
# run = partial(p2m.bash_run, no_cmd_path=True)
now = time.time


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
        for `pyconds'` [title: default lookup function,fmatch=pycond.py,lmatch:def state_get]<SRC>
        function.

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

        # Context On Demand And Lazy Evaluation

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

        cond, ApiCtxFuncs = f15_1()
        """

        But we can do better - we still calculated values for keys which might be
        only needed in dead ends of a lazily evaluated condition.

        Lets avoid calculating these values, remembering the
        [custom lookup function](#custom-lookup-and-value-passing) feature.

        > pycond does generate such a custom lookup function readily for you,
        > if you pass a getter namespace as `lookup_provider`:

        """

        def f15_2():

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

        from pytest2md import html_table as tbl  # just a table gen.

        """
        The output demonstrates that we did not even call the value provider functions for the dead branches of the condition.

        NOTE: Instead of providing a class tree you may also provide a dict of functions as `lookup_provider_dict` argument, see `qualify` examples below.

        ## Caching

        Note: Currently you cannot override these defaults. Drop an issue if you need to.

        - Builtin state lookups: Not cached
        - Custom `lookup` functions: Not cached (you can implment caching within those functions)
        - Lookup provider return values: Cached, i.e. called only once
        - Named conditions (see below): Cached

        ## Named Conditions: Qualification

        Instead of just delivering booleans, pycond can be used to qualify a whole set of
        information about data, like so:
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
                f = pc.qualify(q)

                assert f({'a': 'b'}) == {
                    'first': True,
                    'listed': [False, False],
                    'thrd': True,
                    'zero': True,
                }
                assert f({'c': 'foo', 'x': 1}) == {
                    'first': False,
                    'listed': [False, True],
                    'thrd': False,
                    'zero': True,
                }

            q = {
                'thrd': ['k', 'or', 'first'],
                'listed': [['foo'], ['c', 'eq', 'foo']],
                'zero': [['x', 'eq', 1], 'or', 'thrd'],
                'first': ['a', 'eq', 'b'],
            }
            run(q)

            # The conditions may be passed as list as well:
            q = [[k, v] for k, v in q.items()]
            run(q)

        """
        WARNING: For performance reasons there is no built in circular reference check. You'll run into python's built in recursion checker!


        ### Partial Evaluation

        If you either supply a key called 'root' OR supply it as argument to `qualify`, pycond will only evaluate named conditions required to calculate the root key:

        """

        def f20_4():
            called = []

            def expensive_func(data):
                called.append(data)
                return 1

            def xx(data):
                called.append(data)
                return data.get('a')

            funcs = {'exp': {'func': expensive_func}, 'xx': {'func': xx}}
            q = {
                'root': ['foo', 'and', 'bar'],
                'bar': [['somecond'], 'or', [['exp', 'eq', 1], 'and', 'baz'],],
                'x': ['xx'],
                'baz': ['exp', 'lt', 10],
            }
            qualifier = pc.qualify(q, lookup_provider_dict=funcs)

            d = {'foo': 1}
            r = qualifier(d)
            # root, bar, baz had been calculated, not x
            assert r == {'root': True, 'bar': True, 'baz': True, 'exp': 1}
            # expensive_func result, which was cached, is also returned.
            # expensive_func only called once allthough result evaluated for bar and baz:
            assert len(called) == 1

            called.clear()
            f = pc.qualify(q, lookup_provider_dict=funcs, root='x')
            assert f({'a': 1}) == {'x': True, 'xx': 1}
            assert f({'b': 1}) == {'x': False, 'xx': None}
            assert called == [{'a': 1}, {'b': 1}]

        """
        This means pycond can be used as a lightweight declarative function dispatching framework.

        """

        """
        # Streaming Data

        Since version 20200601 pycond can deliver [ReactiveX](https://github.com/ReactiveX/RxPY) compliant stream operators.

        Lets first set up a test data stream, by defining a function `rx_setup` like so:

        """

        def rx_setup():
            # simply `import rx as Rx and rx = rx.operators`:
            # import pycond as pc, like always:
            Rx, rx = pc.import_rx()

            def subs(*test_pipe, items=4):
                """
                Function which takes a set of operators and runs an interval stream until completed
                """

                # stream sink result holder plus a stream completer:
                l, compl = [], rx.take(items)
                l.clear()  # clear any previous results
                # creates integers: 0, then 1, then 2, ... and so on:
                stream = Rx.interval(0.01)
                # turns the ints into dicts: {'i': 0}, then {'i': 1} and so on:
                stream = stream.pipe(rx.map(lambda i: {'i': i}), compl)
                # defines the stream through the tested operators:
                s = stream.pipe(*test_pipe)
                # runs the stream:
                d = s.subscribe(
                    on_next=lambda x: l.append(x),
                    on_completed=lambda: l.append('completed'),
                )
                # blocks until completed:
                while not (l and l[-1] == 'completed'):
                    time.sleep(0.001)
                l.pop()  # removes completed indicator
                return l  # returns all processed messages

            return Rx, rx, subs

        """
        Lets test the setup by having some messages streamed through:

        """

        def rx_1():
            Rx, rx, subs = rx_setup()
            # test test setup:
            r = subs(items=3)
            assert r == [{'i': 0}, {'i': 1}, {'i': 2}]

        """
        -> test setup works.

        ## Data Filtering

        This is the most simple operation: A simple stream filter.

        """

        def rx_filter():
            Rx, rx, subs = rx_setup()

            # ask pycond for a stream filter based on a condition:
            pcfilter = partial(pc.rxop, ['i', 'mod', 2])

            r = subs(pcfilter())
            assert r == [{'i': 1}, {'i': 3}]  # 4 produced, 2 filtered out

            # try the stream filter with message headered data:
            pl = 'payload'
            r = subs(rx.map(lambda i: {pl: i}), pcfilter(prefix=pl))
            print('Full messages passed:', r)
            r = [m[pl] for m in r]
            assert r == [{'i': 1}, {'i': 3}]

            # We may pass a custom filter function, which will be called,
            # when data streams through. It gets the built cond. as first argument:
            def myf(my_built_filter, data):
                return my_built_filter(data) or data['i'] == 0

            r = subs(pcfilter(func=myf))
            assert r == [
                {'i': 0},
                {'i': 1},
                {'i': 3},
            ]  # 4 produced, only 1 filtered out now

        """
        ## Data Classification

        Using named condition dicts we can classify data, i.e. tag it, in order to process subsequently

        """

        def rx_classifier():
            Rx, rx, subs = rx_setup()

            # generate a set of classifiers:
            conds = [['i', 'mod', i] for i in range(2, 4)]

            def run(offs=0):

                # and get a classifying operator from pycond, adding the results in place, at key 'mod':
                r = subs(pc.rxop(conds, at='mod'))
                i, j = 0 + offs, 1 + offs
                assert r == [
                    {'i': 0, 'mod': {i: 0, j: 0}},
                    {'i': 1, 'mod': {i: 1, j: 1}},
                    {'i': 2, 'mod': {i: 0, j: 2}},
                    {'i': 3, 'mod': {i: 1, j: 0}},
                ]

            # we can also provide the names of the classifiers by passing a dict:
            # here we pass 2 and 3 as those names:
            conds = dict([(i, ['i', 'mod', i]) for i in range(2, 4)])
            run(2)

        """
        Normally the data has headers, so thats a good place to keep the classification tags.

        ### Selective Classification

        We fall back to an alternative condition evaluation (which could be a function call) *only* when a previous condition evaluation returns something falsy - by providing a root condition:
        """

        def rx_class_sel():
            Rx, rx, subs = rx_setup()

            # using the list style right away:
            conds = [[i, [['i', 'mod', i], 'or', 'alt']] for i in range(2, 4)]
            conds.append(['alt', ['i', 'gt', 1]])
            # provide the root condition. Only when it evals falsy, the named "alt" condiction will be evaluated:
            r = subs(pc.rxop(conds, at='mod', root=2))

            assert r == [
                {'i': 0, 'mod': {2: False, 'alt': False}},
                {'i': 1, 'mod': {2: 1}},
                {'i': 2, 'mod': {2: True, 'alt': True}},
                {'i': 3, 'mod': {2: 1}},
            ]

        ## Data Filtering
        p2m.md_from_source_code()
        p2m.write_markdown(with_source_ref=True, make_toc=True)

        # # from rx.scheduler.eventloop import GEventScheduler
        # # # we use gevent
        # # import gevent
        # # from gevent import monkey

        # # monkey.patch_all()
        # # GS = GEventScheduler(gevent)
