"""Make the routing tools board-agnostic (environment overrides; defaults keep candidate B's values):
  geom.py      BOARD_BOX="x0,y0,x1,y1"  (inner box before the 2 mm corner buffer)
  router5.py   GRID="x0,y0,x1,y1"       (raster window; crop to the board to save memory)
  audit_plan.py ANT_BOX="x0,y0,x1,y1"
  build_ops.py BK13_ZONES=path, OPS_OUT=path"""
import os
here = os.path.dirname(os.path.abspath(__file__))


def patch(fn, old, new):
    p = os.path.join(here, fn); s = open(p, encoding='utf-8').read()
    if new in s:
        return
    assert old in s, (fn, old[:60]); open(p, 'w', encoding='utf-8').write(s.replace(old, new))


patch('geom.py', "BOARD = box(12, 12, 83, 48).buffer(2, 16)   # candidate B outline: 75 x 40 mm, r = 2 mm corners",
      "BOARD = box(*[float(v) for v in os.environ.get('BOARD_BOX', '12,12,83,48').split(',')]).buffer(2, 16)   # default: candidate B 75 x 40, r = 2")
patch('router5.py', "RES = 0.05\nX0, Y1 = 9.5, 55.5\nNX, NY = int(round((90.5 - X0) / RES)), int(round((Y1 - 9.5) / RES))",
      "RES = 0.05\n_g = [float(v) for v in os.environ.get('GRID', '9.5,9.5,90.5,55.5').split(',')]\nX0, Y1 = _g[0], _g[3]\n"
      "NX, NY = int(round((_g[2] - X0) / RES)), int(round((Y1 - _g[1]) / RES))")
patch('audit_plan.py', "ANT = box(41.19, 49.44, 53.47, 54.44)   # antenna keep-out moved with the ST67 (-3, -5)",
      "ANT = box(*[float(v) for v in os.environ.get('ANT_BOX', '41.19,49.44,53.47,54.44').split(',')])   # default: B's antenna keep-out")
s = open(os.path.join(here, 'build_ops.py'), encoding='utf-8').read()
s = s.replace("open(G.HERE + 'evidence/BK13_ZONES.csv')", "open(os.environ.get('BK13_ZONES', G.HERE + 'evidence/BK13_ZONES.csv'))")
s = s.replace("with open(G.HERE + 'work/OPS.txt', 'w') as f:", "with open(os.environ.get('OPS_OUT', G.HERE + 'work/OPS.txt'), 'w') as f:")
if 'import os' not in s.split('\n', 12)[8] and '\nimport os\n' not in s:
    s = s.replace('import csv, sys\n', 'import csv, os, sys\n', 1)
open(os.path.join(here, 'build_ops.py'), 'w', encoding='utf-8').write(s)
print('patched')
