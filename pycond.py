'''
Condition parser

See README.
See Tests.

DEV Notes:

    f_xyz denotes a function (we work a lot with lambdas and partials)

'''

from __future__ import print_function
import operator, sys
import inspect
from functools import partial

PY2 = sys.version_info[0] == 2
#is_str = lambda s: isinstance(s, basestring if PY2 else (bytes, str))
if PY2:
    is_str   = lambda s: isinstance(s, basestring)
    sig_args = lambda f: inspect.getargspec(f).args
else:
    is_str   = lambda s: isinstance(s, (bytes, str))
    sig_args = lambda f: list(inspect.signature(f).parameters.keys())



KV_DELIM = ' ' # default seperator for strings

OPS = dict([(k, getattr(operator, k)) for k in dir(operator)])
# see api below for these:
OPS_HK_APPLIED = False

def truthy(k, v=None):
    return True if k else False

OPS['truthy'] = truthy

# if val in these we deliver False:
FALSES = (None, False, '', 0, {}, [], ())

# default lookup of keys here - no module does NOT need to have state.
# its a convenience thing, see tests:
State = {}
def state_get(key, val, cfg, state=State, **kw):
    # a lookup function can modify key AND value, i.e. returns both:
    return state.get(key), val # default k, v access function

def dbg_get(key, val, cfg, state=State, *a, **kw):
    res = state_get(key, val, cfg, state, *a, **kw)
    val = 'FALSES' if val == FALSES else val
    out('Lookup:', key, val, '->', res[0])
    return res

out= lambda *m: print(' '.join([str(s) for s in m]))

# Combining operators:
# NO! spaces in the keys. User may have spaces in the expression though.
# better no lambdas:
def or_not(a, b)             : return a or not b
def and_not(a, b)            : return a and not b
def combine(f_op, f, g, **kw): return f_op(f(**kw), g(**kw))

COMB_OPS = {
         'or'     : operator.or_
        ,'and'    : operator.and_
        ,'or_not' : or_not
        ,'and_not': and_not
        ,'xor'    : operator.xor
        } # extensible



# those from user space are also replaced at tokenizing time:
NEG_REV = {'not rev': 'not_rev', 'rev not': 'rev_not'}

def py_type(v):
    if not is_str(v):
        return v
    def _(v):
        # returns a str(v) if float and int do not work:
        for t in float, int, str:
            try: return t(v)
            except: pass
    return ( True if v == 'true' else False if v == 'false' else
             None if v == 'None' else _(v) )

def tokenize(cond, sep=KV_DELIM, brkts=('[', ']')):
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
            while cond and cond[0] != apo and r[-1] != '\\':
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


def find_closing_brack(cond, openbrkt, closebrkt):
    lev = 1
    i = 0
    for c in cond[1:]:
        i += 1
        lev += 1 if c == openbrkt else -1 if c == closebrkt else 0
        if lev == 0:
            return i
    f, op, n = cond[1:i], None, None
    if i < len(cond) - 1:
        op = cond[i + 1]
        n = cond[i + 2:]
    return f, op, n



