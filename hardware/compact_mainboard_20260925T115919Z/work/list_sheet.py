"""List components of given sheets from BASELINE_COMPONENTS.csv, sorted by y then x (compact planning aid).
usage: python list_sheet.py SHEET [SHEET...]"""
import csv, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = [r for r in csv.DictReader(open(os.path.join(HERE, 'evidence', 'BASELINE_COMPONENTS.csv'))) if r['sheet'] in sys.argv[1:]]
for r in sorted(rows, key=lambda r: (-float(r['y']), float(r['x']))):
    nets = r['nets'].replace('GND', 'G')
    print(f"{r['designator']:18s} {r['side'][0]} x{float(r['x']):6.2f} y{float(r['y']):6.2f} {float(r['w']):5.2f}x{float(r['h']):5.2f} {r['footprint'][:26]:26s} {nets[:70]}")
