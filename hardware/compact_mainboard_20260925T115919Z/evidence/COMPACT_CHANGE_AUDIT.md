# Compact two-sided main board — change audit (R2)

**Status: COMPACT TWO-SIDED PLACEMENT READY FOR REVIEW — ROUTING/MECHANICAL QUALIFICATION STILL OPEN**

Candidate B is a native Altium AD22 placement checkpoint. It is 75 × 40 mm, uses 4 copper layers, and has parts on both sides. The first target was 70 × 40 mm. It was not reached, and the limiting objects are listed below. No fabrication, ordering, RF, charging-safety or body-use approval follows from this document.

## 1. Source recovery and protection

| Item | Path | Identity |
|---|---|---|
| Recovered source (latest integrated 231-part placement checkpoint, saved and reopened 24 Sep, DNP DRL provision kept per user decision) | `hardware/pcb_layout_2026-09-23_drl/MainBoard/` (main checkout, untouched) | PcbDoc SHA-256 `4AF4DDE3…ECBF015`. The 24 Sep checkpoint closure recorded 231 components, 808 pads, 15 free pads and 136 nets. |
| Baseline A (read-only snapshot) | `A_BASELINE_READONLY/MainBoard/` | 75 files, all hash-identical to the source (`A_SNAPSHOT_MANIFEST.csv`). The PcbDoc is still `4AF4DDE3…` at the end of this work. |
| Candidate B | `B_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PrjPcb`, variant **PROTO_1_REMOTE_NTC** | Final PcbDoc `BF906AE6…E33B16`. The PrjPcb had its single absolute print-config path repointed from the drl revision to B itself; no drl references remain. |
| Other boards | V2.0, DEB, flex and `Downloads/EMG_V2_FINAL_REVIEW` | Not opened and not modified. |
| Paused 80 × 45 routing work | `hardware/pcb_layout_2026-09-24_routing/` (worktree) | Separate routing trial: 208 connections written, 0 shorts/clearance errors, 136 unrouted. Kept unchanged as a reference. |

User decisions recorded 25 Sep: switch to R2 now and pause full routing. Keep the 231-part checkpoint with the DNP DRL provision. R2 §4 "do not add body-DRL" is read as "do not add any further".

## 2. Native capability proof (disposable copies only)

| Proof | Result | Log |
|---|---|---|
| `FlipComponent` on U_EN1, UP4, R_PGOOD and Q_SHDN (rotations 0/90/180) | Pads mirror in board X about the component's own centre, nets and UIDs are kept, and the result survives save + reopen. Overlay goes Top→Bottom and paste goes Top→Bottom Paste. The 3D body moves Mech 13 → **Mech 23 (Bottom 3D Body)**, courtyard Mech 15 → **21**, and assembly Mech 5 → **20**. The V6 `AllLayers` iterator hides layers 17–32, so exports use no layer filter. | `FLIP_TEST_LOG.txt`, `FLIP_PROBE2_LOG.txt` |
| `MoveByXY` (track, via, keep-out region, mechanical track, pad); polygon reshape; rule-scope edit | All work, including save/reopen. | `API_TEST_LOG.txt`, `APPLY_FP_DRYRUN_LOG.txt` |
| Board outline edit | Works only inside the project, using read-modify-write of each segment. | `OUTLINE_TEST_LOG.txt` |
| Full placement script dry run | All 567 ops resolved; 231/231 components read back exactly. | `APPLY_B_DRYRUN_LOG.txt` |

**Incident.** Two untested API calls (`LayerStack.FirstLayer` on the live board, and `BoardOutline.BeginModify` outside a project) paused Altium's script debugger and froze scripting. Altium was closed without saving and restarted each time, as the user asked. No board file was affected; the B and A hashes were checked each time. From then on, only proven calls were used, and each was proven on a disposable copy first.

## 3. Baseline A measurement

