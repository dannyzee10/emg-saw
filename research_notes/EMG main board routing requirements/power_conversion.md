# Power-conversion routing requirements: TPS631000 (UP2), TPS7A2030 (UP3), TPS3808G33 (U_UV1), LTC2954-1 (U_EN1)

Context used for every item below. Board: 80 × 45 mm, 4 layers: L1 35 µm / 0.0994 mm 3313 prepreg / L2 GND (17.5 µm) / 0.865 mm core / L3 power + signal (17.5 µm) / 0.0994 mm / L4 35 µm mostly GND. That is about 1.17 mm of copper plus dielectric. One common GND net. Through vias only, default 0.6 mm pad / 0.3 mm hole.

Exact parts from the 2026-09-24 BOM snapshot:
- UP2 = TPS631000DRLR
- L1 = DFE21CCN1R0MELL
- CUP4 = GRM219R60J476ME44D (47 µF 6.3 V X5R 0805)
- CUP4_1 = GCM21BC71E106KE36L (10 µF 25 V X7S 0805)
- RUP_3 = 560 kΩ, RUP_4 = 100 kΩ
- CUP4_FB = GRM1555C1H100JA01D (10 pF C0G 0402)
- UP3 = TPS7A2030PDBVR
- U_UV1 = TPS3808G33DBVR, with C_UV_BYPASS 100 nF
- U_EN1 = LTC2954ITS8-1, with C1_EN1 100 nF, C2_EN1 33 nF, C3_EN1 330 nF, R_EN1_1 1 kΩ, R_EN1_BIAS 10 kΩ

Source: [BOM snapshot CSV](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/ASSEMBLY_SNAPSHOT_20260924T023521434Z/MAIN_BOARD_COMPLETE_ASSEMBLY_BOM.csv)

Tags used below:
- **[HARD]**: a specification limit, or a "must" statement in the part manufacturer's document.
- **[MFR-REC]**: a recommendation or reference layout from the part manufacturer (data sheet, EVM guide).
- **[PRACTICE]**: generic manufacturer application-note guidance or IPC guidance that is not specific to the part.
- **[PROJECT]**: a rule from the project brief. It is not manufacturer evidence.

## 1. TPS631000 layout guidelines, layout example and EVM: critical loops, CIN/COUT/inductor placement, LX copper, GND vias, FB and feed-forward placement, thermal copper, vias under the IC

### Takeaway
TI's text gives only two layout rules for the TPS631000:
- Put CIN and COUT as close as possible, with short, wide, direct traces.
- Treat FB as a signal trace and keep it away from LX1/LX2.

The geometry comes from data-sheet Fig 7-24 and the TPS631000EVM-075 layout:
- CIN sits beside VIN. COUT sits beside VOUT.
- The inductor sits directly over LX1/LX2 on the same layer. There are no vias in the LX nets.
- A GND copper band with about 3 vias runs under the package between the pin rows. It joins CIN-GND, GND pin 7 and COUT-GND.
- Via arrays sit at the capacitor GND pads.
- The FB divider sits on the side away from the inductor. VOUT is sensed beyond COUT.

The DRL package has no thermal pad. No TI document gives a numeric limit on LX copper area or length.

### Cited Findings

