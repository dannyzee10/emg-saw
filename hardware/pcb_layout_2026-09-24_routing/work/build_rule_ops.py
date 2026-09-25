"""Rule operations for the routing pass (appended to OPS.txt by the caller).
- CLR_FINE_ESCAPE_<ref>: pads of a 0.5 mm-pitch part vs TRACKS within 1 mm of the part: 0.15 mm
  (Situs reported these pads unroutable at the 0.20/0.25 class clearances; narrow scope, JLC-capable).
- Routing-pass preferred widths (power/GND/reference) so pads can be escaped; trunks widened later.
- RoutingLayers: L1 + L3 only; nets with bottom-side (DRL) pads may also use L4. L2 never routed.
"""
import geom as G

objs, comps, keep = G.load()
MIL = 1 / 0.0254
out = []
for ref in ('U_MCU1', 'UP1', 'UP2', 'UP4', 'U_DRL1', 'C_DRL_DEC'):
    pads = [o for o in objs if o.kind == 'PAD' and o.comp == ref]
    x0 = min(p.geom.bounds[0] for p in pads) - 1.0; y0 = min(p.geom.bounds[1] for p in pads) - 1.0
    x1 = max(p.geom.bounds[2] for p in pads) + 1.0; y1 = max(p.geom.bounds[3] for p in pads) + 1.0
    reg = f"InRegionAbsolute({x0*MIL:.4f},{y0*MIL:.4f},{x1*MIL:.4f},{y1*MIL:.4f})"
    out.append(f"RULE_CLR|CLR_FINE_ESCAPE_{ref}|0.15|IsPad And InComponent('{ref}')|IsTrack And {reg}")
for rule, mn, fav, mx in (('WIDTH_EMG_POWER', 0.15, 0.25, 3), ('WIDTH_EMG_GND', 0.15, 0.25, 3),
                          ('WIDTH_EMG_SWITCH', 0.2, 0.3, 1.5), ('WIDTH_EMG_REFERENCE', 0.15, 0.2, 0.5),
                          ('Width', 0.15, 0.2, 0.5)):
    out.append(f"SET_WIDTH|{rule}|{mn}|{fav}|{mx}")
out.append("SET_RL|RoutingLayers|1|0|1|0")
bottom_nets = sorted({o.net for o in objs if o.kind == 'PAD' and o.layers == {'Bottom Layer'} and o.net not in ('GND', '-', '')})
scope = ' Or '.join(f"InNet('{n}')" for n in bottom_nets)
out.append(f"RULE_RL|RL_BOTTOM_PAD_NETS|{scope}|1|0|1|1")
open(G.HERE + 'work/RULE_OPS.txt', 'w').write('\n'.join(out) + '\n')
print('\n'.join(o[:160] for o in out))
print('bottom-pad nets:', len(bottom_nets))
