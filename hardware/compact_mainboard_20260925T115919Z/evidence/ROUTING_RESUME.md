# C2 6-layer routing completion — resume note (keep this file current)

**Task (user, 26 Sep 2026):** "switch to 6 layers and now complete all the unrouted" on candidate C2
(`C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc`). No fabrication approval (R2). Never push to main.

## State at 21:50 (26 Sep) - SUPERSEDES the section below
- C2 board = state O: pours added (L5 GND fill, L1 Top GND), repair loop written; DRC copper-clean; **57 unrouted**
  (10 GND, 6 3V0_ANA, 5 3V3_DIG, 36 signals). Geometry before the repair write: GEOMETRY_C2_6L_N.txt (export a fresh one).
- Global re-route experiment finished: 57/64 left -> not applied (throwaway copy only).
- Automated routing has plateaued (~55-60). Asked the user (21:50) to choose: (1) keep rules + small passive nudges
  (charger: C_BAT/R_EN1_BIAS pinch UP1 pins 6/7; MCU edges; channel back-ends), (2) allow 0.20 mm analog clearance
  locally, (3) grow the board 2-3 mm. Default while unanswered: (1).

## State at 19:55 (26 Sep)
- C2 board = state M: 6 layers (JLC06121H-3313), DRC copper-clean, **61 unrouted** (15 GND, 6 3V0_ANA, 5 3V3_DIG, 35 signals).
  Backup of this exact board: `evidence/backups/C2_6L_M/EMG_MainBoard_Layout.PcbDoc` (sha256 3fa1cba3…); committed and pushed
  as 1966451 on pcb-routing-0925.
- Experiment in progress: GLOBAL re-route. The throwaway copy `evidence/disposable_c2stack6/MainBoard/STACK6_PROBE.PcbDoc`
  has all routed copper ripped (fixed copper kept) -> 395 unrouted (`DRC_PROBE_GLOBAL.json`, geometry `GEOMETRY_PROBE_GLOBAL.txt`,
  router input `ROUTE_IN_GLOBAL.json`). Routing variants write `ROUTE_PLAN_C2_GLB{A,B}.csv`, logs in
  `C:/Users/PMLS/.claude/jobs/5c1210bf/tmp/router_glb{a,b}.log`.
- Decision rule: apply to C2 only if (exact-checked) global result leaves fewer than 61 unrouted. To apply: build_ops
  `--del RIP_GLOBAL_M.csv` + the OK plan on GEOMETRY_C2_6L_M.txt, write natively to C2, DRC. Otherwise keep state M and continue
  cluster rip-ups.

## How to run things (work/)
- Router env: `VIP=1 NO_RELAX=1 MCU_FANOUT=1 BIG=1 GRID=9.5,9.5,69.6,46.5 L5_RESERVED="3V0_ANA:10.5,10.5,68.6,25.3;3V0_ANA:10.5,25.3,47.5,27.2;3V0_ANA:31.6,27.2,35.8,30.4" BOARD_BOX=12,12,67.1,44`
  plus `FIRST_NETS="Vservo_,INA_OUT_,NetINA,NetCservo,NetCL,NetCH,VOUT_,..."` (channel-local first worked for Vservo).
- Exact check: `build_ops.py PLAN --drop-bad OK.csv` (same env incl. BK13_ZONES=../evidence/BK13_ZONES_C2.csv); audit `STACK=6 audit_plan.py`.
- Native: `mkvariant.py <template> <prefix> C2 <log>` then `run_wait.ps1` with the PRINTED name; open project first (open_proj_T).
  For the probe copy: target DISP3 and sed the file name to STACK6_PROBE.PcbDoc (+ drop the modified check in apply_ops).
- If Altium says a script is still running / hangs: board saved? -> close X2, restart, reopen project, re-run (user rule).
- Close Altium while long Python routing runs (memory ~0.4 GB free with Altium open).

## Remaining after routing
Pours (`OPS_C2_6L_POURS.txt`: L5 GND fill + L1 Top GND), final DRC, STACK=6 audit, docs (C2_COMPACT_AUDIT.md,
NEXT_AGENT_CHECKPOINT.md), refresh.ps1 / commit / push, final report with `result:` line.
