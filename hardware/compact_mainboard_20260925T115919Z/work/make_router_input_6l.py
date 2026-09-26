"""Router input for the C2 6L completion rounds: every unrouted connection Altium lists, except GND (closed by plane stitching,
stitch.py) and 3V0_ANA links whose two ends both lie inside the L5 analog pour region (also stitched).
usage: python make_router_input_6l.py DRC.json OUT.json   (evidence/ paths)   env R_ANA as for stitch.py"""
import json, os, re, sys
from shapely.geometry import Point, Polygon
EV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'evidence')
R_ANA = Polygon([tuple(map(float, p.split(','))) for p in os.environ['R_ANA'].split(';')])
keep, skip = [], 0
for s in json.load(open(os.path.join(EV, sys.argv[1])))['details']:
    m = re.match(r'Un-Routed Net Constraint: Net (\S+) Between (.*) And (.*)$', s.strip())
    if not m:
        continue
    net = m.group(1)
    if net == 'GND':
        skip += 1; continue
    if net == '3V0_ANA':
        pts = [Point(float(a), float(b)) for part in (m.group(2), m.group(3)) for a, b in re.findall(r'\(([-\d.]+)mm,\s*([-\d.]+)mm\)', part)[:1]]
        if all(R_ANA.contains(p) for p in pts):
            skip += 1; continue
    keep.append(s)
json.dump({'total': len(keep), 'summary': {}, 'details': keep}, open(os.path.join(EV, sys.argv[2]), 'w'))
print(len(keep), 'connections ->', sys.argv[2], '| left to stitching:', skip)
