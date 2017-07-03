#!/usr/bin/env python -tt

import unittest, sys, os
import operator
import time
pth = os.path.abspath(__file__).rsplit('/', 2)[0]
sys.path.insert(0, pth)

from pycond import condf, state_get, dbg_get, OPS, COMB_OPS
from pycond import parse_cond, State as S
from pycond import run_all_ops_thru

keys = []

eq = lambda _, k, v: _.assertEqual(k, v)

def parse(cond, *a, **kw):
    ''' do the parsing with a debugging getter '''
    #kw['lookup'] = kw.get('lookup', dbg_get)
    print('Parsing', cond)
    return parse_cond(cond, *a, **kw)


class T(unittest.TestCase):
    def setUp(s):
        ''' clearing state and keys '''
        while keys: keys.pop()
        S.clear()


class Mechanics(T):


    def test_test(s):
        return 'pass'


    def test_auto_cond(s, cond='foo'):
        '''key only -> we act like python's if val:...
        and insert the 'truthy' operator
        '''

        f, m = parse(cond)
        # shortcut of you don't want meta:
        f = condf(cond)

        eq(s, m['keys'], ['foo'])

        eq(s, f(), False) # when unset
        for v in 0, [], (), {}, False, None, '':
            S['foo'] = v
            eq(s, f(), False)

        for v in 1, [1], (1,), {'a': 1}, True, 's':
            S['foo'] = v
            eq(s, f(), True)


    def test_simple_cond(s, cond='foo eq bar'):

        S['foo'] = 'bar'
        f, m = parse(cond)

        eq(s, f(), True)
        eq(s, m['keys'], ['foo'])

        S['foo'] = 'x'
        eq(s, f(), False)


    def test_simple_comb(s, cond='foo eq bar and baz eq 1'):

        S['foo'] = 'bar'
        S['baz'] = 1
        f, m = parse(cond)

        eq(s, f(), True)
        eq(s, m['keys'], ['baz', 'foo'])

        S['foo'] = 'x'
        eq(s, f(), False)


    def test_apo_space(s):
        S['foo'] = 'b a r'
        eq(s, condf('foo eq "b a r"')(), True)
        eq(s, condf("foo eq 'b a r'")(), True)
        eq(s, condf("foo eq 'b \\a r'")(), False)
        eq(s, condf("foo eq 'b\ a r'")(), False)


    def test_tokenize_brackets(s):
        S['k1'] = 1
        conds =( '[[ k1 eq 1 ] and [ k2 gt 1 ]]'
                , '[[k1 eq 1] and [ k2 gt 1 ]]'
                , '[ k1 eq 1] and [ k2 gt 1 ]'
               )

        for b, v in ((True, 2), (False, 1)):
            S['k2'] = v
            for cond in conds:
                k = []
                f, m = parse(cond)
                eq(s, f(), b)
                eq(s, m['keys'], ['k1', 'k2'])


    def test_auto_brackets(s):
        ''' you don't need to bracket expr between combining ops'''
        # we auto bracket from left to right:
        # i.e.: 'False and True or True' -> False and [ True or True] = False
        # and not [False and True ] or True = True
        S['k1'] = False
        S['k2'] = True
        S['k3'] = True
        f, m = parse('k1 and k2 or k3')
        eq(s, f(), False)
        eq(s, m['keys'], ['k1', 'k2', 'k3'])
        f, m = parse('[k1 and k2] or k3')
        eq(s, f(), True)


        S['k1'] = 1
        conds =( 'k1 eq 1 and k2 gt 1'
                ,'[k1 eq 1] and k2 gt 1'
                ,'k1 eq 1 and [k2 gt 1]'
               )

        for b, v in ((True, 2), (False, 1)):
            S['k2'] = v
            for cond in conds:
                k = []
                f, m = parse(cond)
                eq(s, f(), b)
                eq(s, m['keys'], ['k1', 'k2'])


    def test_round_brackets(s, cond='(k1 and k2) or k3'):
        S['k1'] = False
        S['k2'] = True
        S['k3'] = True
        f, m = parse(cond, brkts='()')
        eq(s, f(), True)
        eq(s, m['keys'], ['k1', 'k2', 'k3'])


    def test_custom_lookup(s):
        def my_lu(k, v):
            return len(k), eval(v)

        for k, b in ('len4', True), ('notlen4', False):
            cond = '%s eq 3+1' % k
            f, m = parse(cond, lookup=my_lu)
            eq(s, f(), b)
        eq(s, m['keys'], ['notlen4'])


    def test_custom_sep(s, cond='[[foo.eq.b ar]and not.bar.eq.foo]'):
        S['foo'] = 'b ar'
        eq(s, parse(cond, sep='.')[0](), True)
        n = '\x01'
        eq(s, parse(cond.replace('.', n), sep=n)[0](), True)


    def test_escape(s, cond='[[foo eq b\ ar] and b\.r eq fo\ o]'):
        S['foo'] = 'b ar'
        S['b.r'] = 'fo o'
        eq(s, parse(cond)[0](), True)


    def test_autoconv(s):
        S['foo'] = 42
        eq(s, condf('foo eq 42')(), True)
        # the 42 in the condition stays string now:
        eq(s, condf('foo eq 42', autoconv=False)(), False)

        S['foo'] = '42'
        # '42' in state, val is autoconved (the default) -> False(!)
        eq(s, condf('foo eq 42')(), False)
        eq(s, condf('foo eq 42', autoconv=False)(), True)
        # now we tell py_conf to also convert the looked up values
        # before sending to the operator:
        eq(s, condf('foo eq 42', autoconv_lookups=True)(), True)
        # putting apos around numbers also prevents autoconf:
        eq(s, condf('foo eq "42"')(), True)


