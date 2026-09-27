# Handoff to Astra — C2 6-layer EMG main board: finish the routing (27 Sep 2026, 21:xx)

## 0. Prompt for Astra (read this first)

> You are taking over the C2 compact EMG main board routing job from Claude. Work ONLY in the git worktree
> `C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925` on branch `pcb-routing-0925`.
> Read, in order: this file, then `evidence/ROUTING_RESUME.md` (same folder), then the repo's `CLAUDE.md`,
> `HANDOFF.md`, `PROJECT_CONTEXT.md`, `QUALITY_BAR.md`.
> Goal: route the last unrouted connections of `C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc`
> (Altium AD22, 6 layers) with the design rules unchanged, copper DRC clean, JLCPCB-standard geometry; then the
> width pass, the gloss (straight/45°) pass, the JLC audit, docs, commit + push. Step 1 is section 4 below: write the
> ready batch MERGE_I (9 -> 6 unrouted). Run ONE heavy process at a time (8 GB laptop; the user asked for this).
> Never push to main, never force-push/merge, no fabrication approval (R2), no Altium GUI keystroke automation.

## 1. Paths

| What | Path (relative to the worktree root) |
|---|---|
| Board (the ONLY CAD file to edit) | `hardware/compact_mainboard_20260925T115919Z/C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc` |
| Project | same folder, `EMG_MainBoard_Layout.PrjPcb` (schematic `MCU_sheet.SchDoc` etc. next to it) |
| Tools (run everything from here) | `hardware/compact_mainboard_20260925T115919Z/work/` |
| Evidence (states, plans, DRC, logs) | `hardware/compact_mainboard_20260925T115919Z/evidence/` |
| Running notes (keep current) | `evidence/ROUTING_RESUME.md` |
| Pin map doc (updated for the pin swaps) | `hardware/03_mainboard_schematic.md` |
| Research used for widths / layout rules | `research_notes/EMG main board routing requirements/`, `reports/EMG main board routing requirements.md` |

Do NOT modify: `hardware/pcb_layout_2026-09-23_drl`, `hardware/pcb_layout_2026-09-16`, V2.0/DEB/flex folders,
`Downloads\EMG_V2_FINAL_REVIEW`, `.claude/settings.local.json`. The file
`hardware/pcb_layout_2026-09-24_routing/MainBoard/EMG_MainBoard_Layout.PcbDoc` shows as modified in git but was not
changed by this job — leave it out of commits.

## 2. Board facts (locked)

- 6 layers, JLC06121H-3313, 1.2 mm: L1 Top | L2 GND | L3 signal (Mid Layer 2) | L4 GND | L5 power/signal + 3V0_ANA pour
  (Mid Layer 4) | L6 Bottom (GND pour).
- Rules kept as designed (user: "keep rules, nudge parts"): 0.2 mm default clearance, 0.25 mm for analog/power
  (WIDE) classes, 0.13 mm only inside the BK13 socket escape zones (vias there still 0.2), fine-pitch 0.15.
- JLC standard (no extra cost): track/space 0.09, via 0.45/0.2 (0.2 hole needs >= 0.45 dia), via-to-track 0.2,
  hole-hole 0.2 (vias) / 0.45 (pad holes), edge 0.2, via-in-pad free on 6L. 0.4 mm vias were dropped (extra cost).
- User-approved pin swaps (done, in schematic + PCB + 03_mainboard_schematic.md): ADC_EMG5 PA4 -> PC4 (ADC1_IN13,
  LQFP pin 33); Wi-Fi UART USART1 PA9/PA10 -> PB6/PB7 (pins 92/93, AF7). Firmware must follow (ADC scan IN5-8 + IN13).
- C_BAT relocated, R_SPI_SCK nudged -0.06 y, earlier nudges listed in ROUTING_RESUME.md.

## 3. Where we are right now

- **In Altium (saved): state AZ = 9 unrouted**, copper DRC clean, 1 Net Antennae (dead VREF_A stub).
  Evidence: `DRC_C2_6L_AZ.json`, `GEOMETRY_C2_6L_AZ.txt`. Last commit on the branch is 506d6d4 (state AY, 11 unrouted);
  state AZ + all tool changes are committed together with this handoff (see git log).
- **Ready, not yet written: `MERGE_I_ADDS_OK.csv` / `MERGE_I_DELS_OK.csv`** (183 add / 134 delete rows, exact check
  0 problems) = NetLED_CHG_C (REP_FC3) + GND CU_14-1 (REP_FA) + 3V0_ANA U1-4 (NEG_C9) + prune of the dead VREF_A stub
  (PRUNE_AZ). Writing it gives **6 unrouted**.
