# CURRENT: BJ — routing complete and all-trace checks, 27 September 2026

- Native DRC: zero opens/antennae/shorts/clearance/width/layer/via errors. Remaining246 =157silk-mask+84silk-silk+5overlay-outline.
- Current savedPCB hash `0acc1e8eefea1bba24c8ec74a84c7dddd757a6bd520cf3d82f972191e28b585c`. Altium left open on this saved PCB; inspect live state before any new writer.
- All2281freecoppertracks and470vias pass5032independent width/layer/via checks. Via rule min.45/.20; preferred/max.60/.30. Native batch kinds9/11 are now enabled; previous coverage gap closed.
- User edit retained. TP_GND_DIG +.20mmX; no schematic/project changes. Remaining raw-serialization and manufacturing limitations are documented, not waived.
- Authoritative summary: ASTRA_ROUTING_COMPLETE_BJ_20260927.md; finalnativebase GEOMETRY_C2_6L_BJ.txt / DRC_C2_6L_BJ.json. All approved adds/deletes named in report. Do not apply old candidates again.
- Next bounded work: overlay finishing. No current unrouted task remains. No fabrication release.

---

# C2 6-layer routing completion — resume note (keep this file current)

**Task (user, 26 Sep 2026):** "switch to 6 layers and now complete all the unrouted" on candidate C2
(`C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc`). No fabrication approval (R2). Never push to main.

## HANDOFF 21:xx (27 Sep): work paused by the user and handed to Astra -> read `HANDOFF_ASTRA_2026-09-27.md` first
- State AZ in Altium (9 unrouted); MERGE_I_ADDS_OK/DELS_OK ready (-> 6); 3V0_ANA U1-4 solved by seeded negotiation
  (NEG_C9). NetINA4_3 sweep (NEG_B8) stopped after tries 0-1; Vc_1, Wi-Fi x4 still open. Commands in the handoff.

## CURRENT — Astra BF, 27 Sep2026, native DRC completed21:22:37local

- **MCU_WIFI_UART_RX routed; two opens remain:**`MCU_WIFI_UART_TX`,`WIFI_SPI_CS`. See `ASTRA_MCU_RX_RESOLUTION_BF.md`.
- Applied ONLY `ASTRA_MCU_RX_REINFORCED_ADDS/DELS.csv`, `OPS_BF_UART_RX_REINFORCED.txt`:33tracks+5vias added,16tracks removed; no component/pin/rule changes. POWER_READY candidate failed clearance and was NOT applied.
- Neighboring3V3_DIG/I2C_SDA/MCU_BOOT0/VSYS routes preserved and adjusted. All added power tracks.40mm, with direct .40mm sourcevia→CUP4_1 feed; original pin escape retained. Target .20mm withtwo.60/.30vias; otherthreevias belong toSDA/BOOT0.
- Native save/reopen and exactdelta PASS:2236free tracks/460vias;231components/812pads/1629fixed records unchanged. EightSchDocs+PrjPcb unchanged. Net/rule/stack/outline streams preserved; opaque body/pad/text differences still documented.
- Fresh DRC254total:2unrouted,6antennae,157silk-mask,84silk-silk,5outline. Only MCU_WIFI_UART_RX diagnostic removed; no new violations. ViaStylebatchcoverage remains open; not fabrication-ready.
- Nextbaseline:`GEOMETRY_C2_6L_BF.txt`,`DRC_C2_6L_BF.json`. Backup:`ASTRA_BF_BEFORE_20260927/`; savedhash:`ASTRA_BF_AFTER_HASH.json`. AltiumPID14888 open at checkpoint, no router/script remains active. Verify live state before writing.
- `run_repair.PLANS` still not extended automatically. Include only accepted final CSVs intentionally as EXTRA_PLANS; protect CH4/Vc_1 boundedL5 routes and completedUART routes. Do not use rejectedcandidates.

## Previous — Astra BE, 27 Sep 2026, native DRC completed20:59:18local

