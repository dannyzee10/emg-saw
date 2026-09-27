# Repair-checker regression evidence

Changed only `work/consistent_repair.py` and added `work/test_consistent_repair.py`; no CAD change belongs to this fix.

Command, from `work/`:

```powershell
& 'C:/Users/PMLS/AppData/Local/Programs/Python/Python312/python.exe' -B -m unittest -v test_consistent_repair
```

Observed on 27 September 2026 after the final staging-path change: **8 tests passed**, 0.147 seconds. Every `build_ops.py` subprocess was mocked; fixtures contain tiny CSV row sets. No geometry engine, router or native application was launched by these tests.

Covered conditions:

- Nonzero checker exit returns failure and publishes no final output.
- Deletion mismatch returns failure even when `--drop-bad` exits zero.
- Missing checker summary cannot be mistaken for a clean check.
- Problems with no droppable groups return failure.
- A legitimate geometric drop removes the target/victim reroute, preserves its original victim copper, then requires a clean recheck before publishing.
- Exhausting the check limit returns failure without final outputs.
- A failed run does not overwrite previously existing output files.
- Extra-plan staging cannot accidentally write the final additions path when its filename lacks a `.csv` extension.

`build_ops.py --drop-bad` intentionally exits zero when it filters problematic addition groups. The fix therefore checks both the process exit code and the structured `PROBLEMS` / `DROPPED_GROUPS` output. It does not reject legitimate filtering merely because the first candidate had geometric problems.

Caller requirement: honor the nonzero exit status. Old final output files remain intact on failure and are not evidence that the new candidate passed. Gloss output still has incompatible deletion-group ownership and must not use this repair-specific helper.
