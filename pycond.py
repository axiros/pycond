"""
Condition parser

See README.
See Tests.

DEV Notes:

    f_xyz denotes a function (we work a lot with lambdas and partials)


Q:  Why not pass state inst
A:  The **kw for all functions at run time are for the custom lookup feature:

    model = {'eve': {'last_host': 'somehost'}}

    def my_lu(k, v, req, user, model=model):
        return (model.get(user) or {}).get(k), req[v]

    f = pc.pycond('last_host eq host', lookup=my_lu)

    req = {'host': 'somehost'}
    assert f(req=req, user='joe') == False 
    assert f(req=req, user='eve') == True

    Note: state= via **kw in the sig is even faster than via state=State in the sig!
"""

from __future__ import print_function
import operator, sys
import inspect
import json
from functools import partial
from copy import deepcopy
from ast import literal_eval

_is = isinstance
nil = '\x01'

PY2 = sys.version_info[0] == 2
# is_str = lambda s: _is(s, basestring if PY2 else (bytes, str))
if PY2:
    is_str = lambda s: _is(s, basestring)
    sig_args = lambda f: inspect.getargspec(getattr(f, 'func', f)).args
else:
    is_str = lambda s: _is(s, (bytes, str))
    sig_args = lambda f: list(inspect.signature(f).parameters.keys())


bbb = bool


def xbool(o):
    print(o)
    return bbb(o)


# fmt:off
# from dir(operator):
_ops = {
    'nr': [
        ['add'        , '+'   ] ,
        ['and_'       , '&'   ] ,
        ['eq'         , '=='  ] ,
        ['floordiv'   , '//'  ] ,
        ['ge'         , '>='  ] ,
        ['gt'         , '>'   ] ,
        ['iadd'       , '+='  ] ,
        ['iand'       , '&='  ] ,
        ['ifloordiv'  , '//=' ] ,
        ['ilshift'    , '<<=' ] ,
        ['imod'       , '%='  ] ,
        ['imul'       , '*='  ] ,
        ['ior'        , '|='  ] ,
        ['ipow'       , '**=' ] ,
        ['irshift'    , '>>=' ] ,
        ['is_'        , 'is'  ] ,
        ['is_not'     , 'is'  ] ,
        ['isub'       , '-='  ] ,
        ['itruediv'   , '/='  ] ,
        ['ixor'       , '^='  ] ,
        ['le'         , '<='  ] ,
        ['lshift'     , '<<'  ] ,
        ['lt'         , '<'   ] ,
        ['mod'        , '%'   ] ,
        ['mul'        , '*'   ] ,
        ['ne'         , '!='  ] ,
        ['or_'        , '|'   ] ,
        ['pow'        , '**'  ] ,
        ['rshift'     , '>>'  ] ,
        ['sub'        , '-'   ] ,
        ['truediv'    , '/'   ] ,
        ['xor'        , '^'   ] ,
        ['itemgetter' , ''    ] , # 'itemgetter(item, ...) --> itemgetter object\n\nReturn a callable object that fetches the given item(s) from its operand.\nAfter f = itemgetter(2), the call f(r) returns r[2].\nAfter g = itemgetter(2, 5, 3), the call g(r) returns (r[2], r[5], r[3])',
        ['length_hint', ''    ] , #'Return an estimate of the number of items in obj.\n\nThis is useful for presizing containers when building from an iterable.\n\nIf the object supports len(), the result will be exact.\nOtherwise, it may over- or under-estimate by an arbitrary amount.\nThe result will be an integer >= 0.',
    ],
    'str': [
        ['attrgetter' , ''    ] , # "attrgetter(attr, ...) --> attrgetter object\n\nReturn a callable object that fetches the given attribute(s) from its operand.\nAfter f = attrgetter('name') , the call f(r) returns r.name.\nAfter g = attrgetter('name' , 'date') , the call g(r) returns (r.name , r.date).\nAfter h = attrgetter('name.first' , 'name.last') , the call h(r) returns\n(r.name.first , r.name.last)." ,
        ['concat'     , '+'   ] ,
        ['contains'   , ''    ] , # 'Same as b in a (note reversed operands).']  ,
        ['countOf'    , ''    ] , #'Return the number of times b occurs in a.'] ,
        ['iconcat'    , '+='  ] ,
        ['indexOf'    , ''    ] , #'Return the first index of b in a.']         ,
        ['methodcaller', ''   ] , #  "methodcaller(name, ...) --> methodcaller object\n\nReturn a callable object that calls the given method on its operand.\nAfter f = methodcaller('name'), the call f(r) returns r.name().\nAfter g = methodcaller('name', 'date', foo=1), the call g(r) returns\nr.name('date', foo=1).",
        ],
}
# fmt:on
OPS = {}
OPS_SYMBOLIC = {}