- **The 6 still open (after MERGE_I):**
  1. `NetINA4_3` (channel-4 in-amp IN+: INA4-3 (51.43,15.85) -> RDD10-2/RDD12-2 node at x 57.2). Must cross Vc_4
     (socket -> RDD12-1) in a saturated corner. Seeded negotiation got within 0.001 mm (VOUT_4 vs fixed Vservo_4
     0.249 < 0.25); a 4-try seed sweep was stopped after tries 0 and 1 (no convergence). Since then a fixed-copper
     margin (NEG_FIX_MARGIN 0.035) + near-miss handling was added — re-run the sweep (section 5).
  2. `Vc_1` (channel-1 electrode Vc: socket escape via (15.9,11.2) -> RDD3 via (24.18,19.33)). The escape via is
     sealed (J_REF snap pad copper, J_FPC1 3V0_ANA socket via (15.95,12.55), socket keep-out incl. L3, NetJ_REF_1 L3
     track). With socket vias rippable an all-L3 path exists; the J_FPC1 3V0 via must move.
  3. `WIFI_UART_RX` (U_WIFI1-23 -> via 43.53,40.08), 4. `MCU_WIFI_UART_TX`, 5. `MCU_WIFI_UART_RX` (link resistors under
     the ST67 -> MCU pins 92/93): crowded MCU top-left fan-out (I2C, BOOT, SYS_EN, 3V3_DIG, VSYS).
  6. `WIFI_SPI_CS` (R_SPI_CS-1 at 58.5,25.5 under the MCU -> ST67 side 45.8,43.9): ~22 mm across the MCU fan-out.
     Fallback needs the USER's OK: move CS (software NSS, any GPIO) to a free MCU pin next to the ST67 + move
     R_SPI_CS there (same kind of change as the approved UART swap).

## 4. Next step: write MERGE_I -> state BA (one process at a time)

From `work/` (Git Bash for python, PowerShell for Altium):
```
OPS_OUT=OPS_BA.txt VIP=1 BK13_ZONES=../evidence/BK13_ZONES_C2.csv L5_RESERVED="3V0_ANA:10.5,10.5,68.6,25.3;3V0_ANA:10.5,25.3,47.5,27.2;3V0_ANA:31.6,27.2,35.8,30.4" GEOM_FILE=../evidence/GEOMETRY_C2_6L_AZ.txt BOARD_BOX=12,12,67.1,44 python build_ops.py ../evidence/MERGE_I_ADDS_OK.csv --del ../evidence/MERGE_I_DELS_OK.csv
python mkvariant.py open_proj_T.pas opb C2 OPEN_PROJ_C2_6L_BA_LOG.txt
OPS_FILE=OPS_BA.txt python mkvariant.py apply_ops_T.pas apb C2 APPLY_BA_LOG.txt
python mkvariant.py run_drc_T.pas dba C2 DRC_C2_6L_BA.txt
python mkvariant.py export_geometry_T.pas gba C2 GEOMETRY_C2_6L_BA.txt
```
Each mkvariant prints the real script name (e.g. `opb_2130xx.PrjScr`) — use THAT name. PowerShell:
```
Start-Process -FilePath 'C:/Program Files/Altium/AD22/X2.EXE' -WindowStyle Normal   # wait until the window title shows "Altium Designer"
.\run_wait.ps1 -Script <opb_...>.PrjScr -Result OPEN_PROJ_C2_6L_BA_LOG.txt -TimeoutSec 400
.\run_wait.ps1 -Script <apb_...>.PrjScr -Result APPLY_BA_LOG.txt -TimeoutSec 500     # expect PHASE1_OK, SAVED
.\run_wait.ps1 -Script <dba_...>.PrjScr -Result DRC_C2_6L_BA.txt -TimeoutSec 500
.\run_wait.ps1 -Script <gba_...>.PrjScr -Result GEOMETRY_C2_6L_BA.txt -TimeoutSec 400
```
Then `python parse_drc.py ../evidence/DRC_C2_6L_BA.txt.html ../evidence/DRC_C2_6L_BA.json` and
`python unrouted_summary.py DRC_C2_6L_BA.json` -> expect 6 unrouted, no clearance/short rows, no antenna.
JLC check: `GEOM_FILE=../evidence/GEOMETRY_C2_6L_BA.txt BOARD_BOX=12,12,67.1,44 python fab_check.py`.
Before closing Altium: re-run open_proj (it reports `PCB_OPEN|MODIFIED=`) and close only when MODIFIED=False
(`Get-Process X2 | Stop-Process -Force` is how it was closed after a verified save). Then add `'MERGE_I_ADDS_OK'` to
`PLANS` in `work/run_repair.py` (so the new copper is rippable in later rounds) and use state `BA` from then on.

