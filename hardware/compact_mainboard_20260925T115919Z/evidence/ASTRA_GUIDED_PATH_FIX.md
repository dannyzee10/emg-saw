# Guided partial-rip corridor and seed plan inputs, 27 September 2026

The planner correction is in `work/repair.py:785-789`; its exact five-added/one-removed-line diff is retained in `ASTRA_GUIDED_PATH_FIX.patch`. `work/repair_guided_fix.py` is the identical controlled snapshot originally tested before the root agent authorized updating the runtime script. No native CAD, router process, production geometry load, design or rule edit was performed by this subtask.

## Planner correction

Previously `fixed_path_victims` saved `LAST_PATH` from the first route found with all local victim groups ripped. It then restored unrelated groups and verified a second route `r2` with only the selected victims ripped. That second route could take a different corridor, but `split_group` still received the first corridor. At `PARTIAL=0.35` or `0.5`, this could leave the verified route blocked while unnecessarily ripping copper elsewhere.

The function now converts successful `r2` into rows and track/via envelopes, assigns their union to `LAST_PATH`, and returns those same diagnostic rows. Failure or an empty already-connected result leaves `LAST_PATH=None`. Victim selection, tolerance values, raster checks, exact checks, clearance calculations, route ordering and final acceptance checks are unchanged. Full state restoration remains in the existing `finally` clause.

This fixes the corridor mismatch; it does not guarantee that a partially ripped route or all victim reconnections will succeed.

## Seed wrapper correction

`work/astra_route_seed.py:54-59` reads `EXTRA_PLANS` from the merged environment, including command-line overrides, using the same comma parsing and empty-entry filtering as `run_repair.py`. It rejects entries containing paths, drive separators or parent-directory names. The default plan list plus extras is recorded as `routed_plans` in `MANIFEST.json` and passed, in that order, to `repair.py` at line 66.

The tested concrete option is:

```text
EXTRA_PLANS=ASTRA_MCU_RX_REINFORCED_ADDS,ASTRA_UART_READY_ADDS
```

Seed copper remains part of the planning geometry; these extra plans identify existing native routed copper that repair may nominate as victims.

## Test evidence

Command from `work/`:

```powershell
& 'C:/Users/PMLS/AppData/Local/Programs/Python/Python312/python.exe' -B -m unittest -v test_repair_guided_path test_astra_route_seed_plans
```

Observed result: **exit 0; nine tests in 0.411 seconds; OK**.

The six planner tests compile only `fixed_path_victims`, `split_group` and `rows_for` from the actual runtime source. They use real Shapely envelopes and the real partial group selection with mocked routing results/snapshots; they never import the router. They cover both requested partial distances, verified track/via output, later-tolerance success, all-verification failure, exception rollback, and an already-connected verification. The fixture deliberately puts old-corridor copper at y=0, verified-corridor copper at y=2 and remote copper at y=5. Only the y=2 piece is selected after the fix.

The three seed-wrapper tests execute the wrapper inside temporary synthetic files with its routing subprocess mocked. They confirm the exact two requested extra plans are appended and recorded, command-line values override inherited values, empty comma entries are ignored, inherited extras work, and path entries are rejected before any subprocess starts.

`git diff --check` on the runtime files returned exit 0, with only Git's line-ending notice. The seed wrapper is an existing untracked file, so its focused changes are described above rather than appearing in the tracked repair diff.

SHA-256 before the planner edit: `DB5C92DAC31DF73A9D341EF0DA0F15261D916C9D5F159DBC2F4BF89DF3B3ED3A`.

SHA-256 after the edit, identical for `repair.py` and `repair_guided_fix.py`: `2438B5ACB61B796931D79166956BEB36827CBF5788345742AA468ACE17ABDC71`.

SHA-256 of the updated seed wrapper: `DC4CB8F86D028D483FF464886787542B394FE67E0359CB0907268DE339BDFF5A`.

Native build/delta/DRC acceptance remains the root agent's subsequent work. Repository graph refresh is also left to root because this subtask was restricted to lightweight planner edits and evidence.