# extending operators with those:
def truthy(k, v=None):
    return operator.truth(k)


falsy = lambda k, v=None: not truthy(k, v)


def _in(a, b):
    return a in b


def get_ops():
    return _ops


def add_built_in_ops():
    OPS['truthy'] = truthy
    OPS['falsy'] = falsy
    OPS['in'] = _in


def clear_ops():
    OPS.clear()
    OPS_SYMBOLIC.clear()


def parse_ops():
    """Sets up OPs from scratch, using txt opts only"""
    clear_ops()
    for t in 'str', 'nr':
        for k, alias in _ops[t]:
            f = getattr(operator, k, None)
            # the list is python3.7 - not all have all:
            if f:
                OPS[k] = f
                if alias:
                    OPS_SYMBOLIC[alias] = f
    add_built_in_ops()


def ops_use_symbolic(allow_single_eq=False):
    OPS.clear()
    OPS.update(OPS_SYMBOLIC)
    add_built_in_ops()
    if allow_single_eq:
        OPS['='] = OPS['==']


def ops_use_symbolic_and_txt(allow_single_eq=False):
    parse_ops()
    OPS.update(OPS_SYMBOLIC)
    if allow_single_eq:
        OPS['='] = OPS['==']


def ops_reset():
    parse_ops()


ops_use_txt = ops_reset

ops_use_txt()
# see api below for these:
OPS_HK_APPLIED = False


# if val in these we deliver False:
FALSES = (None, False, '', 0, {}, [], ())

# default lookup of keys here - no, module does NOT need to have state.
# its a convenience thing, see tests:
# Discurraged to be used in non-cooperative async situations, since clearly not thread safe - just pass the state into pycond:
State = {}


def state_get_deep(key, val, cfg, state=State, deep='.', **kw):
    # key maybe already path tuple - or string with deep as seperator:
    parts = key.split(deep) if _is(key, str) else list(key)
    while parts:
        part = parts.pop(0)
        try:
            state = state.get(part)
        except AttributeError as ex:
            try:
                state = state[int(part)]
            except:
                return None, val
        if not state:
            break
    return state, val


def state_get(key, val, cfg, state=State, **kw):
    # a lookup function can modify key AND value, i.e. returns both:
    if _is(key, tuple):
        return state_get_deep(key, val, cfg, state, **kw)
    else:
        return state.get(key), val  # default k, v access function


def dbg_get(key, val, cfg, state=State, *a, **kw):
    res = state_get(key, val, cfg, state, *a, **kw)
    val = 'FALSES' if val == FALSES else val
    out('Lookup:', key, val, '->', res[0])
    return res


out = lambda *m: print(' '.join([str(s) for s in m]))


OR, AND, OR_NOT, AND_NOT, XOR = 0, 1, 2, 3, 4