- **WIFI_UART_RX routed; three opens remain.** See `ASTRA_UART_RESOLUTION_BE.md` and independent BEreview.
- Final applied plan ONLY:`ASTRA_UART_READY_ADDS.csv` / `ASTRA_UART_READY_DELS.csv`; `OPS_BE_UART_READY.txt`.18tracks+1via added,15tracks removed. One .45/.20 VIP atU_WIFI1.23(42.275,42.325). No parts/pins/rules changed.
- Neighboring tracks adjusted on MCU_SPI_MISO,SYS_EN,WIFI_UART_TX,WIFI_BOOT,VSYS; allsix nets graph-verified and native-verified. OriginalVSYSvia(43.125,41.625) retained; every addedVSYStrack .40mm. **Reject earlier raw ASTRA_BD_WIFI_LOCAL/OPS_BE_UART candidate**: long thin VSYSdetour was NOT applied.
- Fresh native DRC255total:3unrouted,6antennae,157silk-mask,84silk-silk,5outline. Only WIFI_UART_RXopen removed; every other diagnostic unchanged. Zero reported shorts/clearance/width/component-clearance.
- Remaining:`WIFI_SPI_CS`,`MCU_WIFI_UART_RX`,`MCU_WIFI_UART_TX`. Nextbaseline:`GEOMETRY_C2_6L_BE.txt`,`DRC_C2_6L_BE.json`.
- Native save/reopen and exactcopperdelta PASS:2219free tracks/455vias;231components/812pads/1629fixed records unchanged. EightSchDocs+PrjPcb preserved. Rules/nets/stack/outline unchanged; rawbody/pad/text/cache differences remain documented. ViaStylebatchcoverage stillopen.
- Backup:`ASTRA_BE_BEFORE_20260927/`; afterhash:`ASTRA_BE_AFTER_HASH.json`. AltiumPID19436 open at checkpoint, no routing script remains active. Verify live PID/state before anotherwrite.
- `run_repair.PLANS` not automatically extended: include ONLY final READY files as EXTRA_PLANS if intending future rip-up; protect CH4/Vc_1 boundedL5routes. Do not include rejectedrawUARTplan.

## Previous — Astra BD, 27 Sep 2026, native DRC completed 20:25:32 local

- **Vc_1 solved in native Altium; four unrouted remain.** See `ASTRA_VC1_RESOLUTION_BD.md`.
- Added seven .20mm L5/Mid Layer4 tracks between existing Vc_1 vias(15.9,11.2) and(24.175,19.325). No component/via moves, no deletions, no rules changed. Actual socket keepout avoided. Limited L5 exception; preserve L2/L4 GND.
- Applied `OPS_BD_VC1.txt`; native save/reopen completed. Exact copper delta PASS:2216free tracks/454vias; all231packages/812pads/1629fixed records unchanged. EightSchDocs+PrjPcb hash-preserved.
- Fresh native DRC256total:4unrouted,6antennae,157silk-mask,84silk-silk,5outline; zero reported copper-clearance/short/width/component-clearance. Only Vc_1 violation removed; all other details unchanged.
- Remaining:`WIFI_SPI_CS`,`WIFI_UART_RX`,`MCU_WIFI_UART_TX`,`MCU_WIFI_UART_RX`. Baseline for next work:`GEOMETRY_C2_6L_BD.txt`,`DRC_C2_6L_BD.json`.
- Before backup:`ASTRA_BD_BEFORE_20260927/`; saved hash:`ASTRA_BD_AFTER_HASH.json`. Strict stream comparison retains opaque Pads6/Texts and cached violation changes; via-style batch coverage remains open. No full-board DRC/fabrication approval.
- Vc_1 and CH4 new copper remain protected from routine rip-up unless their CSVs are explicitly included. No native process was left running by the scripts; Altium remains open with the saved board.

## Previous — Astra BC, 27 Sep 2026, native DRC completed 20:10:52 local

