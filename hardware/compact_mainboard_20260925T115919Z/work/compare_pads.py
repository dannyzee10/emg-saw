"""Electrical preservation check between two native geometry exports (baseline A vs candidate B):
every component's pad-name -> net map must be identical; free pads and net sets are compared too.
usage: python compare_pads.py A_GEOMETRY.txt B_GEOMETRY.txt"""
import sys
from collections import defaultdict

def load(fn):
    comp, free, nets, sides = defaultdict(dict), [], set(), {}
    for l in open(fn, encoding='utf-8', errors='replace'):
        f = l.rstrip('\n').split('|')
        if f[0] == 'PAD':
            if f[1] in ('', 'FREE', '-') or f[1].startswith('Free'):
                free.append((f[2], f[3]))
            else:
                comp[f[1]][f[2]] = f[3]
            if f[3] not in ('', '-'):
                nets.add(f[3])
        elif f[0] == 'COMP':
            sides[f[1]] = f[2]
    return comp, free, nets, sides

a, fa, na, sa = load(sys.argv[1])
b, fb, nb, sb = load(sys.argv[2])
bad = []
for ref in sorted(set(a) | set(b)):
    if ref not in a or ref not in b:
        bad.append(f'{ref}: present only in {"A" if ref in a else "B"}'); continue
    if a[ref] != b[ref]:
        diff = {p: (a[ref].get(p), b[ref].get(p)) for p in set(a[ref]) | set(b[ref]) if a[ref].get(p) != b[ref].get(p)}
        bad.append(f'{ref}: pad/net differences {diff}')
print(f'components A {len(a)} B {len(b)}; pads A {sum(len(v) for v in a.values())} B {sum(len(v) for v in b.values())}; '
      f'free pads A {len(fa)} B {len(fb)} same-set={sorted(fa) == sorted(fb)}; nets A {len(na)} B {len(nb)} same={na == nb}')
print('pad/net mismatches:', len(bad))
for x in bad[:30]:
    print('  ', x)
moved_side = [r for r in sa if r in sb and sa[r] != sb[r]]
print('components that changed side:', len(moved_side))
print('PRESERVATION', 'PASS' if not bad and na == nb and sorted(fa) == sorted(fb) else 'FAIL')