## 5. How the remaining 6 were being attacked (and the commands)

Everything goes through `run_repair.py STATE TAG KEY=VALUE...` (it sets the standard router env and the PLANS list).
One run at a time. Logs: redirect to a file and grep `it [0-9]+:|NEGOTIATE|conflict|exact`.

- **NetINA4_3** (seed sweep, sequential, stops at first success; winner copied to `evidence/NEG_B9_ADDS/DELS.csv`):
  ```
  python neg_sweep.py BA NEG_B9 "23:0.01,5:0.02,7:0.0,11:0.01" PLANE=1 DEBUG=1 PASSES=0 NEG_SEED=1 NEG_HOLD=8 ALLOW_BOTTOM="NetINA4_3,NetINA4_2" ONLY_NETS="NetINA4_3" NEGOTIATE="49.6,13.9,59.2,20.6" NEG_ITER=40
  ```
  If it keeps failing: widen the box a little, or ask the user about a small part nudge in the ch4 resistor column
  (RDD10/RDD11/RDD12) or rotating RDD12 so the DDp node faces INA4.
- **Vc_1** (only the J_FPC1 3V0_ANA socket via may move):
  ```
  python run_repair.py BA NEG_D3 PLANE=1 DEBUG=1 PASSES=0 NEG_SEED=1 NEG_HOLD=8 NEG_MARGIN=0.0 RIP_BK13=1 RIP_BK13_ONLY=J_FPC1:3V0_ANA EXTRA_PLANS=BK13_ESCAPE_PLAN_C2 ONLY_NETS="Vc_1" NEGOTIATE="14.6,10.6,24.8,19.8" NEG_ITER=40
  ```
- **Wi-Fi UART x3** (one box around the ST67 / MCU top-left):
  ```
  python run_repair.py BA NEG_W1 PLANE=1 DEBUG=1 PASSES=0 NEG_SEED=1 NEG_HOLD=8 NEG_MARGIN=0.0 ONLY_NETS="WIFI_UART_RX,MCU_WIFI_UART_RX,MCU_WIFI_UART_TX" NEGOTIATE="41.0,39.2,57.2,44.6" NEG_ITER=40
  ```
- **WIFI_SPI_CS**: try the sequential repair first
  (`python run_repair.py BA REP_W2 PLANE=1 DEBUG=1 PASSES=2 MAXV=14 REORDER=10 GUIDED=2.0 CASCADE=26 PARTIAL=0.35 ONLY_NETS=WIFI_SPI_CS`),
  otherwise ask the user about the CS pin move (section 3, item 6).
- **Merging results** (several wins computed on the same state): `python merge_rounds.py OUT_ADDS OUT_DELS TAG1 TAG2 ...`
  (priority order, ids renamed) -> `consistent_repair.py` on that state's geometry -> build_ops -> write (section 4).
  Two parallel wins can collide (both re-route a victim into the same gap): the exact check drops them; write the
  compatible subset, redo the rest on the new state.
- Useful diagnostics: `DIAG_FIXED=<box>` (does a path exist against fixed copper only? which groups block it?),
  `render_window.py OUT.png "x0,y0,x1,y1" DRC.json` (x-ray picture with unrouted lines),
  `prune_chain.py OUT_DEL.csv NET X Y` (delete a dead antenna chain up to its first real junction).

## 6. What was done today and WHY (short)

1. **Parallel repair rounds** per board area (user: "solve the unrouted in parallel") with `ONLY_BOX`/`ONLY_NETS`
   and `merge_rounds.py`. Worked, but wins on one base collide -> merge, write the compatible subset, redo the rest.
   The user later asked for ONE process at a time (usage limit / 8 GB RAM) — keep it that way.
2. **Diagnosis first** (`DIAG_FIXED`): route against fixed copper only -> tells "rip-up problem" (list of blockers)
   from "placement/pin problem" (no path).
3. **Guided victims** (`GUIDED`) = exactly the groups the fixed-copper path hits; **cascade** (`CASCADE`) = a victim
   that cannot re-route pulls in its own blockers (measured with the target in place); reverse cascade.