def _parse_cond( cond, cfg, nfo ):
    '''Recursively scanning through a tokenized expression and building the
    condition function step by step
    '''
    openbrkt, closebrkt = cfg['brkts']
    strct = nfo['strct'] # structure of lambdas to return. not relevant.
    expr1 = None
    # ----------------------------------------------- Handle nesting recursions
    if cond and cond[0] == openbrkt: # [
        idx = find_closing_brack(cond, openbrkt, closebrkt)
        expr1, strct1 = _parse_cond(cond[1:idx], cfg, nfo)
        cond = cond[idx + 1:]
    if not cond:
        return expr1, [strct1]

    # ---------------------------------------------- Handle combining operators
    # and / or ?
    # foo eq bar and baz..., i.e. given w/o brackets?
    # we return then parse_cond( [ foo eq bar ] and [baz...]
    # c i: just temp. helpers for within the checking loop:
    c, i = [cond[0]], 1
    for part in cond[1:]:
        i += 1

        if part == openbrkt:
            break # all well, brackets given

        if is_str(part) and part in COMB_OPS:
            c.insert(0, openbrkt)
            [ c.append(v) for v in (closebrkt, part, openbrkt) ]
            c.extend(cond[i:])
            c.append(closebrkt)
            return _parse_cond(c, cfg, nfo)

        else:
            c.append(part)

    # now we have the first expression in brkts parsed and do the next one
    # after a combining operator:
    f_op = COMB_OPS.get(cond[0]) # f_op: combining-operator function
    if f_op:
        op_n, nxt = cond[0], 1
        # we recurse into the second part, first we have
        expr2, strct2 = _parse_cond(cond[nxt:], cfg, nfo)
        #strct = [strct1, "COMB_OPS['%s']" % op_n, strct2]
        return partial(combine, f_op, expr1, expr2), strct

    # ------------------------------------------------ Handle atomic conditions
    # cond like ['foo', 'not', 'le', '10']
    key = cond.pop(0)
    # autocondition for key only: not rev contains (None, 0, ...):
    if len(cond) == 0:
        cond.insert(0, 0)
        cond.insert(0, 'truthy')

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
        if cfg.get('autoconv', True): # can do this in the build phase already:
            val = py_type(val) # '42' -> 42

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
                f_atomic_arn, f_op, fp_lookup, key, val, not_, rev_, acl)
    else:
        # normal case:
        f_res = partial(f_atomic, f_op, fp_lookup, key, val)
    return f_res, strct

    ## document what we did:
    #strct = [ "%s('%s', '%s')" % (lookup.__name__, key, val),
    #          "OPS['%s']"% op, val ]
    #if not_:
    #    strct.insert(1, 'not')

# ------------------------------------------------------------ Evaluation Phase
# we do these two versions for with cfg and w/o to safe a stackframe
# (otherwise a lambda would be required - or checking for cfg at each eval)
# when you change, check this number for effect on perf:
# 2 ~/GitHub/pycond/tests $ python test_pycond.py Perf.test_perf | grep 'fast
# ('With fast lookup function:', 2.1161916086894787)
def f_atomic(f_op, fp_lookup, key, val, **kw):
    # normal case - be fast:
    return f_op(*fp_lookup(**kw))

def f_atomic_arn(f_op, fp_lookup, key, val, not_, rev_, acl, **kw):
    # when some switches are set in cfg:
    k, v = fp_lookup(**kw)
    if acl  is True: k = py_type(k)
    if rev_ is True: k, v = v, k
    return not f_op(k, v) if not_ == True else f_op(k, v)



# ------------------------------------------------------------------ Public API
def parse_cond( cond, lookup=state_get, **cfg ):
    ''' Main function.
        see tests
    '''

    cfg['brkts'] = brkts = cfg.get('brkts', '[]')

    sep = cfg.pop('sep', KV_DELIM)
    if is_str(cond):
        cond = tokenize(cond, sep=sep, brkts=brkts)

    nfo = {'keys': set(), 'strct': []}
    cfg['lookup'] = lookup
    cfg['lookup_args'] = sig_args(lookup)
    cond, strct = _parse_cond(cond, cfg, nfo)
    nfo['keys'] = sorted(list(nfo['keys']))
    return cond, nfo


def condf(cond, *a, **cfg):
    ''' condition function - for those who don't need meta infos '''
    return parse_cond(cond, *a, **cfg)[0]


def run_all_ops_thru(f_hook):
    ''' wraps ALL operator evals within a custom function'''
    global OPS_HK_APPLIED
    if OPS_HK_APPLIED == f_hook:
        return
    def ops_wrapper(f_op, f_hook, a, b):
        return f_hook(f_op, a, b)
    ops= OPS.keys()
    for k in ops:
        OPS[k] = partial(ops_wrapper, OPS[k], f_hook)
    OPS_HK_APPLIED = f_hook