- **Channel 4 solved in native Altium. Current saved state is BC, five unrouted.** Details: `ASTRA_CHANNEL4_RESOLUTION_BC.md`.
- INA4 unchanged. CL_4 Bottom moved x51.3 to48.2mm, y16.05/rotation180 unchanged. Short NetINA4_3 route uses L5 within x51.2–57.6/y15.1–17.35; existing native routing-layer rule allows it. No rule change or GND split.
- Applied `OPS_BC_CH4.txt`, exact `ASTRA_CH4_READY_ADDS.csv` / `ASTRA_CH4_READY_DELS.csv`. Native save/reopen and explicit translation-aware geometry delta PASS. Free geometry:2209tracks/454vias (writer net-assigned track count2199).
- Native DRC257total:5unrouted,6antennae,157silk-mask,84silk-silk,5outline. Zero reported copper-clearance,short,width,component-clearance violations. ViaStyle batch coverage remains OPEN; do not claim full DRC clean.
- Remaining opens:Vc_1,WIFI_SPI_CS,WIFI_UART_RX,MCU_WIFI_UART_TX,MCU_WIFI_UART_RX. Use `GEOMETRY_C2_6L_BC.txt` / `DRC_C2_6L_BC.json` for future work.
- Backup BB:`ASTRA_BC_BEFORE_20260927/`; after hash:`ASTRA_BC_AFTER_HASH.json`. Eight SchDocs+PrjPcb unchanged. Strict raw-stream checker still reports component/pad/body/text changes; see limitations in resolution report.
- New BC copper is not yet added to `run_repair.PLANS`; include `EXTRA_PLANS=ASTRA_CH4_READY_ADDS` if intentionally allowing it to be ripped. Prefer protecting the solved input route during unrelated repairs. Keep bounded L5 exception rather than globally permitting new L5 analog routes.

## Astra update — 27 Sep 2026, 19:10 local (actual native timestamps)
- State BA is now saved/reopened after MERGE_I. Native DRC reports **8 unrouted**, not the handoff's predicted6.
  No copper shorts/clearance violations;8antennae,159silk-mask,84silk-silk,5outline violations remain.
- Newly open VREF_A is the pruned path between vias(14.525,20.625) and(15.125,23.025). Do not repeat that prune.
  GND remains between Bottom track(53.475,21.175)-(53.475,22.275) andTop track(54.075,19.775)-(54.075,20.375).
  Other six remain NetINA4_3,Vc_1,WIFI_UART_RX,MCU_WIFI_UART_TX,MCU_WIFI_UART_RX,WIFI_SPI_CS.
- Backup/source hashes: `ASTRA_BA_20260927/`. Fresh nativeAZ export exactly matched handoff geometry before writing.
- `ASTRA_BA_DELTA.json` verifies every requested copper delta:2189free tracks/451vias, unchanged nativePAD/COMP/fixed
  geometry. NativeapplyPHASE1_OK/RULES=0,SAVED,AFTER_REOPEN,COMPLETE. Rules,nets,classes,stack/outline/origin frozen.
  OLEstructural checker separately flags native serialization changes in pad/body/text streams; not silently masked.
- `run_repair.PLANS` includesMERGE_I. `neg_sweep` logs now defaultinsideworktree `evidence/routing_logs/` ratherthan
  the previous session's external Claude job folder. Oneheavyprocessatatime; Altium mustclosecleanly before routing.

## Update 19:30 (27 Sep) - on top of the 17:50 state below
- Wins on AZ (not written yet, exact-checked together as MERGE_H: 177 add / 132 del rows, 0 problems):
  REP_FC3 NetLED_CHG_C (partial rip-up PARTIAL=0.35 + cascade, 24 partial victims), REP_FA GND CU_14-1,
  PRUNE_AZ (dead VREF_A stub, 3 L1 tracks from the via at 15.125,23.025; prune_chain.py).  -> writing gives 7 left.
- New repair.py modes: PARTIAL=<mm> (rip only the part of a victim near the path; split groups renamed '#p<k>');
  plane islands without a via site now join ANY other touch point by copper; RIP_BK13 loads only escape VIAS (+stub)
  as groups (in-socket tracks use the 0.13 zone clearance the router cannot redo); NEGOTIATE=<box>: PathFinder
  negotiated-congestion re-route of a dense box (exact-zone penalties via distance transforms, own copper excluded,
  pres capped 40, history 1.0/pass); prints the last conflict cells when it does not converge.
