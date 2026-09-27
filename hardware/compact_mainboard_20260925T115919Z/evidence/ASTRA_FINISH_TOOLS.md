# Finishing-tool readiness — read-only review, 27 September 2026

Scope: scripts inside this compact C2 project. No router, gloss job, native script or CAD mutation was run for this review. Commands below run from `work/`; use the installed Python executable already selected by the root agent. Replace `STATE` with the latest saved, exported, DRC-checked state.

## Gloss: usable generator, with specific limitations

[gloss.py](../work/gloss.py) writes only ADD/DEL CSVs. Its native mutation boundary is the subsequent `build_ops.py` → `apply_ops_T.pas` step. It selects existing tracks by net/layer/endpoints found in supplied historical plan CSVs, ignores plan filenames starting `BK13_ESCAPE` or `STITCH`, and ignores rows whose group prefix starts `S`. It preserves each accepted chain's existing width. It creates/deletes no vias, pads, components or rules.

Standard environment:

```powershell
$env:GEOM_FILE='../evidence/GEOMETRY_C2_6L_STATE.txt'
$env:BOARD_BOX='12,12,67.1,44'
$env:BK13_ZONES='../evidence/BK13_ZONES_C2.csv'
$env:L5_RESERVED='3V0_ANA:10.5,10.5,68.6,25.3;3V0_ANA:10.5,25.3,47.5,27.2;3V0_ANA:31.6,27.2,35.8,30.4'
$env:VIP='1'
```

The direct interface is:

```text
python gloss.py ../evidence/GLOSS_STATE_ADDS.csv ../evidence/GLOSS_STATE_DELS.csv ../evidence/PLAN1.csv ../evidence/PLAN2.csv ...
```

Use the current `PLANS` list from [run_repair.py](../work/run_repair.py), plus every later successfully applied plan. Do **not** import `run_repair.py` to obtain that list: it launches `repair.py` at module level. A static extraction is possible without importing it:

```python
import ast, pathlib, subprocess, sys
tree = ast.parse(pathlib.Path('run_repair.py').read_text())
plans = next(ast.literal_eval(node.value) for node in tree.body
             if isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'PLANS' for t in node.targets))
# Add only later plans whose CAD writes and native readback actually succeeded.
subprocess.run([sys.executable, 'gloss.py', '../evidence/GLOSS_STATE_ADDS.csv',
                '../evidence/GLOSS_STATE_DELS.csv']
               + ['../evidence/' + p + '.csv' for p in plans], check=True)
```

Close Altium before running gloss, honoring the one-heavy-process limit. Check the entire output batch together:

```powershell
$env:OPS_OUT='OPS_GLOSS_STATE.txt'
python build_ops.py ../evidence/GLOSS_STATE_ADDS.csv --del ../evidence/GLOSS_STATE_DELS.csv
```

Proceed to native apply only after exit 0 and `PROBLEMS 0`; omit `--rules`. Inspect that generated noncomment operations are only `TRACK` / `DEL_TRACK`. Use `astra_native_checked.ps1`, native save/reopen, fresh geometry, the routing-delta verifier and fresh native DRC. Native apply also repours all polygons, so retain before/after unrouted and antenna comparisons even for a geometrically legal replacement. Generate before/after pictures with:

```text
python render_window.py ../evidence/GLOSS_STATE_BEFORE.png "12,12,67.1,44" ../evidence/DRC_C2_6L_STATE.json
```

Change `GEOM_FILE`, output filename and DRC input to the new state for the after image.

Specific findings from the implementation:

