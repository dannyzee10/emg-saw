# All free trace audit and via evidence — 2026-09-27

Read-only helper work; this agent made no native CAD, copper, rule or silkscreen changes. Root owns final native verification and all design writes.

## Saved rule audit

`work/astra_audit_trace_rules.py` evaluates every exported free copper TRACK and every VIA against the matching saved board's Rules6 and Classes6 records. It supports exact All, InNet and InNetClass scopes, native priorities and explicit per-layer width limits. Unknown or ambiguous applicable scopes remain unresolved. Identically named native classes are accepted only when all memberships agree. Netless copper is included under applicable rules. Nine focused regressions passed.

BG pre-alignment evidence `ASTRA_BG_ALL_FREE_TRACE_RULES.json`:

- 2,269 free copper tracks: all width and routing-layer checks passed.
- 464 vias: 327 within the old rule envelope; 137 failed the old 0.60/0.30 mm minima (132 at 0.45/0.20 mm, five at 0.50/0.30 mm).
- No unresolved scopes. Ten remaining free tracks are all Mechanical Layer 4, net `-`; their full records are retained. There is no skipped netless copper.
- This proves saved width/layer/envelope compliance only. Clearance, connectivity, current capacity, impedance, footprint copper and pours require other/native checks. The export does not establish via spans.

For a completed final state, use its matching saved board and complete native geometry export:

```powershell
python -B astra_audit_trace_rules.py --pcb ../C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc --geometry ../evidence/GEOMETRY_C2_6L_BI.txt --output ../evidence/ASTRA_BI_ALL_FREE_TRACE_RULES.json
```

Exit 0 means passed; 1 means a rule violation; 2 means unresolved coverage. Input hashes are retained. Do not substitute an old geometry export after copper changes.

## Native DRC coverage

`work/astra_read_drc_coverage.py` reads saved DRC options and rules without launching Altium. BFS evidence `ASTRA_BFS_DRC_COVERAGE_REQUIRED.json` correctly failed required categories 9 (Routing Layers) and 11 (Routing Via Style): both were online-only, absent from saved batch selection and native report summaries. All saved rules inspected were enabled; checkbox coverage is a separate issue.

Other online-only categories were 17 (ViasUnderSMD, with no corresponding saved rule) and 51 (DifferentialPairsRouting, default All rule; actual pair applicability not determined). Kind 19 MinimumAnnularRing was batch-selected but had no saved rule. Generation-only routing rules absent from batch must not be called missing electrical checks indiscriminately. No guessed native options accessor was used. `run_drc_T.pas` itself does not change selected categories.

After the root saves native options, prove both categories from the saved file, then inspect fresh native report summaries:

```powershell
python -B astra_read_drc_coverage.py --pcb ../C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc --sdk C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/work/api/INSTALLED_SDK_SIGNATURES.txt --require-batch 9,11 --output ../evidence/ASTRA_BI_DRC_COVERAGE.json
```

The existing `astra_align_via_rule_T.pas` was reviewed: assignments are limited to the unique named VIA_STD_060_030 rule's MinWidth=0.45 mm and MinHoleWidth=0.20 mm. Guards preserve rule count, identity, UID, kind, enabled state, All/All scopes, priority, via style and preferred/maximum diameter/hole. It saves and reopens for readback. `astra_read_via_rule_T.pas` is a separate prepared getter-only readback that verifies the aligned rule and all via dimensions/spans. Root executes native helpers; preparation is not evidence of native success.

## JLCPCB primary sources

Current official six-layer capabilities explicitly include 1.2 mm thickness and a 0.15 mm minimum via hole with 0.25 mm diameter. [Six-layer capability table](https://jlcpcb.com/resources/6-layer-pcbs)

The manufacturing table specifies via diameter at least hole diameter +0.10 mm, with +0.15 mm preferred, and a preferred minimum via hole of 0.20 mm. Therefore 0.45/0.20 mm and 0.50/0.30 mm satisfy those published geometric requirements: their diameter-minus-hole differences are 0.25 and 0.20 mm, and radial annular rings are 0.125 and 0.10 mm. This is an inference from the published specifications, not an individual order approval. [JLCPCB via manufacturing requirements](https://jlcpcb.com/capabilities/pcb-capabilities)

The official impedance calculator exposes a six-layer 1.2 mm option and a general 0.20 mm minimum-via table, but the accessible page did not independently expose exact stack code JLC06121H-3313 or a stack-specific drill override. The local design records identify that stack; do not present the generic capabilities as a verified exact-stack certificate. [Official impedance/stackup selector](https://jlcpcb.com/impedance)

## Five outline findings

BG and BH native DRC contain the same five outline-clearance findings, all against a 0.5 mm threshold. All affected objects are overlay graphics/text, not copper or the ten mechanical tracks:

| Object | Layer | Location, mm | Reported clearance |
|---|---|---|---|
| Text J_REF | Top Overlay | (10.197,14.783) | 0.047 mm |
| Text RV1 | Bottom Overlay | (9.9,24.9) | Collision |
| Text UP1 | Bottom Overlay | (11.5,43.166) | 0.35 mm |
| Graphic track | Top Overlay | (10.66,10.93)–(10.66,13.47) | 0.191 mm |
| Graphic track | Top Overlay | (10.66,10.93)–(15.74,10.93) | 0.191 mm |

Retain copper and the board-edge rule. Overlay relocation/trim is separate finishing work and was not performed here. The report identifies the two graphic tracks by layer and endpoints; component ownership is not inferred.

## Informational shape inventory

`work/astra_trace_shape_inventory.py` is separate from the verified rule checker. It includes every free copper track regardless of net, normalizes endpoint direction for exact duplicates, and preserves net/layer/width distinctions. It does not flag partial overlaps or delete anything. Four focused tests passed.

Tested command:

```powershell
python -B astra_trace_shape_inventory.py --geometry ../evidence/GEOMETRY_C2_6L_BH.txt --output ../evidence/ASTRA_BH_TRACE_SHAPE_INVENTORY.json
```

BH result: 2,292 copper tracks, ten Mechanical Layer 4 exclusions, zero netless copper. One zero-length record: Top Layer NetJ_FPC1_8, width 0.20 mm, both endpoints (21.9386,12.4386). Two exact duplicate Bottom Layer GND groups, width 0.30 mm: (12.475,40.275)–(12.725,40.525) occurs twice; (12.475,40.125)–(12.775,40.125) occurs three times. Total three extra records. Equality is limited to the four-decimal native text export; any cleanup requires native object inspection and connectivity-preserving validation.

BH geometry SHA-256: `d3a094dc5ccabc24051e295fdc2878f064df6e4070c22d0490e69668f5c1689b`.