def comb(op, lazy_on, negate=None):
    """Absolut Hotspot. Fastest way to do it."""

    def _comb(
        f,
        g,
        op=op,
        lazy_on=lazy_on,
        negate=negate,
        ands={AND, AND_NOT},
        ors={OR, OR_NOT},
        fr=nil,
        **kw,
    ):
        try:
            fr = f(**kw)
            if fr:
                if lazy_on:
                    return True

            elif lazy_on == False:
                return False

            if op == AND:
                return fr and g(**kw)
            elif op == OR:
                return fr or g(**kw)
            elif op == AND_NOT:
                return fr and not g(**kw)
            elif op == OR_NOT:
                return fr or not g(**kw)
            else:
                return fr is not g(**kw)

        except Async as ex:
            h = ex.args[0][0]
            if fr == nil:
                fgr = [op, h, g]
            else:
                fgr = [op, bool(fr), h]
            ex.args[0][0] = fgr
            raise ex

    return _comb


# fmt: off
COMB_OPS = {
    'or':      comb(OR, True),
    'and':     comb(AND, False),
    'or_not':  comb(OR_NOT, True, True),
    'and_not': comb(AND_NOT, False, True),
    'xor':     comb(XOR, None),
}
# fmt: on

# those from user space are also replaced at tokenizing time:
NEG_REV = {'not rev': 'not_rev', 'rev not': 'rev_not'}


def is_deep_list_path(key):
    """
    Identify the first list is a key, i.e. should actually be a tuple:

    [[['a', 'b', 0, 'c'], 'eq', 1], 'and', 'a'] -> should be:
    [[('a', 'b', 0, 'c'), 'eq', 1], 'and', 'a']

    When transferred over json we can't do paths as tuples
    We find if have a deep path by excluding every other option:
    """
    if not _is(key, list):
        return
    if any([k for k in key if not _is(k, (str, int))]):
        return
    if not (len(key)) > 1:
        return
    if key[1] in COMB_OPS:
        return
    if key[1] in OPS:
        return
    if len(key) == 4 and key[1] in OP_PREFIXES:
        return
    return True


def parse_struct_cond_after_deep_copy(cond, cfg, nfo):
    # resolve any conditions builds using the same subcond refs many times -
    # i.e. remove those refs can create unique items we can modify during parsing:
    # NOTE: This is build time, not eval time, i.e. does not hurt much:
    cond = literal_eval(str(cond))
    res = parse_struct_cond(cond, cfg, nfo)
    p = cfg.get('prefix')
    if not p:
        return res

    def f(prefix, res):
        def f1(prefix, res, *a, state=State, **kw):
            state = state.get(prefix)
            return res(*a, state=state, **kw)

        return partial(f1, prefix=prefix, res=res)

    return f(p, res)


KEY_STR_TYP, KEY_TPL_TYP, KEY_LST_TYP = 1, 2, 3


def key_type(key):
    if _is(key, str):
        return KEY_STR_TYP
    elif _is(key, tuple):
        return KEY_TPL_TYP
    elif _is(key, list) and is_deep_list_path(key):
        return KEY_LST_TYP
    return None


def parse_struct_cond(cond, cfg, nfo):
    """this expects json style conditions
    Examples:
    a and b or c - then we map those to the truthy op
    a eq foo and b eq bar
    [a eq foo] and b
    [a eq foo] and [b is baz]
    """
    cfg['foo'] = 'bar'
    nfo['foo'] = 'bar1'
    f1 = None
    while cond:
        key = cond.pop(0)
        kt = key_type(key)
        if kt:
            if kt == KEY_STR_TYP:
                if f1 and key in COMB_OPS:
                    # cond: b eq bar
                    return partial(
                        COMB_OPS[key], f1, parse_struct_cond(cond, cfg, nfo),
                    )
            elif kt == KEY_LST_TYP:
                key = tuple(key)
            ac = [key]
            while cond:
                if _is(cond[0], str) and cond[0] in COMB_OPS:
                    break
                ac.append(cond.pop(0))
            f1 = atomic_cond(ac, cfg, nfo)
            # now a combinator MUST come:
        else:
            # key is not a key but the first cond:
            f1 = parse_struct_cond(key, cfg, nfo)
    return f1


