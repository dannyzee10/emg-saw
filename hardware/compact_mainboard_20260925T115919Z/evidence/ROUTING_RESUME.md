# C2 6-layer routing completion — resume note (keep this file current)

**Task (user, 26 Sep 2026):** "switch to 6 layers and now complete all the unrouted" on candidate C2
(`C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc`). No fabrication approval (R2). Never push to main.

## State at 03:45 (27 Sep) - SUPERSEDES everything below
- C2 = state Z: **28 unrouted** (5 GND, 4 3V3_DIG, 1 3V0_ANA, 18 signals), copper DRC clean, 0 antennae.
  Geometry GEOMETRY_C2_6L_Z.txt, DRC DRC_C2_6L_Z.json. Channels 3 and 5 now route after the RG_3/RG_5 rotation
  (REP_X +20, exact-clean, 60 rows); two antenna prune passes (OPS_PRUNE_X/Y).
- Plan list for repair/rip tools: previous list + REP_X_ADDS_OK.csv.
- Next: ADC_EMG2/3 region rip (46,25.5)-(53.5,32.5) so the 3V0_ANA L5 track at x=51.62 is re-routed and
  pin 24/25 can use inner fan-out vias (R_ADC pads are only ~0.22 mm from the MCU pads - no left escape);
  then ST67 SPI/UART (4), charger VBUS x3 / VBAT_CELL x2 / USB_PGOOD, INA_OUT_3 / NetINA2_3 / NetINA4_3, Vc_1, DRL_LIMITED.

## State at 02:55 (27 Sep)
- REP_W (regions on V) gained 0 write-safe rows -> not applied.
- Nudge written to C2 (not committed yet): RG_3 and RG_5 rotated 270 -> 90 in place (VOUT/NetCH pad-order crossing
  removed), attached copper ripped (RIP_RG35.csv, 38 objects). State W: 46 unrouted, copper DRC clean, 3 antennae.
  Geometry GEOMETRY_C2_6L_W.txt, DRC DRC_C2_6L_W.json.
- Running: REP_X = repair.py on W (MARGIN 0.025, FIRST_NETS channel nets, 2 passes), log tmp/rep_x.log,
  outputs REP_X_ADDS/DELS.csv -> consistent_repair -> write -> DRC. If it does not beat 36, restore by re-routing.
- Next nudge clusters: MCU ADC fan-in (ADC_EMG2/3), ST67 SPI/UART (4), charger VBUS x3 / VBAT_CELL x2 / USB_PGOOD.

## State at 01:40 (27 Sep)
- C2 = state V, committed db59c86: 36 unrouted (6 GND, 4 3V3_DIG, 2 3V0_ANA, 24 signals), copper DRC clean, 0 antennae.
  Geometry GEOMETRY_C2_6L_V.txt, DRC DRC_C2_6L_V.json.
- Loop per round: repair.py (EXACT=1, MARGIN=0.02-0.025, BK13_ZONES set) -> consistent_repair.py -> build_ops -> write -> DRC
  -> commit. Add each round's *_ADDS_OK.csv to the plan list (latest: REP_V_ADDS_OK.csv).
- Running: REP_W (regions analog/MCU-ADC/charger + 2 passes, MARGIN 0.02), log tmp/rep_w.log.
- Pinches still open: MCU ADC fan-in (R_ADC2/3 vs pins 24/25, needs inner-layer via path), SPI/UART to ST67,
  VBUS/VBAT at the charger, VOUT_3/5 back-ends.

## State at 23:05 (26 Sep)
- C2 = state R, committed 63bfefb: 44 unrouted (7 GND, 5 3V0_ANA, 4 3V3_DIG, 28 signals), 5 antennae, copper DRC clean.
  Geometry GEOMETRY_C2_6L_R.txt, DRC DRC_C2_6L_R.json.
- Working method now: repair.py (corridor rip + strict acceptance) -> consistent_repair.py (exact check, drop repairs
  with their victims) -> write -> DRC. Plan CSV list for repair/rip tools must include every routed plan written so far:
  TRIAL_OK, C2R2_OK, 6L1_OK, BATCH_C_OK, 6L3_OK, 6L5_OK, 6L6A_OK, 6L7B_OK, REPAIR_ADDS_N3_OK, REG_MCU_ADDS_OK,
  ROUTE_PLAN_C2_6L8A_OK, REG_ANA_ADDS_OK.
- Known pinches: USB-C CC2 (B5) + VBUS (B4_A9) blocked by the NetR_LIM_2 via at (18.325,37.575) -> repair should rip it;
  analog band = via-site limited (L3 38 %, L5 19 % used).

## State at 22:10 (26 Sep)
- User chose (21:52): KEEP RULES, NUDGE PARTS.
- Written to C2 (not yet committed; last commit 466af2d = state O, 57 unrouted): MCU-edge region re-route (+2) and the
  charger-box rip; charger nudges C_BAT -0.30 x, R_TS_TOP -0.40 x, C_IN_ -> (14.85,36.75), R_PGOOD -> (17.60,42.35)
  (legal: native DRC 0 component clearance). State P: 79 unrouted (charger box ripped). GEOMETRY_C2_6L_P.txt.
- Running: router charger-first variants A/B (OUT_TAG _C2_6L8A/_C2_6L8B, logs router_6l8a/b.log).
- Next: pick best, exact-check (build_ops on GEOMETRY_C2_6L_P), write, DRC; then repair.py loop; then analog back-end nudges.

## State at 21:50 (26 Sep)
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
