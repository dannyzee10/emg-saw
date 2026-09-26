# C2 6-layer routing completion — resume note (keep this file current)

**Task (user, 26 Sep 2026):** "switch to 6 layers and now complete all the unrouted" on candidate C2
(`C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc`). No fabrication approval (R2). Never push to main.

## State at 06:55 (27 Sep) - SUPERSEDES everything below
- C2 = state AH, committed aee3750 (pushed): **21 unrouted** (6 GND, 1 3V0_ANA, 14 signals), copper clean.
  Charger nudge (R_LIM, R_PGOOD off the USB-C VBUS pins) -> all VBUS links routed. PLANS include REP_AI_ADDS_OK.
- repair.py: victims of one net whose copper touches are merged into one cluster (set_ends / touch_points_multi); the
  shared touch point vanished when both were ripped and made every reconnect fail ("victim-first ... " failures).
- Running: REP_AJ on AH (clusters + reorder + plane), log tmp/rep_aj.log.
- Known: new Top copper can cut the L1 GND pour away from a pad (D_CC_ESD-3 at AH) - pours are not modelled; plane mode
  gives such pads their own via in the next round.

## State at 06:05 (27 Sep)
- Last commit fc11aef = state AF (22 unrouted). Written since (NOT committed yet): charger nudge
  R_LIM (17.047,37.536,0) -> (18.90,37.55,180) and R_PGOOD (17.60,42.35,0) -> (18.85,42.40,90), attached copper ripped
  (RIP_CHG2.csv, 55 objects; rip_attached.py) so the USB-C VBUS pins B4_A9 / A4_B9 can take via-in-pad.
  State AG: 25 unrouted (+3 ripped), copper clean, 0 component clearance. GEOMETRY/DRC _AG.
- Running: REP_AI on AG (VBUS / NetR_LIM_2 / 3V3_DIG / USB_PGOOD_N first, REORDER 3), log tmp/rep_ai.log.
  If it does not get below 22: restore fc11aef's PcbDoc (git checkout fc11aef -- <PcbDoc>) or keep and continue.
- REP_AG (regions) and REP_AH (reorder) on AF gained 0; diagnostics: most failures are "target (no path)" after ripping
  12 victims -> fixed copper / placement blocks (see tmp/rep_ah.log "repair fail" lines).

## State at 05:45 (27 Sep)
- C2 = state AF, committed fc11aef (pushed): **22 unrouted** (5 GND, 1 3V0_ANA, 16 signals), copper clean, 0 antennae.
  Geometry GEOMETRY_C2_6L_AF.txt, DRC DRC_C2_6L_AF.json. PLANS in run_repair.py include REP_AE_ADDS_OK.
- repair.py now: safe-margin retry (SAFE_MARGIN 0.06) when the exact check fails; plane mode falls back to the partner;
  region_pass restores a victim's ORIGINAL copper when it cannot be re-routed but is still legal (restore_group).
- Running: REP_AG = regions (MCU bottom-left; ch2 INA; ch4 INA; charger; DRL corner) + 1 pass on AF,
  log tmp/rep_ag.log.
- Nudge candidates if regions stall: U1 +0.25 mm x (opens a 0.6 mm edge channel for U1-11 GND to the edge GND via);
  TP_VREF_B_SRC relocation; ch2/ch4 INA pin-3 (Vc_2 via / y=17.15 track box in the pin).

## State at 05:10 (27 Sep)
- C2 = state AC, committed f8465cf (pushed): **24 unrouted** (5 GND, 2 3V0_ANA, 17 signals), copper clean, 0 antennae.
  Geometry GEOMETRY_C2_6L_AC.txt, DRC DRC_C2_6L_AC.json. Offline prediction now matches Altium (touch-point fix).
- Round = `python run_repair.py <STATE> <TAG> PLANE=1 DEBUG=1 PASSES=2 CORRIDOR=.. MAXV=..` -> consistent_repair.py
  (geometry of STATE) -> build_ops (--del DELS_OK) -> write (open_proj/apply_ops) -> DRC/export -> parse_drc ->
  unrouted_summary -> prune antennae if any -> commit/push; add <TAG>_ADDS_OK to run_repair.PLANS.
- Running: REP_AD on AC (MAXV 16, CORRIDOR 1.5, PLANE_WIN 4), log tmp/rep_ad.log.
- Remaining: GND x5 / 3V0_ANA x2 (enclosed, no via site), VBUS x3, VBAT_CELL x2, USB_PGOOD_N, NetINA2_3 / NetINA4_3
  (INA pin 3 boxed in on Top), ADC_EMG5, FG_ALRT, VOUT_2, Vc_1, DRL_LIMITED, ST67 SPI/UART x4.
- Avoid REGIONS for now: region acceptance allows victim losses (net +1 only).

## Update 04:35 (27 Sep)
- C2 on disk = state Z (committed d652812, pushed): 28 unrouted.
- Running: REP_Y = `python run_repair.py Z REP_Y DEBUG=1 PASSES=2 CORRIDOR=1.0 MAXV=10 REGIONS="46.0,25.0,55.5,32.5"
  FIRST_NETS=ADC_EMG,3V3_DIG,3V0_ANA` (log tmp/rep_y.log). ADC region accepted (+1). Then consistent_repair -> write -> DRC.
- New: `run_repair.py STATE TAG [K=V]` (standard env + full plan list; add each *_ADDS_OK to PLANS).
- Fixed: router5.end_copper now prefers copper on the DRC-named layer (TP_3V3_DIG was matched to CUP4-1 on Bottom ->
  false "already connected").
- New repair modes: DEBUG=1 (prints why each direct route fails, incl. exact-check object + distance), ONLY_NETS,
  PLANE=1 (GND/3V0_ANA end without plane access routes to the nearest legal via site, with victims),
  PLANE_DEAD (L2/L4 pour fragment 10.87,10.5-15.66,11.51 is cut off by the corner TH pads: a via there is NOT plane
  access -> the J_FPC1 pin-7 GND island needs a via in the main plane).
- Finding: raster can be one cell (0.05) optimistic at a via edge; MARGIN 0.025 lets such paths through and the exact
  check rejects them (VBUS x3 fail by 0.025 vs NetR_LIM_2 / 3V3_DIG vias) -> VBUS needs victims, not a margin change.

## State at 03:45 (27 Sep)
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
