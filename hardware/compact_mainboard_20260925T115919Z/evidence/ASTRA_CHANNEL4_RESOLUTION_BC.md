# Channel 4 routing correction — native checkpoint BC

27 September 2026. Routing checkpoint only; not fabrication or hardware-performance approval.

## Applied correction

The former open `NetINA4_3` connected INA4 pin3 to RDD10 pin2 / RDD12 pin2. It was before the ADC; an ADC pin swap would not address it.

- Preserved INA4 position, rotation, side, pin mapping and schematic.
- Moved CL_4 on Bottom from (51.3, 16.05) to (48.2, 16.05) mm. Its 180-degree rotation, UID `\KJVBWSRF`, value, footprint and nets are unchanged.
- Added the short NetINA4_3 route on L5 / Mid Layer4, inside the documented copper envelope x51.2–57.6, y15.1–17.35 mm. The existing native RoutingLayers rule permits this layer; no clearance or layer rule was relaxed.
- Reconnected CL_4 and every INA_OUT_4 endpoint. Applied exactly 19 tracks + 4 vias and removed exactly 18 tracks + 3 vias.
- The input escape and RDD endpoint vias overlap SMT copper; filled/capped via-in-pad process qualification remains required. They are not a declaration that open barrels or tenting alone are suitable.
- Rebuilt the six existing polygons. L2 and L4 GND definitions, stack and outline were preserved; native DRC reported no newly open GND or 3V0_ANA net.

Rotating INA4 was a fallback, not the chosen edit. The checked alternative needed a 0.65 mm relocation and rework of multiple connected routes. Flipping it to Bottom was not implemented.

## Native evidence

Working project: `../C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PrjPcb`.

Working PCB: `../C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc`.

| Evidence | Result |
|---|---|
| `ASTRA_BC_BEFORE_20260927/BEFORE_HASHES.json` | BB PCB/project/eight schematic sheets backed up before mutation |
| `ASTRA_MOVE_CL4.txt` | Native preflight, save, reopen, exact component position and pin/net readback complete |
| `ASTRA_APPLY_BC.txt` | Exact operation preflight, six polygon rebuilds, save/reopen complete; no rule edits |
| `GEOMETRY_C2_6L_BC.txt` | Fresh native read-only geometry export completed |
| `ASTRA_BC_DELTA.json` | PASS: exact copper delta; only authorized CL_4 translation; 230 other packages, 810 other pads and 1,629 fixed records unchanged |
| `ASTRA_BC_SCHEMATIC_PROJECT_PRESERVATION.json` | All eight SchDocs and PrjPcb byte-identical to BB backup |
| `ASTRA_BC_AFTER_HASH.json` | Saved PCB hash for this checkpoint |
| `DRC_C2_6L_BC.txt.html` / `.json` | Fresh native batch DRC: 257 violations; breakdown below |

The geometry verifier counts 2,209 free tracks and 454 vias. Native writer's NET_TRACKS counter is 2,199 because it excludes ten tracks with no assigned net; these two counters have different scopes.

## Actual DRC disposition

| Category | BB | BC |
|---|---:|---:|
| Unrouted | 6 | 5 |
| Net antennae | 6 | 6 |
| Silk-to-mask | 159 | 157 |
| Silk-to-silk | 84 | 84 |
| Board-outline clearance | 5 | 5 |
| Copper clearance | 0 | 0 |
| Shorts | 0 | 0 |
| Width | 0 | 0 |
| Component clearance | 0 | 0 |

Channel 4's NetINA4_3 open is absent from the new native report. There are no new capacitor/output-node opens. The five remaining opens are Vc_1, WIFI_SPI_CS, WIFI_UART_RX, MCU_WIFI_UART_TX and MCU_WIFI_UART_RX.

The native DRC call returned Boolean False, completed processing, and left the document unmodified. Its 257 reported violations, not that Boolean, are the result.

Coverage limitation: Routing Via Style is still excluded from the saved batch selection, and its legacy fixed 0.60/0.30 mm envelope still needs the separately authorized alignment to existing small vias. This checkpoint is not a clean full-board DRC claim.

## Preservation limitations

`ASTRA_BC_STRUCTURE.json` verifies unchanged nets, rules, classes, models, DRC settings, stack/layer configuration, outline and origin. Its strict byte-equality result is **not PASS**: component, pad, body and text streams changed. CL_4's geometric translation is explicitly verified by the native export comparison; save-time model/text serialization also changes these streams. Do not present this strict raw-stream checker as a full pass or infer complete mechanical/model equivalence from the exported fields alone.

## Next work

Resolve the five remaining opens against BC geometry, then complete the separately documented via-rule, width, trace-cleanup, silkscreen and release-evidence work. Keep NetINA4_3's bounded L5 exception intact; do not globally unreserve L5 for analog routing. No schematic pin swaps are required by this channel-4 correction.
