"""Readback check after a native write: expected end state = BEFORE - deletions + additions (multisets of
tracks/vias with net/layer/geometry/width), compared with the fresh native AFTER export; pads and
component records must be unchanged.
usage: python verify_readback.py BEFORE_GEOMETRY.txt AFTER_GEOMETRY.txt OPS.txt"""
import sys
from collections import Counter

before, after, ops = sys.argv[1:4]
R = lambda v: round(float(v), 3)


def tkey(layer, net, x1, y1, x2, y2, w):
    a, b = (R(x1), R(y1)), (R(x2), R(y2))
    return (layer, net, min(a, b), max(a, b), R(w))


def load(p):
    tr, vi, other = Counter(), Counter(), Counter()
    for l in open(p, encoding='utf-8', errors='replace'):
        r = l.rstrip('\n').split('|')
        if r[0] == 'TRACK':
            tr[tkey(r[1], r[2], r[3], r[4], r[5], r[6], r[7])] += 1
        elif r[0] == 'VIA':
            vi[(r[1], R(r[2]), R(r[3]), R(r[4]), R(r[5]))] += 1
        elif r[0] in ('PAD', 'COMP'):
            other[tuple(r)] += 1
    return tr, vi, other


tb, vb, ob = load(before)
ta, va, oa = load(after)
exp_t, exp_v = Counter(tb), Counter(vb)
problems = []
for l in open(ops):
    f = l.rstrip('\n').split('|')
    if f[0] == 'TRACK':
        exp_t[tkey(f[2], f[1], f[3], f[4], f[5], f[6], f[7])] += 1
    elif f[0] == 'VIA':
        exp_v[(f[1], R(f[2]), R(f[3]), R(f[4]), R(f[5]))] += 1
    elif f[0] == 'DEL_TRACK':
        a, b = (R(f[3]), R(f[4])), (R(f[5]), R(f[6]))
        hits = [k for k in exp_t if k[0] == f[2] and k[1] == f[1] and k[2] == min(a, b) and k[3] == max(a, b) and exp_t[k] > 0]
        if len(hits) != 1:
            problems.append(f'delete target ambiguous/missing: {f}')
        else:
            exp_t[hits[0]] -= 1
    elif f[0] == 'DEL_VIA':
        hits = [k for k in exp_v if k[0] == f[1] and k[1] == R(f[2]) and k[2] == R(f[3]) and exp_v[k] > 0]
        if len(hits) != 1:
            problems.append(f'via delete target ambiguous/missing: {f}')
        else:
            exp_v[hits[0]] -= 1
    elif f[0] == 'WIDEN_TRACK':
        a, b = (R(f[3]), R(f[4])), (R(f[5]), R(f[6]))
        hits = [k for k in exp_t if k[0] == f[2] and k[1] == f[1] and k[2] == min(a, b) and k[3] == max(a, b) and exp_t[k] > 0]
        if len(hits) != 1:
            problems.append(f'widen target ambiguous/missing: {f}')
        else:
            exp_t[hits[0]] -= 1
            exp_t[(hits[0][0], hits[0][1], hits[0][2], hits[0][3], R(f[7]))] += 1
exp_t = +exp_t; exp_v = +exp_v
if exp_t != ta:
    problems.append(f'track state mismatch: missing {sum((exp_t - ta).values())}, unexpected {sum((ta - exp_t).values())}')
    problems += [f'  missing {k}' for k in list(exp_t - ta)[:5]] + [f'  unexpected {k}' for k in list(ta - exp_t)[:5]]
if exp_v != va:
    problems.append(f'via state mismatch: missing {sum((exp_v - va).values())}, unexpected {sum((va - exp_v).values())}')
if ob != oa:
    problems.append(f'pad/component records changed: -{sum((ob - oa).values())} +{sum((oa - ob).values())}')
print(f'tracks {sum(tb.values())} -> {sum(ta.values())} (expected {sum(exp_t.values())}) | vias {sum(vb.values())} -> {sum(va.values())} (expected {sum(exp_v.values())}) | pads/comps unchanged={ob == oa}')
print('READBACK', 'PASS' if not problems else 'FAIL')
for p in problems:
    print(' ', p)
