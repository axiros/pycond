# we use gevent
from gevent import monkey
import time, sys

monkey.patch_all()
import gevent, pycond as pc

from rx.scheduler.eventloop import GEventScheduler
import rx.scheduler.eventloop as e

from threading import Event, current_thread as ct

# _thn = lambda msg, data: print('thread:', cur_thread().name, msg, data)
tn = lambda: ct().name
GS = GEventScheduler(gevent)
# GS = None


Rx, rx = pc.import_rx()

now = time.time
count = 10000
prnt = 0


class F:
    def odd(v, data, cfg, **kw):
        data['odd'] = tn()  # add the thread name
        return 1, v

    def blocking(v, data, cfg, **kw):
        data['blocking'] = tn()
        if data['i'] == 0:
            time.sleep(0.001)
        if prnt:
            print(data)
        return 3, v


class Tests:
    cond = [
        ['i', 'lt', 1000000],  # just make it a bit complex
        'and',
        [['odd', 'eq', 1], 'and_not', ['i', 'eq', 2]],
        'and_not',
        ['blocking', 'eq', 3],
    ]

    conds = [['mycond', cond,]]

    def test_perf_compare(self):
        res = {}
        print()

        d = lambda i: {'i': i}

        def _measure(f):
            fn = f.__name__
            t0 = now()
            l = f()
            dt = now() - t0
            assert len(l) > count - 2
            assert 'odd' in l[-1] and 'blocking' in l[-1]
            # item 2 was failing the condition to even check the blocking
            zt = [f for f in l if f['i'] in (0, 2)]
            assert zt[0].get('blocking') != zt[1].get('blocking')
            print(fn, dt)
            res[fn] = dt

        def direct():
            pcd = pc.parse_cond(Tests.cond, lookup_provider=F)[0]
            l = [d(i) for i in range(count)]
            [pcd(state=m) for m in l]
            return l

        def qual():
            pcn = pc.qualify(Tests.conds, lookup_provider=F)
            l = [d(i) for i in range(count)]
            [pcn(m) for m in l]
            return l

        def _rxrun(**kw):
            ev = Event()
            unblock = lambda *a: ev.set()
            rxop = lambda **kw: pc.rxop(
                Tests.conds,
                into='mod',
                scheduler=GS,
                lookup_provider=F,
                timeout=0.01,
                **kw
            )
            l = []
            add = lambda m: l.append(m)

            # Rx.interval(0, scheduler=GS).pipe(
            rxcond = rxop(**kw)
            s = Rx.from_(range(count)).pipe(rx.map(d), rxcond, rx.take(count))
            s.subscribe(add, on_completed=unblock)
            ev.wait()
            if not kw:
                # same thread
                assert l[-1]['odd'] == l[-1]['blocking']
                assert l[0]['i'] == 0  # 0 was sleeping a bit but we are sync
            else:
                # ran not on same thread
                time.sleep(0.1)
                try:
                    assert l[-1]['odd'] != l[-1]['blocking']
                except Exception as ex:
                    print('breakpoint set')
                    breakpoint()
                    keep_ctx = True
                assert l[0]['i'] != 0  # 0 was sleeping a bit
            return l

        def rxsync():
            return _rxrun()

        def rxasync():
            res = _rxrun(asyn=['blocking'])
            return res

        _measure(direct)
        _measure(qual)
        _measure(rxsync)
        _measure(rxasync)
        head = '%s Items' % count
        print('\n'.join(('', head, '=' * len(head))))
        [print('%9s' % k, v) for k, v in res.items()]
<<<<<<< HEAD
        # yes, we are 10 times slower when all items are processed async:
        # doing this with rx.group_by(needs_asnc) -> flat_map(s.pipe(map(rx.just(x, GS)))) was far far slower yet, so I'm sort of ok with our 10k / sec:
        assert res['rxasync'] < 15 * res['direct']
=======
>>>>>>> 998bb838ea5795b886478f4eea0389530204ed31


if __name__ == '__main__':
    Tests().test_perf_compare()
