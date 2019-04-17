# these are from dir(operator) and testing with ints vs strs:
iop = [
    'add',
    'and_',
    'eq',
    'floordiv',
    'ge',
    'gt',
    'iadd',
    'iand',
    'ifloordiv',
    'ilshift',
    'imod',
    'imul',
    'ior',
    'ipow',
    'irshift',
    'is_',
    'is_not',
    'isub',
    'itemgetter',
    'itruediv',
    'ixor',
    'le',
    'length_hint',
    'lshift',
    'lt',
    'mod',
    'mul',
    'ne',
    'or_',
    'pow',
    'rshift',
    'sub',
    'truediv',
    'xor',
]
sop = [
    'attrgetter',
    'concat',
    'contains',
    'countOf',
    'iconcat',
    'indexOf',
    'methodcaller',
]

M = {}

import operator as o

for ops, typ in (iop, 'nr'), (sop, 'str'):
    l = [(k, getattr(o, k)) for k in sorted(ops)]

    L = []
    same = 'Same as a '

    for k, f in l:
        d = f.__doc__
        alias = ''
        if same in d:
            alias = d.split(same)[1].split(' ', 1)[0]
            d = ''
        L.append([k, alias, d])
    M[typ] = L

import json

print(json.dumps(M, indent=2, default=str))
