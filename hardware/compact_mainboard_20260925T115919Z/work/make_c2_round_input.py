"""Next routing round input: the trial signal connections Altium still lists as unrouted (same exclusions as the trial).
usage: python make_c2_round_input.py DRC.json OUT.json"""
import json, os, re, sys
EV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'evidence')
keep = []
for s in json.load(open(os.path.join(EV, sys.argv[1])))['details']:
    m = re.match(r'Un-Routed Net Constraint: Net (\S+) Between (.*) And (.*)$', s.strip())
    if m and m.group(1) not in ('GND', '3V3_DIG', '3V0_ANA') and 'J_FPC' not in m.group(2) + m.group(3):
        keep.append(s)
json.dump({'total': len(keep), 'summary': {}, 'details': keep}, open(os.path.join(EV, sys.argv[2]), 'w'))
print(len(keep), 'connections ->', sys.argv[2])