# _parse_cond = x_parse_cond

OP_PREFIXES = {'not', 'not_rev', 'rev_not', 'rev'}


def atomic_cond(cond, cfg, nfo):
    # ------------------------------------------------ Handle atomic conditions
    # cond like ['foo', 'not', 'le', '10']
    key = cond.pop(0)
    # autocondition for key only: not rev contains (None, 0, ...):
    if len(cond) == 0:
        comp = 'truthy'
        cond.insert(0, 0)
        cond.insert(0, comp)
    elif len(cond) == 1 and key == 'not':
        key = cond.pop(0)
        comp = 'falsy'
        cond.insert(0, 0)
        cond.insert(0, comp)

    nfo['keys'].add(key)

    # prefixes infront of the operator: not and rev - in any combi:
    # if sep was spc we replaced them at tokenizing with e.g. not_rev
    not_, rev_ = False, False
    # we accept [not] [rev] and also [rev] [not]
    for i in 1, 2:
        if cond[0] in OP_PREFIXES:
            nr = cond.pop(0)
            not_ = True if 'not' in nr else not_
            rev_ = True if 'rev' in nr else rev_

    op = cond.pop(0)
    f_op = OPS.get(op)
    if not f_op:
        raise Exception('Operator %s not known' % op)

    f_ot = cfg.get('ops_thru')
    if f_ot:
        f_op = partial(f_ot, f_op)

    val = cond.pop(0)
    # foo eq "42" -> tokenized to 'foo', 'eq', 'str:42' -> should now not
    # become number 42:
    if str(val).startswith('str:'):
        val = str(val[4:])
    else:
        if cfg.get('autoconv', True):  # can do this in the build phase already:
            val = py_type(val)  # '42' -> 42

    f_lookup = cfg['lookup']
    # we do what we can in the building not the evaluation phase:
    acl = cfg.get('autoconv_lookups', False)
    if 'cfg' in cfg['lookup_args']:
        fp_lookup = partial(f_lookup, key, val, cfg=cfg)
    else:
        fp_lookup = partial(f_lookup, key, val)

    # try save stackframes and evaluations for the eval phase:
    if any((acl, rev_, not_)):
        f_res = partial(f_atomic_arn, f_op, fp_lookup, key, val, not_, rev_, acl)
    else:
        # normal case:
        f_res = partial(f_atomic, f_op, fp_lookup, key, val)
    return f_res


# ------------------------------------------------------------ Evaluation Phase
# we do these two versions for with cfg and w/o to safe a stackframe
# (otherwise a lambda would be required - or checking for cfg at each eval)
# when you change, check this number for effect on perf:
# 2 ~/GitHub/pycond/tests $ python test_pycond.py Perf.test_perf | grep 'fast
# ('With fast lookup function:', 2.1161916086894787)
def f_atomic(f_op, fp_lookup, key, val, **kw):
    # normal case - be fast:
    try:
        return f_op(*fp_lookup(**kw))
    except Exception as ex:
        if ex.__class__ == Async:
            raise
        msg = ''
        if fp_lookup != state_get:
            msg = '. Note: A custom lookup function must return two values:'
            msg += ' The cur. value for key from state plus the compare value.'
        raise Exception(
            '%s %s. key: %s, compare val: %s%s'
            % (ex.__class__.__name__, str(ex), key, val, msg)
        )


def f_atomic_arn(f_op, fp_lookup, key, val, not_, rev_, acl, **kw):
    # when some switches are set in cfg:
    k, v = fp_lookup(**kw)
    if acl is True:
        k = py_type(k)
    if rev_ is True:
        k, v = v, k
    return not f_op(k, v) if not_ == True else f_op(k, v)


# ------------------------------------------------------------------ Public API
def sorted_keys(l):
    a = [i for i in l if _is(i, tuple)]
    b = l - set(a)
    return sorted(list(b)) + sorted(a, key=len)


