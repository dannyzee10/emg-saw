"""Analyse FLIP_TEST_LOG.txt: per component, the transform FlipComponent applied to pad offsets (relative to the
component origin), rotation before/after, and primitive layer changes; and whether save/reopen preserved them."""
import os, re
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
comp, pads, prims = {}, defaultdict(dict), defaultdict(Counter)
for l in open(os.path.join(HERE, 'evidence', 'FLIP_TEST_LOG.txt'), encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if len(f) < 3:
        continue
    tag, kind = f[0], f[1]
    kv = {x.split('=', 1)[0]: x.split('=', 1)[1] for x in f if '=' in x}
    if kind == 'COMP':
        comp[(tag, f[2])] = (f[3], float(kv['X']), float(kv['Y']), kv['ROT'], kv['UID'])
    elif kind == 'PAD':
        pads[(tag, f[2])][f[3]] = (f[4], float(kv['X']), float(kv['Y']), kv['NET'])
    elif kind == 'PRIM':
        prims[(tag, f[2])][(kv['OBJ'], f[4])] += 1
refs = sorted({r for t, r in comp})
for r in refs:
    b, a, o = comp[('BEFORE', r)], comp[('AFTER_FLIP', r)], comp[('REOPEN', r)]
    print(f'{r}: BEFORE {b[0]} rot {b[3]} at ({b[1]},{b[2]}) -> FLIP {a[0]} rot {a[3]} at ({a[1]},{a[2]}) -> REOPEN {o[0]} rot {o[3]} uid_same={b[4] == o[4]}')
    for name, (lay, x, y, net) in sorted(pads[('BEFORE', r)].items()):
        la, xa, ya, na = pads[('AFTER_FLIP', r)][name]
        lo, xo, yo, no = pads[('REOPEN', r)][name]
        dxb, dyb = round(x - b[1], 4), round(y - b[2], 4)
        dxa, dya = round(xa - a[1], 4), round(ya - a[2], 4)
        print(f'   pad {name:3s} {lay[:10]:10s} off ({dxb:+.3f},{dyb:+.3f}) -> {la[:12]:12s} ({dxa:+.3f},{dya:+.3f})  reopen same={abs(xa-xo)<1e-4 and abs(ya-yo)<1e-4 and la==lo}  net {net} -> {na} / {no}')
    ch = []
    for k in set(prims[('BEFORE', r)]) | set(prims[('AFTER_FLIP', r)]):
        if prims[('BEFORE', r)][k] != prims[('AFTER_FLIP', r)][k]:
            ch.append(f"{k}: {prims[('BEFORE', r)][k]}->{prims[('AFTER_FLIP', r)][k]}")
    print('   primitive layer changes:', '; '.join(sorted(ch)))
    print('   reopen primitives identical to after-flip:', prims[('AFTER_FLIP', r)] == prims[('REOPEN', r)])