class TestCombiningOps(T):

    def test_all(s, cond='k1 %s k2'):

        # that minimum we just need to have:
        for k in 'and', 'or', 'xor', 'and_not', 'or_not':
            assert k in COMB_OPS

        k1 = S['k1'] = True
        for b in True, False:
            k2 = S['k2'] = b

            # and, or, and not....
            for op in COMB_OPS:
                # we allow foo and not bar but also: foo and_not_bar
                cnd_under = cond % op
                cnd = cond % op.replace('_', ' ')
                exp = eval(cnd) if not op == 'xor' else operator.xor(k1, k2)
                eq(s, parse(cnd)[0](), exp)
                eq(s, parse(cnd_under)[0](), exp)



val_splitting_get = lambda k, v: (S.get(k), v.split(','))



class TestComparisonOps(T):

    def test_contains(s, cond='foo contains bar'):
        S['foo'] = 'abara'
        eq(s, parse(cond)[0](), True)
        S['foo'] = [1,2,3, 'bar']
        eq(s, parse(cond)[0](), True)
        S['foo'] = 'bar'

    def test_rev_and_negation(s):
        S['foo'] = 'b'
        eq(s, condf('foo rev not contains "abc"') ( ), False)
        S['foo'] = 'bar'
        eq(s, condf('foo contains a'            ) ( ) , True  )
        eq(s, condf('foo contains x'            ) ( ) , False )
        eq(s, condf('foo rev contains abara'    ) ( ) , True  )
        eq(s, condf('foo rev contains abxra'    ) ( ) , False )
        eq(s, condf('foo rev not contains axra' ) ( ) , True  )
        eq(s, condf('foo rev contains axra'     ) ( ) , False )
        eq(s, condf('foo rev contains 1,2,3,bar',
                      lookup=val_splitting_get)(), True)
        S['foo'] = 'a'
        cond = ['foo', 'rev', 'contains', [1, 'a']]
        eq(s, parse(cond)[0](), True)


    def test_gt_eq_not_le_and_rev_lt(s, tcond='foo %s bar'):
        # we look up v as well for this test, so foo AND bar from S:
        def g(k, v, state=S):
            return state[k], state[v]

        for a, b in ( (1, 2                )
                    , (1 / 10000., 1/10001 )
                    , ('a', 'b'            )
                    , ([1,2], [1, 2]       )
                    , ([1,2], [2, 3]       )
                    ) :
            S['foo'] = a; S['bar'] = b
            print (a, b)
            res = ( condf(tcond % 'gt', lookup=g)()
                  , condf(tcond % 'not le', lookup=g)()
                  , condf(tcond % 'rev lt', lookup=g)())
            eq(s, *res[0:2])
            eq(s, *res[1:3])
            # we just want trues and falses
            assert all([q in (True, False) for q in res])




class Filtering(T):
    users = """
    id,first_name,last_name,email,gender,ip_address,nr
    1,Rufe,Morstatt,rmorstatt0@newsvine.com,Male,216.70.69.120,1
    2,Kaela,Kaminski,kkaminski1@opera.com,Female,73.248.145.44,2
    3,Dale,Belderfield,dbelderfield2@drupal.org,Female,219.190.115.44,3
    4,Sal,Males,smales3@ca.gov,Male,195.20.33.196,4
    5,Bobby,Edmundson,bedmundson4@sciencedaily.com,Female,83.182.215.98,5
    6,Pete,Roizin,proizin5@ucsd.edu,Male,101.44.167.8,6
    7,Mariann,Twaite,mtwaite6@buzzfeed.com,Female,153.155.6.192,7
    8,Reidar,MacCaghan,rmaccaghan7@spiegel.de,Male,232.43.62.204,8
    9,Andras,Sesons,asesons8@tripadvisor.com,Male,4.151.83.156,9
    10,Melanie,Pichmann,mpichmann9@bbb.org,Female,183.94.212.212,10
    11,Wrong,Email,foobar,Mail,1.2.3.4,11
    12,OK,Email,foo@bar,Mail,1.2.3.4,12
    13,have space,have also space,foo@bar,Mail,1.2.3.4,13
    """.strip().splitlines()
    # argh.. py3 fails, would not find h w/o that, fuck.
    globals()['h'] = users[0].split(',')
    users = [(dict([(h[i], u.split(',')[i]) for i in range(len(h))]))
                                            for u in users[1:]]
    for u in users: u['id'] = int(u['id'])


    def test_filter_dicts_convenience_state_kw_arg(s):

        does_match = condf('email not contains @')
        matches = [u for u in s.users if does_match(state=u)]

        assert len(matches) == 1 and matches[0]['email'] == 'foobar'


    def test_filter_dicts_convenient_compl(s):
        for cond in ('[email not contains @] or [id not lt 12]'
                    , 'email not contains @  or id gt 11'
                    , 'email not contains @  or not [id lt 12]'
                    ):

            matches = [u for u in s.users if condf(cond)(state=u)]

            for m in matches:
                assert m['first_name'] == 'Wrong' or m['id'] > 11


    def test_filter_dicts(s):
        ''' doing it w/o passing state with the condition as above '''
        cond = 'first_name eq Sal or last_name contains i'

        matcher = condf(cond, lookup=lambda k, v, **kw: (S['cur'].get(k), v))

        def match(u):
            S['cur'] = u
            return matcher()

        # apply condf
        matches = [u for u in s.users if match(u)]

        # verify correctness:
        for m in matches:
            assert m['first_name'] == 'Sal' or 'i' in m['last_name']
        assert len(m) < len(s.users)


    def test_space(s):
        cond = 'first_name eq "have space"'
        matches = [u for u in s.users if condf(cond)(state=u)]
        assert len(matches) == 1 and matches[0]['first_name'] == 'have space'

    def test_autoconv(s):
        cond = 'nr lt 5'
        matches = [u for u in s.users if condf(cond, autoconv_lookups=True)(
            state=u)]
        assert len(matches) == 4