def deserialize_str(cond, check_dict=False, **cfg):
    try:
        return json.loads(cond), cfg
    except:
        pass
    cfg['brkts'] = brkts = cfg.get('brkts', '[]')

    if check_dict:
        # in def qualify we accept textual (flat) dicts.
        # The cond strings (v) will be sent again into this method.
        p = cond.split(':', 1)
        if len(p) > 1 and not ' ' in p[0] and not brkts[0] in p[0]:
            kvs = [c.strip().split(':', 1) for c in cond.split(',')]
            return dict([(k.strip(), v.strip()) for k, v in kvs]), cfg

    sep = cfg.pop('sep', KV_DELIM)
    if cond.startswith('deep:'):
        cond = cond.split('deep:', 1)[1].strip()
        cfg['deep'] = '.'
    cond = tokenize(cond, sep=sep, brkts=brkts)
    return to_struct(cond, cfg['brkts']), cfg


def parse_cond(cond, lookup=state_get, **cfg):
    """ Main function.
        see tests
    """
    nfo = {'keys': set()}
    if is_str(cond):
        cond, cfg = deserialize_str(cond, **cfg)

    if cfg.get('get_struct'):
        return cond, cfg

    if cfg.get('deep'):
        lookup = partial(state_get_deep, deep=cfg['deep'])

    for _lp in ('lookup_provider', 'lookup_provider_dict'):
        lp = cfg.get(_lp)
        if lp:
            lookup = lookup_from_provider(lp, cfg, lookup, is_dict='dict' in _lp)

    cfg['lookup'] = lookup
    cfg['lookup_args'] = sig_args(lookup)
    cond = parse_struct_cond_after_deep_copy(cond, cfg, nfo)
    nfo['keys'] = sorted_keys(nfo['keys'])
    provider = cfg.get('ctx_provider')
    if provider:
        nfo['complete_ctx'] = complete_ctx_data(nfo['keys'], provider=provider)
    return cond, nfo


def complete_ctx_data(keys, provider):
    def _getter(ctx, keys, provider):
        for k in keys:
            v = ctx.get(k, nil)
            if v != nil:
                continue
            ctx[k] = getattr(provider, k)(ctx)
        return ctx

    return partial(_getter, keys=keys, provider=provider)


# where we store intermediate results, e.g. from lookup providers:
CACHE_KEY = '.pyc_cache'
CACHE_KEY_ASYNC = '.async'


def pop_cache(state, prefix):
    """prefix e.g. "payload" in full messages with headers"""
    if prefix:
        state = state.get(prefix)
    return state.pop(CACHE_KEY, 0)


def add_cache(state, k, v):
    state[CACHE_KEY][k] = v


def from_cache(state, key, val=None):
    cache = state.get(CACHE_KEY)
    if cache is None:
        cache = state[CACHE_KEY] = {}
    v = cache.get(key, nil)
    if v != nil:
        return v, val


class Async(Exception):
    pass


def func_is_async_but_we_are_sync(k, state, cfg):
    if k in cfg.get('asyn', '') and not from_cache(state, CACHE_KEY_ASYNC):
        return True


def lookup_from_provider(provider, cfg, lookup, is_dict):
    """
    Wrapping the normal lookup function into a fallback to getting a function
    from a lookup provider and calling it.

    Provider can be dict of functions or a class.
    """

    def wrapped(provider, lookup, is_dict, k, v, cfg, state=State, **kw):
        """
        First try the normal lookup, then fall back to provider.

        Provider lookup result values get cached.
        """
        kv = from_cache(state, k, v)
        if kv:
            return kv
        kv = lookup(k, v, cfg, state=state, **kw)
        if kv[0] != None:
            return kv
        if is_dict:
            f = provider.get(k)
            if f:
                # convention, dict of functions under this key:
                f = f['func']
        else:
            f = getattr(provider, k, None)

        if func_is_async_but_we_are_sync(k, state, cfg):
            add_cache(state, CACHE_KEY_ASYNC, True)
            raise Async([1])

        if not f:
            # return what the normal lookup returned:
            return None, v
        # key is dropped, it was the function name:
        kv = f(v, state, cfg, **kw)
        add_cache(state, k, kv[0])
        return kv

    return partial(wrapped, provider, lookup, is_dict, cfg=cfg)


