"""
Condition parser

See README.
See Tests.

DEV Notes:

    f_xyz denotes a function (we work a lot with lambdas and partials)

"""

from __future__ import print_function
import operator, sys
import inspect
from functools import partial
from copy import deepcopy

PY2 = sys.version_info[0] == 2
# is_str = lambda s: isinstance(s, basestring if PY2 else (bytes, str))
if PY2:
    is_str = lambda s: isinstance(s, basestring)
    sig_args = lambda f: inspect.getargspec(getattr(f, 'func', f)).args
else:
    is_str = lambda s: isinstance(s, (bytes, str))
    sig_args = lambda f: list(inspect.signature(f).parameters.keys())

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
State = {}


def state_get_deep(key, val, cfg, state=State, deep='.', **kw):
    # key maybe already path tuple - or string with deep as seperator:
    parts = key.split(deep) if isinstance(key, str) else list(key)
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
    if key == 'gkfoo':
        breakpoint()
    if isinstance(key, tuple):
        return state_get_deep(key, val, cfg, state, **kw)
    else:
        return state.get(key), val  # default k, v access function


def dbg_get(key, val, cfg, state=State, *a, **kw):
    res = state_get(key, val, cfg, state, *a, **kw)
    val = 'FALSES' if val == FALSES else val
    out('Lookup:', key, val, '->', res[0])
    return res


out = lambda *m: print(' '.join([str(s) for s in m]))

# Combining operators:
# NO! spaces in the keys. User may have spaces in the expression though.
# better no lambdas:
def or_not(a, b):
    return a or not b


def and_not(a, b):
    return a and not b


def combine(f_op, f, g, **kw):
    f1 = f(**kw)
    # lazy eval:
    if not f1:
        if f_op.__name__ in ('and_', 'and_not'):
            return False
    return f_op(f1, g(**kw))


COMB_OPS = {
    'or': operator.or_,
    'and': operator.and_,
    'or_not': or_not,
    'and_not': and_not,
    'xor': operator.xor,
}  # extensible


# those from user space are also replaced at tokenizing time:
NEG_REV = {'not rev': 'not_rev', 'rev not': 'rev_not'}


def parse_struct_cond_after_deep_copy(cond, cfg, nfo):
    res = parse_struct_cond(deepcopy(cond), cfg, nfo)
    return res


def parse_struct_cond(cond, cfg, nfo):
    """this expects json style conditions
    Examples:
    a and b or c - then we map those to the truthy op
    a eq foo and b eq bar
    [a eq foo] and b
    [a eq foo] and [b is baz]
    """
    f1 = None
    while cond:
        key = cond.pop(0)
        if isinstance(key, (str, tuple)):
            if f1 and key in COMB_OPS:
                # cond: b eq bar
                return partial(
                    combine,
                    COMB_OPS[key],
                    f1,
                    parse_struct_cond(cond, cfg, nfo),
                )
            ac = [key]
            while cond:
                if isinstance(cond[0], str) and cond[0] in COMB_OPS:
                    break
                ac.append(cond.pop(0))
            f1 = atomic_cond(ac, cfg, nfo)
            # now a combinator MUST come:
        else:
            f1 = parse_struct_cond(key, cfg, nfo)
    return f1


# _parse_cond = x_parse_cond


def atomic_cond(cond, cfg, nfo):
    # ------------------------------------------------ Handle atomic conditions
    # cond like ['foo', 'not', 'le', '10']
    key = cond.pop(0)
    # autocondition for key only: not rev contains (None, 0, ...):
    if len(cond) == 0:
        cond.insert(0, 0)
        cond.insert(0, 'truthy')
    elif len(cond) == 1 and key == 'not':
        key = cond.pop(0)
        cond.insert(0, 0)
        cond.insert(0, 'falsy')

    nfo['keys'].add(key)

    # prefixes infront of the operator: not and rev - in any combi:
    # if sep was spc we replaced them at tokenizing with e.g. not_rev
    not_, rev_ = False, False
    # we accept [not] [rev] and also [rev] [not]
    for i in 1, 2:
        if cond[0] in ('not', 'not_rev', 'rev_not', 'rev'):
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
        if cfg.get(
            'autoconv', True
        ):  # can do this in the build phase already:
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
        f_res = partial(
            f_atomic_arn, f_op, fp_lookup, key, val, not_, rev_, acl
        )
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
        msg = ''
        if fp_lookup != state_get:
            msg = '. Note: A custom lookup function must return two values:'
            msg += ' The cur. value for key from state plus the compare value.'
        raise Exception(
            '%s. key: %s, compare val: %s%s' % (str(ex), key, val, msg)
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
def parse_cond(cond, lookup=state_get, **cfg):
    """ Main function.
        see tests
    """
    lp = cfg.get('lookup_provider')
    if lp:
        lookup = lookup_from_provider(provider=lp)
    else:
        if cfg.get('deep'):
            lookup = partial(state_get_deep, deep=cfg['deep'])

    cfg['brkts'] = brkts = cfg.get('brkts', '[]')

    sep = cfg.pop('sep', KV_DELIM)
    nfo = {'keys': set()}
    if is_str(cond):
        cond = tokenize(cond, sep=sep, brkts=brkts)
        cond = to_struct(cond, cfg['brkts'])
    if cfg.get('get_struct'):
        return cond, nfo

    cfg['lookup'] = lookup
    cfg['lookup_args'] = sig_args(lookup)
    cond = parse_struct_cond_after_deep_copy(cond, cfg, nfo)
    nfo['keys'] = sorted(list(nfo['keys']))
    provider = cfg.get('ctx_provider')
    if provider:
        nfo['complete_ctx'] = complete_ctx_data(nfo['keys'], provider=provider)
    return cond, nfo


nil = '\x01'


def complete_ctx_data(keys, provider):
    def _getter(ctx, keys, provider):
        for k in keys:
            v = ctx.get(k, nil)
            if v != nil:
                continue
            ctx[k] = getattr(provider, k)(ctx)
        return ctx

    return partial(_getter, keys=keys, provider=provider)


def lookup_from_provider(provider):
    def _lookup(k, v, state, provider):
        kv = state.get(k, nil)
        if kv == nil:
            kv = state[k] = getattr(provider, k)(state)
        return kv, v

    return partial(_lookup, provider=provider)


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
            cond = cond.replace(op.replace('_', ' '), op)
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
