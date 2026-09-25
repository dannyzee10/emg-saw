# Placement checkpoint files

**Current working package, 24 September 2026. Fresh native compile is complete and the named native image package is complete. Final PCB save/reopen closure is still pending. Not fabrication approval.**

Open [EMG_MainBoard_Layout.PrjPcb](MainBoard/EMG_MainBoard_Layout.PrjPcb), then [EMG_MainBoard_Layout.PcbDoc](MainBoard/EMG_MainBoard_Layout.PcbDoc). Select **PROTO_1_REMOTE_NTC**.

| Deliverable | Location | Current evidence |
|---|---|---|
| Placement review and remaining qualification gates | [MAIN_BOARD_PLACEMENT_REVIEW.md](MAIN_BOARD_PLACEMENT_REVIEW.md) | Review draft; image package recorded in section 11 |
| Current controlled schematic-symbol snapshot | [EMG_MainBoard_Placement_Frozen_20260924.SchLib](MainBoard/Libraries/EMG_MainBoard_Placement_Frozen_20260924.SchLib) | 231 complete-package definitions; current local footprint bindings verified |
| Native inventory, rules, classes and stack | [NATIVE_FINAL_20260924T015854610Z](evidence/NATIVE_FINAL_20260924T015854610Z/) | Completed read-only native export |
| Current PCB terminal/model evidence | [FINAL_CHECKPOINT_CONNECTIVITY_20260924T030756297Z.md](evidence/FINAL_CHECKPOINT_CONNECTIVITY_20260924T030756297Z.md) | 1479/1479 checks against the fresh 24 September compile |
| Fresh native compile | [NATIVE_COMPILE_FINAL_SEP24.txt](evidence/CHECKPOINT_CLOSE_20260924T025659139Z/NATIVE_COMPILE_FINAL_SEP24.txt) | 0 active errors, 39 active warnings, 3 inherited suppressed diagnostics; complete |
| Fresh circuit and source preservation | [PRESERVATION_FRESH_20260924T030755428Z](evidence/PRESERVATION_FRESH_20260924T030755428Z/) | 658/658 checks; twelve interfaces/five VREF branches; 266 original baseline hashes unchanged |
| Actual component positions, partition and BOMs | [ASSEMBLY_SNAPSHOT_20260924T023521434Z](evidence/ASSEMBLY_SNAPSHOT_20260924T023521434Z/) | 522/522 checks; 231 provisions, 25 DNP, 205 fitted PCB parts, one required remote sensor |
| Placement DRC | [DRC07_PLACEMENT_CHECKPOINT_RESULT.md](evidence/DRC07_PLACEMENT_CHECKPOINT_RESULT.md) | 510 unrouted only; zero other reported categories |
| Native DRC report | [DRC07 native HTML](evidence/DRC07_BODY_ENVELOPES_TMR_FIXED_2026_09_24_NATIVE.html) | Actual Altium report |
| Controlled footprint-identity correction | [MANAGED_IDENTITY_NORMALIZATION_VERIFIED.md](evidence/MANAGED_IDENTITY_NORMALIZATION_VERIFIED.md) | Native ECO proposes no component/footprint/net/pad changes |
| Native CAD images | [images](images/) · index in [IMAGE_PACKAGE_20260924](evidence/IMAGE_PACKAGE_20260924/) | Complete: 8 named board views (top/bottom placement, 3D top/bottom, L1–L4) + 5 closeups; display-only, SHA-256 manifest, `PCBDOC_MODIFIED=False` |
| Final closure backup and operation plan | [CHECKPOINT_CLOSE_20260924T025659139Z](evidence/CHECKPOINT_CLOSE_20260924T025659139Z/) | Project save/diff and fresh compile completed; PCB save/reopen pending |

The assembly snapshot contains:

- `MAIN_BOARD_COMPLETE_ASSEMBLY_BOM.csv` — main-board subsystem procurement; required quantity is zero for DNP provisions.
- `MAIN_BOARD_PCB_ASSEMBLY_BOM.csv` — 205 fitted PCB parts.
- `MAIN_BOARD_MACHINE_ASSEMBLY_BOM.csv` and `MACHINE_PLACEMENT_REVIEW_ONLY.csv` — 195 SMT/mixed candidates with actual CAD origins; assembler conventions still require qualification.
- `MAIN_BOARD_THROUGH_HOLE_ASSEMBLY_BOM.csv` — 10 through-hole PCB parts.
- `MAIN_BOARD_REMOTE_NTC_MANUAL_ASSEMBLY_BOM.csv` — the same single required 103AT-2 already counted in the master procurement view; no second purchase quantity.
- `MAIN_BOARD_VARIANT_POPULATION.csv`, `BOARD_PARTITION_MANIFEST_CURRENT.csv`, `ACTUAL_NATIVE_PCB_COMPONENT_POSITIONS.csv` and `PCB_FREE_TESTPAD_POSITIONS.csv`.

The NTC PCB location is a two-wire termination only. The sensor body is manually attached to the cell. All 22 optional DRL components and the three optional Wi-Fi capacitors are Not Fitted. The main-board BOM excludes the five DEBs and five manufactured flexes.

Historical failing DRC, interrupted-run logs, pre-edit boards and older evidence are intentionally retained. They are not alternative production layouts. No full-board routing or manufacturing-ready output is included.
