# NetINA4_3 saved routing-layer rule review

Read-only inspection of the saved C2 PCB on 2026-09-27, using `olefile` to read `Rules6/Data` and `Classes6/Data`. No native CAD process or routing search was run, and the board was not modified.

- Board: `C:/Users/PMLS/Desktop/emg-saw/.claude/worktrees/pcb-routing-0925/hardware/compact_mainboard_20260925T115919Z/C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc`
- SHA256: `507b78e6315a746c8b6bdb499e60dbc8da84d46abded21128838baa93ca94ed5`

Exactly one serialized `RULEKIND=RoutingLayers` record was found:

| Field | Saved value |
| --- | --- |
| NAME | `RoutingLayers` |
| ENABLED | `TRUE` |
| PRIORITY | `1` |
| SCOPE1EXPRESSION | `All` |
| SCOPE2EXPRESSION | `All` |
| NETSCOPE | `AnyNet` |
| LAYERKIND | `SameLayer` |
| UNIQUEID | `GOIBPUCB` |
| MID LAYER 4_V5 | `TRUE` |

All serialized routing-layer flags are `TRUE`: `TOP LAYER_V5`, `MID LAYER 1_V5` through `MID LAYER 30_V5`, and `BOTTOM LAYER_V5`. No separate `EMG_ANALOG`-scoped RoutingLayers record was found.

`Classes6/Data` contains two `EMG_ANALOG` records with `KIND=0`, `SUPERCLASS=FALSE`, and unique IDs `IXUAYIVU` and `IGFYNGTX`. Both contain `M25=NetINA4_3`.

The saved native RoutingLayers rule therefore permits `NetINA4_3` on physical L5 (`Mid Layer 4`). This conclusion does not depend on which duplicate `EMG_ANALOG` record is resolved because the only RoutingLayers rule has scope `All`.

`L5_RESERVED` is a separate Python planning and pre-write validation policy: `work/router5.py:32` and `work/build_ops.py:51` read it from the environment; `work/repair.py:162` and `work/build_ops.py:71` reject foreign-net L5 tracks intersecting the specified reserved regions. It is not a restriction encoded in the inspected native RoutingLayers rule. This distinction does not establish that the policy can be removed without affecting the intended 3V0_ANA pour or board requirements.

This inspection establishes saved rule fields and membership only. It does not prove a proposed L5 route's clearance, connectivity, plane integrity, or design suitability, and it does not evaluate unsaved CAD state. Physical L4 (`Mid Layer 3`, GND) was untouched. Any candidate still needs geometry checks and native DRC after application.
