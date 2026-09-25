"""Candidate B limited routing trial -> work/OPS.txt for apply_ops_v6.pas:
  * scoped fine-pitch escape rules CLR_FINE_ESCAPE_B_<ref> (0.15 mm, pads of <ref> vs tracks inside the pads' bbox +1 mm),
    the same form proven in the routing revision, computed at B's new component positions;
  * the routed trial copper from evidence/ROUTE_PLAN_TRIAL.csv (already verified by build_ops.py).
usage: GEOM_FILE=../evidence/GEOMETRY_B_PLACED.txt python make_trial_ops.py"""
import csv, os
import geom as G
objs, comps, keepouts = G.load()
MIL = 1 / 0.0254
lines = []
for ref, reg in sorted(G.FINE_REGIONS.items()):
    x0, y0, x1, y1 = reg.bounds
    s2 = f"IsTrack And InRegionAbsolute({x0 * MIL:.4f},{y0 * MIL:.4f},{x1 * MIL:.4f},{y1 * MIL:.4f})"
    lines.append(f"RULE_CLR|CLR_FINE_ESCAPE_B_{ref}|0.15|IsPad And InComponent('{ref}')|{s2}")
ops = open(os.path.join(G.HERE, 'work', 'OPS.txt')).read().splitlines()
open(os.path.join(G.HERE, 'work', 'OPS.txt'), 'w').write('\n'.join(lines + ops) + '\n')
print('rules', len(lines), 'copper ops', len(ops))
for l in lines:
    print(' ', l[:150])
