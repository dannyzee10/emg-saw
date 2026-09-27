# Vc_1 native routing checkpoint BD — 27 September 2026

## Applied change

Added seven 0.20 mm tracks on physical L5 / Mid Layer4, connecting the existing Vc_1 vias at (15.900,11.200) and (24.175,19.325) mm. The 15.7069 mm route follows the `larger_keepout_gap` candidate in `ASTRA_VC1_L5_MANUAL_PATH_BC.json`, avoiding J_FPC1's real all-layer keepout.

No components, vias or existing tracks were moved or removed. No vias were added. No schematic, net assignment, layer rule, width rule, clearance rule, board outline or ground-plane definition was changed. The short route is a bounded exception to the offline L5 pour-reservation policy, not a global removal of that policy. Its copper fits x15.8–24.825, y10.825–19.425 mm. The saved native RoutingLayers rule already permits L5.

Exact operations: `../work/OPS_BD_VC1.txt`. Exact addition/deletion records: `ASTRA_VC1_READY_ADDS.csv` and header-only `ASTRA_VC1_READY_DELS.csv`.

## Native results

- Before-edit BC backup and hashes: `ASTRA_BD_BEFORE_20260927/`.
- Full candidate precheck: seven tracks, zero vias/deletions, **PROBLEMS 0**.
- `ASTRA_APPLY_BD.txt`: native preflight accepted seven additions, rebuilt all six existing polygons, saved and reopened successfully.
- `DRC_C2_6L_BD.txt`: processing completed at 20:25:32 local, document unmodified before/after. Boolean return was False; the actual HTML diagnostic report supplies the counts.
- `DRC_C2_6L_BD.txt.html` / `.json`: **256 total violations, four unrouted**. The sole removed diagnostic versus BC is Vc_1's open connection. No new diagnostic was introduced.
- Remaining unrouted: `WIFI_SPI_CS`, `WIFI_UART_RX`, `MCU_WIFI_UART_TX`, `MCU_WIFI_UART_RX`.
- Other counts unchanged: 6 net antennae, 157 silk-to-mask, 84 silk-to-silk, 5 outline-clearance. Zero reported copper-clearance, short-circuit, width or component-clearance violations. No new GND or supply-net open.
- `GEOMETRY_C2_6L_BD.txt` and `ASTRA_BD_DELTA.json`: exact seven-track addition verified; all 231 component records, 812 pad records and 1,629 fixed records unchanged. Free-track count 2,209→2,216; vias remain454. The writer's net-assigned track count is2,206, excluding ten unassigned tracks counted by the geometry comparison.
- `ASTRA_BD_SCHEMATIC_PROJECT_PRESERVATION.json`: eight SchDocs and PrjPcb byte-identical to BC backup.
- Independent review: `ASTRA_BD_INDEPENDENT_REVIEW.json`.
- Saved PCB hash: `ASTRA_BD_AFTER_HASH.json`.

Channel 4's previously corrected route remains intact. Current native project and PCB are in `../C2_COMPACT_4L_2SIDE/MainBoard/`, named `EMG_MainBoard_Layout.PrjPcb` and `EMG_MainBoard_Layout.PcbDoc`.

## Limits and continuation

The board is not fabrication-ready. The existing via-style batch-check gap and remaining routing/silkscreen/outline work are not resolved by this change. No diagnostics were suppressed.

`ASTRA_BD_STRUCTURE.json` confirms unchanged nets, rules, components, classes, stack, outline and origin. Its conservative whole-stream result remains **not PASS**, retaining opaque Pads6/Texts changes and a changed cached silk-violation stream. The native exported pad geometry/net fields are unchanged; this comparison does not prove every omitted pad/text metadata field identical. These limitations are not hidden behind the routing PASS.

Use BD geometry/DRC for subsequent routes. Preserve both the Vc_1 and channel-4 bounded L5 exceptions. The new Vc_1 addition is intentionally not automatically made rippable in `run_repair.PLANS`; include its CSV explicitly only for an intentional, verified reroute.