4. **Bugs found and fixed in the repair tool** (they caused many earlier "no path"s): piecewise rollback leaked
   (one net id per raster cell, holes re-stamped from circles) -> exact `snap()/restore()` rollbacks; ripped via holes
   stayed in the hole raster; a failing victim route was returned as success (`STRICT_VICTIMS`); guided victim tolerance
   too tight (now verified by re-routing with only the victims ripped).
5. **Partial rip-up** (`PARTIAL`): rip only the part of a victim near the new path (the USB CC1 escape at the
   connector could not be redone whole) -> this solved NetLED_CHG_C.
6. **Socket escapes** (`RIP_BK13`, `RIP_BK13_ONLY`): only escape VIAS (+stub) may move; in-socket tracks use the
   0.13 mm zone clearance the router cannot reproduce.
7. **Plane nets**: an island without a legal via site may join any other same-net touch point / plane-connected copper.
8. **Negotiated congestion routing** (`NEGOTIATE=<box>`, PathFinder): all nets of a dense box re-routed together,
   other nets' copper allowed but priced; exact penalty zones (distance transforms), own copper excluded, history,
   capped price. **Seeded mode** (`NEG_SEED=1`): victims start at their original copper, only conflicting ones move,
   `NEG_HOLD` passes let the new connection adapt first -> this solved 3V0_ANA U1-4 with 12 of 13 pieces untouched.
   The exact model is the judge (raster may keep a 1-cell conflict); near misses widen that task's zone / that net's
   fixed-copper margin (`NEG_FIX_MARGIN`, default 0.035). Minimum widths inside dense boxes (0.25 for VSYS/VBUS/VBAT/
   3V3_DIG) — the width pass widens later where there is room.
9. **Policy override** `ALLOW_BOTTOM=<nets>`: Bottom is normally only for nets with a Bottom pad; NetINA4_3/NetINA4_2
   were stuck on L1/L3 (L5 is reserved for the 3V0_ANA pour there). Bottom here has a GND pour next to the quiet
   3V0_ANA plane — electrically fine for a short hop; mention it to the user.

Win history: 11 (AY) -> 9 written (AZ: VOUT_2, GND C_DRL_DEC-2) -> 6 ready (MERGE_I: LED, GND CU_14, 3V0_ANA U1-4).

## 7. After the routing is complete (agreed with the user)

1. Width pass (user strategy: wide where current flows, neck down only at pins; thin digital/control to 0.10 mm,
   clearances unchanged). Targets: VBUS <= 0.5 A -> >= 0.3 mm outer; VSYS / VBAT_CELL ~1 A -> 0.4-0.5 mm and >= 2 vias
   per layer change; buck-boost LX 0.8-1.0 A peak -> ~0.4 mm; 3V3_DIG 0.6 A -> ~0.3 mm; inner layers ~2x.
2. Gloss / straighten pass (`work/gloss.py`, octilinear string pulling) with before/after renders + DRC — the user
   asked for professional-looking traces: straight runs, 45° corners, straight pad entries.
3. Final JLC standard-price audit (fab_check + mask dams + drills/annular + order options). OPEN USER DECISION: the
   via-style rule VIA_STD_060_030 (0.6/0.3 only) vs the 0.45/0.2 vias used (JLC standard) -> widen the rule to
   0.45-0.6 / 0.2-0.3.
4. Silkscreen cleanup (84 silk-silk, 159 silk-mask, 5 outline), STACK=6 audit, docs (C2_COMPACT_AUDIT.md,
   NEXT_AGENT_CHECKPOINT.md), `.\scripts\refresh.ps1` (graph + agent map, QUALITY_BAR HG8), commit + push.
5. Open items to list for the user: button ESD, flex width, battery/enclosure, fab notes (POFV, JLC06121H-3313),
   stale EMG_Service_C2.PcbLib, firmware pin changes (ADC IN13, USART1 PB6/PB7), no fabrication approval (R2).

## 8. Rules of engagement (from the user / project)

- Nothing final without Daniyal's approval; ask before schematic changes (pin moves), part moves beyond small legal
  nudges, rule changes.
- One agent writes CAD at a time; check MODIFIED before closing Altium; restart Altium if a script hangs (save, close,
  reopen — allowed without asking).
- One heavy process at a time; close Altium while routing processes run (8 GB RAM).
- Commit trailer lines used on this branch: `Co-Authored-By: ...` and the session link (see earlier commits).