1. **Do not feed gloss output to `consistent_repair.py`.** Gloss additions use `G<n>:<net>`, while every deletion uses `GLOSS_DEL`. The consistency helper restores victim deletions only for its `P<n>` repair scheme. If it drops a gloss addition, it retains that chain's deletions. This can open a net. Likewise, `build_ops --drop-bad` drops additions without restoring their corresponding deletions. Keep the whole batch or implement explicit per-chain add/delete ownership before partial filtering.
2. **Interior junctions are not fully protected.** `gloss.py:127` tests anchors only at existing segment endpoints. A same-net pad, via or branch touching the interior of a segment without a shared endpoint need not become an anchor. Clearance checking skips same-net objects, so legal geometry is not a connectivity proof. Native before/after unrouted verification is required; splitting at every physical junction before gloss would address the cause.
3. **`WINDOW` is an intersection filter, not a mutation fence.** If a chain intersects the window, the entire chain can change outside it (`gloss.py:158`).
4. **Movable identity is approximate.** Endpoint keys round to 0.001 mm and omit width; the selector also has no explicit `INCOMP`/`INPOLY` exclusion. The planner's CSV provenance and the native free-track deletion check are therefore important. The native writer refuses deleting footprint tracks, but the planner can still nominate one if its key collides.
5. **It cannot fulfill every promised cosmetic action.** It never removes needless vias or enforces pad-entry direction. A lone non-45-degree segment requires at least two octilinear replacements, but the acceptance rule rejects increased segment count, so it remains. Mixed-width chains and closed loops lacking an anchor are skipped.

## Width pass: native setter exists; automatic sizing planner does not

No dedicated current-aware width-pass generator was found. Available native operations in [apply_ops_T.pas](../work/apply_ops_T.pas):

```text
WIDEN_TRACK|net|layer|x1|y1|x2|y2|new_width_mm
SET_WIDTH|existing_rule_name|min_mm|preferred_mm|max_mm
```

`WIDEN_TRACK` assigns `T.Width` directly. Despite its name it can also narrow a track. Phase 1 only confirms one geometric track match and parses the requested width; it does not verify the resulting clearance or fabrication limits. Prefer an ADD/DEL plan with identical endpoints and revised widths, checked through `build_ops.py`, then exact native delta/DRC verification.

`SET_WIDTH` changes the existing rule on all six copper layers via `IPCB_MaxMinWidthConstraint.MinWidth`, `.MaxWidth`, and `.FavoredWidth`. It modifies a design rule; it does not resize the existing copper. It also assumes the found named rule has the expected interface, without checking `RuleKind` before casting.

Use the read-only native rule dump to inspect the actual per-layer limits before preparing width operations:

```text
python mkvariant.py dump_rules_T.pas astra_widthrules C2 ASTRA_WIDTH_RULES_STATE.txt
```

Run the printed fresh `.PrjScr` with the checked native runner. The saved BA report has 0.15 mm minimums for the default/control/SPI/analog/ADC classes (switching minimum 0.20 mm). Therefore a digital/control 0.10 mm geometry pass also needs the intended class-specific width-rule change; `build_ops.py` does not enforce width-rule minima. The earlier user strategy recorded in `ROUTING_RESUME.md:122` calls for current-based power widening first and digital/control thinning afterwards, while preserving analog widths and clearances. Match the concrete rule edits to that authorized scope.

Do not reuse [gen_trial_cleanup_ops.py](../work/gen_trial_cleanup_ops.py) as a finishing width pass. It hardcodes the old `DRC_C2_TRIAL.json`, trial plan and a four-layer label map; it also emits a catch-all `SET_WIDTH|Width|0.15|0.2|0.5` plus antenna deletions. It is neither a current-state sizing planner nor a silk cleaner.

## Silk: no ready cleanup writer in this project

No dedicated silkscreen relocation/resize/visibility writer or planner was found in the compact C2 scripts. The footprint-replacement scripts mention `eTextObject` only to preserve/exclude component text while replacing footprint primitives; those scripts have much broader CAD scope and are not suitable substitutes.

The native geometry exporter omits `eTextObject`, so its PAD/COMP/free-copper verifier does not validate silk placement. A silk pass needs an explicit text inventory and narrowly scoped text edits, with fresh native silk-mask/silk-silk/board-edge DRC and before/after views.

