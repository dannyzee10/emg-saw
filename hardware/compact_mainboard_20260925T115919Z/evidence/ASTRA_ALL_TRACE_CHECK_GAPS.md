# All-trace verification coverage review

Read-only text review, 27 September 2026. No geometry process, router, native application or CAD operation was run. This records the BF/BFS evidence and current checking scripts; it does not pre-judge the in-progress BG result.

## Native coverage: width and clearance present; categories 9 and 11 absent

The latest reviewed native report is `DRC_C2_6L_BFS.txt.html`, generated at 22:38:12, SHA256 `18c6b636effdd0e3a172a4270832ac8c72d54a4e9c494ce24ed762f04dc9b799`. Its 122 summary rows include **98 Clearance Constraint rules and 10 Width Constraint rules, all with zero violations**. The general All/All clearance row is at line 394 and All-scope width row at line 666; class-specific width rows follow through line 702. These checks are present across the native board, rather than limited to the latest additions. BF has the same coverage and zero width/clearance result.

Neither report contains a Routing Layers or Routing Via Style summary row. Their absence is **unverified coverage**, not a zero-violation result:

- `work/run_drc_T.pas:15` calls `B.RunBatchDesignRuleCheck(Report,eDRC_HTML,False,False)` without changing the selected check set. Its Boolean is explicitly processing status, not a DRC pass (`:2`).
- The last recorded saved batch list in `ASTRA_VIA_RULE_REVIEW.md:53` omits both **9** and **11**; the online list at `:54` includes both.
- Installed SDK evidence at root-repository `hardware/pcb_layout_2026-09-16/work/api/INSTALLED_SDK_SIGNATURES.txt:2743` identifies `eRule_RoutingLayers=9`; `:2745` identifies `eRule_RoutingViaStyle=11`.
- `work/astra_review_mcu_rx_bf.py:45` includes Routing Layers among critical names, but `:47` rejects only existing matching nonzero rows. It does not require a category to exist. Consequently the BF note's wording that the routing-layer summary remains zero must not be interpreted as proof that this check ran.
- The last documented native via rule still fixes 0.60/0.30 mm while smaller existing vias are present (`ASTRA_VIA_RULE_REVIEW.md:3`, `:19`). The authorized alignment writer is prepared separately (`ASTRA_FINISH_TOOLS.md:100`); it does not enable batch category 11 (`:108`). Fresh rule readback, selected-category evidence and a fresh native report remain necessary for claiming that coverage.

Width-rule compliance does not establish current capacity: BFS's EMG_POWER row at line 686 permits a minimum of 0.15 mm while preferring 0.9 mm. An undersized feed can therefore pass native width DRC if it still satisfies the configured minimum.

## Offline checks cover different, narrower questions

| Checker | Established scope | Important limit |
|---|---|---|
| `work/build_ops.py:64` and `:81` | All supplied new copper versus retained copper, and new versus new; edge, keepout, L5 reservation and drill checks | Does not recheck retained-versus-retained copper. Does not load or enforce native width-rule minima, maxima or priorities. Uses `geom.py`'s explicit clearance model rather than evaluating every saved native rule. |
| `work/astra_check_final_opens_graph.py:76` | Nets named in additions/deletions plus explicitly required endpoint nets | Other nets are not graphed. It detects newly split retained connections and detached additions, not every pre-existing open. Endpoint closure is required only for `--require-net` (`:129`). |
| Same graph checker, `:108`, `:140` | Width-threshold connectivity preservation for affected EMG_POWER nets; source-to-pad threshold reporting for 3V3_DIG from UP2.1 | Does not prove effective junction width, via current capacity or thermal/current limits. Its explicit limits at `:181` also exclude complete pour geometry. |
| `work/astra_verify_routing_delta.py:45` | Exact authorized changes to exported free copper and protection of exported fixed geometry, pads and components | This is edit fidelity, not electrical correctness. Polygon-generated records are skipped at `:58`; via spans, rules/net objects and stack are excluded by the export (`:9`). |
| `work/fab_check.py:12` | Worst separations among exported TRACK/VIA/PAD copper and drill pairs, plus width/via inventories | Reports metrics only; it has no fail verdict and does not evaluate native rule scopes. `mask_dam` is only a declared/printed capability constant, with no actual mask-shape calculation. |

The shared geometry model excludes poured region shapes (`work/geom.py:106`) and represents all vias as spanning all six copper layers (`:89`). Native exporter `work/export_geometry_T.pas:24` records via XY/diameter/hole but no spans; arcs and regions have bounding rectangles rather than full contours (`:26`). These facts limit independent plane continuity, return-path, thermal-spoke and same-net copper-neck verification. A successful repour or zero Modified Polygon result alone does not establish those physical properties.

## Gloss and finishing are not all-trace electrical verification

`work/gloss.py:45` selects only tracks that match supplied historical routing-plan rows; it excludes escape/stitch groups and leaves other copper untouched. It retains the chain's width (`:11`), skips mixed-width chains (`:190`), and does not remove vias or size tracks for current. Its window is an intersection filter (`:187`), so a selected chain can extend outside it. A gloss pass therefore does not establish that every trace was checked or optimized.

The **current** gloss implementation does have the conservative same-net contact guard (`work/gloss.py:62`, invoked at `:194`) and matching per-chain ADD/DEL ownership. Do not repeat the superseded claims in `ASTRA_FINISH_TOOLS.md:56` and `:57` that those are absent. `ASTRA_GLOSS_CONTACT_GUARD.md:28` explicitly supersedes those claims and retains the incomplete-pour and downstream-filtering limits.

The geometry exporter omits text objects (`work/export_geometry_T.pas:19`). Thus the exported PAD/COMP/free-copper comparison cannot validate silkscreen text positions or all fabrication presentation. BFS still reports **2 opens, 157 silk-to-mask, 84 silk-to-silk, 6 antennae and 5 board-clearance violations: total 254** (`DRC_C2_6L_BFS.txt.html:658`, `:722` through `:750`). These are existing unresolved finish items, not new failures introduced by a passing routing delta. Final native reports and any documented resolutions must cover them separately.

No files other than this review note were changed for this subtask.