- router5: astar(pen=...) (per-cell penalty, pen['VIA']); ALLOW_BOTTOM=<nets> policy override (Bottom is normally
  only for nets with a Bottom pad).
- Findings: NetINA4_3 (IN+ node of INA4) may only use L1/L3 here (L5 reserved for the 3V0_ANA pour, no Bottom pad)
  and must cross Vc_4 (socket -> RDD12-1) -> negotiation stuck on exactly NetINA4_3 vs Vc_4; retry with
  ALLOW_BOTTOM=NetINA4_3,NetINA4_2 and a larger box.  Vc_1: the J_FPC1 corner via is sealed (J_REF pad copper, 3V0_ANA
  socket via, socket keep-out incl. L3, NetJ_REF_1 L3 track at y 13.7-13.85) -> NEGOTIATE over 14.6-24.8 x 10.6-19.8.
  WIFI_SPI_CS (22 mm across the MCU fan-out): if routing fails, propose moving CS to a free MCU pin next to the ST67
  (software NSS = any GPIO; like the approved UART swap) - needs the user's OK (schematic change).

## State at 17:50 (27 Sep) - SUPERSEDES the older state notes below (the plan below still applies)
- C2 = state AZ (written + saved, Altium DRC): **9 unrouted** (3V0_ANA U1-4, GND CU_14-1, NetINA4_3, NetLED_CHG_C, Vc_1,
  WIFI_SPI_CS, WIFI_UART_RX, MCU_WIFI_UART_TX, MCU_WIFI_UART_RX); copper clean; 1 Net Antennae = dangling VREF_A stub
  L1 (14.725,21.275)-(15.725,20.275) left by a victim re-route -> prune it (check the chain) in the next write.
  AZ = AY + MERGE_G (REP_CB3 VOUT_2 + REP_DA4 GND C_DRL_DEC-2), OPS_AZ.txt. PLANS include MERGE_G_ADDS_OK.
- User asked (27 Sep) to solve the unrouted IN PARALLEL: one repair process per problem area on the same state
  (ONLY_NETS / ONLY_BOX), then merge_rounds.py (priority order, ids renamed P<ROUND><k>) -> consistent_repair -> write.
  Parallel wins on one base can collide (two victims re-routed into the same gap) -> the exact check drops both; write
  the compatible subset, re-run the rest on the new state (that is why 3V0_ANA U1-4 and GND CU_14 are open again).
- repair.py upgrades (27 Sep evening), all env-gated:
  - ONLY_BOX: keep connections with an end in the box(es).  DIAG_FIXED=box: route each connection against FIXED copper
    only (every routed group of other nets in the box ripped) -> 'no path' = needs placement/pin change, else lists the
    groups the path collides with.
  - GUIDED=<margin>: victims = exactly the groups the fixed-copper path collides with (verified by re-routing with only
    them ripped, tolerance widened 0.12 -> 0.7).  CASCADE=<max victims>: a victim that cannot be re-routed pulls in its
    own blockers (measured with the target in place); reverse cascade when victim-first ordering blocks the target.
  - Exact rollbacks: snap()/restore() of the router rasters + copper/hole lists (piecewise undo leaked: one net id per
    raster cell, holes re-stamped from approximate circles).  unstamp_holes no longer re-stamps the ripped holes.
  - STRICT_VICTIMS (default on): a victim route failing the exact check after retries is a failed victim (reorder /
    cascade react) instead of failing the whole repair at the final check.
  - RIP_BK13=1 + EXTRA_PLANS=BK13_ESCAPE_PLAN_C2: hand-placed socket escapes become rippable, one group per socket+net.
    Needed for Vc_1: its escape via (15.9,11.2) is sealed by the mounting hole, the J_FPC1 3V0_ANA via (15.95,12.55),
    the socket body keep-out (16.79-20.61 x 11.39-13.02, all layers) and L3/GND copper; with escapes rippable an
    all-L3 path exists (6 victims incl. the J_FPC1 3V0_ANA escape).
