"""Merge repair rounds that ran IN PARALLEL on the same state (each usually limited with ONLY_BOX / REGIONS).
Rounds are given in priority order. Per round every repair unit (all rows sharing a repair id P<k>, victims P<k>v included)
is renamed P<ROUND><k> so ids never collide.  A unit is dropped when an earlier round already closed the same unrouted
connection or already ripped one of the unit's victims (that victim then stays in the earlier round's hands); deletions
are de-duplicated.  The merged pair still has to go through consistent_repair.py (exact check of everything together).
usage: python merge_rounds.py OUT_ADDS.csv OUT_DELS.csv TAG[=NET,NET...] [TAG ...]
  TAG            round output prefix in evidence/ (REP_BB -> REP_BB_ADDS.csv / REP_BB_DELS.csv)
  =NET,NET...    optional: keep only this round's repairs of these nets (region victim re-routes are always kept)"""
import csv, re, sys

EV = '../evidence/'
fields = ['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax']
pid = lambda g: re.sub(r'v$', '', g.split(':')[0])
out_a, out_d = sys.argv[1:3]
taken_conns, taken_victims = set(), set()
all_adds, all_dels, seen_del = [], [], set()


def del_key(r):
    if r['kind'] == 'TRACK':
        return ('T', r['net'], r['layer'], frozenset(((r['x1'], r['y1']), (r['x2'], r['y2']))))
    return ('V', r['net'], r['x1'], r['y1'])


for spec in sys.argv[3:]:
    tag, _, nets = spec.partition('=')
    nets = set(nets.split(',')) if nets else None
    short = tag.split('_')[-1]
    adds = list(csv.DictReader(open(f'{EV}{tag}_ADDS.csv')))
    dels = list(csv.DictReader(open(f'{EV}{tag}_DELS.csv')))
    units = {}
    for r in adds:
        units.setdefault(pid(r['group']), []).append(r)
    kept, dropped, keep_victims = [], [], set()
    for u, rows in units.items():
        main = [r for r in rows if not r['group'].split(':')[0].endswith('v')]
        conns = {r['conn'] for r in main}
        victims = {r['conn'].split('|', 1)[1] for r in rows if r['conn'].startswith('repair|')}
        victims = {v.split('|', 1)[1] for v in victims}          # 'PLAN_TAG|group' -> plan group name (as in DELS rows)
        bad = (nets is not None and main and not any(r['net'] in nets for r in main)) \
            or (conns & taken_conns) or (victims & taken_victims)
        if bad:
            dropped.append(u); keep_victims |= victims
            continue
        kept.append(u)
        taken_conns |= conns
        for r in rows:
            q = dict(r)
            head, _, rest = q['group'].partition(':')
            q['group'] = re.sub(r'^P', f'P{short}', head) + ':' + rest
            all_adds.append(q)
    own_victims = set()
    for u in kept:
        for r in units[u]:
            if r['conn'].startswith('repair|'):
                own_victims.add(r['conn'].split('|', 2)[2])
    nd = 0
    for r in dels:
        if r['group'] in keep_victims and r['group'] not in own_victims:
            continue                                            # victim of a dropped unit: stays on the board
        k = del_key(r)
        if k in seen_del:
            continue
        seen_del.add(k); all_dels.append(r); nd += 1
    taken_victims |= {r['group'] for r in dels if r['group'] not in keep_victims or r['group'] in own_victims}
    print(f'{tag}: units kept {len(kept)} {sorted(kept)}, dropped {len(dropped)} {sorted(dropped)}; dels kept {nd}/{len(dels)}')
    for u in kept:
        m = [r for r in units[u] if not r['group'].split(':')[0].endswith('v')]
        if m:
            print(f'   {u}: {m[0]["net"]}')
for p, rows in ((out_a, all_adds), (out_d, all_dels)):
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', restval=''); w.writeheader(); w.writerows(rows)
print(f'merged: adds {len(all_adds)} rows, dels {len(all_dels)} rows')
