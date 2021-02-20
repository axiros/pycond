# we use gevent
from gevent import monkey
import time, sys

monkey.patch_all()
import gevent, pycond as pc

from rx.scheduler.eventloop import GEventScheduler
import rx.scheduler.eventloop as e

from threading import Event, current_thread as ct

# _thn = lambda msg, data: print('thread:', cur_thread().name, msg, data)
tn = lambda: ct().name.replace('Thread', '')
GS = GEventScheduler(gevent)
# GS = None


Rx, rx = pc.import_rx()

# set this higher and watch mem getting constant:
now, count, prnt = time.time, 1, 0


class F:
    def blocking(k, v, cfg, data, **kw):
        data[k] = tn()
        return True, v

    blocking2 = blocking


class Tests:
    """Asserting some special cases"""

    cond = {
        'root': [':b1', 'and', ':b2'],
        'b1': ['a', 'and', ':blocking'],
        'b2': ['a', 'and', ':blocking2'],
    }

    def test_rx_async1_prefix(self):
        """is prefix working over async runs"""
        res = {}

        def d(i):
            return {'payload': {'a': i + 1}}

        rxop = lambda **kw: pc.rxop(
            Tests.cond,
            into='mod',
            prefix='payload',
            scheduler=GS,
            lookup_provider=F,
            asyn=['blocking', 'blocking2'],
        )
        l = []
        # Rx.interval(0, scheduler=GS).pipe(
        rxcond = rxop()
        s = Rx.from_(range(count)).pipe(rx.map(d), rxcond, rx.take(count))
        s.subscribe(lambda x: l.append(x))
        while not l:
            time.sleep(0.01)
        # same thread set in def blocking:
        t = [l[0]['payload'].pop(b) for b in ['blocking', 'blocking2']]
        assert t[0] == t[1]
        assert 'Dummy' in t[0]
        assert l == [
            {'mod': {'b2': True, 'b1': True, 'root': True}, 'payload': {'a': 1}}
        ]


if __name__ == '__main__':
    Tests().test_perf_compare()