- Round launch pattern: `python run_repair.py AZ REP_Fx PLANE=1 DEBUG=1 PASSES=2 MAXV=12 REORDER=10 GUIDED=2.0
  CASCADE=20 [RIP_BK13=1 EXTRA_PLANS=BK13_ESCAPE_PLAN_C2] ONLY_NETS=...`; merge: `python merge_rounds.py OUT_A OUT_D
  TAG1 TAG2 ...` then consistent_repair (AZ geometry) -> build_ops OPS_OUT=... -> open_proj/apply_ops/run_drc/export.
- Width reference for the later width pass (research notes): VBUS <=0.5 A -> >=0.3 mm outer; VSYS / VBAT_CELL ~1 A on
  battery -> 0.4-0.5 mm, >=2 vias per layer change; LX 0.8-1.0 A peak -> ~0.4 mm; 3V3_DIG 0.6 A -> ~0.3 mm; inner
  0.5 oz ~2x.

## State at 16:50 (27 Sep)
- User-approved MCU pin swaps (schematic MCU_sheet + PCB pads + hardware/03_mainboard_schematic.md, each verified):
  ADC_EMG5 PA4(29, ADC1_IN9) -> PC4(33, ADC1_IN13) [commit 715f580, pinswap_T.pas; R_SPI_SCK nudged -0.06 y];
  Wi-Fi UART USART1 PA9/PA10(68/69) -> PB6/PB7(92/93) [commit 506d6d4, uartswap_T.pas].
- C2 = state AY, committed 506d6d4 (pushed): **11 unrouted** (GND C_DRL_DEC-2, GND CU_14-1, 3V0_ANA U1-4, NetINA4_3,
  NetLED_CHG_C, VOUT_2, Vc_1, WIFI_SPI_CS, WIFI_UART_RX, MCU_WIFI_UART_TX, MCU_WIFI_UART_RX); copper clean.
  PLANS include REP_AU_ADDS_OK. rip_attached.py accepts REF.PIN.
- Running: REP_AV on AY (region around ST67 pins + passes, UART nets first), log tmp/rep_av.log.
- Corner x 51-56 / y 19-22 (channel 4 meets MCU bottom): NetINA4_3 blocked by 3V0_ANA group R56 (L5 feed to a pad near
  52.2,20.5) and GND CU_14-1 there -> needs a small part nudge (CU_14) next.
- Memory: user closed Edge and WeChat; laptop is Lenovo V14 G3 IAP (8 GB soldered + empty SO-DIMM slot -> 8 GB DDR4-3200
  SO-DIMM gives 16 GB dual-channel; answered in chat).

## State at 15:30 (27 Sep)
- C2 = state AV, committed ef917d8 (pushed): **11 unrouted** (GND C_DRL_DEC-2, GND CU_14-1, 3V0_ANA U1-4, NetINA4_3,
  NetLED_CHG_C, VOUT_2, ADC_EMG5, Vc_1, WIFI_UART_RX, WIFI_SPI_CS, MCU_WIFI_UART_TX); copper clean; JLC geometry clean.
  PLANS include REP_AS_ADDS_OK. Edge + background apps closed by the user's request (2.6 GB free without Altium).
- Running: REP_AT on AV (regions WIFI_UART_RX, ch4 big box, CU_14, U1-right + 2 passes, MAXV 14, CORRIDOR 1.5),
  log tmp/rep_at.log.

## State at 14:05 (27 Sep)
- User (14:0x): "yes restart and relocate C_BAT, edge is closed" -> routing restarts approved.
- C2 = state AU, committed f1d564c (pushed): C_BAT -> (14.25,44.20,90), R_EN1_BIAS -> (12.95,42.25,0); UP1 pins 6/7
  escapes hand-routed (evidence/UP1_ESCAPE_PLAN.csv, deliberately NOT in run_repair.PLANS so it stays fixed copper).
  21 unrouted = 17 real + 4 opened by the move (VBAT_CELL x2, C_BAT GND, R_EN1_BIAS VSYS).