| Metric | Value | Method |
|---|---|---|
| Board shape | 80.0 × 45.0 mm, r = 2 mm corners, 3,596.6 mm² | native `BoardOutline` segments |
| Components | 231: 209 Top, 22 Bottom (DNP DRL provision) | native inventory |
| Top bounding-box occupancy | 2,113 mm², 59 % of the board | component bboxes ∪ pads |
| Installed XY envelope | 82.9 × 49.6 mm | includes USB-C, J_SWD and ST67 antenna overhang |
| Max model height | Top 5.08 mm (six THT 5021 test points), USB-C 3.31 mm, ST67 2.40 mm | 3D body `OverallHeight` as stored |

## 4. What changed in candidate B

- **Outline.** The native Board Shape is now 75 × 40 mm at (10,10)–(85,50) with r = 2 mm corners, 2,996.6 mm², a **16.7 % reduction**. The L2 and L4 GND polygons were reshaped to 10.5–84.5 × 10.5–49.5 and repoured.
- **Five BK13 sockets.** They stay on the long bottom edge at the unchanged 13 mm pitch, translated −2 mm in X as a rigid band with all five AFE channels and the shared references. The mating transform is unchanged.
- **Rigid functional-block moves.** Each block keeps its internal geometry, including the already-routed local tracks:

  | Block | Move (mm) |
  |---|---|
  | AFE band and ADC column | (−2, 0) |
  | MCU | (−2, 0) |
  | ST67 + crystal network | (−3, −5); antenna keep-out moved with it |
  | USB-C + charger cell | (0, −3.6) |
  | TPS631000 cell | (0, −4.25); **hot loop and FB network unchanged**, LX/FB tracks moved with it |
  | TPS7A2030 cell | (−2, −0.8) |

- **22 parts moved to Bottom** (`BOTTOM_MOVE_PLAN.csv`). Whole local circuits only, each group mirrored as a unit:
  - LTC2954 pushbutton controller with its timing/kill/interrupt network and Q_SHDN (10 parts), under the MCU.
  - MAX17048 fuel gauge with its CELL bypass, ALRT and I2C pull-ups (5), below the charger.
  - TPS3808 supervisor with its bypass and SYS_EN pull-up (3), under the charger/LED area.
  - Non-critical pulls: R_PGOOD and R_EN_PD, each under its own IC.
  - DNP C_WIFI_BULK, at the radio supply entry.
  - R_WIFI_BOOT_OVR, beside JP_WIFI_BOOT.

  None of them sits under the AFE inputs, the ADC corner, L1/LX, the UP1 thermal pad or the antenna zone (`views/RENDER_B_xray_projection.png`).
- **Repacked on Top.**
  - Right-edge service band: J_SWD edge header, the six 5021 test points in a 2 × 3 grid, JP_WIFI_BOOT and the UART links.
  - PWR_BTN_N moved into the space freed above the converter.
  - Charge LED beside the charger.
  - J_Li-Po and the remote-NTC pads on the left edge.
  - Four small nudges: C_MCU_VDD5 and R_MCU_BOOT0_PD rotated, C_MCU_BULK and CUP5_5 moved.

  The full ledger of 230 moved parts is in `COMPONENT_MOVE_LEDGER.csv`.
- **15 native free test pads** moved with their groups; TP_GND_PWR was relocated beside J_Li-Po.
- **27 region-scoped clearance rules** were translated with their owning blocks. **Six fine-pitch escape rules** (0.15 mm; U_MCU1, UP1, UP2, UP4, U_DRL1, C_DRL_DEC) and **SMX_VIA_TENTED** (−0.35 mm, all vias tented) were added, in the same form as the 24 Sep routing revision.
- **Free copper.** 138 items moved with their blocks and 2 stale GND items were removed (`COPPER_PLAN.csv`). 136 assembly leader/flex-envelope lines were moved, and 31 leaders of flipped or rotated parts were removed.
- **Execution defect found and fixed.** Five UP1 exposed-pad thermal vias moved twice: Altium carried them with UP1, then the free-via move applied again. The geometry diff caught it; they were moved back into the pad in a documented fix pass (`APPLY_B_FIX_LOG.txt`) and verified.