def pycond(cond, *a, **cfg):
    """ condition function - for those who don't need meta infos """
    return parse_cond(cond, *a, **cfg)[0]


def run_all_ops_thru(f_hook):
    """ wraps ALL operator evals within a custom function"""
    global OPS_HK_APPLIED
    if OPS_HK_APPLIED == f_hook:
        return

    def ops_wrapper(f_op, f_hook, a, b):
        return f_hook(f_op, a, b)

    ops = OPS.keys()
    for k in ops:
        OPS[k] = partial(ops_wrapper, OPS[k], f_hook)
    OPS_HK_APPLIED = f_hook


def py_type(v):
    if not is_str(v):
        return v

    def _(v):
        # returns a str(v) if float and int do not work:
        for t in float, int, str:
            try:
                return t(v)
            except:
                pass

    return (
        True
        if v == 'true'
        else False
        if v == 'false'
        else None
        if v == 'None'
        else _(v)
    )


# -------------- Following Code Only for Parsing String Conditions Into Structs

KV_DELIM = ' '  # default seperator for strings


def tokenize(cond, sep=KV_DELIM, brkts=('[', ']')):
    """ walk throug a single string expression """
    # '[[ a' -> '[ [ a', then split
    esc, escaped, have_apo_seps = [], [], False

    # remove the space from the ops here, comb ops are like 'and_not':
    for op in COMB_OPS:
        if '_' in op:
            cond = cond.replace(op.replace('_', sep), op)
    for op, repl in NEG_REV.items():
        cond = cond.replace(op, repl)

    cond = [c for c in cond]
    r = []
    while cond:
        c = cond.pop(0)
        have_apo = False
        for apo in '"', "'":
            if c != apo:
                continue
            have_apo = True
            r += 'str:'
            while cond and cond[0] != apo:  # and r[-1] != '\\':
                c = cond.pop(0)
                if c == sep:
                    c = '__sep__'
                    have_apo_seps = True
                r += c
            if cond:
                cond.pop(0)
            continue
        if have_apo:
            continue

        # esape:
        if c == '\\':
            c = cond.pop(0)
            if c in escaped:
                key = esc[escaped.index(c)]
            else:
                escaped.append(c)
                key = '__esc__%s' % len(escaped)
                esc.append(key)
            r += key
            continue

        isbr = False
        if c in brkts:
            isbr = True
            if r and r[-1] != sep:
                r += sep
        r += c
        if isbr and cond and cond[0] != sep:
            r += sep

    cond = ''.join(r)

    # replace back the escaped stuff:
    if not esc:
        # be fast:
        res = cond.split(sep)
    else:
        # fastets before splitting:
        cond = cond.replace(sep, '__ESC__')
        for i in range(len(esc)):
            cond = cond.replace(esc[i], escaped[i])
        res = cond.split('__ESC__')
    # replace back the previously excluded stuff in apostrophes:
    if have_apo_seps:
        res = [part.replace('__sep__', sep) for part in res]
    return res


def to_struct(cond, brackets='[]'):
    """Recursively scanning through a tokenized expression and building the
    condition function step by step
    """
    openbrkt, closebrkt = brackets
    expr1 = None
    res = []
    while cond:
        part = cond.pop(0)
        if part == openbrkt:
            lev = 1
            inner = []
            while not (lev == 1 and cond[0] == closebrkt):
                inner.append(cond.pop(0))
                if inner[-1] == openbrkt:
                    lev += 1
                elif inner[-1] == closebrkt:
                    lev -= 1
            cond.pop(0)
            res.append(to_struct(inner, brackets))
        else:
            res.append(part)

    return res