class OperatorHooks(T):

    def test_global_hk(s):
        ''' globally changing the OPS '''
        orig = {}
        orig.update(OPS)
        l = []
        def hk(f_op, a, b, l=l):
            l.append((getattr(f_op, '__name__', ''), a, b))
            return f_op(a, b)
        run_all_ops_thru(hk)
        S.update({'a': 1, 'b': 2, 'c': 3})
        f = condf('a gt 0 and b lt 3 and not c gt 4')
        assert l == []
        assert f() == True
        expected_log = [  ('gt', 1, 0.0)
                        , ('lt', 2, 3.0)
                        , ('gt', 3, 4.0)]
        assert l == expected_log
        f()
        assert l == expected_log * 2

        # composition:
        run_all_ops_thru(hk)
        f()
        # no effect, same hook not applied twice directly:
        assert l == expected_log * 3

        # revert hook:
        OPS.clear()
        OPS.update(orig)


    def test_cond_local_hook(s):
        def myhk(f_op, a, b):
            return True
        S['a'] = 1
        f = condf('a eq 2')
        assert f() == False
        f = condf('a eq 2', ops_thru=myhk)
        assert f() == True




class Perf(T):

    def test_perf(s):
        '''
        We assemble a deeply nested condition string and parse it into
        the lambda funcs. At the same time we assemble an executable python
        expression, w/o function lookups.
        then we compare runtime of both
        '''
        levels = 60
        S['foo'] = 'a'
        py = 'S.get("foo") == "a"'
        cond = 'foo eq "a"'
        # assemble the thing:
        for lev in range(levels):
            key = 'k' + str(lev)
            S[key] = key
            cond = '[%s and [%s eq %s]]' % (cond, key, key)
            py   = '[%s and [S["%s"] == "%s"]]' % (py, key, key)

        def fast_lu(k, v):
            # no cfg pasing, not .get:
            return S[k], v

        f, m      = parse(cond, lookup=state_get)
        ffast, m2 = parse(cond, lookup=fast_lu)

        # all set up correct?
        for t in f, ffast:
            eq(s, t(), True)
        # now the biiig expression must be false in total:
        S['k12'] = 0
        for t in f, ffast:
            eq(s, t(), False)

        assert all(['k' + str(lev) in m['keys'] for lev in range(levels)])
        py = 'def py_ev(): return %s' % py
        exec (py, {'S': S}, globals())

        r = range(1000)
        t1 = time.time()
        for i in r:
            f()
        dt1 = time.time() - t1

        t1fast = time.time()
        for i in r:
            ffast()
        dt1fast = time.time() - t1fast

        # and now direct python, just one function call, to py_ev:
        t1 = time.time()
        for i in r:
            py_ev()
        dt2 = time.time() - t1
        # i see currently around 2-3 time slower compared to pure python w/o
        # functions: -> perf ok.

        # on py3 it is a bit slower, factor here nearly 3
        # also I see out of stack memory errors on the pure python exprssion
        # when I go to levels = 100 but no probs on condf
        print('condf time / raw single func. python eval time:', dt1 / dt2)
        print('With fast lookup function:', dt1fast / dt2)

        msg = 'One condf run of %s levels deeply nested conditions: %.4fs '
        print (msg % (levels, dt1 / levels))
        assert dt1 / dt2 < 8, 'Expected max 8 times slower, is %s' % (dt1/dt2)


if __name__ == '__main__':
    # tests/test_pycond.py PyCon.test_auto_brackets
    unittest.main()