## 5. Verification (saved state)

| Check | Result |
|---|---|
| Component readback after save/reopen vs plan | 231/231: side, XY within 2 µm, source UID |
| Electrical preservation vs A (pad→net per component, net set, free pads) | **PASS**: 231 components, 791 pads, 136 nets, 15 free pads; exactly 22 changed side |
| Native batch DRC (`DRC_B_CHECKPOINT.*`) | **0 shorts, 0 clearance, 0 component clearance, 0 mask sliver**; 460 unrouted (placement checkpoint); 40 silk-to-mask, 34 silk-to-silk, 1 designator text within 0.5 mm of the edge (open legibility pass) |
| Limited routing trial (R2 stage E) | 37/50 connections routed; 147 tracks and 33 vias written. Exact clearance check: 0 problems. Topology audit: nothing on L2, nothing in the antenna zone, no vias on LX/VCAP. 0.67 mm² of L3 over non-GND L4 (Vc_1 0.45, WIFI_SPI_CS 0.22 mm²) |
| Height per side | Top 5.08 mm (THT test points); Bottom 1.45 mm (U_DRL1), 1.11 mm (Q_SHDN, U_UV1), 1.00 mm (U_EN1). 45 parts have no 3D body (explicit list): all BK13, J_SWD, JP, J_REF, J_Li-Po, PWR_BTN_N, some R_VREF/RDD, the DRL resistors |

**Unrouted in the trial (13), by cause:**
- **Missing scoped escape rules (7):** the six BK13 channel-1 Va/Vb/Vc fanouts need the 0.13 mm BK13 zone rules proven on 24 Sep, and ADC_EMG3 has the same entry squeeze at the MCU pin as the 80 × 45 board.
- **Charger QFN escapes (2):** RISET and TMR at UP1.
- **Long cross-board control lines (4), a direct consequence of placing the LTC2954 group under the MCU:** SYS_EN (≈39 mm), USB_PGOOD_N (≈45 mm), FG_ALRT (≈52 mm) and MCU_SPI_MISO (≈31 mm). These are slow control/status signals, but they occupy the congested middle band.

## 6. Why not 70 × 40 (limiting objects) — candidate C not attempted

- **Top band width.** In the 19 mm band above the AFE, USB-C + charger + converter, the ST67 (mid top edge) and the MCU already use ≈69 of 70 mm.
- **Service parts.** J_SWD is a right-angle through-hole header whose mating pins must overhang an edge. The six 5021 test points and JP_WIFI_BOOT are also through-hole, so their pads occupy the top side wherever their bodies go. They need a ≈5 mm right-edge band beside the MCU and channel 5.
- **R2 constraints.** R2 forbids changing header or test-point contracts without approval, and the BK13 flex/stiffener envelope is still OPEN. Any pitch reduction is unverified.

**Options that could reach 70 × 40, each needing a user decision:**
1. Replace J_SWD, the test points and JP_WIFI_BOOT with a Tag-Connect / SMT pad field. This is a schematic, BOM and service-contract change.
2. Move J_SWD to the top-left edge, which means relocating the button.
3. Tighten the BK13 pitch from 13 mm to ≈12 mm once the real flex and stiffener dimensions exist.

B's margin does not justify a C study now.

## 7. Return-path strategy (R2 §8, option A retained)

- **Layer roles:**
  - L1 carries the parts and critical loops.
  - L2 is the continuous common GND (0 tracks; pour has 29 holes, only through-hole/via antipads).
  - L3 is for power and reviewed corridors.
  - L4 is GND pour plus the Bottom support parts (pour has 73 holes).
- **SPI rule:** the LTC2954 group under the MCU creates L4 voids at x 63.5–76.5, y 38.9–45.1 mm. An **L3 SPI corridor must avoid that area**, or SPI must run on L1 over L2. Re-check the 22 Ω source resistors and the return path when routing.
- **Ground:** one GND net; no split. L2 is untouched under the switching cell, the AFE and the ADC corner.

## 8. Mechanical, assembly and cost