- Running: REP_AS on AU (regions ch4, U1-right, VOUT_2, ADC_EMG5 + 2 passes), log tmp/rep_as.log.

## State at 13:20 (27 Sep)
- REP_AR was KILLED by the system for low memory (2nd time) - it had no gains yet (UP1 + ch4 regions rejected).
  Harness rule: do not restart killed jobs without the user's go-ahead -> asked the user. Edge uses ~0.6 GB; the user can
  also start Claude Code with CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1.
- UP1 pins 6/7 (EN1_BIAS + USB_PGOOD_N) hand escape attempted (R_EN1_BIAS moved to (14.22,44.55) rot 270, plan
  evidence/UP1_ESCAPE_PLAN.csv): FAILS by 0.03-0.07 mm - SH3 is a rectangle (corner 13.30,43.22) and C_BAT pad 2
  (x >= 14.18 up to y 42.73) pinch the two escapes. Board file RESTORED to 9bbd96c (git checkout of the PcbDoc).
  Real fix needs C_BAT relocated (or a 0.4/0.2 via = JLC extra cost -> rejected).
- Board on disk = state AQ = commit 9bbd96c, 18 unrouted.

## State at 12:50 (27 Sep)
- C2 = state AQ, committed 9bbd96c (pushed): 18 unrouted = REP_AQ +4 then 5 links opened on purpose by the JLC fixes
  (UP1-8 GND, C_MCU_BULK GND + 3V3_DIG, J_FPC1 pin-7 GND, MCU_SWCLK). JLC geometry clean: edge 0.5, pad-hole >= 0.45,
  via-to-track >= 0.2 (geom.required gives vias 0.2 even in BK13 zones; geom.hole_gap 0.45 for pad holes).
- Running: REP_AR on AQ (plane mode, taller UP1 box incl. R_EN1_BIAS, ch4, U1-right, VOUT_2, ADC_EMG5), log tmp/rep_ar.log.
- Do NOT prune the DRL_SUM antenna (26.475,14.775-15.575): part of the open DRL_SUM link.
- After each write: run fab_check.py (JLC) as well as DRC.

## Plan agreed with the user (13:xx 27 Sep) - do in this order after the current round is written
1. Write REP_AQ (+2 so far) together with: C_MCU_BULK (67.83,43.90,90) -> (67.55,43.60,90) (was 0.169 mm from the board
   corner, JLC >= 0.2; rip RIP_CBULK.csv incl. its stitch via) and removal of the S0:GND stitch via (15.4865,42.7668)
   (0.336 mm hole-to-hole to the USB-C NPTH peg, JLC pad holes >= 0.45) -> plane mode re-stitches UP1-8 / C_MCU_BULK-2.
   Tools now enforce JLC pad-hole spacing 0.45 (geom.hole_gap / router pad-hole growth); fab_check.py = JLC audit.
2. Width strategy (user): FIRST size nets that must be wide (VBUS / VBAT_CELL / VSYS charger path ~1 A, 3V3_DIG MCU+WiFi,
   3V0_ANA feeds, GND stubs) from real currents (IPC, 1 oz outer / 0.5 oz inner), wide trunks + neck-down only in the last
   <= 1 mm at fine-pitch pins; THEN thin digital/control signals 0.15 -> 0.10 mm (JLC standard 0.09). Analog EMG widths and
   all clearances (0.2 / 0.25) unchanged. Apply as Altium width rules per class, then gloss/straighten with the new widths.
3. Gloss pass (gloss.py written, not run yet) -> before/after renders -> DRC.
4. Remaining unrouted with the freed space; UP1 pins 6/7: taller region incl. R_EN1_BIAS copper (0.4 mm vias dropped:
   JLC charges extra for 0.2 holes < 0.45 dia).
5. Final JLC standard-price audit (fab_check + mask dams + drill/annular + order options); via-style rule 0.6/0.3 vs
   123 x 0.45/0.2 vias -> user decision to widen the rule.

