# Gloss contact guard: code and synthetic test evidence, 27 September 2026

Scope: only `work/gloss.py`, new `work/test_gloss_contacts.py`, and this note. No production board geometry was loaded, no native CAD or router process was launched, and no design or rule was edited. `consistent_repair.py` is owned by a separate agent and was not edited here.

## Changes

- `work/gloss.py:62` adds a conservative same-net contact guard. It queries the existing geometry index for copper-envelope contacts on the chain's layer, including other movable tracks and earlier additions in the same batch. It skips objects being replaced by this chain and stale deleted objects. Boundary-distance tolerance is 0.000001 mm.
- `work/gloss.py:194` skips a chain before any path generation if a contacting object's copper does not cover either retained endpoint center. This preserves interior pad, via, branch and edge-only contacts without trying to split the graph. Endpoint contacts that cannot be guaranteed are also skipped. This can reject cosmetic opportunities even when a particular proposed path would happen to keep them.
- `work/gloss.py:225` assigns one `G<n>:<net>` ID to every addition and deletion for the chain. CSV columns stay the same. This supplies ownership metadata; a downstream filter still needs to honor it.
- `work/gloss.py:241` reports the number of skipped chains. The module description now describes its endpoint anchors and conservative skip behavior accurately.

## Focused test result

From `work/`:

```powershell
& 'C:/Users/PMLS/AppData/Local/Programs/Python/Python312/python.exe' -B -m unittest -v test_gloss_contacts
```

Observed result: **exit 0; 11 tests, 0.372 seconds; OK**. The runner mocks only the board load, constructs tiny synthetic copper fixtures, then executes the actual gloss script with its real geometry index and CSV output.

The tests cover interior pads, vias, fixed and movable branches, copper-edge contact without centerline contact, conservative near-endpoint skipping, endpoint contacts that still allow simplification, another-layer pad exclusion, a via at an existing vertex, distinct paired add/delete groups for two chains, and a later chain protected by an earlier addition in the same batch. The original plan reader emits pre-existing `ResourceWarning` messages for its unclosed input handle; these do not fail the tests.

`git diff --check -- hardware/compact_mainboard_20260925T115919Z/work/gloss.py hardware/compact_mainboard_20260925T115919Z/work/test_gloss_contacts.py` returned exit 0 (Git emitted only its line-ending conversion notice).

## Limits and integration

This is synthetic code evidence, not native board connectivity evidence. Polygon pours remain outside the offline model; approximate movable keys and the intersection-only `WINDOW` behavior remain as described in `ASTRA_FINISH_TOOLS.md`. Native delta/unrouted/DRC checks remain necessary for any later applied batch. This note supersedes that review's statements that gloss lacks an interior-contact guard and emits `GLOSS_DEL` for every deletion; its downstream filtering warning remains relevant until the separate consistency-helper repair is verified.

The required read-only graph query was run using the root workspace venv and found `gloss.py`, `is_anchor`, `legal`, `k_src`, `k_row`, and `build_ops.py`. A repository-wide graph refresh and any commit are left to the root agent because this assignment is limited to `work/` plus new evidence notes and shares a constrained laptop with an active routing task.