# ----------------------------------------------------------------------------- qualify


def qualify(conds, lookup=state_get, return_type=False, **cfg):
    """
    conds = set of conditions in any acceptable format or a single one.

    """
    if _is(conds, str):
        conds, cfg = deserialize_str(conds, check_dict=True, **cfg)
    built = {}  # store all built named conditions here
    conds, is_single, is_named_listed = init_conds(conds, cfg, built)

    # built dict of named conds - conds is the list of them, i.e. with order:
    b = build(conds, lookup=sub_lookup(lookup, built), cfg=cfg, into=built)

    # was a single condition passed?
    if is_single:
        built = {'root': b}
        conds = [['root', conds]]

    root = cfg.get('root')
    if 'root' in built and root is None:
        root = cfg['root'] = 'root'

    if root is not None:
        # put it first, we'll break after evaling that:
        c = []
        for k, v in conds:
            if k == root:
                c.insert(0, [k, v])
            else:
                c.append([k, v])
        conds = c

    f = partial(run_conds, conds=conds, built=built, is_single=is_single, **cfg)
    if return_type:
        return f, is_single
    else:
        return f


def norm(cond):
    """
    Do we have a single condition, which we return double bracketted or a list of conds?

    We also return if the cond is_single
    """
    # given as ['foo', 'eq', 'bar'] instead [['foo', 'eq', 'bar']]?
    kt = key_type(cond[0])
    if kt:
        cond = [cond]
    if len(cond) == 1:
        # could be a single key multicond, given as list, then len is 2:
        if len(cond[0]) != 2:
            return cond, True
        return cond, False

    elif _is(cond[1], str) and cond[1] in COMB_OPS:
        return cond, True

    # A list of conds:
    return cond, False


def is_named_listed_set_of_conds(cond):
    """
    Is cond like: [[<name>, <conditionlist>], ...] I.e. just given alternative to dicts, since ordered?
    """
    try:
        for c in cond:
            if _is(c, list) and c and _is(c[0], (int, bool, float)):
                continue
            if not key_type(c[0]):
                return
            if not _is(c[1], list):
                return
            if _is(c[1], str) and c[1] in COMB_OPS:
                return
    except:
        return
    # breakpoint()  # FIXME BREAKPOINT
    return True


def init_conds(conds, cfg, built, prefix=()):
    """
    Recurses into conds

    Returns
    - conds in normalized format as list of {'cond': ..} dicts
    - is_single
    - is_named_listed
    """
    # save some clutter:
    def recurse(conds, cfg=cfg, built=built, prefix=prefix):
        return init_conds(conds, cfg, built, prefix)[0]

    # a multi cond is a list of conds, with substreams behind
    if _is(conds, str):
        conds = deserialize_str(conds, **cfg)[0]

    if not _is(conds, (list, dict)) or not conds:
        raise Exception('Cannot parse: %s' % str(conds))

    is_single = False
    if _is(conds, list):

        cond, is_single = norm(conds)
        if is_single:
            return {'cond': conds}, is_single, False

        elif is_named_listed_set_of_conds(cond):
            cs = [[key, recurse(c)] for key, c in cond]
            return cs, is_single, True

        else:
            return [recurse(c) for c in conds], is_single, False

    elif _is(conds, dict):
        res = [[k, recurse(v, prefix=prefix + (k,))] for k, v in conds.items()]
        for k in dict(res):
            built[k] = {}

        return res, is_single, False

    raise  # never


def build(conds, lookup, cfg, into):
    if _is(conds, dict) and 'cond' in conds:
        # conds['built'] = parse_cond(conds['cond'], lookup)  # , **cfg)
        return parse_cond(conds['cond'], lookup, **cfg)

    for k, v in conds:
        if _is(v, list):
            if norm(v)[1] == True:
                into[k] = build(v, lookup, cfg, into)
            else:
                into[k] = [build(c, lookup, cfg, into) for c in v]
        else:
            into[k] = build(v, lookup, cfg, into)


