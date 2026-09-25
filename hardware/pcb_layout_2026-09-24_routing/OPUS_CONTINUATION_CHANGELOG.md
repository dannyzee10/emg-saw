# Opus continuation changelog — routing revision

Working revision: `hardware/pcb_layout_2026-09-24_routing/` (copied from the saved/reopened placement
checkpoint `hardware/pcb_layout_2026-09-23_drl/`, variant `PROTO_1_REMOTE_NTC`, DNP DRL provision kept per
user decision 24 Sep). The drl revision, the 16 Sep layout, the verified baseline and the user's electrode
boards are read-only for this work.

## 24 Sep 2026

| Time | Block | Result |
|---|---|---|
| 17:0x | Placement checkpoint closure in drl revision (Astra's guarded save/reopen script, user-approved) | `PCB_SAVE_REOPEN.txt` COMPLETE: 231 components / 808 pads / 15 free / 136 nets identical before and after |
| 17:1x | Routing revision created; start manifest `evidence/ROUTING_START_MANIFEST.csv` | copy of saved checkpoint |
| 17:2x | Read-only native probe + geometry export | 259 net/annotation tracks, 48 GND vias, 2 GND polygons (L2, L4), 570 connection lines |
| 18:41 | Unsaved GUI edit of NetINA1_7 found in routing copy; user chose **discard** | closed without save; reopened geometry identical to disk (0 diff), file hash unchanged |
| 19:25 | Batch 1: 5 BK13 socket escapes, GND fanout (126 vias), 6 fine-pitch escape rules, routing-layer rules (L2 never; L4 only for bottom-pad nets), routing-pass widths | readback PASS (+275 tracks, +126 vias, pads/components unchanged) |
| 20:17 | Batch 2: BK13 escapes v2 (0.13 mm keepout-clearance correct), U_WIFI1-32 via moved off antenna keepout | readback PASS (166 tracks replaced, 1 via moved) |
| 20:33 | Batch 3: solder-mask rule SMX_VIA_TENTED (IsVia, -0.35 mm): tents all vias (native via tenting setters proved non-persistent on a disposable copy) | DRC: 344 unrouted, 10 net antennae, 1 inherited silk-to-mask; 0 clearance/short/sliver |
| 20:40–21:27 | Situs autorouter trial (Route All, pre-routes locked) | **rejected, not saved**: 29 real track shorts (incl. 3V3_DIG–VSYS, CC1–CC2, 3V0_ANA–Vservo_4), 62 clearance, 75 unrouted, all SPI unrouted, analog detours up to 3x. Board reverted; geometry identical to batch-3 state (0 diff). Evidence: `evidence/DRC_SITUS1*.json`, `evidence/ROUTE_QUALITY_SITUS1.csv` |

## 25 Sep 2026 (resumed; this copy lives in worktree `.claude/worktrees/pcb-routing-0925`, branch `pcb-routing-0925`)

| Time | Block | Result |
|---|---|---|
| 15:0x | Revision copied into a git worktree (background-job isolation); Altium switched to the worktree project | reopened inside its project: MODIFIED=False; geometry identical to batch-3 (0 diff) |
| 15:1x–17:15 | Full-board router runs (router4, then array-A* + resume); two runs stopped by low system memory; a forked session briefly wrote the same output files and stood down | pass-1 partial plan recovered clean: 210 connections |
| 17:16 | Batch ROUTE_A: 803 tracks + 114 vias (208 connections), exact-checked (2 groups dropped), topology audit G1/R1/P2/M2 = 0 | readback PASS; DRC 136 unrouted, 0 clearance/short |
| 17:2x | router5 (component-to-component targets, scoped 0.2 mm fallback, bounded failures) prepared; resume run stopped by low memory | not written |
| 18:57 | **User switched to R2 (compact two-sided candidate); routing of this 80 x 45 board PAUSED** | see `hardware/compact_mainboard_20260925T115919Z/` |

## Method

All CAD writes go through native DelphiScript run inside the open Altium AD22 (22.5.1)
(`work/apply_ops.pas`: phase-1 validation of every op, then one transaction, GND polygon rebuild, save,
close, reopen, readback). Plans are computed offline from the native geometry export and pre-verified
against true pad copper and the saved clearance-rule priorities (`work/geom.py`, `work/build_ops.py`).
Altium DRC (`work/run_drc.pas`, batch HTML) is the authority after each block.