The existing [drc_details.py](../work/drc_details.py) is incompatible with current [parse_drc.py](../work/parse_drc.py) output: it calls `.get()` on each `details` element, but those elements are strings. For current silk details, this read-only PowerShell command works:

```powershell
(Get-Content ../evidence/DRC_C2_6L_STATE.json -Raw | ConvertFrom-Json).details |
    Where-Object { $_ -match '^Silk|^Board Clearance' }
```

## Via rule and batch-category API readiness

After the user requested aligning the existing vias to JLC's limits, a narrow writer was prepared but **not run**: [astra_align_via_rule_T.pas](../work/astra_align_via_rule_T.pas). Subsequent read-only research in the existing September 16 API evidence found proven `IPCB_RoutingViaStyleRule.MinWidth` and `.MinHoleWidth` setters in `hardware/pcb_layout_2026-09-16/work/create_rules.pas:53`; the preferred properties are spelled `PreferedWidth` and `PreferedHoleWidth` (one r). The installed SDK reflection confirms the interface and `eRule_RoutingViaStyle=11`.

The writer requires the exact C2 path, a saved board, a unique enabled priority-1 All-scope rule and the expected original or already-aligned limits. It audits every existing via against the approved through-via size envelope before changing anything, sets only minimum diameter 0.45 mm and minimum hole 0.20 mm, preserves the other rule properties, saves, reopens and reads back the limits and via count. It does not repour or alter copper. Instantiate with:

```text
python mkvariant.py astra_align_via_rule_T.pas astra_via C2 ASTRA_ALIGN_VIA_RULE.txt
```

The batch selection remains **unchanged** by this writer. Existing `INSTALLED_SDK_SIGNATURES.txt:2801` confirms `IPCB_DesignRuleCheckerOptions.RuleSetToCheck` setters, but neither later workspace scripts nor a fresh read-only search of the installed SDK found a callable getter for that options object. `Board.OutputOptions` contains drill/plot settings, not this DRC interface. The only established route found to select batch categories is the observed native DRC dialog (`RunProcess('PCB:DesignRuleCheck')`); saved OLE readback must then prove category 11 was added without dropping existing categories.

`dump_rules_T.pas` currently has typed branches only for routing layers and widths. `run_drc_T.pas` calls batch DRC without setting the selected categories. Do not claim Routing Via Style batch coverage until the stored `RULESETTOCHECK` and the fresh native report confirm it. See [ASTRA_VIA_RULE_REVIEW.md](ASTRA_VIA_RULE_REVIEW.md) for exact limits and coverage evidence. No guessed options getter or working-board binary patch was added.

The [official API reference](https://www.altium.com/documentation/altium-dxp-developer/pcb-api-system-interfaces-reference) confirms `RuleSetToCheck : TRuleSet` and rules-to-check parameter import/export, but gives no accessor that obtains this options object from Board/PCBServer. The [AD22 DRC instructions](https://www.altium.com/documentation/altium-designer/pcb/drc/setting-up-running?version=22.) document the native dialog's Rules To Check → Batch selection. This corroborates the installed API limitation rather than establishing a script getter.

## Repair-checker failure handling fixed separately from CAD

The former `consistent_repair.py` ignored checker return codes and could publish `_OK` files after a failure or deletion mismatch. It now aborts with exit 1 on those conditions, incomplete/inconsistent check summaries, unresolved problems without droppable groups, and exhaustion of the iteration limit. Final output files are written only after a successful checker run explicitly reports `PROBLEMS 0`. Existing outputs are preserved on failure, so callers must honor the exit code.

Eight mocked regression tests passed; the legitimate `--drop-bad` → restore victim → clean recheck path remains supported. [ASTRA_TOOL_FIX_TESTS.md](ASTRA_TOOL_FIX_TESTS.md) records the checks. The separate gloss deletion-ownership limitation above remains: this helper is still for repair.py groups. Keep the final direct `build_ops.py` check before a CAD write.