#### Source revision register (applies to all five sections)
- TPS631000 data sheet SLVSFH3C, Oct 2021, **rev. C Aug 2026**. This is current: the local copy was retrieved 2026-09-16 from TI's always-latest symlink, SHA-256 b52a4064…. The revision history says rev. C changed the LX1/LX2 <10 ns absolute minimum from –0.3 V to –2 V, and changed the CDM standard. — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf); [local source index](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/sources/analog_power/SOURCE_READING_INDEX.md)
- TPS631000EVM-075 User's Guide **SLVUC09, Sept 2021** (no later revision found). **Older than the data-sheet rev. C.** It uses a DFE252012P-1R0M=P2 inductor and 22 µF 0603 capacitors, not this board's parts. — [TI SLVUC09](https://www.ti.com/lit/pdf/slvuc09)
- TPS7A20 data sheet SBVS338H, Mar 2020, **rev. H Jul 2024**. This is the revision TI served on 2026-09-16 (archive SHA-256 663a9ff5…). — [TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)
- TPS3808 data sheet SBVS050N, May 2004, **rev. N Aug 2026**. Current. — [TI SBVS050N](https://www.ti.com/lit/ds/symlink/tps3808.pdf)
- LTC2954 data sheet **2954fb Rev B** (LT 0211, i.e. Feb 2011). This is still the PDF ADI links (archived 2026-09-16). **Old; it has no layout section.** — [ADI LTC2954 Rev B](https://www.analog.com/media/en/technical-documentation/data-sheets/2954fb.pdf)
- Generic notes, used only where the part documents are silent. Flagged as older or written for other parts:
  - TI SLVAFJ3 (Sep 2023, written for the LM5177 controller with external FETs) — [TI SLVAFJ3](https://www.ti.com/lit/pdf/slvafj3)
  - TI SSZTAE3 (Feb 2017, controller designs) — [TI SSZTAE3](https://www.ti.com/lit/pdf/ssztae3)
  - TI SNVA021C / AN-1149 (Oct 1999, revised Apr 2013) — [TI SNVA021C](https://www.ti.com/lit/pdf/snva021)
  - TI SLVA535B (Jan 2018, revised Jul 2018) — [TI SLVA535B](https://www.ti.com/lit/pdf/slva535)
  - ADI/LT AN-139 Rev A (Oct 2012) — [ADI AN-139](https://www.analog.com/media/en/technical-documentation/application-notes/an139f.pdf)
  - ADI/LT AN101 (Jul 2005) — [ADI AN101](https://www.analog.com/media/en/technical-documentation/application-notes/an101f.pdf)

#### TPS631000 data-sheet requirements
- **[HARD] Pinout (DRL / SOT-5X3, 8 pins).** One row is VOUT 1, LX2 2, LX1 3, VIN 4. The other row is EN 5, MODE 6, GND 7, FB 8. The data sheet's "PGND" in §7.2.2.3/§7.2.2.4 refers to this single GND pin; there is no separate AGND. (§4, Fig 4-1 / Table 4-1, p3) — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)
- **[HARD] EN and MODE:** "This pin must not be left floating" (both pins). EN input current is ±0.25 µA max with "no pullup resistor", so there is no internal pull-up. (Table 4-1 p3; §5.5 p5) — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)
- **[HARD] Recommended operating conditions (§5.3, p4):**
  - Input capacitance C_I ≥ 4.2 µF.
  - Output capacitance C_O for 1.2 V ≤ V_O ≤ 3.6 V (nominal value at V_O = 3.3 V): 10.4 µF min, 16.9 µF nom, 330 µF max.
  - L = 0.7 / 1 / 1.3 µH.
  - §7.2.2 p10: "Tolerance and derating must be taken into account when selecting nominal inductance and capacitance."
  - — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)
- **[HARD] Absolute maximum ratings (§5.1, p4):**
  - VIN, LX1, LX2, VOUT, EN, FB, MODE: –0.3 V to 6 V.
  - LX1/LX2 for less than 10 ns: –2.0 V to 7 V. This bounds the switch-node ringing that the layout's loop inductance may produce.
  - — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)
- **[HARD] Feedback divider (§6.3.3 p7; §7.2.2.5 p13; §5.5 p5):**
  - "The low-side resistor R2 (between FB and GND) must not exceed 100kΩ."
  - V_FB is 495 / 500 / 505 mV.
  - This design uses RUP_4 = 100 kΩ (at the limit) and RUP_3 = 560 kΩ, giving V_OUT = 0.5 × (1 + 5.6) = 3.30 V.
  - TI's own EVM uses the same pair, R2 560 kΩ / R3 100 kΩ (SLVUC09 Fig 4-1 p5, Table 4-1 p6).
  - — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf); [TI SLVUC09](https://www.ti.com/lit/pdf/slvuc09)
- **[MFR-REC] Layout Guidelines §7.4.1 (p18), quoted in full:**
  - "Place input and output capacitors as close as possible to the IC. Traces must be kept short. Route wide and direct traces to the input and output capacitors results in low trace resistance and low parasitic inductance."
  - "The sense trace connected to FB is signal trace. Keep these traces away from LX1 and LX2 nodes."
  - — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)
- **[MFR-REC] Output capacitor (§7.2.2.3, p12):**
  - "use small ceramic capacitors placed as close as possible to the VOUT and PGND pins of the IC. The recommended nominal output capacitor value is a single 47μF."
  - If large capacitors cannot be close, "use a smaller ceramic capacitor in parallel to the large capacitor. The small capacitor must be placed as close as possible to the VOUT and PGND pins of the IC."
  - Table 7-3 lists **GRM219R60J476ME44 (47 µF, 6.3 V, 10 mΩ, 0805)**, the same part as CUP4.
  - — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)
- **[MFR-REC] Input capacitor (§7.2.2.4, p12):**
  - "TI recommends a 22μF input capacitor … An X5R or X7R ceramic capacitor placed as close as possible to the VIN and PGND pins of the IC is recommended."
  - Add about 47 µF of bulk capacitance if the source is "more than a few inches" away.
  - This design's CUP4_1 is 10 µF 25 V X7S 0805: below TI's 22 µF recommendation. It must still give ≥ 4.2 µF effective at up to about 4.2 V (see Gaps).
  - — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf); [BOM](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/ASSEMBLY_SNAPSHOT_20260924T023521434Z/MAIN_BOARD_COMPLETE_ASSEMBLY_BOM.csv)

#### TI reference geometry (observed from figures; not dimensioned)
- **[MFR-REC] Layout Example Fig 7-24 (p18).** The IC is drawn with the VIN–LX1–LX2–VOUT row facing the inductor.
  - The inductor sits directly beside that row. Its two pads join LX1 and LX2 through short, tapered copper. Nothing else is drawn between the IC and the inductor.
  - One input capacitor sits immediately beside the VIN pin. It bridges a VIN pour and a GND pour.
  - Two output-capacitor footprints sit immediately beside the VOUT pin. They bridge a VOUT pour and a GND pour.
  - A GND copper band runs between the two pin rows under the package body. It joins the input-capacitor GND, the GND pin and the output-capacitor GND.
  - Vias shown: 3 in the band under the package; a 2×3 array beside the input-capacitor GND; a 2×3 array beside the output-capacitor GND; 2 below the GND pin; 2 at R2's GND end.
  - R1 and R2 sit at the FB pin on the side away from the inductor.
  - R1's far end connects to VOUT through a via on the VOUT pour beyond the output capacitors. The sense trace appears to run on another layer.
  - EN and MODE leave straight away from the package.
  - — [TI SLVSFH3C Fig 7-24](https://www.ti.com/lit/ds/symlink/tps631000.pdf)
- **[MFR-REC] EVM layout (SLVUC09 Fig 3-1 / 3-2, p4, top and bottom views only):**
  - Inductor L1 sits directly on U1's LX side.
  - Input capacitors C2 (not fitted) and C3 (22 µF 0603, fitted) are immediately to the left. Output capacitors C4/C5 (fitted) and C6 (not fitted) are immediately to the right, in one row with U1.
  - About three small vias sit between U1's pin rows.
  - Small GND vias sit beside the capacitor GND pads.
  - The feedback parts are at U1's lower right, away from L1: R3 100 kΩ, R2 560 kΩ, C7 10 pF C0G 0402 (**not fitted**) and R1 50 Ω next to TP1.
  - A short bottom-layer jumper appears to link a via on the VOUT pour beyond C6 to R1, i.e. VOUT is sensed at the output capacitors.
  - The bottom layer is an essentially continuous pour.
  - — [TI SLVUC09](https://www.ti.com/lit/pdf/slvuc09)
- **[MFR-REC] Feed-forward capacitor.**
  - The rev. C data sheet's typical application (Fig 7-1, p10: 511 k / 91 k, CI 22 µF, CO 47 µF) has no feed-forward capacitor and no recommendation for one.
  - The EVM guide says "Extra positions are available for additional input and output capacitors and a feedforward capacitor" (§1.3, p2). Its 10 pF C0G position C7 is not fitted (Table 4-1, p6).
  - AN-1149: "Some designs require the use of a feed-forward capacitor connected from the output to the feedback pin … In this case it should also be positioned as close to the IC as possible." (§3, p2)
  - — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf); [TI SLVUC09](https://www.ti.com/lit/pdf/slvuc09); [TI SNVA021C](https://www.ti.com/lit/pdf/snva021)
- **[MFR-REC] Feedback placement (SLVAFJ3 §2.5, p7):** "Locate the upper and lower feedback resistors close to the FB pin, keeping the FB traces as short as possible. Route the trace from the upper feedback resistor or resistors to the output voltage sense point." — [TI SLVAFJ3](https://www.ti.com/lit/pdf/slvafj3)

#### Hot loops and switch-node guidance (generic notes)
- **[PRACTICE] Critical loops in a 4-switch buck-boost.**
  - SSZTAE3 p1: "The input loop (No. 1) carries the switching current when in buck cycles. The output loop (No. 2) carries the switching current when in boost cycles … the lowest loop area and the most compact design when optimizing both loops using a symmetric layout."
  - SLVAFJ3 §2.1–2.2 (p2–3): the input loop is CIN plus Q1/Q2; the output loop is COUT plus Q3/Q4 "along with their return paths". "Connect the negative terminal of the capacitor close to the source of the low-side MOSFETs (at ground). Similarly, connect the positive terminal of the capacitor or capacitors close to the drain of the high-side MOSFETs of both loops."
  - AN-139 p4: a 4-switch buck-boost "consists of a buck circuit followed by a boost circuit", and a common GND path "belongs to both hot loops".
  - — [TI SSZTAE3](https://www.ti.com/lit/pdf/ssztae3); [TI SLVAFJ3](https://www.ti.com/lit/pdf/slvafj3); [ADI AN-139](https://www.analog.com/media/en/technical-documentation/application-notes/an139f.pdf)
- **[PRACTICE] Switch-node area.**
  - SLVAFJ3 §2.1 (p2–3): "The areas of the switching nodes SW1 and SW2 need to be as small as possible. If the SW1 and SW2 are poured with big area copper planes, the high dv/dt noisy signal can couple into other traces nearby through capacitive coupling."
  - SSZTAE3 p2: extra switch-node copper is only a thermal measure "for relatively higher-power designs".
  - — [TI SLVAFJ3](https://www.ti.com/lit/pdf/slvafj3); [TI SSZTAE3](https://www.ti.com/lit/pdf/ssztae3)

#### Thermal, land pattern and inductor
- **[HARD] No thermal pad.**
  - DRL thermal metrics (§5.4, p4): RθJA 132.7 °C/W, RθJB 27.3 °C/W, ΨJB 26.6 °C/W, RθJC(bot) "N/A".
  - Land pattern DRL0008A (drawing 4224486/G, 11/2024, p26): 8 pads of 0.67 × 0.3 mm, 0.5 mm pitch, 1.48 mm row-to-row pitch, no centre pad, non-solder-mask-defined pads preferred, 0.05 mm mask margin. Note 5: "Publication IPC-7351 may have alternate designs."
  - Stencil (p27) is based on a 0.1 mm stencil.
  - — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)
- **[MFR-REC] Inductor current margin (§7.2.2.2, p11–12).**
  - TI: "select an inductor with a saturation current 20% higher than the value calculated using Equation 3."
  - TI's Table 7-2 does not list the DFE21CCN1R0MELL. It lists DFE252012P-1R0M=P2 (4.3 A, 42 mΩ), HTEK20161T, MAKK2016T1R0M and DFE18SAN1R0ME0.
  - The Murata reference drawing JTE243A-0052C-01 (p1) gives for DFE21CCN1R0MELL: 1.0 µH ±20 %, DCR 0.060 Ω max (0.054 Ω typ). Rated current is 3300 mA (inductance –30 %; 3700 mA typ) and 2700 mA (self-heating ≤ 40 °C; 3200 mA typ). The smaller of the two is the rating, and product temperature must stay ≤ 125 °C.
  - — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf); [Murata JTE243A-0052](https://search.murata.co.jp/Ceramy/image/img/P02/JTE243A-0052.pdf)

#### Generic layout practice
- **[PRACTICE] AN-1149 (SNVA021C §2, §4, §5, p2):**
  - "The grounds of the IC, input capacitors, output capacitors … should be connected close together directly to a ground plane."
  - "Try to run the feedback trace as far from the inductor and noisy power traces as possible … It is often a good idea to run the feedback trace on the side of the PCB opposite of the inductor with a ground plane separating the two."
  - Compensation parts "should not be located very close to the inductor".
  - "Arrange the components so that the switching current loops curl in the same direction."
  - — [TI SNVA021C](https://www.ti.com/lit/pdf/snva021)
- **[PRACTICE] AN-139 (p12):**
  - "Use short ceramic capacitors, i.e., 0402, or reverse geometry capacitors because the block capacitors need low equivalent series inductance (ESL)."
  - "Use reverse geometry capacitors or a stack of 0402 closest to the filter point and larger cases close by. Any trace length significantly increases the few hundred pH inductance your small block capacitors have. Ensure that the routing path of the VIN and the return trace go through the filter capacitor pads."
  - — [ADI AN-139](https://www.analog.com/media/en/technical-documentation/application-notes/an139f.pdf)
- **[PRACTICE] Vias on high-current paths (SLVAFJ3 §3, p8):**
  - "Try to avoid using via holes on the high current path unless they are necessary. When using vias, you need to use an adequate number of via holes."
  - "Too many via holes crowded in a small area can hinder current flow due to the loss of copper area."
  - "Route high current traces as well as the critical control signal paths before routing other traces."
  - — [TI SLVAFJ3](https://www.ti.com/lit/pdf/slvafj3)

#### Project rules
- **[PROJECT] Project brief:**
  - Place UP2, L1, CUP4_1 and CUP4 "as one compact cell … no large switching-node pour, long layer excursion, test loop or unrelated trace under the switching cell. Route FB from a quiet output-sense point, with the divider/feed-forward capacitor near FB and away from LX nodes … Do not invent a thermal pad" (line 205).
  - LX1/LX2: "Dedicated keepout from sensitive wiring; not a generic signal trace" (line 117).
  - No large test pads on LX1/LX2 (line 241).
  - L3: "Do not create enormous VBUS or switched-node planes" (line 91).
  - "Prefer short same-layer connections for converter loops" (line 223).
  - — [Project brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)

### Inferences

**Checklist for UP2, derived from the findings above:**

- **Hot-loop mapping for this pinout.**
  - Buck-mode loop: CUP4_1(+) → VIN pin 4 → internal high-/low-side FETs → GND pin 7 → GND copper → CUP4_1(–).
  - Boost-mode loop: CUP4(+) → VOUT pin 1 → pin 7 → CUP4(–).
  - Pin 7 is on the opposite row from VIN and VOUT, directly across from LX2. So both loops close through the GND copper that crosses from the capacitor grounds to pin 7.
  - This path should be short, wide L1 copper (TI's under-body band) plus immediate L2 stitching. A GND return that detours around the package, necks down, or relies on a single via is the main defect to look for.
- **Placement order.** CUP4_1 is the part nearest pins 4/7 and CUP4 is the part nearest pins 1/7. Any other VSYS or 3V3_DIG capacitors are "downstream" and do not replace them. If board space allows, a small 0402 in parallel at the pins shortens the loop (TI §7.2.2.3; AN-139 p12).
- **LX1/LX2.**
  - Route on L1 only, directly from pin to inductor pad. Start at pad width (0.3 mm) and flare to the inductor pad.
  - Keep them as short as placement allows (≈1 mm class).
  - No vias, test pads, pours on other layers, or unrelated copper between the IC and L1.
  - MODE (pin 6) sits directly across from LX1 (pin 3) and EN (pin 5) across from VIN (pin 4). Escape both on the pin 5/6 side, away from the LX row, as in Fig 7-24.
- **Vias under the body.** On TI's land pattern the gap between the pin rows is 1.48 − 0.67 = 0.81 mm.
  - A default 0.6 mm-pad via centred there leaves about 0.105 mm to each pad row. That is below common clearance rules and an assembly risk under a 0.6 mm-high body.
  - Either use a smaller, tented/plugged via if the fab allows, or omit under-body vias. Keep the L1 GND band anyway, and put the stitching vias immediately outside the package at pin 7 and at the CUP4_1/CUP4 GND pads.
  - Also check the Altium footprint SOT50P160X60-8N against DRL0008A: the inner gap and pad length set whether a band fits.
- **GND stitching.** Use via clusters right at the CIN and COUT GND pads, as many as fit; TI's figure shows 6 each. Two vias near pin 7 and a separate via for RUP_4's GND.
  - With the 0.0994 mm L1–L2 prepreg, an L1→L2 via connection is only ~0.13 mm of barrel. So via count is limited by space, not by barrel length.
  - Follow AN-139 on quiet grounds: the FB divider's ground via and any analog ground vias go outside the hot-loop via field.
- **FB network.**
  - Keep RUP_3, RUP_4 and CUP4_FB within a few mm of pin 8, on the side away from L1 (Fig 7-24 / EVM).
  - The FB node is high-impedance: 560 kΩ ∥ 100 kΩ ≈ 84.8 kΩ, with about 5 µA divider current. Keep its copper minimal.
  - Take the top of RUP_3 from the CUP4 VOUT pad or just downstream of it, never from copper between the IC and COUT or near LX.
  - Route that sense trace thin and away from LX. If it changes layer, L3 under the unbroken L2 is consistent with AN-1149's "opposite side … ground plane separating".
- **CUP4_FB (10 pF, fitted).** TI's current data sheet does not call for it, and TI's EVM leaves the same 10 pF position unfitted.
  - With 560 kΩ it adds a zero at about 28.4 kHz and a pole at about 187.6 kHz.
  - Loop and transient behaviour should be checked on the bench. That is outside routing scope.
  - For layout: put the footprint across RUP_3 at the FB end, as close to the IC as possible (AN-1149).
- **Thermal.** At 0.6 A and 3.3 V with η ≈ 0.9, total loss is about 0.22 W; inductor DCR loss is about 0.03 W. That leaves about 0.19 W in the IC, roughly 25 °C rise using the JEDEC RθJA of 132.7 °C/W. The ordinary VIN, VOUT and GND copper is enough, and no thermal pad or extra LX copper is needed.

### Gaps
- No TPS631000 document gives a numeric limit on LX copper area or length, a minimum via count, via size, or keep-out distance. Fig 7-24 and the EVM are undimensioned. Via counts and positions above are read from figures; EVM drill sizes and layer count are not stated (only top and bottom views are shown). EVM Gerbers were not reviewed.
- The current data sheet has no feed-forward capacitor guidance, and no TI loop-stability data exists for 560 kΩ ∥ 10 pF on this part. TI E2E posts were not used as evidence.
- Not verified: whether CUP4_1 (GCM21BC71E106KE36L) keeps ≥ 4.2 µF effective at VSYS up to 4.2–5.0 V, and CUP4's effective value at 3.3 V against the 10.4 µF minimum. The DC-bias curves were not retrieved.
- Package descriptions disagree: data-sheet p1 says "1.2mm × 2.1mm SOT-583"; the package table says 2.1 × 1.6 mm; SLVUC09 says "2.2-mm × 1.7-mm". The DRL0008A drawing (2.0–2.2 mm long, 1.5–1.7 mm lead span, 0.6 mm max height) should govern.

## 2. Peak inductor/switch currents at 3.3 V / 0.6 A from 3.0–4.2 V, and the resulting trace widths and via counts (1 oz outer, 0.5 oz inner)

### Takeaway
At the 0.6 A / 3.3 V planning load:
- Boost mode at 3.0 V: peak inductor/switch current is **≈0.80 A** by TI's data-sheet Eq. 3 with its default assumptions, and **≈0.87 A** at tolerance corners.
- TI's SLVA535B method gives **0.86 A typical / 1.01 A corner** at 3.0 V.
- Buck mode: **0.78 A typical / 0.89 A corner** at 4.2 V, and 0.88 / 1.06 A if VSYS reaches 5.0 V.
- Continuous currents: about **0.73–0.78 A** on VSYS at 3.0 V (0.82–0.86 A at 2.7 V), **0.6 A** on 3V3_DIG, and **≈0.6–0.8 A RMS** on LX.
- The switch current limit (**2.6–3.35 A**, higher in operation) is the fault/transient ceiling.

TI's generic copper rule is ≥ 0.381 mm (15 mil) per ampere and one standard via per 200 mA. For a 1 A design current that means ≥ 0.38 mm and 5 vias per layer change.

The IPC fallback for 1 A at 10 °C rise:
- 0.30 mm on 1 oz outer copper.
- 1.56 mm on 0.5 oz inner copper by the conservative IPC-2221 internal formula.
- Roughly 0.6 mm on 0.5 oz inner copper if treated as IPC-2152 suggests (closer to external behaviour).

### Cited Findings
- **[MFR-REC] TPS631000 peak-current equations (§7.2.2.2, p11).**
  - Eq. 2: D = (V_OUT − V_IN)/V_OUT.
  - Eq. 3: I_PEAK = I_OUT/(η(1 − D)) + V_IN·D/(2·f·L).
  - "η = estimated converter efficiency (use the number from the efficiency curves or 0.9 as an assumption)"; "The calculation must be done for the minimum input voltage in boost mode."
  - Only the boost-mode equation is given "because this provides the highest value of current".
  - Eq. 3's note says f is "typical 2.2MHz", but the Electrical Characteristics give f_SW = 1.8 / 2.0 / 2.2 MHz (§5.5, p5). The two statements are inconsistent.
  - — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)
- **[HARD] Current limit (§5.5, p5; p1).**
  - Switch peak current limit I_L(PEAK), Q1, V_O = 3.3 V: 2.6 / 3 / 3.35 A sourcing; –0.7 / –0.55 / –0.45 A sinking.
  - Footnote: "The current limit in operation is somewhat higher and depending on propagation delay and the applied external components."
  - Features (p1): "3A peak switch current", "2A output current for V_IN ≥ 3V, V_OUT = 3.3V".
  - Thermal shutdown stops operation when the die overheats (§6.3.6.4, p8).
  - — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)
- **[PRACTICE] TI's 4-switch buck-boost equations (SLVA535B §2 p2, §4 p3–4).**
  - Duty cycles: D_Boost = 1 − V_INmin·η/V_OUT (Eq. 1); D_Buck = V_OUT/(V_INmax·η) (Eq. 2).
  - Buck mode: ΔI = (V_INmax − V_OUT)·D_Buck/(F_SW·L) (Eq. 5); I_SWmax = ΔI/2 + I_OUT (Eq. 6).
  - Boost mode: ΔI = V_INmin·D_Boost/(F_SW·L) (Eq. 8); I_SWmax = ΔI/2 + I_OUT/(1 − D_Boost) (Eq. 9).
  - "Derive the maximum switch current for both cases. Use the greater of the two."
  - — [TI SLVA535B](https://www.ti.com/lit/pdf/slva535)
- **[PRACTICE] TI copper and via rules of thumb (AN-1149, SNVA021C §5, p2).**
  - "It is good practice on a standard PCB board to make the traces an absolute minimum of 15 mils (0.381mm) per Ampere."
  - "It is good practice to use one standard via per 200 mA of current if the trace will need to conduct a significant amount of current from one plane to the other."
  - "Make all of the power (high current) traces as short, direct, and thick as possible."
  - — [TI SNVA021C](https://www.ti.com/lit/pdf/snva021)
- **[PRACTICE] IPC-2221 fallback formula.** I = k·ΔT^0.44·A^0.725 (A in mil²), with k = 0.048 external and 0.024 internal. The IPC-2221 standard itself was not accessed; this is a secondary source. — [Sierra Circuits IPC-2152 article](https://www.protoexpress.com/blog/how-to-optimize-your-pcb-trace-using-ipc-2152-standard/)
- **[PRACTICE] IPC-2152 context (M. Jouppi, chair, "The Value of IPC-2152", IPC paper).**
  - "The IPC-2221 internal conductor sizing chart … actually represents a conductor in free air."
  - "The old charts oversize conductors."
  - The IPC-2152 baseline "is a 0.07-inch thick, polyimide printed circuit board, suspended in vacuum and free air."
  - "reducing the board thickness from the baseline increases conductor temperature rise."
  - "The presence of thermal (copper) planes for heat spreading have one of the most significant impacts on lowering conductor temperature rise."
  - A secondary summary adds that under IPC-2152 "internal traces can carry higher currents, which are close to external traces".
  - — [Jouppi, IPC](https://www.electronics.org/system/files/technical_resource/E7&S22_03.pdf); [Sierra Circuits](https://www.protoexpress.com/blog/how-to-optimize-your-pcb-trace-using-ipc-2152-standard/)
- **[MFR-REC] Inductor rating.** DFE21CCN1R0MELL is rated 2700 mA (the thermal rating, the lower of its two) with 0.060 Ω max DCR. — [Murata JTE243A-0052](https://search.murata.co.jp/Ceramy/image/img/P02/JTE243A-0052.pdf)
- **[PROJECT] Project brief.**
  - 0.6 A at 3.3 V is "a planning case, not a guaranteed maximum". Evaluate "low-battery current, converter peak inductor/switch currents, neckdowns … LX routing is not sized merely from the average radio current" (line 207).
  - Trunks: "Polygon or 0.8–1.0 mm starting corridor"; local branches 0.30–0.50 mm (lines 114–115).
  - "do not assign a universal amperage rating to a via" (line 223).
  - The project power-tree doc lists VSYS as 3.0–5.0 V; the task statement says 3.0–4.2 V.
  - — [Project brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md); [power-tree doc](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/01_power_tree_design.md)

### Inferences
All figures below are my calculations with the equations cited above. "Typ" assumes η 0.9, f 2.2 MHz and L 1.0 µH. "Corner" assumes η 0.85, f_min 1.8 MHz and L −20 % (0.8 µH).

**Peak currents**

| Case (I_OUT 0.6 A, V_OUT 3.3 V) | Data-sheet Eq. 2/3 | SLVA535B |
|---|---|---|
| Boost, V_IN 3.0 V | 0.795 A typ (0.802 A at f 2.0 MHz); 0.871 A corner | 0.857 A typ; 1.013 A corner |
| Boost, V_IN 2.7 V (sensitivity: low battery / VSYS sag) | 0.926 A typ; 1.033 A corner | 0.977 A typ; 1.148 A corner |
| Buck, V_IN 4.2 V | not given | 0.779 A typ (ΔI 0.36 A); 0.889 A corner (ΔI 0.58 A) |
| Buck, V_IN 5.0 V (project doc VSYS max) | not given | 0.883 A typ; 1.058 A corner |

**Average and RMS currents**
- VSYS input, average: 0.733 A (3.0 V, η 0.9); 0.776 A (η 0.85); 0.815–0.863 A at 2.7 V; 0.52–0.56 A at 4.2 V.
- In boost mode the input current equals the inductor current, so it is continuous on VSYS.
- In buck mode at 4.2 V the input current is pulsed: Q1 RMS is about 0.53 A and CIN RMS about 0.25 A. That pulsed current stays inside the CUP4_1–IC loop.
- COUT RMS in boost mode at 3.0 V is about 0.19 A.
- LX RMS is about 0.6–0.78 A.
- Inductor margin: TI's +20 % rule applied to 0.87–1.03 A calls for about 1.05–1.24 A. The DFE21's 2.7 A / 3.3 A ratings clear that easily. Only a current-limit event (≤ 3.35 A DC-tested, "somewhat higher" in operation) approaches the 3.3 A inductance-drop rating.

**Design current.** Size continuous-current copper for **1.0 A**. That covers the 2.7 V / η 0.85 input case with margin. Treat 2.6–3.35 A+ as a short fault or start-up peak, limited by current limit and thermal shutdown. Paths must not neck down to single thin traces or single vias. The layout is not expected to carry that current continuously; IPC-2221 would need 1.59 mm of 1 oz outer copper at 10 °C rise for 3.35 A.

**Minimum widths for 1 A**

| Layer | TI 15 mil/A | IPC-2221, ΔT 10 °C | IPC-2221, ΔT 20 °C | Internal with the external k (IPC-2152-style bound, not a chart value) |
|---|---|---|---|---|
| L1 / L4, 35 µm | 0.38 mm | 0.30 mm | 0.20 mm | — |
| L3, 17.5 µm | 0.38 mm (TI does not distinguish layers) | 1.56 mm | 1.03 mm | 0.60 mm (10 °C); 0.39 mm (20 °C) |

For 0.8 A the corresponding figures are:
- 0.30 mm (TI rule).
- 0.22 mm (IPC-2221 external, 10 °C).
- 1.15 mm (IPC-2221 internal, 10 °C).

**Recommendations**
- **VSYS → CUP4_1 / pin 4:** L1 polygon or ≥ 0.8–1.0 mm (brief). If carried on L3, ≥ 1.0–1.6 mm or a polygon.
- **3V3_DIG trunk from CUP4:** the same.
- **LX:** width is limited by the 0.3 mm pad; keep it about 1 mm long, which is only about 1.6 mΩ.
- **Voltage drop.**
  - Sheet resistance is about 0.49 mΩ/□ on L1 and about 0.98 mΩ/□ on L3 (ρ(Cu) = 1.72 µΩ·cm).
  - A 0.5 × 10 mm L1 trace is 9.8 mΩ, i.e. 8.6 mV at 0.87 A.
  - A 1 × 20 mm L3 trace is 19.7 mΩ, i.e. 11.8 mV at 0.6 A.
  - Drops of this size matter to the 300 mV LDO headroom (Section 3).
- **Vias.**
  - Assuming 20–25 µm plating (confirm with the fab), a 0.3 mm-hole via has about 0.020–0.026 mm² of copper. That equals about 0.57–0.73 mm of 35 µm trace width. Full-length resistance through ~1.17 mm is about 0.8–1.0 mΩ.
  - TI's "1 via / 200 mA" rule means ≥ 5 vias for any 1 A VSYS/3V3_DIG layer change, and 3 for 0.6 A branches.
  - GND at the hot-loop capacitors follows Fig 7-24 (up to 6 per pad) as space allows.
  - This is more conservative than barrel cross-section alone, and it is consistent with the brief's refusal to give vias a universal amp rating.

### Gaps
- TI gives no TPS631000-specific trace widths or via counts.
- The IPC-2152 charts and board-thickness/plane modifiers were not accessed (paywalled). The internal-layer "IPC-2152-style" number above is a bound, not an IPC-2152 chart value.
- Via plating thickness and the board's final outer copper thickness after plating are unknown (fab data needed).
- The real VSYS range is uncertain: the brief says about 3.0–4.2 V, the project doc says 3.0–5.0 V. It depends on the BQ24072T power path and low-battery cutoff, which were not researched here.
- The data sheet gives no numeric value for the start-up inrush clamp I_L(lim_SS).
- Efficiency at 0.6 A and 3.0 V input was assumed (0.85–0.9), not read from the curves.

## 3. TPS7A2030 (UP3) layout: capacitor placement, ground return, PSRR when fed from the switching 3V3_DIG rail, distributing 3V0_ANA to the analog bank

### Takeaway
TI's DBV guidance is simple: CIN and COUT as close as possible, with a shared GND copper area at GND pin 2 (Fig 7-7), plus copper planes and thermal vias. Thermal needs are trivial here.

The hard constraints:
- CIN ≥ 1 µF (≥ 0.47 µF effective recommended).
- **COUT 1–200 µF with ESR ≤ 100 mΩ.** This must count all capacitance on 3V0_ANA.
- V_IN ≥ V_OUT(nom) + 0.3 V.
- An input "well regulated and free of spurious noise".

Near the 2 MHz switching frequency, PSRR is only about 40–50 dB at light load, and about 30 dB at 300 mA with 0.3 V headroom. ADI's AN101 shows that wideband switching spikes pass straight through LDOs and through stray layout capacitance. So physical separation of 3V3_DIG/LX from 3V0_ANA and its distribution, over an unbroken L2, is the main defence. The layout cannot rely on the LDO alone.

### Cited Findings
- **[HARD] DBV pinout (pin table p4; Fig 7-7 p31).** IN 1, GND 2, EN 3, N/C 4 ("No internal electrical connection"), OUT 5. — [TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)
- **[HARD] Recommended operating conditions (§5.3, p5).**
  - C_IN 1 µF. Note 2: "An input capacitor is not required for LDO stability. However, an input capacitor with an effective value of 0.47 μF minimum is recommended …"
  - C_OUT 1 µF min, 200 µF max.
  - Output capacitor ESR ≤ 100 mΩ.
  - §7.1.1 p27: expect effective capacitance to "decrease by as much as 50%"; the recommended values "account for an effective capacitance of approximately 50% of the nominal value".
  - — [TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)
- **[HARD] Supply recommendations (§7.3, p31).**
  - "The input supply must be well regulated and free of spurious noise."
  - "the input supply must be at least V_OUT(nom) + 0.3V or 1.6V, whichever is greater. TI highly recommends using a 1μF or greater input capacitor to reduce the impedance of the input supply, especially during transients."
  - Output tolerance is ±1.5 % for DBV with V_OUT ≥ 2.8 V and V_IN ≥ V_OUT(nom) + 0.3 V.
  - Dropout (DBV, 2.5 V ≤ V_OUT < 5.5 V) is 145 mV max at 300 mA (p6).
  - — [TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)
- **[MFR-REC] Input capacitor sizing (§7.1.2, p27).** The input capacitor "is recommended if the source impedance is greater than 0.5 Ω". A larger one may be needed "if the device is located more than a few centimeters from the input power source". — [TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)
- **[MFR-REC] Layout Guidelines (§7.4.1, p31).**
  - "Place input and output capacitors as close to the device as possible."
  - "Use copper planes for device connections to optimize thermal performance."
  - "Place thermal vias around the device to distribute the heat."
  - The fourth bullet (no via under the thermal pad) applies to the DQN package only; the DBV has no pad. The thermal-pad text in §7.1.5 and the p32 diagrams also refer to other packages.
  - — [TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)
- **[MFR-REC] Layout example Fig 7-7 (p31), observed.**
  - CIN bridges the V_IN copper at pin 1 and a GND copper area.
  - COUT bridges the V_OUT copper at pin 5 and GND copper.
  - GND pin 2 sits in the GND copper that connects both capacitor grounds.
  - Enable is a separate trace to pin 3.
  - No vias or dimensions are shown.
  - — [TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)
- **[HARD] PSRR specification (Electrical Characteristics, p7).**
  - At 20 mA, V_IN = V_OUT + 1.0 V: 95 dB at 100 Hz, 95 dB at 1 kHz, 75 dB at 10 kHz, 75 dB at 100 kHz, **45 dB at 1 MHz**.
  - At 300 mA: 65 / 92 / 75 / 60 / **40 dB** at the same frequencies.
  - Output noise is 7 µV RMS (10 Hz–100 kHz, 300 mA).
  - — [TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)
- **[MFR-REC] PSRR typical curves (p18; values read by eye from the graphs, approximate; V_OUT 2.8 V).**
  - Fig 5-61 (20 mA, V_IN 3.1 / 3.3 / 3.8 V): PSRR is about 42–45 dB near 1 MHz and about 50 dB near 2 MHz. Headroom has little effect at this load.
  - Fig 5-62 (300 mA): with 0.3 V headroom (V_IN 3.1 V), PSRR falls to about 27–30 dB around 1–2 MHz, versus about 40 dB at 3.3 or 3.8 V.
  - Fig 5-63: PSRR near 1 MHz drops as I_OUT rises from 20 mA to 300 mA.
  - Fig 5-64 (20 mA): C_OUT of 10 µF or 200 µF gives higher PSRR in the 1–5 MHz range than 1 µF.
  - Fig 7-6 (p31, TPS7A2028 at 200 mA) dips to about 32 dB near 1–2 MHz.
  - — [TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)
- **[PRACTICE] ADI/LT AN101 (Jul 2005), "Minimizing Switching Regulator Residue in Linear Regulator Outputs":**
  - "all linear regulators encounter some difficulty with ripple and spikes, particularly as frequency rises."
  - "The regulator is better at rejecting the ripple than the very wideband spikes"; "Switching Spike Harmonic Content Approaches 100MHz; Passes Directly From Input to Output."
  - "Stray layout capacitance provides additional unwanted feedthrough paths."
  - "Ground potential differences, promoted by ground path resistance and inductance, add additional error."
  - A ferrite bead "immediately precedes CIN2", and a second bead at the regulator output before COUT, cut the spike to 900 µV, "almost 20× lower than without the ferrite beads".
  - — [ADI AN101](https://www.analog.com/media/en/technical-documentation/application-notes/an101f.pdf)
- **[PRACTICE] AN-1149 scope (SNVA021C p3).** Its guidelines "are also useful for linear regulators, that also use a feedback control scheme, that are used in conjunction with switching regulators". — [TI SNVA021C](https://www.ti.com/lit/pdf/snva021)
- **[PROJECT] Project documents.**
  - 3V0_ANA = TPS7A2030 fed "from 3V3_DIG". It supplies 5 electrode boards over FFC, the AFE, and STM32 VDDA/VREF+.
  - It was chosen to give "300 mV of headroom — exactly TI's lowest characterised PSRR condition".
  - Load ≈ 5 × (AD8237 0.575 mA + AD8648), "well under the 300 mA rating".
  - Brief: the LDO sits at the power/analog boundary (line 141); keep "the 3V0_ANA feed away from the SPI/power corridor" (line 179); VREF+ = 3V0_ANA (line 279).
  - Some older lines in the power-tree doc still say "TPS7A2033 … 3.3 V". The BOM says TPS7A2030PDBVR.
  - — [power-tree doc](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/01_power_tree_design.md); [Project brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)

### Inferences

**Checklist for UP3:**

- **Headroom is at the 0.3 V limit with no margin.**
  - The TPS631000's V_FB tolerance alone (±1 %) can put 3V3_DIG at 3.267 V, i.e. 0.267 V headroom. Divider tolerance and IR drop between CUP4 and UP3's IN pin reduce it further.
  - Regulation should still hold at the tens-of-mA analog load, since dropout scales down from 145 mV at 300 mA. But PSRR is only characterised down to 0.3 V headroom.
  - So feed UP3 with a short, low-resistance 3V3_DIG branch taken at or near CUP4. Do not take it from the far end of the digital/radio distribution. Budget ≤ ~10 mV of IR drop (see Section 2 resistances).
- **Keep LDO input and output copper apart.**
  - Do not run 3V3_DIG (LDO input) and 3V0_ANA (output) in parallel or adjacent: AN101 notes stray capacitance bypasses the LDO.
  - Do not route 3V0_ANA near LX1/LX2, L1 or the CUP4_1/CUP4 hot loops, or through the SPI corridor.
  - Run 3V0_ANA on L1, or on L3 over the continuous L2, as a trunk or star from UP3's COUT to the AFE bank and the MCU VDDA/VREF+ corner, with local decoupling at each load.
- **Ground.** Put UP3's GND pin, CIN and COUT on a shared L1 GND copper area (Fig 7-7) with vias to L2 right there. Keep those vias away from the TPS631000 via field (AN-139 on quiet vias).
- **Total output capacitance.** Count all capacitance on 3V0_ANA, including AFE bypasses, VDDA/VREF+ capacitors and electrode-board capacitors reached through the FFC. It must stay ≤ 200 µF with ESR ≤ 100 mΩ. Larger C_OUT (≥ 10 µF) near UP3 helps MHz-range PSRR (Fig 5-64).
- **Expected attenuation.** A 20 mV ripple on 3V3_DIG (the TPS631000's "< 20mV" ripple claim, p1) attenuated by about 45 dB gives about 0.1 mV at 3V0_ANA. That is before downstream filtering and excluding spikes. Because VREF+ = 3V0_ANA, the residue reaches the ADC reference directly.
- **Optional ferrite beads (schematic change, not routing).** AN101's bead before CIN, and possibly at the output, would need its own stability and transient check. The TI data sheet does not require it.
- **Thermal.** Dissipation is about 0.3 V × tens of mA, i.e. milliwatts, so no thermal copper is needed. If the MODE pin puts the TPS631000 in power-save mode at light load, some ripple energy moves to lower frequencies. There the TPS7A20's PSRR is 75–95 dB, which is favourable.

### Gaps
- TI gives no PSRR curve for V_OUT = 3.0 V at 0.3 V headroom and the actual (tens-of-mA) load at 2 MHz. The values above are read from 2.8 V curves and are approximate.
- TI gives no guidance on distributing an LDO output to multiple remote loads: trace impedance, star versus trunk, or capacitor distribution.
- Fig 7-7 has no vias or dimensions.
- It was not verified which BOM capacitors (CUP5_1/CUP5_2 1 µF 0402, CUP5_3/CUP5_5 10 µF 0805) sit at UP3's IN and OUT; the schematic/netlist was not reviewed.

## 4. TPS3808G33 (U_UV1, CT open) and LTC2954-1 (U_EN1): layout notes, timing pins, pull-ups, noise susceptibility, keep-away from switch nodes

### Takeaway
**TPS3808 (current rev. N, Aug 2026):**
- Make a low-impedance VDD connection with 0.1 µF at the VDD pin.
- With CT open (20 ms), minimise parasitic capacitance on CT. A capacitor ≥ 100 pF is detected as a timing capacitor, and stray capacitance shifts the delay.
- 1–10 nF on SENSE is "good analog design practice".
- The RESET pull-up must be ≥ 10 kΩ (10 kΩ–1 MΩ).

**LTC2954 (Rev B, 2011):** there is no layout section; the guidance is electrical.
- PB is a high-impedance input (100 kΩ to an internal ~1.9 V bias). Use a 5.1 kΩ + 0.1 µF R-C close to the PB pin when the switch is remote or the environment is noisy. Add a 10 kΩ pull-up to VIN if board leakage exceeds 2 µA.
- KILL has a 0.6 V threshold and 30 µs minimum pulse width. Add a bypass capacitor if glitches longer than 30 µs can occur.
- ONT and PDT are ±3 µA timing nodes (6.4 s/µF).

Neither data sheet gives a keep-away distance from switch nodes.

### Cited Findings
- **[HARD] TPS3808 threshold and pinout.**
  - TPS3808G33: nominal rail 3.3 V, threshold V_IT = 3.07 V (Table 4-1, p3).
  - DBV pinout: RESET 1, GND 2, MR 3, CT 4, SENSE 5, VDD 6 (Fig 5-1 / Table 5-1, p4).
  - — [TI SBVS050N](https://www.ti.com/lit/ds/symlink/tps3808.pdf)
- **[HARD] TPS3808 CT pin (Table 5-1 p4; §7.3.2 p11).**
  - "Connecting this pin to V_DD through a 40kΩ to 200kΩ resistor or leaving it open results in fixed delay times … Connecting this pin to a ground referenced capacitor ≥ 100pF gives a user-programmable delay time."
  - Open CT gives 20 ms.
  - "The capacitor C_T must be ≥ 100pF nominal value for the TPS3808xxx to recognize that the capacitor is present."
  - "stray capacitance around this pin can cause errors in the reset delay time."
  - — [TI SBVS050N](https://www.ti.com/lit/ds/symlink/tps3808.pdf)
- **[HARD] TPS3808 RESET output (Table 5-1 p4; §7.3.4 p12).** Open-drain. "A pull-up resistor from 10kΩ to 1MΩ should be used"; "The pullup resistor must be no smaller than 10kΩ." — [TI SBVS050N](https://www.ti.com/lit/ds/symlink/tps3808.pdf)
- **[MFR-REC] TPS3808 Layout Guidelines (§8.4.1, p15), quoted in full.** "Make sure the connection to the V_DD pin is low impedance. Place a 0.1-μF ceramic capacitor near the V_DD pin. If no capacitor is connected to the C_T pin, parasitic capacitance on this pin should be minimized so the RESET delay time is not adversely affected." Fig 8-3 (p16) is the "Layout Example for a 20ms Delay": C_IN at V_DD, CT unconnected, vias "used to connect pins for application-specific connections". — [TI SBVS050N](https://www.ti.com/lit/ds/symlink/tps3808.pdf)
- **[MFR-REC] TPS3808 SENSE, MR and supply.**
  - SENSE (§7.3.1, p10): "Good analog design practice is to put a from 1nF to 10nF bypass capacitor on the SENSE input to reduce sensitivity to transients and layout parasitics."
  - The device "is relatively immune to short negative transients on the SENSE pin"; immunity depends on overdrive (§8.2.2.1, p14; Fig 8-2, p15).
  - MR is "internally tied to V_DD using a 90kΩ resistor, so this pin can be left unconnected" (§7.3.3, p11).
  - "Use a low-impedance power supply to eliminate inaccuracies caused by current changes during the voltage reference refresh" (§8.3, p15).
  - — [TI SBVS050N](https://www.ti.com/lit/ds/symlink/tps3808.pdf)
- **[HARD] LTC2954 pinout and PB input (p2, p6; EC p3).**
  - TS8 pinout: VIN 1, PB 2, ONT 3, GND 4, INT 5, EN 6 (the -1 version is active-high), PDT 7, KILL 8.
  - PB: "An internal 100k pull-up resistor connects to an internal 1.9V bias voltage"; ±10 kV HBM; it may be pulled up to 26.4 V.
  - PB threshold 0.6 / 0.8 / 1.0 V; open-circuit voltage 1 / 1.6 / 2 V.
  - — [ADI 2954fb](https://www.analog.com/media/en/technical-documentation/data-sheets/2954fb.pdf)
- **[MFR-REC] LTC2954 PB routing.**
  - High Voltage Pins (p12): "if the pushbutton switch is physically located far from the LTC2954 PB pin, parasitic capacitances may couple onto the high impedance PB input. Additionally, parasitic series inductance may cause unpredictable ringing at the PB pin. Placing a 5.1k resistor from the PB pin to the pushbutton switch would mitigate parasitic inductance problems. Placing a 0.1μF capacitor on the PB pin would lessen the impact of parasitic capacitive coupling."
  - PB in a noisy environment (p13, Fig 8): "place an R-C network close to the PB pin. A 5.1k resistor and a 0.1μF capacitor should suffice for most noisy applications."
  - External pull-up (p14, Fig 9): if board leakage is ">2μA, the PB voltage may fall close to the threshold window … a 10k resistor to VIN is recommended."
  - — [ADI 2954fb](https://www.analog.com/media/en/technical-documentation/data-sheets/2954fb.pdf)
- **[HARD] LTC2954 ONT, PDT and KILL (p3, p6, p9, p13).**
  - ONT and PDT: a capacitor to ground adds "6.4 seconds/μF", with C = 1.56×10⁻⁴ µF/ms × (t − 1 ms). Floating gives the defaults of 32 ms (ONT) and 64 ms (PDT). Pull-up and pull-down currents are 2.4–3.6 µA.
  - KILL: threshold 0.57–0.63 V, 30 mV hysteresis, 30 µs minimum pulse width, 512 ms turn-on blanking. "If there are glitches on the resistor pull-up voltage that are wider than 30μs and transition below 0.6V, then an appropriate bypass capacitor should be connected to the KILL pin."
  - — [ADI 2954fb](https://www.analog.com/media/en/technical-documentation/data-sheets/2954fb.pdf)
- **[MFR-REC] LTC2954 EN and VIN (p6, p12, p14).**
  - EN (-1): "This pin can connect directly to a DC/DC converter shutdown pin that provides an internal pull-up. Otherwise a pull-up resistor to an external supply is required." The TPS631000 EN has no internal pull-up and must not float (Section 1).
  - Typical applications show 0.1 µF on VIN (Figs 5–7).
  - Reverse-battery protection: "place a 1k resistor in series with the VIN pin" (Fig 10, p14).
  - The Rev B data sheet contains no layout section or layout example.
  - — [ADI 2954fb](https://www.analog.com/media/en/technical-documentation/data-sheets/2954fb.pdf); [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)
- **[PROJECT] Project brief (line 211).** "put small timing/control components close to their ICs and away from LX/SPI. Preserve SYS_EN versus KILL_CTRL; CT stays intentionally open." — [Project brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)

### Inferences

**Checklist for U_UV1 and U_EN1:**

- **U_UV1 CT (pin 4).**
  - No trace, no stub and no test pad. Keep normal polygon clearance around the pad.
  - A few pF of stray capacitance is far below the 100 pF detection level, but TI still says "minimized".
- **U_UV1 VDD.** C_UV_BYPASS goes at pin 6 with a short via to L2.
- **U_UV1 SENSE (pin 5).**
  - Tap the monitored rail at a quiet point, not in the TPS631000 LX/CIN area.
  - The BOM shows no dedicated 1–10 nF SENSE capacitor. Check whether SENSE is tied to VDD and whether the 100 nF also serves SENSE.
- **U_UV1 MR.** Leave it unconnected or keep it short, because it is a weak 90 kΩ pull-up node.
- **U_UV1 RESET.** Check that its pull-up is ≥ 10 kΩ.
- **U_EN1 part mapping (to confirm in the schematic).**
  - C2_EN1 (33 nF) matches the data sheet's ONT example (0.033 µF, +211 ms).
  - C3_EN1 (330 nF) is plausibly PDT (+2.11 s).
  - C1_EN1 (100 nF) is plausibly the VIN bypass or the PB capacitor.
  - R_EN1_1 (1 kΩ) is plausibly the VIN series resistor (Fig 10) or a PB series resistor.
  - R_EN1_BIAS (10 kΩ) is plausibly the PB pull-up to VIN (Fig 9).
- **U_EN1 placement.** Put the ONT and PDT capacitors at pins 3 and 7 with the shortest loop to GND pin 4. They are ±3 µA nodes, so leakage and coupling shift timing.
- **PWR_BTN_N.** The button is at an enclosure-dictated location, so the PB trace may be long. Put the R-C at the PB pin end, not the button end, and route PB away from LX and SPI.
- **EN, INT and KILL.** These are high-impedance logic nets (100 kΩ / 10 kΩ pull-ups). EN drives the TPS631000's EN, whose thresholds are 0.77–1.2 V with 300 mV hysteresis. Keep these nets off the LX side of UP2 and do not run them parallel to LX or the inductor.
- **Why distance still matters.** Coupled 2 MHz spikes are much shorter than KILL's 30 µs filter and the debounce timers. Continuous coupling into CT, ONT or PDT could still bias timing. Distance and the L2 shield are the only defences either data sheet leaves open.

### Gaps
- LTC2954 Rev B has no layout guidance, and no ADI layout note for it was found. ADI's product page returned HTTP 403, so a newer revision could not be ruled out beyond the 2026-09-16 archive.
- The LTC2954 data sheet is internally inconsistent on PB's internal bias: the pin text says 1.9 V, the block diagram 2.4 V, and the EC open-circuit voltage is 1–2 V.
- Not verified from the schematic: which rail U_UV1 SENSE monitors (its 3.07 V threshold suggests 3V3_DIG or VSYS; the power-tree doc does not say), and the net assignments of the C/R_EN1 parts.

## 5. Separating the switching converter from sensitive analog: minimum distances, what must not run under the inductor or switch node, and whether L2 must stay unbroken under the switcher

### Takeaway
No TI, ADI or Murata document reviewed gives a numeric minimum distance between a switcher and analog circuitry. The consistent manufacturer guidance is:
- Make switch nodes and hot loops as small as possible.
- Keep FB, sense and other noise-sensitive traces away from the high-di/dt loops and high-dv/dt nodes, ideally on the other side of a ground plane (for FB, on the side opposite the inductor).
- Keep **layer 2 solid directly under the hot loops**. AN-139: "Keep the layer 2 shield solid". Its data shows a 0.12–0.13 mm plane spacing cutting loop inductance from 187 nH to 13 nH.
- Put quiet-ground vias away from the hot loop.

The project brief's own numbers are project rules, not manufacturer numbers: ≥ 0.5–1.0 mm routing separation and a placement goal of "several millimetres".

### Cited Findings
- **[MFR-REC] TPS631000 (§7.4.1, p18).** "The sense trace connected to FB is signal trace. Keep these traces away from LX1 and LX2 nodes." In Fig 7-24 the only copper near the inductor is the LX1/LX2 connections and the VIN/VOUT/GND power copper. — [TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)
- **[PRACTICE] TI SLVAFJ3 §2.1 (p3).** "optimize the surface areas of high dv/dt nodes, and keep the noise-sensitive traces away from the noisy (high di/dt and high dv/dt) portions of the circuit and minimize thier loop areas." — [TI SLVAFJ3](https://www.ti.com/lit/pdf/slvafj3)
- **[PRACTICE] TI SLVAFJ3 §2.5–2.6 (p7).**
  - "Separate power and signal traces, and use a ground plane to provide noise shielding."
  - "Use an internal layer or layers as ground plane or planes. Pay particular attention to shielding the feedback (FB) trace from power traces and components."
  - §2.6 recommends separate AGND and PGND joined at one point. That was written for the LM5177, which has separate AGND and PGND pins. The TPS631000 has a single GND pin, and the project mandates one GND net.
  - — [TI SLVAFJ3](https://www.ti.com/lit/pdf/slvafj3); [Project brief line 98](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)
- **[PRACTICE] TI AN-1149 (SNVA021C §1, §2, §5, p2).**
  - Use a closed-core, low-EMI inductor. Open-core parts should be "located a bit more away from the low power traces and components."
  - FB trace "as far from the inductor and noisy power traces as possible … on the side of the PCB opposite of the inductor with a ground plane separating the two."
  - "For multi-layer boards with more than two layers, a ground plane can be used to separate the power plane (where the power traces and components are) and the signal plane (where the feedback and compensation and components are)."
  - Ground planes absorb "more of the EMI radiated by the inductor".
  - — [TI SNVA021C](https://www.ti.com/lit/pdf/snva021)
- **[PRACTICE] ADI AN-139 Rev A: plane spacing and continuity.**
  - Table 1 (p2), for a 10 cm × 10 cm loop at 27 MHz: "The inductance of a single-layer loop of 187nH gets down to 13nH in the case of only 0.13mm insulation between the plane and loop traces."
  - p3: "A solid plane on the next layer in a multilayer board (four layers or more) will have over 3× less inductance than a normal 1.5mm 2-layer board with a solid bottom plane … A solid plane with minimum distance to the hot loop is one of the most effective ways to reduce EMI."
  - p3: the plane current "will produce as much voltage across the plane as is necessary to sustain the current. To the outside it will show up as GND bounce."
  - — [ADI AN-139](https://www.analog.com/media/en/technical-documentation/application-notes/an139f.pdf)
- **[PRACTICE] ADI AN-139 Rev A: vias, return path, sense lines and skin effect.**
  - p11: "The second layer from top is typically only about 200μm distance … Keep the layer 2 shield solid. Place vias away from the hot loop for connections to GND planes you want to keep quiet. The hot loop shield cancellation currents create HF voltage across the loop, and you do not want to couple it with vias in areas you need quiet. This current decays with distance, but often remains a problem."
  - p11: "If you can, let the return current flow in the closest layer. Make its dielectric (isolation) as thin as practical."
  - p9: place sense-loop traces "on the other side of a shielding plane from the high current loops".
  - p12: "Place filter inductors at a distance from the main inductor."
  - p16: "copper on typical PC-board material is affected by skin effect starting in the 5MHz to 50MHz range."
  - — [ADI AN-139](https://www.analog.com/media/en/technical-documentation/application-notes/an139f.pdf)
- **[PRACTICE] TI SSZTAE3 (p2).** "Smaller di/dt loops and smaller dv/dt nodes have lower parasitics and also radiate less. They are also more robust in the presence of external noise, as smaller loop areas couple less noise." — [TI SSZTAE3](https://www.ti.com/lit/pdf/ssztae3)
- **[MFR-REC] Murata article (16 Sep 2016), qualitative only.**
  - "In the case of the metal alloy inductor, there is little leakage of magnetic flux from either the top or the sides."
  - Metal-alloy inductors free designers "from having to take into account interference when laying out components on the board."
  - This is not a routing rule. TI's EVM BOM describes a DFE-family part (DFE252012P) as "Shielded, Metal Composite"; applying the article to DFE21CCN1R0MELL is an assumption.
  - — [Murata article](https://article.murata.com/en-eu/article/characteristics-of-compact-metal-alloy-power-inductors); [TI SLVUC09](https://www.ti.com/lit/pdf/slvuc09)
- **[PRACTICE] ADI AN101.** "Stray layout capacitance provides additional unwanted feedthrough paths" around a linear regulator. — [ADI AN101](https://www.analog.com/media/en/technical-documentation/application-notes/an101f.pdf)
- **[PROJECT] Project brief.**
  - "If routing density prevents continuous references, demonstrate the problem and propose six layers before cutting L2 apart" (line 96).
  - One GND net, with no AGND/DGND split, ferrite link or narrow joining bridge (line 98).
  - "seek at least 0.5–1.0 mm lateral routing separation … keep the switching cell several millimetres away from the quiet analog bank as a placement goal. These are not sufficient proof of noise rejection" (line 125).
  - "No arbitrary ground slit … Any local copper pullback for … switching-node coupling must be specifically justified" (line 227).
  - — [Project brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)

### Inferences

**Checklist for the switcher/analog boundary:**

- **L2 must be unbroken** under UP2, L1, CUP4, CUP4_1, the LX copper, and the path between the capacitor grounds and pin 7.
  - No L2 routing, no slots, no chains of overlapping antipads, no pullback.
  - The stack's 0.0994 mm L1–L2 prepreg is thinner than AN-139's 0.12–0.13 mm example, so L2 is a very effective image and return plane here, but only if it is continuous.
  - Any L2 cut near the switcher should be treated as stop-the-line under the brief's rule (line 96).
- **Under the inductor and switch node:**
  - On L1, nothing but the LX1/LX2 connections.
  - On L3/L4, avoid sensitive nets directly under L1/LX and under the hot loops: FB, 3V0_ANA, VREF, AFE, CT, PB, ONT/PDT, crystal and SPI.
  - Reason: at 2 MHz, copper's skin depth is about 47 µm (δ = √(ρ/(π·f·µ0))), thicker than the 17.5 µm L2. So L2's eddy-current magnetic shielding of the switching fundamental is only partial, while it is strong for the MHz-to-hundreds-of-MHz edge harmonics (AN-139 p16).
  - The shielded metal-alloy inductor lowers but does not remove this concern.
- **Quiet-ground vias** go outside the hot-loop via field: AFE, VREF, ADC, VDDA/VREF+ decoupling, and UP3's GND if placement allows. Do not let the TPS631000 hot-loop return share a narrow copper neck with analog returns (brief line 98).
- **Distances.** No manufacturer gives a number. Use the brief's ≥ 0.5–1.0 mm lateral separation as a floor, and avoid parallel runs.
  - Suggested (unsourced) for review: keep the analog-sensitive nets above completely out of the UP2/L1/CUP4/CUP4_1 footprint plus about 1–2 mm around LX and the inductor.
  - Keep 3V0_ANA and 3V3_DIG from running side by side.
- **Do not add an AGND/PGND split** because SLVAFJ3 §2.6 recommends one. It does not apply: the TPS631000 has one GND pin and the project uses one GND net. Separation is achieved by placement, same-layer power loops and via placement.

### Gaps
- No manufacturer document found gives a numeric minimum spacing between a switcher and analog nets, or quantifies coupling from a 2 MHz buck-boost into traces under a metal-alloy inductor.
- TDK's leakage-flux application note returned HTTP 403. No Murata FAQ on routing under power inductors was found. The Murata DFE21 reference drawing pages reviewed (ratings, p1) contain no wiring-under-part statement.
- No source quantifies the magnetic shielding of a 17.5 µm L2 plane at 2 MHz. The skin-depth argument above is an inference.
- AN-139 and AN-1149 are generic and older (2012 / 2013). No 2024–2026 TI document specific to TPS631000 separation or EMI was found.
