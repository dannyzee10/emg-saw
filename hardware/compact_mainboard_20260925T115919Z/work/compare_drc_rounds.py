"""Compare two parsed DRC reports: rule counts, board-outline items, and supply-net unrouted differences.
usage: python compare_drc_rounds.py OLD.json NEW.json   (files in evidence/)"""
import json, os, sys
from collections import Counter
EV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'evidence')
a = json.load(open(os.path.join(EV, sys.argv[1])))['details']
b = json.load(open(os.path.join(EV, sys.argv[2])))['details']


def kind(s):
    return s.split(':')[0].strip()


print('OLD', dict(Counter(kind(s) for s in a)))
print('NEW', dict(Counter(kind(s) for s in b)))
for tag, d in (('OLD', a), ('NEW', b)):
    for s in d:
        if kind(s).startswith('Board'):
            print('%s outline: %s' % (tag, s.strip()[:220]))
sup = lambda d: {s.strip() for s in d if 'Net GND ' in s or 'Net 3V3_DIG ' in s or 'Net 3V0_ANA ' in s}
print('supply unrouted only in NEW:')
for s in sorted(sup(b) - sup(a)):
    print('  ', s[:220])
print('supply unrouted only in OLD:')
for s in sorted(sup(a) - sup(b)):
    print('  ', s[:220])
