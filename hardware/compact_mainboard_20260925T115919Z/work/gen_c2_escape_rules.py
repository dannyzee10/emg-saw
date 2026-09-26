"""Re-anchor the six CLR_FINE_ESCAPE_B_<ref> rules (0.15 mm pad-to-track inside the part's pad bbox + 1 mm; created by
B's trial at B positions) to the parts' C2 positions -> work/C2_RULE_ESC_OPS.txt (RULE|name|2|scope2) for apply_C2_T.pas.
usage: GEOM_FILE=../evidence/GEOMETRY_C2_PLACED.txt BOARD_BOX=12,12,67.1,44 python gen_c2_escape_rules.py"""
import os
import geom as G
G.load()
MIL = 1 / 0.0254
ops = []
for ref, reg in sorted(G.FINE_REGIONS.items()):
    x0, y0, x1, y1 = reg.bounds
    ops.append("RULE|CLR_FINE_ESCAPE_B_%s|2|IsTrack And InRegionAbsolute(%.4f,%.4f,%.4f,%.4f)" % (ref, x0 * MIL, y0 * MIL, x1 * MIL, y1 * MIL))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'C2_RULE_ESC_OPS.txt'), 'w').write('\n'.join(ops) + '\n')
print('\n'.join(o[:150] for o in ops))
