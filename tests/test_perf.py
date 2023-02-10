"""
Abusing the travis environment param. possiblities to compare a few perf.
statements...
E.g. Did they change 'is' vs '==' in Py2 vs Py3 ?
And Is there a significant effect?
"""

import time
import sys
from collections import OrderedDict as OD
from functools import partial
import unittest
from operator import itemgetter
from timeit import timeit, Timer
from time import time

print('\n\nSome Performance Tests\n\n')

PY2 = sys.version_info[0] == 2
range = xrange if PY2 else range

loops = range(100000)
number = 10
repeat = 10
R = []


class T(unittest.TestCase):
    def init(self, k1, k2, setup=None):
        print('')
        self.res = OD({k1: 0})
        self.res[k2] = 0
        print('\n%s\n' % ('- ' * 40))
        print('Test: "%s" vs "%s"' % tuple(self.res.keys()))
        print('\n%s\n' % ('- ' * 40))
        if setup:
            print('setup: %s' % setup)
        return self.res

    def tearDown(self):
        print('')
        for k, dt in self.res.items():
            print('dt was %s for %s' % (dt, k))
        vs = list(self.res.values())
        q = vs[0] / vs[1]
        k1, k2 = self.res.keys()
        if q > 1:
            k1, k2 = k2, k1
            q = vs[1] / vs[0]
        msg = '=> "%s" is better than "%s" by:' % (k1, k2)
        print(msg)
        print('\n>>>> %.2f <<<<<' % q)
        R.append((q, msg))

    def run_(self, k, expr, setup='pass', number=number):
        # min? read timeit module doc, repeat function:
        print('test expression for "%s":' % k)
        print(expr)
        self.res[k] = min(Timer(expr, setup=setup).repeat(10, number))


class Tests(T):
    def test_lambd_vs_partial(self):
        k1 = 'Lambda'
        k2 = 'Partial'

        setup = """if 1:
        from functools import partial
        def sum(a, b): return a + b
        a = 10
        lf = lambda b, a=a: sum(a, b)
        pf = partial(sum, 10)
        assert lf(42) == pf(42) == 52
        """
        m = self.init(k1, k2, setup)
        self.run_(k1, 'for i in range(1000): lf(i)', setup)
        self.run_(k2, 'for i in range(1000): pf(i)', setup)

    def test_if_vs_if_is_None(self):
        """if foo:...  must check for all kinds of truthyness.
        => is explictly saying e.g. if foo == None better?
        """
        k1 = 'if'
        k2 = 'if is None'

        m = self.init(k1, k2)
        nr = 10000
        e = "[j for j in (0, [1,2], {'a': 'b'}, {}, 'a', '') if j %s]"
        self.run_(k1, e % '', number=nr)
        self.run_(k2, e % 'is None', number=nr)

    def test_eq_vs_is(self):
        """if foo is None vs if foo == None"""
        k1 = 'is None'
        k2 = '== None'
        m = self.init(k1, k2)
        nr = 10000
        e = "[j for j in (0, [1,2], {'a': 'b'}, {}, 'a', '') if j %s]"
        self.run_(k1, e % '== None', number=nr)
        self.run_(k2, e % 'is None', number=nr)

    def test_local_scope(self):
        k1 = 'global lookup'
        k2 = 'local scope via function default'
        setup = """if 1:
        A = 100
        # 1000 keys in globals():
        for k in range(1000): globals()[str(k)] = k
        def glob(a): return A + a
        def locl(a, b=A): return b + a
        """
        m = self.init(k1, k2, setup)
        e = 'for j in range(1, 100): %s(j)'
        self.run_(k1, e % 'glob', setup=setup, number=1000)
        self.run_(k2, e % 'locl', setup=setup, number=1000)


if __name__ == '__main__':
    # tests/test_pycond.py PyCon.test_auto_brackets
    try:
        unittest.main()
    except:
        print('\nAll Results Again\n')
        for q, msg in R:
            print('%s\n%.2f' % (msg, q))
