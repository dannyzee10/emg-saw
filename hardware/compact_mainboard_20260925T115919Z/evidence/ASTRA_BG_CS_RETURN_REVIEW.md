# CS final candidate: return-path and power review

Read-only review of native BF geometry and frozen `ASTRA_CS_FINAL_ADDS.csv` / `ASTRA_CS_FINAL_DELS.csv` on 2026-09-27. No CAD operations.

Final additions SHA256: `b713babdb147ff524d17168a47eff48c87f4089c44e58c4744d79bb6a185ff2e`.
Final deletions SHA256: `e204cb66ca68241bea0044e2f687120cc8e1f680b081883882b0517d55793e97`.

| CS transition (mm) | Connected signal layers | Nearest retained GND via (mm) | Centre distance |
| --- | --- | --- | --- |
| 50.825, 44.525 | Top / Bottom | 49.1884, 44.5174 | 1.636618 mm |
| 59.125, 44.625 | Bottom / L3 | 57.5759, 44.9410 | 1.581002 mm |
| 60.725, 24.375 | L3 / Top | 61.5780, 24.5427 | 0.869329 mm |

These ground vias are present in `GEOMETRY_C2_6L_BF.txt` and are not deleted by the final candidate. The candidate replaces one other GND via at (51.725,36.375) with (51.675,37.425), which does not change this nearest-via result. All three listed GND vias have 0.60 mm diameter and 0.30 mm drill.

The reopened stack in `STACK6_C2_LOG.txt` places Top 0.0994 mm from L2 GND, L3 0.1164 mm from L4 GND, and Bottom 0.0994 mm from L5. Thus the likely closest references are L2, L4 and local L5 copper respectively. This is an inference from layer spacing, not a field-solver result.

The complete CS Bottom segment, including its local y=43.700 mm detour, lies within the nominal L5 GND-fill outline from `work/OPS_C2_6L_POURS.txt` (at these x coordinates, y=25.6..45.5 mm). Its transition to Top at the resistor uses L3/Top via (60.725,24.375); the superseded seed at (58.38,25.838) and optional stitch at (58.88,24.638) are not included. Therefore the old seed's location near the L5 analog/GND boundary does not describe this route.

`ASTRA_BG_CS_FINAL_GRAPH.json` passes for the frozen 94 additions / 48 deletions: CS endpoints merge; all affected retained copper connections survive. The 3V3_DIG checks pass at original track-width thresholds 0.15, 0.20, 0.30 and 0.40 mm, and VSYS at 0.15, 0.30 and 0.40 mm. No source-to-pad width threshold regresses from 3V3 source UP2.1. The final CS detour changes only CS rows relative to the previously proved power correction.

The geometry export lacks complete poured copper and via layer spans. Via proximity and polygon outlines do not prove local plane attachment, absence of voids, or signal integrity. Fresh native repour/DRC and saved-board verification remain necessary. This note does not authorize additional ground vias or claim that all board finishing work is complete.