- **Assembly process.** The board is now double-sided: JLC Standard PCBA, double-sided placement. The 0.35 mm BK13 already required Standard. A 75 × 40 mm board is below JLC's 70 × 70 mm single-board minimum, so it needs a **panel with rails and fiducials**, kept away from the antenna edge. Bottom parts are low (≤ 1.45 mm model height); the reflow sequence and bottom-side retention must be confirmed with the assembler.
- **Cost.** **Unknown**: not quoted.
- **Not verified here:**
  - battery/enclosure fit and clearance (dimensions not provided)
  - button actuation through the enclosure (button now at x ≈ 30–39, top edge)
  - probe/fixture access to the THT test points
  - BK13 mating/fold envelope (pitch unchanged)
  - antenna detuning by the enclosure, battery or body. The keep-out geometry is preserved, but the host board is smaller; RF performance needs bench verification.

## 9. Evidence index (this folder)

| Topic | Files |
|---|---|
| Measurement | `BASELINE_COMPONENTS.csv`, `GEOMETRY_A_BASELINE.txt`, `BODIES_EXPORT.txt` (A, top layers), `BODIES_B_PLACED.txt` (B, all layers) |
| Plan | `PLAN_B_COMPONENTS.csv`, `../work/plan_B.py`, `../work/plan_B_overrides.csv`, `PLAN_B_v*.png` |
| Native writes | `B_OPS_SUMMARY.txt`, `APPLY_B_LOG.txt`, `APPLY_FP_LOG.txt`, `APPLY_B_FIX_LOG.txt`, `APPLY_OPS_LOG_TRIAL.txt`; backups before each stage in `backups/` |
| Verification | `GEOMETRY_B_PLACED.txt`, `GEOMETRY_B_TRIAL.txt`, `DRC_B_PLACED.*`, `DRC_B_TRIAL.*`, `DRC_B_CHECKPOINT.*`, `compare_pads.py` output |
| Tables | `BASELINE_VS_COMPACT.csv`, `BOTTOM_MOVE_PLAN.csv`, `COMPONENT_MOVE_LEDGER.csv`, `TOP_INVENTORY_B.csv`, `BOTTOM_INVENTORY_B.csv`, `BOARD_PARTITION_MANIFEST.csv` |
| Views | Native captures: `views/B_native_2D_top.png`, `views/B_native_2D_bottom_viewed_from_bottom.png`, `views/B_native_3D_top.png`, `views/B_native_3D_bottom_viewed_from_bottom.png`. Renders from saved native geometry, labelled as renders: `views/RENDER_A_vs_B_same_scale.png`, `views/RENDER_B_xray_projection.png`. The oblique 3D side view was not captured (the user stopped further GUI view commands); per-side heights come from the native 3D-body export instead. |

## 10. Open issues (ranked)

1. **Silkscreen legibility pass:** 74 silk items plus 1 text-edge item.
2. **Routing:**
   - Add the BK13 0.13 mm escape rules at B's positions (proven 24 Sep form).
   - Resolve the ADC_EMG3 entry.
   - Decide whether SYS_EN, FG_ALRT and USB_PGOOD_N run on L3 or whether the LTC2954 group moves nearer the power block.
3. **Mechanical:** battery/enclosure dimensions; button, USB, SWD and test-point access; bottom-side height clearance.
4. **3D bodies:** 45 parts lack them (listed); the stored heights still need checking against datasheets.
5. **Fabrication (routing requirements report, reports/):**
   - F1: name JLC04121H-3313 on the order.
   - F2: set the edge rule to 0.5 mm.
   - F3: plan the panel.
   - F4: write the via-in-pad treatment for the UP1 and ST67 exposed-pad vias into the order notes.
6. **Schematic items that no layout can fix** (routing requirements report §"Six schematic issues"): D_VBUS breakdown voltage below the charger's OVP, and others listed there.

**Next review decision:** accept candidate B's 75 × 40 placement (or request option 1, 2 or 3 above for a 70 × 40 study C). Then authorize full routing of B.
