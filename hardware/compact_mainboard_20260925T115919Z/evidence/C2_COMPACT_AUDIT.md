# Compact candidate C2 — change audit (26 Sep 2026)

**Status:** C2 PLACEMENT CHECKPOINT + 4-LAYER ROUTING TRIAL (2 rounds). The trial found the board 85 % routable DRC-clean on 4 layers, but only by breaking the P0 rule G2 on 32 connections (§7). **Recommendation: 6 layers** (the user's pre-approved fallback); awaiting go-ahead. Mechanical qualification still open. No fabrication or ordering approval.

## 1. Result

| | A (baseline) | B (75 × 40) | **C2** |
|---|---|---|---|
| Board | 80.0 × 45.0 mm | 75.0 × 40.0 mm | **59.1 × 36.0 mm** |
| Area (r = 2 mm corners) | 3,596.6 mm² | 2,996.6 mm² | **2,124.2 mm²** |
| vs A | — | −16.7 % | **−40.9 %** |
| vs B | — | — | **−29.1 %** |
| Parts top / bottom | 209 / 22 | 187 / 44 | **109 / 122** |
| Tallest part, top / bottom | 5.08 mm (5021 TP) | 5.08 / 1.45 mm | **3.31 mm (USB-C) / 1.45 mm** |
| BK13 pitch | 13.0 mm | 13.0 mm | **10.8 mm** |

Layers: 4 (JLC04121H-3313) for the placement stage and the routing trial. The trial fails G2 on 4 layers (§7), so the approved 6-layer fallback is recommended.

## 2. User decisions this change rests on (26 Sep)

- "yes go with C2": includes the four items proposed on 25 Sep. These are:
  1. Tag-Connect + flat test pads + solder jumper instead of J_SWD / 5021 test points / JP_WIFI_BOOT.
  2. Power cell on the Bottom, under the digital side only.
  3. Via-in-pad where needed.
  4. 6 layers if the 4-layer trial fails.
- BK13 spacing: the user asked whether a reduction affects anything. The answer given:
  - Electrically: no change.
  - Mechanically: a width limit on the future DEB flex end.
  - Spacing reduced moderately, to 10.8 mm.
- MCU package unchanged.
- "if placing more components on the bottom side solves the size issue, do it".
- Altium restart approved for script problems.

## 3. Floorplan (x-ray)

- **Analog half, along the BK13 edge, both faces.**
  - Top: 5 BK13 at 10.8 mm pitch; each channel's INA/RDD/INA-feedback input stage, identical to B's template and only translated; J_REF; the five 68 Ω VREF branch resistors beside socket pin 8.
  - Bottom: U1, U2 and U3 as package-aware groups directly under their own channels. Each channel's servo and post-amp networks sit at the op-amp pins that serve it. U1 is turned 180° so channel 1 faces its amplifier sections and the VREF-buffer side faces the edge. The divider/filter sits beside U1. The DNP DRL provisions sit under the sockets and J_REF.
- **Digital/power half, both faces.**
  - Top: USB-C + button (left edge); a service column holding Tag-Connect, battery header, remote-NTC terminals and charge LED; the ST67 module (antenna overhang at the top edge); the STM32 block with ADC/VCAP/bypass and the ADC RC networks (B local layouts, rigid).
  - Bottom:
    - charger (UP1 exposed-pad GND vias land under the grounded USB-C shell);
    - converter cell flipped whole (B hot loop) under the STM32, clear of the ST67 thermal-via field, the crystal, the antenna margin and the ADC corner;
    - supervisor;
    - gauge;
    - LDO at the power/analog boundary;
    - pushbutton controller under the STM32;
    - flat probe pads + solder jumper + UART links beside the pins they serve.

## 4. Rule compliance and the documented departures from R2 "initial" dispositions

| Rule (R2 / routing requirements) | C2 |
|---|---|
| INA/RDD/INA feedback Top | kept Top, B template unchanged |
| U1–U3 + post/servo/reference passives "Top initially; no long cross-side high-impedance feedback connections" | **moved to Bottom as package-aware groups directly under their channels.** Only low-impedance nets cross (INA_OUT ≤ 9.2 mm span, Vservo ≤ 5.7 mm, VOUT, VREF_A/VREF_B_SRC, supplies). High-impedance nodes (NetCservo, NetCH, NetCL, INA inputs/FB) stay single-sided. `C2_RULE_EVIDENCE.txt` |
| STM32 + ADC/VCAP/critical bypass Top | kept, rigid |
| ST67 + 32 kHz crystal Top at outer edge, antenna exclusion | kept; antenna keep-out moved with the module; no part or via on either side inside it |
| TPS631000 "Top switching cell initially" | **Bottom** (user-approved), flipped whole; ≥ 11 mm from any analog part, 23.6 mm from references, 11.3 mm from the crystal |
| Charger coherent, thermal copper kept | Bottom; 5 exposed-pad vias kept; 9.2 mm from references |
| Quiet analog bank, nothing unrelated under analog/ADC region | enforced as zones on both faces and the ADC corner (`plan_C2.py`) |
| One GND, L2 continuous | unchanged; L2/L4 pours reshaped to the new outline |
| Test access / service contract | changed only as approved: pads kept on the same nets; parts Not Fitted in PROTO_1_REMOTE_NTC |

## 5. Native execution (AD22, proven calls only; every new call proven on a disposable copy first)

1. C2 copied from B (72 files, hash-identical; `C2_SETUP_MANIFEST.csv`).
2. Service change (`svc_swap3_T.pas`):
   - New library `Libraries/EMG_Service_C2B.PcbLib` holds:
     - `EMG_TC2030_NL` (Tag-Connect TC2030-IDC-NL-FP rev B: 6 × 0.787 pads on 1.27 grid, 3 × 0.991 NPTH, plated = False read back);
     - `EMG_TP_FLAT_1R2`;
     - `EMG_SJ_2P_NO`.
   - MCU_sheet footprint links swapped.
   - The 8 PCB components rebuilt with the same source UID, path and nets.
   - Rule `PASTE_NONE_SERVICE_PADS` (−1.0 mm) removes paste from these pads.
   - The 8 are marked Not Fitted in PROTO_1_REMOTE_NTC (33 variations).
3. Placement write (`apply_C2_T.pas`, 731 ops resolved before any change):
   - 231 components, 78 flipped.
   - 15 free test pads moved.
   - 238 free tracks and 55 vias removed (C2 is re-routed).
   - UP1 (5) and ST67 (20) thermal vias kept with their parts.
   - 10 socket markers moved; 126 stale assembly leaders removed.
   - 27 region rules re-anchored.
   - Outline 59.1 × 36.0.
   - Pours reshaped and repoured.
4. Defects found by the native checks and fixed in two fix passes (`gen_C2_fix_ops.py`):
   - (a) The first library placed pads from absolute zero; the PcbLib origin is 1270, 1270 mm, so the service pads landed 1270 mm off. Rebuilt relative to the origin.
   - (b) FlipComponent drags vias lying in the part's pads, and the explicit via move applied again, so UP1's vias were moved twice. They were re-placed individually.
   - (c) The ST67 via field was missing from the planner's keep-clear list; the converter and supervisor moved.
   - (d) The planner used pad-extent bodies for parts without a 3D model, but Altium's component clearance uses the courtyard/extent. Planner rules were aligned with the native DRC (0.25 mm power clearance, 0.2 mm component clearance, 0.3 mm to through-hole pads).

## 6. Verification (saved state, after close/reopen)

| Check | Result |
|---|---|
| Component readback vs plan | 246/246 (231 parts + 15 free pads): side, XY within 2 µm, rotation, source UID |
| Pad-level geometry vs plan | 812/812 pads, worst 0.0001 mm |
| Electrical preservation vs B | 0 pad→net differences; 136/136 nets; 15 free pads; no free copper; 25 GND thermal vias |
| Native batch DRC (`DRC_C2_CHECKPOINT.*`) | **0 short, 0 clearance, 0 component clearance, 0 mask sliver, 0 net antennae**; 535 unrouted (placement checkpoint); 257 silkscreen + 5 silkscreen-to-edge (legibility pass open) |
| Heights (3D bodies) | Top 3.31 mm (USB-C), Bottom 1.45 mm; 51 parts without a 3D body (incl. the flat service footprints) |

## 7. Routing trial on 4 layers (26 Sep)

**Scope.**
- 283 signal connections Altium listed as unrouted after placement.
- Excluded on purpose: GND (to be closed by pours and stitching), 3V3_DIG and 3V0_ANA (supply pass), and BK13 socket escapes.
- Router: `router5.py`, 0.05 mm grid, layers Top / L3 / Bottom, never L2.
- Every route is exact-checked (`build_ops.py --drop-bad`) and topology-audited (`audit_plan.py`) before it is written natively.
- Altium's own DRC is the judge.

**Preparation (round 1).**
- Converter hot loop restored from B's designed copper (16 tracks + 2 cap GND vias, mirrored with the flipped cell).
- Six CLR_FINE_ESCAPE rules re-anchored to C2 part positions.
- DNP DRL input resistors stood upright; TP_WIFI_CHIP_EN moved clear of C_WIFI_EN.
- Catch-all Width rule set to 0.15 / 0.2 / 0.5 mm.

| | Round 1 | Round 2 | Total |
|---|---|---|---|
| Router result (pass 1) | 243 / 283 | 48 / 77 (849 s) | |
| Kept by exact check | 205 | 35 | **240 (+1 already joined) = 241 / 283 = 85 %** |
| Written natively (saved, reopened) | 773 tracks, 112 vias | +176 tracks, +37 vias | 939 tracks, 173 vias |
| Altium DRC: short / clearance / width / component / antenna | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | |
| Unrouted (Altium) | 335 = 258 excluded + 77 trial | 302 = 260 excluded + 42 trial | |
| G1 (no copper on L2) / R1 (antenna zone bare) / P2-M2 (no via on LX, VCAP) | pass / pass / pass | pass / pass / pass | |
| **G2 (solid L4 under every L3 trace)** | 15 nets, 11.0 mm² | 9 nets, 14.2 mm² | **32 connections fail, 12 of them analog** |

**Round-2 drops.** The exact check dropped 13 connections:
- Vc_1…5: the router ran 0.19 mm from the BK13 socket keep-outs; 0.25 mm is required.
- VOUT_3/5: 0.227 mm from the RG_n pads.
- Four vias landed on pads.
- One crossing: MCU_SPI_MISO / WIFI_UART_TX.

**G2 per connection** (`C2_G2_BY_CONNECTION.txt`, judged on the native state after both rounds):
- 208 / 240 routed connections are G2-clean.
- 32 fail. The analog ones:
  - VREF_A ×5;
  - VOUT_1/2/3/4 ×7.
- Also failing: power (VSYS, VBUS, VBAT_CELL), WIFI_SPI_CS and WIFI_SPI_CLK (the report names the SPI corridor explicitly), MCU control lines, DRL_AMP_OUT/DRL_SUM.

**Why G2 fails on 4 layers.**
- In the JLC04121H-3313 stack, L3 is 0.099 mm from L4 but 0.865 mm (core) from L2, so L4 is L3's reference.
- In C2, L4 carries 122 bottom parts, their pads and the bottom routing. It can no longer be a solid ground under L3.
- Round 2 also began splitting the L4 pour: two new GND unrouted pairs on L4, beside UP2 and R_SHDN_PD.
- Each routing round made G2 worse (11.0 → 25.1 mm² in total).

**The 42 still unrouted** (`C2_TRIAL_UNROUTED.txt`):
- 18 long control/digital lines. Most are cross-board runs, 30–41 mm, from the left service/charger/gauge column to the STM32: SWDIO, I2C, FG_ALRT, PGOOD, PWR_BTN, WIFI_BOOT/SPI/UART.
- 12 analog cross-side lines: Vservo_2–5 from the Top INA to the Bottom op-amp, INA_OUT_3/5, VOUT_3/5.
- 5 charger-local lines (TS, BAT_TEMP, TMR, EN1_BIAS).
- 5 DNP DRL provisions (Vc_n).
- 2 other.

The supply nets (3V3_DIG 39, 3V0_ANA 52) are not routed yet and also need L3.

**Verdict.** 4 layers do not qualify for C2.
- The copper fits DRC-clean to 85 %.
- But every route through the dense middle needs L3. L3 has no solid reference, because two-sided placement uses L4 for parts.
- The remaining connections and the supply pass would need still more L3.

**Recommendation.** 6 layers, the fallback the user approved on 25 Sep:
- L1 parts/signal;
- L2 GND;
- L3 signal;
- L4 power/signal;
- L5 GND;
- L6 parts/signal.

Both inner signal layers then sit next to a solid GND, and the remaining 42 connections plus the supply nets get the room they need. The placement stays unchanged. The trial copper is disposable: re-route after the stack change. Cost and stack template (JLC 6-layer impedance stack) are to be confirmed before the switch.

## 8. Open issues (ranked)

1. **Layer count: needs the user's go-ahead.** Switch C2 to 6 layers (§7), then route supplies, GND stitching and the remaining connections. Via-in-pad (filled + capped) is needed for the UP1 and ST67 thermal vias and is to be named in the fab notes.
2. **Silkscreen legibility pass.** 262 items. Proposal: designators on an assembly layer; silk only for polarity, connectors and test labels.
3. **Mechanical.**
   - The 10.8 mm BK13 pitch limits each DEB flex end to roughly 7–8 mm wide, including stiffener, so that it still unplugs with tweezers.
   - Battery and enclosure dimensions are still missing.
   - Probe access to the Bottom flat pads needs a fixture or a pogo clip.
   - The Tag-Connect plug face on Top needs clear access.
4. **Button ESD.** PWR_BTN_N is 3.65 mm from INA1; review ESD protection or the button position.
5. **Housekeeping.**
   - The first, superseded `EMG_Service_C2.PcbLib` is still listed in the C2 project. Remove it with Altium closed.
   - The TP part comments still read "5021". They are Not Fitted, so they are not in the BOM.
6. **Fabrication.** From the routing requirements report: F1 stack, F2 0.5 mm edge, F3 panel (the board is below the 70 × 70 mm minimum), F4 via-in-pad.

## 9. Evidence (this folder)

- **Routing trial:**
  - plans: `ROUTE_PLAN_C2TRIAL_PASS1.csv` / `_OK.csv`, `ROUTE_PLAN_C2R2_PASS1.csv` / `_OK.csv`;
  - audits: `AUDIT_ROUTE_PLAN_C2TRIAL_OK.txt`, `AUDIT_ROUTE_PLAN_C2R2_OK.txt`, `C2_G2_BY_CONNECTION.txt`;
  - native logs: `APPLY_OPS_C2_*_LOG.txt`;
  - DRC: `DRC_C2_TRIAL5.*` (round 1), `DRC_C2_R2.*` (round 2);
  - geometry: `GEOMETRY_C2_R2.txt` (native export after round 2);
  - unrouted list: `C2_TRIAL_UNROUTED.txt`.

- **Plan:** `PLAN_C2_COMPONENTS.csv`, `PLAN_C2_AUDIT.json`, `PLAN_C2_TOP.png`, `PLAN_C2_BOTTOM_xray.png`.
- **Native logs:** `SVC_SWAP3_C2_LOG.txt`, `VARIANT_SVC_C2_LOG.txt`, `APPLY_C2_LOG.txt`, `APPLY_C2_SVC_LOG.txt`, `APPLY_C2_FIX_LOG.txt`, `APPLY_C2_FIX2_LOG.txt`, `C2_OPS_SUMMARY.txt`.
- **Verification:**
  - `GEOMETRY_C2_PLACED.txt` and `BODIES_C2_PLACED.txt` (native exports);
  - `C2_PAD_VERIFICATION.txt`, `C2_RULE_EVIDENCE.txt`;
  - `DRC_C2_CHECKPOINT.txt.html` and `DRC_C2_CHECKPOINT.json`.
- **Tables:** `C2_COMPONENT_LEDGER.csv`, `C2_TOP_INVENTORY.csv`, `C2_BOTTOM_INVENTORY.csv`, `C2_SUMMARY.txt`.
- **Renders of saved native geometry:** `views/RENDER_C2_native_TOP.png`, `views/RENDER_C2_native_BOTTOM_xray.png`, `views/RENDER_A_B_C2_same_scale.png`, `views/C2_SERVICE_PARTS_MAP.png`.
- **Proofs** (disposable copies): `PROBE_PADPROPS_LOG.txt`, `PROBE_LIBADD_LOG.txt`, `PROBE_PASTERULE_LOG.txt`, `SVC_SWAP_DISP2B_LOG.txt`.