## State at 12:40 (27 Sep)
- REP_AP (on AN) was KILLED by the system for low memory (not a tool failure) before writing its outputs; it had found
  +3 (D_CC_ESD region, C_DRL_DEC region, Va_1 repair) - lost. Board unchanged = state AN = commit 4c5a2b6, 17 unrouted.
  Rule from the harness: do not restart killed jobs without the user's go-ahead.
- repair.py now checkpoints ADDS/DELS after every accepted gain (save_outputs) -> a killed run keeps its progress
  (consistent_repair + write can use the partial files).
- Also new: plane routing starts on any layer of the island (vias) and searches around the whole small island (J_FPC1
  pin-7 GND via sits in the dead L2/L4 pour strip -> can now reach the main plane via L3 between the corner TH pads);
  SMALL_VIA_NETS prefer 0.4/0.2 vias for UP1 pins 6/7.
- User (12:3x) asked why traces are not "professional" (straight, clean 45 deg, into pads, via when needed). Plan agreed
  in chat: after the next write, build a straightening/gloss pass (fewest octilinear segments, straight pad entries,
  remove needless vias; every change exact-checked; before/after renders; Altium DRC) and run it on all router copper.

## State at 11:10 (27 Sep)
- C2 = state AN, committed 4c5a2b6 (pushed): **17 unrouted** (4 GND, 1 3V0_ANA, 12 signals). PLANS incl. REP_AO_ADDS_OK.
- FINDING for the final report (needs user decision): via-style rule VIA_STD_060_030 is min = max = 0.6/0.3 mm, but the
  board has 123 vias 0.45/0.2 and 5 vias 0.5/0.3 (router secondary size); batch DRC does not test Routing Via Style so
  they never showed. JLC 6-layer can make them. Options: widen the rule to 0.45-0.6 / 0.2-0.3, or rework (not possible in
  the dense areas).
- router5: SMALL_VIA_NETS env allows 0.4/0.2 vias for named nets only (UP1 pins 6/7: USB_PGOOD_N, NetR_EN1_BIAS_2).
- Running: REP_AP on AN = 9 regions (UP1 top, D_CC_ESD, ch4, C_DRL_DEC, CU_14, R_ADC2/VOUT_2, ADC_EMG5, U1 right, Va_1)
  + 2 passes, log tmp/rep_ap.log.

## State at 10:00 (27 Sep)
- Last commit 0601824 = state AL: **18 unrouted** (pushed).
- On disk (not committed): TP_VREF_B_SRC free pad moved (12.5,20.2) -> (11.4,22.95) (PMOVE, OPS_TPVB_MOVE.txt; legal by
  chk_tp.py), its attached Top copper ripped (RIP_TPVB.csv) -> state AM 21 (+3 VREF_B_SRC). Goal: free U1-11 GND via site
  and the VREF_B_SRC path that also blocks C_DRL_DEC-2 GND.
- Running: REP_AO on AM (VREF_B_SRC first; regions U1-left + C_DRL_DEC), log tmp/rep_ao.log. If it ends above 18,
  restore 0601824's PcbDoc (git checkout 0601824 -- <PcbDoc>) and try differently.
- Next idea for UP1 pins 6/7 (EN1_BIAS + USB_PGOOD_N): 0.4/0.2 vias fit in the C_BAT pad gap - EN1_BIAS via
  (13.39,41.80), PGOOD straight up x=13.9 to via (13.65,42.95); DRC decides whether 0.4 mm passes the via-style rule.
- Pour connectivity (L1 GND / L5 3V0_ANA pours) is not modelled: new copper can cut a pad off its pour -> expect 1-2
  surprise links per round.

## State at 08:45 (27 Sep)
- User (08:1x): "do it and solve the unrouted and complete it" -> keep going to zero.
- Last commit 261e3b1 = state AI (19). On disk now (not committed): state AK = REP_AM written (ch2 NetINA2_3 closed by
  region, +1 -> 18) then an antenna prune that over-deleted a live VOUT_2 chain (prune_from_antennae misses a via
  contact) -> 19. ALWAYS DRC-verify a prune; VOUT_2 corridor (via 32.425,17.875 -> via 47.025,22.225) is free again.
