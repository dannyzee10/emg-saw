"""Print DRC detail rows for the given rule-name fragments (default: everything except unrouted and silkscreen)."""
import json, os, sys
d = json.load(open(sys.argv[1]))
det = d['details']
keys = sys.argv[2:] or None
skip = ('Un-Routed', 'Silk')
items = det.items() if isinstance(det, dict) else [(r.get('rule', ''), [r]) for r in det]
for rule, rows in items:
    if keys and not any(k in rule for k in keys):
        continue
    if not keys and any(s in rule for s in skip):
        continue
    print('==', rule, len(rows))
    for r in rows[:40]:
        print('   ', r if isinstance(r, str) else json.dumps(r)[:260])
