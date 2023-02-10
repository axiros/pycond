import time
from pycond import parse_cond

_is = isinstance

now = time.time


def test_comp_perf():
    """6 times faster deep lookups when preassembled
    at first match
    """
    now = time.time
    s = {'a': {'b': [{'c': 42}]}}

    class t:
        a = s

    # S = {'A': {'a': s}}
    S = {'A': t}

    count = 100000

    def run(count=count, **kw):
        pc = parse_cond('A.a.a.b.0.c eq 42', **kw)[0]
        t0 = now()
        for i in range(count):
            assert pc(state=S)
        return now() - t0

    dt1 = run(deep='.')
    dt2 = run(deep2='.')
    dt3 = run(deep3='.')
    print('Cached item getter perf vs get_deep:', dt1 / dt2)
    print('Eval perf vs get_deep:', dt1 / dt3)
    assert 2 * dt2 < dt1


if __name__ == '__main__':
    test_comp_perf()