- repair.py region_pass: retries with lost groups routed first (REORDER); GND/3V0_ANA victims only need plane access
  (reconnect gives each island a via) -> ch2 region accepted on try 1.
- Running: REP_AN on AK = 9 focused regions (ch4, DRL corner x4, MCU x2, charger x2) + 2 passes, log tmp/rep_an.log.
  PLANS include REP_AM_ADDS_OK.

## State at 07:45 (27 Sep)
- C2 = state AI, committed 261e3b1 (pushed): **19 unrouted** (6 GND, 1 3V0_ANA, 12 signals), copper clean.
  PLANS include REP_AJ_ADDS_OK. Offline prediction = Altium count for the last 4 rounds.
- repair.py: victim clusters + exact-checked reconnects (safe margin, then min width).
- Running: REP_AK = regions ch2 (29.0,15.0-36.5,18.9) and ch4 (50.6,15.0-58.1,18.9) + 1 pass; log tmp/rep_ak.log.
  Evidence: with the ch2 window's routed copper removed (scratch GEOMETRY_C2_6L_CH2TEST.txt), NetINA2_3 routes cleanly
  on Top -> not a placement block, only a re-route problem.
- Remaining after that: GND x6 (C_DRL_DEC-2, CU_14-1, D_CC_ESD-3, INA1-4, U1-11, J_FPC1 pin-7 pour fragment),
  3V0_ANA U1-4, USB_PGOOD_N x2, ADC_EMG5, VOUT_2, DRL_LIMITED, Vc_1, ST67 SPI/UART x4.

## State at 06:55 (27 Sep)
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
# Astra update — 27 September 2026, state BB

Authoritative saved PCB remains `C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc` in branch `pcb-routing-0925`.

- Applied `ASTRA_REP_BA1_ADDS_OK.csv` / `_DELS_OK.csv` after exact clearance check: 47 additions, 26 deletions, zero precheck problems. This restores the GND and VREF_A connections left open after MERGE_I.
- Native save/reopen: `ASTRA_APPLY_BB.txt`. Fresh DRC: `DRC_C2_6L_BB.txt.html` / `.json`: **6 unrouted, 6 antennae, 159 silk/mask, 84 silk/silk, 5 outline violations**. No reported shorts, copper-clearance, width or component-clearance violations. Batch Via Style is NOT enabled yet; do not call the full rule set clean.
- Remaining nets: NetINA4_3, Vc_1, WIFI_SPI_CS, WIFI_UART_RX, MCU_WIFI_UART_TX, MCU_WIFI_UART_RX.
- `ASTRA_BB_DELTA.json`: PASS; actual 2,208 free tracks and 453 vias, all requested copper changes matched, exported pads/component geometry preserved.
- `ASTRA_BB_STRUCTURE.json`: rules/nets/components/stack/outline invariant checks pass. Whole protected-stream byte comparison fails on native model/pad/text serialization streams, as in BA. Retain this limitation; do not relabel it an unconditional byte-preservation PASS.
- Backup before BB: `ASTRA_BB_BEFORE_20260927/`. Original AZ backup: `ASTRA_BA_20260927/`.
- Native clean-close check `ASTRA_CLEAN_CLOSE_BB.txt`: all documents saved, `UNSAVED_COUNT=0`. Task-owned Altium PID7056 closed normally before the next heavy router.
- Running next: single `ASTRA_NEG_BB1` channel-4 routing search, seed23/margin0.01, at most40 iterations; output only, PCB unchanged until checked/applied. Logs under `evidence/routing_logs/`.
- User requested JLC minimum verification for existing via sizes. Current JLC capability page confirms preferred0.20mm hole, diameter>=0.45mm avoids its stated small-via surcharge category. Plan: align saved via minimums to0.45/0.20mm, keep preferred/max0.60/0.30mm and existing clearances. Script prepared but not yet executed. See `ASTRA_VIA_RULE_REVIEW.md`; no verified native batch-selection setter is established yet.
