# Next-agent checkpoint — compact main board (R2)

**Status:** COMPACT TWO-SIDED PLACEMENT READY FOR REVIEW — ROUTING/MECHANICAL QUALIFICATION STILL OPEN.
Stop point reached: COMPACT PLACEMENT REVIEW. Unrestricted full-board routing and fabrication release are NOT authorized yet.

## Open this

- **Project:** `.claude/worktrees/pcb-routing-0925/hardware/compact_mainboard_20260925T115919Z/B_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PrjPcb`
- **Variant:** `PROTO_1_REMOTE_NTC`.
- **Opening the board:** open it **inside the project**. Opened as a free document, Altium marks it modified.
- **Board (PcbDoc):** SHA-256 `BF906AE64F0FCB948407013271120432FE008E39A34BC148308AC281D4E33B16`.
- **Git:** branch `pcb-routing-0925`, in worktree `.claude/worktrees/pcb-routing-0925`.
- **Baseline A (read-only):** `A_BASELINE_READONLY/MainBoard/`, PcbDoc `4AF4DDE3…ECBF015`, identical to `hardware/pcb_layout_2026-09-23_drl` in the main checkout.

## Completed operations (25 Sep 2026)

1. **Stage A.** Recovered and snapshotted the 231-part checkpoint (hash manifest).
2. **Stage B.** Measured the baseline: 80 × 45 mm, 3,596.6 mm², 209 top / 22 bottom parts.
3. **Proved** the native APIs on disposable copies (flip, MoveByXY, polygon, rule scope, outline).
4. **Stage C.** Implemented candidate B natively: 75 × 40 mm (−16.7 %), 22 parts moved to Bottom as whole groups, block repack, free pads, rules, polygons. Save/reopen readback matched for 231/231; preservation PASS.
5. **Fixed** the double-moved UP1 thermal vias. Added six fine-pitch escape rules and the via-tenting rule.
6. **Stage E.** Limited routing trial: 37/50 connections routed and written. Final DRC: 0 shorts / clearance / component / mask; 460 unrouted; 74 silk + 1 text-edge open.
7. **Stage F.** Native 2D/3D Top and Bottom captures, renders, tables, and `evidence/COMPACT_CHANGE_AUDIT.md`.

## Tooling (all in `work/`)

- **Launcher:** `run_wait.ps1` / `run_native.ps1`. Dispatch into the running AD22; results are files ending `COMPLETE`.
- **Script copies:** always run a fresh-named copy of a `.pas`. Altium caches loaded script projects.
- **Writers:**
  - `apply_B.pas`: ops-driven placement writer. Phase 1 resolves every op exactly; phase 2 applies, repours, saves, reopens and reads back.
  - `apply_ops_v6.pas`: TRACK/VIA/RULE/CUTOUT/POLY writer.
  - `apply_fp.pas`: free pads.
- **Offline tools:** `plan_B.py` (planner + overrides), `gen_B_ops.py`, `router5.py` (component-aware, scoped 0.2 mm fallback), `build_ops.py` (exact check, `--drop-bad`), `audit_plan.py`, `compare_pads.py`, `compare_readback.py`, `gen_evidence.py`.
- **Never call unproven API methods on the live board.** The script debugger halts even inside `Try` and freezes scripting. If that happens: close Altium without saving (confirm the B hash first), restart it, then reopen B inside its project.

## Next authorized step (after the user's review)

1. The user accepts B at 75 × 40, or asks for a 70 × 40 study C via one of the audit's §6 options (each needs an explicit decision).
2. Silkscreen legibility pass.
3. Add the BK13 0.13 mm zone escape rules at B positions.
4. Full routing with `router5.py`, following the routing requirements report. Written in batches through `apply_ops_v6.pas`, with DRC after each batch.
5. Pours and stitching.

The paused 80 × 45 routing work (`hardware/pcb_layout_2026-09-24_routing/`, 208 connections written) stays as a reference only.
