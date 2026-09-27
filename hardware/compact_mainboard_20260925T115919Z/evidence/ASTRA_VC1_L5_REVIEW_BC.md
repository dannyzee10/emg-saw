# Vc_1 L5 escape feasibility from native BC geometry

The remaining native DRC connection is between the existing Vc_1 through vias
at (15.900,11.200) and (24.175,19.325). A fixed seven-segment path on Mid Layer 4
(physical L5), width 0.20 mm, clears all modeled fixed copper and board edges:

```text
(15.900,11.200)
(16.175,10.925)
(20.675,10.925)
(21.675,11.925)
(22.550,11.925)
(24.725,14.100)
(24.725,18.775)
(24.175,19.325)
```

Length is 15.7069 mm. This is a feasible manually specified route, not a claim of
globally minimum length. It requires no new vias, no deleted copper and no
component or via movement. J_REF, J_FPC1 and its 3V0_ANA via stay fixed.

There is a real native J_FPC1 region on Keep Out Layer, x16.7925..20.6075 and
y11.385..13.015. The candidate goes around its board-edge side and east corner;
it does not route beneath the keepout. The nearest copper gap to that corner is
0.272999 mm, exceeding even 0.25 mm. The limiting copper gap is 0.236396 mm to
NetJ_FPC1_8's existing via at (21.500,10.850), versus the geometry model's 0.20 mm
via clearance inside the existing J_FPC1 escape zone. The entire diagonal
(20.675,10.925)..(21.675,11.925), including width, stays inside that zone. After
leaving it, the nearest GND via gap is 0.387209 mm versus 0.25 mm.

Existing L5 power tracks in the source region run from (16.225,12.625) toward
(17.925,14.925) and (17.325,16.725), away from this detour. L2 and L4 ground
layers are not touched. Native RoutingLayers permissions were separately read
and documented in `ASTRA_NETINA4_3_ROUTING_LAYERS_REVIEW.md`: its sole enabled,
priority-1 All-net rule permits L5, and therefore also applies to Vc_1.

Evidence: `ASTRA_VC1_L5_MANUAL_PATH_BC.json`, path name `larger_keepout_gap`.
The JSON includes the original BC geometry path/hash, all segments, closest
obstacles and clearances. `work/astra_check_vc1_l5_paths.py` checks only fixed
hand-specified segments; no router, native application or CAD mutation ran.
The final three width/path comparisons completed in 1.065 s.

Native DRC must confirm exact escape-rule applicability, and native repour must
clear the L5 3V0_ANA polygon around the track. The offline export does not fully
represent poured copper. Routing-width applicability and electrical completion
are not asserted by this geometry-only result.
