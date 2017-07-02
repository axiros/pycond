from functools import partial
from time import time


def foo(a, b, c, d):
    return a + b + c + d

fp = partial(foo, 1,2)
a, b = 1, 2
fl = lambda c, d, a=a, b=b: foo(a, b, c, d)
import pdb; pdb.set_trace()

t1 = time()
for i in range(1000):
    fp(10, 20)
dtp = time() - t1

t1 = time()
for i in range(1000):
    fl(10, 20)
dtl = time() - t1
import pdb; pdb.set_trace()

