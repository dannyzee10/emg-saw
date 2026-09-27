# Native via-rule review — 27 September 2026

The saved C2 board's enabled `VIA_STD_060_030` rule permits only nominal **0.60 mm diameter / 0.30 mm drill** through vias. BA contains **135 vias outside that envelope**. The current native batch DRC does **not** check Routing Via Style, so its zero clearance/short results do not resolve this mismatch.

This review read the saved PCB's OLE streams using installed `olefile`, the BA native geometry export, the native DRC report and the batch script. It made no CAD or DRC-setting changes.

## Concrete reviewed change

Status update: following this review, the user asked to check JLC's minimum limits because the board already uses the new vias. The root agent verified the current JLC capability page and authorized preparing the rule alignment for the existing compliant sizes, with no rerouting or clearance relaxation. [astra_align_via_rule_T.pas](../work/astra_align_via_rule_T.pas) is prepared but was not run by this reviewer. Batch-category selection remains a separate native step because no callable getter for the DRC options object has been established; [ASTRA_FINISH_TOOLS.md](ASTRA_FINISH_TOOLS.md) records that limitation.

> Approve updating `VIA_STD_060_030` to allow through-via diameters **0.45–0.60 mm** and drills **0.20–0.30 mm**, retaining **0.60/0.30 mm** as the preferred size, and include Routing Via Style in the final batch DRC? This accommodates the three via sizes already present: **0.45/0.20, 0.50/0.30 and 0.60/0.30 mm**. Clearance rules remain unchanged.

The numeric rule edit is only `MINWIDTH` to 0.45 mm and `MINHOLEWIDTH` to 0.20 mm; keep `MAXWIDTH`, `WIDTH`, `MAXHOLEWIDTH`, `HOLEWIDTH`, scope, priority, enabled state and through-hole style. Add category `11` to the batch check set, retain the other selected checks, rerun native DRC, and re-export/read back the rule. The source handoff explicitly left this rule change to the user: [HANDOFF_ASTRA_2026-09-27.md](HANDOFF_ASTRA_2026-09-27.md), section 7 item 3; the status update above records the subsequent authorization.

## Exact saved rule

Source: `C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc`, OLE `Rules6/Data`.

| Field | Saved value | Nominal metric value |
|---|---|---|
| `NAME` | `VIA_STD_060_030` | — |
| `RULEKIND` | `RoutingVias` (binary rule kind 11) | — |
| `ENABLED` | `TRUE` | enabled |
| `PRIORITY` | `1` | — |
| `SCOPE1EXPRESSION`, `SCOPE2EXPRESSION` | `All`, `All` | all objects |
| `NETSCOPE`, `LAYERKIND` | `AnyNet`, `SameLayer` | — |
| `VIASTYLE` | `Through Hole` | through via |
| `MINWIDTH` | `23.622mil` | 0.600 mm |
| `WIDTH` (preferred) | `23.622mil` | 0.600 mm |
| `MAXWIDTH` | `23.622mil` | 0.600 mm |
| `MINHOLEWIDTH` | `11.811mil` | 0.300 mm |
| `HOLEWIDTH` (preferred) | `11.811mil` | 0.300 mm |
| `MAXHOLEWIDTH` | `11.811mil` | 0.300 mm |

The literal decimal-mil strings convert to 0.5999988 and 0.2999994 mm; the table uses their intended nominal 0.60/0.30 mm sizes, consistent with the native geometry's four-decimal precision.

## BA inventory and DRC coverage

Source: [GEOMETRY_C2_6L_BA.txt](GEOMETRY_C2_6L_BA.txt).

| Diameter / drill, mm | Count | Existing rule's dimensional envelope |
|---|---:|---|
| 0.45 / 0.20 | 130 | diameter and drill below minimum |
| 0.50 / 0.30 | 5 | diameter below minimum |
| 0.60 / 0.30 | 316 | nominally within limits |
| Total | 451 | 135 outside limits |

The 135 figure is an independent dimensional inventory, not a claim that native DRC emitted 135 violation records. Native reports may aggregate violations differently.

Saved `Design Rule Checker Options6/Data` contains:

```text
RULESETTOCHECK=0,1,2,3,4,5,6,15,16,18,19,21,22,23,24,26,42,45,46,47,50,52,53,54,55,56,60,62,63,64
ONLINERULESETTOCHECK=0,1,2,3,4,5,9,11,15,17,18,22,23,24,45,46,47,50,51,55,60,62
```

Category 11 is absent from the batch list and present in the online list. `ENABLED=TRUE` on the rule therefore does not establish batch coverage. [run_drc_T.pas](../work/run_drc_T.pas) invokes `B.RunBatchDesignRuleCheck(Report,eDRC_HTML,False,False)` and does not modify either check set.

[DRC_C2_6L_BA.txt.html](DRC_C2_6L_BA.txt.html) and its [parsed report](DRC_C2_6L_BA.json) contain no Routing Via Style entry. They do include clearance, shorts, unrouted nets, modified polygons, width, plane connections, hole size, hole-to-hole clearance, mask sliver, silk clearances, antennae, board clearance, component clearance and height. The BA report has zero clearance/short violations, 8 unrouted, 8 antennae, 159 silk-to-mask, 84 silk-to-silk and 5 board-clearance violations; total 264. Those results describe BA and do not supersede later routing states.

The project handoff and existing routing research identify 0.45/0.20 mm as the intended standard-price small via. This review did not revalidate current manufacturer pricing or order options; rule reconciliation is separate from the final fabrication audit. [fab_check.py](../work/fab_check.py) reports geometry/capability metrics but does not compare vias against this native RoutingVias rule, and does not by itself certify all design rules.

## Recorded source identity

- Saved PCB SHA-256 at inspection: `35520317d5b9ab6ca86dc7ccf572e7d4e18cfef164e92927b83c5528366467bc`.
- `Rules6/Data` SHA-256: `195482691ae58ab5a424c5115d3cb3e96eacbfc46e2771e44129af6b186fa295`.
- [ASTRA_BA_STRUCTURE.json](ASTRA_BA_STRUCTURE.json) independently records that Rules6 was unchanged by the AZ-to-BA copper batch.

No native via rule, batch selection, CAD geometry, schematic or project file was edited during this review.