def sub_lookup(lookup, built):
    """
    Returns the wanted lookup function but with a fallback to other named sub conds
    """

    def lu(key, v, cfg, state=State, lookup=lookup, built=built, **kw):
        kv = from_cache(state, key, v)
        if kv:
            return kv
        kv = lookup(key, v, cfg, state, **kw)
        if kv[0] != None:
            return kv

        # not found -> check: is the key a named condition?
        sub_cond_ref = lookup(key, v, cfg, state=built, **kw)
        if sub_cond_ref[0] == None:
            # nope - so return the None:
            return kv
        # cache value of named condition:
        val = state[CACHE_KEY][key] = sub_cond_ref[0][0](state=state, **kw)
        return val, v

    return lu


def run_conds(state, conds, built, is_single, **kw):
    """In data path (hot)"""
    if is_single:
        r = built['root'][0](state=state, **kw)
        pop_cache(state, kw.get('prefix'))
        return r

    if _is(conds, dict) and conds.get('cond'):
        f = built[0](state=state, **kw)
        return f

    r = {}
    for k, v in conds:
        b = built[k]
        if _is(v, list):
            r[k] = [
                run_conds(state, c, b[i], is_single, **kw)
                for i, c in zip(range(len(v)), v)
            ]
        else:
            r[k] = run_conds(state, v, b, is_single, **kw)

        # user wants only partial evaluation?
        if kw.get('root') not in (None, False):
            break

    c = pop_cache(state, kw.get('prefix'))
    # deliver this as well, contains the function call results.
    # can't hurt r anyway not part of the original data:
    if c:
        # r[CACHE_KEY] = c
        # print('cache', c)
        r.update(c)
    return r


# ---------------------------------------------------------------------------------  rx


def import_rx():
    from rx import operators as rx
    import rx as Rx

    return Rx, rx


import time


def rx_async(exc_msg):
    Rx, rx = import_rx()
    x, cfg, pcond, is_single, into = exc_msg

    sched = cfg.get('scheduler')
    timeout = cfg.get('timeout', 1)
    # no action by default:
    timeout_cb = partial(cfg.get('timeout_cb', lambda x: nil))

    def runconds(x, cfg=cfg, pcond=pcond, into=into):
        """
            We are in a seperate greenlet now, and may block
            """
        r = pcond(x)
        into.update(r)
        # forward the item itself:
        return x

    return Rx.merge(
        Rx.just([x, cfg]).pipe(rx.delay(timeout), rx.map(timeout_cb)),
        Rx.just(x).pipe(rx.delay(0, sched), rx.map(runconds)),
    ).pipe(rx.first(), rx.filter(lambda x: x != nil))


def rxop(cond, func=None, into=None, **cfg):
    """for streaming data (optional)"""
    Rx, rx = import_rx()
    pcond, is_single = qualify(cond, return_type=True, **cfg)

    asyn = cfg.get('asyn')
    if is_single:
        if asyn:
            raise Exception('Async mode not supported for simple filters')
        f = func or (lambda pcond, x: bool(pcond(x)))
        return rx.filter(partial(f, pcond))

    def fsync(x, pcond=pcond, cfg=cfg, into=into, asyn=asyn):
        d = x if into is None else x.setdefault(into, {})
        print(x)
        try:
            m = pcond(x)
            d.update(m)
            return x
        except Async as ex:
            if not asyn:
                raise
            exc_msg = [x, cfg, pcond, is_single, d]
            return exc_msg

    if not asyn:
        return rx.map(fsync)
    else:
        return rx.pipe(
            rx.map(fsync),
            rx.group_by(lambda x: isinstance(x, dict)),
            rx.flat_map(lambda s: s if s.key else s.pipe(rx.flat_map(rx_async))),
        )
