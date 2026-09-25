# Charger / USB-C input / ESD / fuel gauge / battery-NTC: PCB routing requirements (UP1 BQ24072T, J_USB_C USB4105-GF-A, D_VBUS PESD5V0S1BA, D_CC_ESD PESD5V0X2UT, UP4 MAX17048, R_TH_BAT 103AT-2)

Tags: **[HARD]** = the manufacturer says "must / do not / connect to". **[REC]** = a manufacturer layout recommendation (device datasheet, EVM guide or manufacturer app note). **[DATA]** = a manufacturer number used for sizing. **[N/A]** = guidance that does not apply to this design. **[PROJECT]** = a fact from the read-only project files. Page numbers are PDF page numbers. Derived numbers and applied checklist items appear only under "Inferences". They are engineering inferences, not manufacturer statements.

## 1. BQ24072T (UP1): IN/OUT/BAT capacitor placement, high-current paths, exposed-pad vias and via-in-pad treatment, ISET/ILIM/TMR/TS placement and quiet ground, thermal guidance

### Takeaway
TI's device-level layout guidance is qualitative:
- Place the IN and OUT ceramics (and BAT) as close as possible, with short runs to the thermal-pad ground.
- Keep low-current (programming/sense) grounds off the battery charge/discharge current paths.
- Size the charge paths for maximum current.
- Solder the exposed pad to ground. TI's device-specific RGT0016C example uses a 1.68 mm land, five Ø0.2 mm vias and 85 % paste, and says vias under paste should be filled, plugged or tented.

On this board the IN path carries at most 0.5 A, because EN2 = GND selects USB100/USB500. The OUT and BAT copper, however, must carry the whole system load when running on battery (planning figure about 1 A). Worst-typical charger dissipation is about 0.75–1.0 W, a junction rise of about 35–46 °C at the JEDEC RθJA of 45.8 °C/W.

### Cited Findings

#### Document basis and revision status (checked September 2026)
- TI BQ24072T/75T/79T datasheet **SLUS937C** (December 2009, revised December 2019). The appended RGT0016C mechanical drawing is **4222419/E (07/2025)**. The project copy was fetched from the TI symlink on 16 Sep 2026, so it is current, but the body text dates from 2019. — [TI SLUS937C](https://www.ti.com/lit/ds/symlink/bq24072t.pdf); [project source index](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/sources/analog_power/SOURCE_READING_INDEX.md)
- EVM user's guide **SLVU274E** (November 2008, revised January 2017). The ti.com/lit/pdf/slvu274 alias resolved to rev E on 24 Sep 2026: current but old, and it describes a 2-layer EVM. — [TI SLVU274E](https://www.ti.com/lit/ug/slvu274e/slvu274e.pdf)
- **SLUA271C**, "QFN and SON PCB Attachment" (June 2002, revised December 2023). The alias resolved to rev C on 24 Sep 2026. — [TI SLUA271C](https://www.ti.com/lit/an/slua271c/slua271c.pdf)
- **SLUSF65B**, the BQ25185 datasheet (revised August 2026). It is used only to corroborate TI's current layout practice for a similar power-path linear charger. — [TI SLUSF65B](https://www.ti.com/lit/gpn/BQ25185)

#### Pin/net map (project; verify against copper)
- [PROJECT] UP1 pin assignments:
  - 1 TS → R_TS_SER.2
  - 2, 3 BAT → VBAT_CELL
  - 4 CE → GND; 5 EN2 → GND
  - 6 EN1 → R_EN1_BIAS.2
  - 7 PGOOD → R_PGOOD
  - 8 VSS → GND
  - 9 CHG → LED_CHG.C
  - 10, 11 OUT → VSYS
  - 12 ILIM → R_LIM.2
  - 13 IN → VBUS
  - 14 TMR → R_TMR.2
  - 15 TD → GND
  - 16 ISET → RISET.1
  - 17 EP → GND

  The VBUS net also includes C_IN_.1, C_VBUS.2, D_VBUS.1, both J_USB_C VBUS pads and R_TS_TOP.2. VBAT_CELL also includes C_BAT.1, CU6_1.2, J_Li-Po.3 and UP4.2/3. — [project pin table](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/review_2026-09-16/power_evidence/power_pin_tables.md)
- [PROJECT] Component values:
  - C_IN_: 1 µF 16 V X7S 0402 (GRM155C71C105KE11D).
  - C_OUT_ and C_BAT: 10 µF 25 V X7S 0805 (GCM21BC71E106KE36L).
  - RISET 2.94 kΩ; R_LIM 3.48 kΩ; R_TMR 68.1 kΩ.
  - R_TS_TOP 33.2 kΩ; R_TS_BOTTOM 28 kΩ; R_TS_SER 100 kΩ.

  — [project BOM](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/ASSEMBLY_SNAPSHOT_20260924T023521434Z/MAIN_BOARD_COMPLETE_ASSEMBLY_BOM.csv)
- [DATA] Pin geography, top view:
  - Pins 1–4: TS, BAT, BAT, CE.
  - Pins 5–8: EN2, EN1, PGOOD, VSS.
  - Pins 9–12: CHG, OUT, OUT, ILIM.
  - Pins 13–16: IN, TMR, TD, ISET.

  ILIM sits between OUT and IN, TMR sits next to IN, and ISET sits next to TS. — [SLUS937C p4 §7](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)

#### Hard requirements (datasheet wording)
- [HARD] VSS: "Connect to the thermal pad and to the ground rail of the circuit." The thermal pad "must be connected to the same potential as the VSS pin on the printed circuit board. Do not use the thermal pad as the primary ground input for the device. VSS must be connected to ground at all times." — [SLUS937C p4–5, Pin Functions](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [HARD] "The package thermal pad must be soldered to the printed circuit board for thermal and mechanical performance." — [SLUS937C p41, RGT0016C drawing 4222419/E note 3](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [HARD] CE, EN1, EN2 and TD have internal pull-downs of about 285 kΩ, but must not be left unconnected. In the project, CE, EN2 and TD go to GND and EN1 goes through R_EN1_BIAS. — [SLUS937C p4–5](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [HARD] Programming-pin rules:
  - ISET: connect 590 Ω to 3 kΩ to VSS. Charging is disabled if ISET is open. While charging, the ISET voltage reflects the actual charge current.
  - ILIM: connect 1.07 kΩ to 7.5 kΩ to VSS. "Leaving ILIM unconnected disables all charging."
  - TMR: connect 18 kΩ to 72 kΩ to VSS. Connecting TMR to VSS disables all safety timers; leaving TMR open selects the default timers.

  — [SLUS937C p4–5](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [HARD] At power-up the device checks ISET and ILIM for shorts. It then turns on the IN–OUT FET at a 100 mA limit to check OUT for a short, and only then applies the EN1/EN2/RILIM limit. — [SLUS937C p31 §11.1, Fig. 36](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [HARD] Bypass and connection rules:
  - IN to VSS: 1–10 µF ceramic.
  - OUT to VSS: 4.7–47 µF ceramic.
  - BAT to VSS: 4.7–47 µF ceramic.
  - BAT connects to the battery positive terminal, OUT to the system load, IN to the DC supply.

  The p1 typical application shows 1 µF on IN and 4.7 µF on OUT and BAT. — [SLUS937C p1, p4](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [HARD] USB inrush: the input capacitance "must be selected small enough to prevent a violation (<10 μF), as this current is not limited." — [SLUS937C p20 §9.4.1](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)

#### TI layout recommendations
- [REC] §12.1 item 1: the IN-to-GND (thermal pad) decoupling capacitor and the OUT-to-GND (thermal pad) filter capacitors "should be placed as close as possible to the BQ2407xT, with short trace runs to both IN, OUT and GND (thermal pad)." — [SLUS937C p33 §12.1](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [REC] §12.1 item 2: "All low-current GND connections should be kept separate from the high-current charge or discharge paths from the battery. Use a single-point ground technique incorporating both the small signal ground path and the power ground path." — [SLUS937C p33 §12.1](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [REC] §12.1 item 3: the high-current paths into IN and out of OUT "must be sized appropriately for the maximum charge current in order to avoid voltage drops in these traces." No numeric width is given. — [SLUS937C p33 §12.1](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [REC] The thermal pad "is also the main ground connection for the device. Connect the thermal pad to the PCB ground connection." Full PCB guidance is deferred to SLUA271. — [SLUS937C p33](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [REC] Figure 37 (layout example):
  - IN, OUT and BAT capacitors sit immediately around the IC.
  - Each capacitor's VSS pad drops to one or two vias right at the pad.
  - The ISET and ILIM resistors sit directly beside their pins; the TS resistor sits just below.
  - Wide top-layer copper surrounds the IC, and a cluster of small vias sits inside the thermal pad.

  — [SLUS937C p33, Fig. 37](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [REC] TI's current wording for the analogous BQ25185 (August 2026):
  - The IN, SYS and BAT capacitors "must be placed as close as possible to the device".
  - "A solid ground plane tied to the GND pin and thermal pad must be used".
  - The TS/MR pushbutton GND "must be connected as close to the device as possible".
  - The IN/SYS/BAT paths are sized for maximum charge current.

  — [SLUSF65B p23 §7.4.1](https://www.ti.com/lit/gpn/BQ25185)
- [REC] EVM guidance:
  - The EVM "thermal design is optimized (8+ vias, 0.031-inch PCB, 2-oz. copper) to give θJA ~ 27°C/W".
  - Recommended input is 4.75–5.5 V, "with a preference toward the lower values"; above 5.5 V, dissipation rises and the part goes into thermal regulation.
  - The 45.2 × 44.8 mm EVM is two-layer, with a nearly continuous bottom pour (Figs 6–8).
  - The EVM BOM uses 10 µF 25 V X5R (C1, C4) and 10 µF 6.3 V X5R (C2, C3).

  — [SLVU274E p3, pp9–12](https://www.ti.com/lit/ug/slvu274e/slvu274e.pdf)

#### Exposed-pad land, thermal vias, via-in-pad treatment and stencil
- [REC] RGT0016C example land pattern (4222419/E):
  - Thermal land 1.68 × 1.68 mm.
  - 16 leads, 0.24 × 0.6 mm, at 0.5 mm pitch on a 2.8 mm lead-centre span.
  - Example via pattern: five Ø0.2 mm vias, one at the centre and four at 0.58 mm x/y offsets.
  - NSMD (preferred) with 0.07 mm solder-mask clearance.
  - Note 5: "Vias are optional depending on application, refer to device data sheet. If any vias are implemented, refer to their locations shown on this view. It is recommended that vias under paste be filled, plugged or tented."

  — [SLUS937C p42](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [REC] Example stencil: 0.125 mm thick; the pad-17 aperture is 1.55 × 1.55 mm, giving "85% printed solder coverage by area under package". Laser-cut trapezoidal walls with rounded corners are suggested; IPC-7525 may have alternatives. — [SLUS937C p43](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [REC] The PCB thermal pad should equal the exposed pad, with at least 0.2 mm pad-to-lead clearance. Published θJA assumes a JEDEC High-K four-layer board with thermal vias (JESD51-7). — [SLUA271C p7 §3.4](https://www.ti.com/lit/an/slua271c/slua271c.pdf)
- [REC] SLUA271C thermal-via guidance:
  - Via count: the vias in TI land patterns are "an example starting point. Not all applications require vias."
  - Thermally challenging applications: "thermal vias be placed on a pitch of approximately 1,0 mm … 0,3 mm diameter drill holes are recommended as a starting point, but a smaller via offers less risk of solder volume loss."
  - Plugged vias eliminate solder-volume loss; tenting "also can offer benefit".
  - Tenting from the top or back can cause chemistry entrapment in plating at some fabs. Back-side plugging or tenting can increase voiding because air is trapped.
  - Top tenting: "The via solder-mask diameter must be 0,1 mm larger than the via hole diameter." Top tenting is "less likely to produce random voids".
  - With an OSP finish, untented vias soldered repeatably. Excessive soak time produces large voids.

  — [SLUA271C p7 §3.4.1](https://www.ti.com/lit/an/slua271c/slua271c.pdf)
- [REC] Use NSMD pads. At 0.5 mm pitch, gang the solder mask around each row with 0.05 mm clearance or less, and round the inner corners. "TI recommends maintaining a routing and via keep-out area next to pin 1 on all QFN designs." — [SLUA271C p8 §3.5](https://www.ti.com/lit/an/slua271c/slua271c.pdf)
- [REC] Exposed-pad paste is "typically … approximately 50% to 70% of the pad area"; a 1:1 aperture can "float" the part and cause opens. Voiding should not exceed 50 % (verify by x-ray); 25 % is the point of diminishing thermal returns. — [SLUA271C p11 §4.4](https://www.ti.com/lit/an/slua271c/slua271c.pdf)
- [PROJECT] For the BQ thermal land, use a manufacturer- or assembler-qualified filled/capped, or approved tented/plugged/stencil, arrangement. "Open barrels can wick solder; tenting is not equivalent to filling." — [Master prompt §13](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)

#### Thermal data and TI thermal method
- [DATA] RGT thermal metrics: RθJA 45.8, RθJC(top) 53.6, RθJB 18.1, ψJT 1.1, ψJB 18.0, RθJC(bot) 5.2 °C/W. — [SLUS937C p7 §8.4](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [DATA] Thermal limits:
  - TJ(REG) is 125 °C; above it, charge current folds back.
  - TJ(OFF) is 155 °C, with 20 °C hysteresis.
  - Recommended TJ is 0–125 °C.
  - Operational charging life is reduced to 20,000 h at 1.5 A and 125 °C.

  — [SLUS937C p6, p9](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [REC] TI thermal method:
  - The power pad "should be directly connected to VSS".
  - Maximum dissipation occurs early in charge; use 3.4 V as the minimum battery voltage in the calculation.
  - Verify by plotting PCB-bottom temperature under the IC ("pad should have multiple vias"), charge current and battery voltage against time, starting from a fully discharged battery.
  - Dissipation: P = (VIN − VOUT)(IOUT + IBAT) + (VOUT − VBAT)·IBAT (Eq. 8).
  - Do not rely on thermal regulation under typical conditions.

  — [SLUS937C p34 §12.3](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [DATA] On the BQ24072T, OUT is regulated to VBAT + 225 mV, and clamped to 3.4 V when VBAT is below 3.2 V. — [SLUS937C p20 §9.4.1](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)

#### Current and programming numbers for copper sizing
- [DATA] Input-current modes and thresholds:
  - EN2 = 0 selects USB100 (IIN-MAX 90/95/100 mA) or USB500 (450/475/500 mA), depending on EN1.
  - The RILIM limit applies only with EN2 = 1 and EN1 = 0.
  - VIN-DPM in the USB modes is 4.35/4.5/4.63 V.
  - UVLO is 3.2–3.4 V; OVP is 6.4/6.6/6.8 V.

  — [SLUS937C p5 Table 1, p7](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [DATA] Absolute maximum ratings: IN −0.3 to 28 V; IN current 1.6 A; BAT charging current 1.5 A. Recommended operating conditions: IN 4.35–6.4 V; IIN up to 1.5 A; IOUT up to 4.5 A; IBAT (discharging) up to 4.5 A. The pin table on p4 instead says 4.35–6.6 V and "up to 26 V", a minor inconsistency inside the datasheet. — [SLUS937C p4, p6](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [DATA] Programming equations:
  - ICHG = KISET/RISET, with KISET 797/890/975 A·Ω.
  - tPRECHG = KTMR·RTMR and tMAXCHG = 10·KTMR·RTMR, with KTMR 35/45/55 s/kΩ.
  - KILIM is 1330/1512/1700 A·Ω for 200–500 mA.

  — [SLUS937C pp7–9, p15, p17, p26](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [DATA] Ceramic capacitors are tested at twice their rating, "so a 16 V capacitor may be adequate for a 30 V transient (verify tested rating with capacitor manufacturer)". — [SLUS937C p27 §10.2.1.2.8](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [PROJECT] Main VBUS/VBAT/VSYS trunks: "Polygon or 0.8–1.0 mm starting corridor", with drop and heating to be calculated. The power planning case is 0.6 A at 3.3 V, which means 0.52–0.86 A of converter input current from VSYS across 4.2–2.7 V at 85–90 % efficiency. — [Master prompt §7](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md); [ANALOG_POWER_LAYOUT_BASIS](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/work/analog_power/ANALOG_POWER_LAYOUT_BASIS.md)
- [N/A] SYSOFF exists only on the BQ24075T/79T (pin 15). On the BQ24072T, pin 15 is TD. — [SLUS937C p4–5](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)

### Inferences
**Programmed operating points:**
- RISET 2.94 kΩ gives ICHG ≈ 0.30 A (0.27–0.33 A).
- R_TMR 68.1 kΩ gives a precharge timer of about 51 min (40–62 min) and a fast-charge timer of about 8.5 h (6.6–10.4 h).
- R_LIM 3.48 kΩ is inactive with EN2 = GND, but it must stay fitted and routed: an open ILIM disables charging, and the part checks ILIM for shorts at start-up.
- The IN path therefore carries at most 0.5 A (USB500).

**Checklist for routed copper:**

1. **C_IN_ at UP1.13.** Keep pin 13 to C_IN_.1 as short as possible (about 1–2 mm). C_IN_.2 should return to the thermal-pad/VSS region through its own GND via(s) at the pad, as in Fig. 37. C_VBUS belongs at the connector (see §3); it is not the IN bypass. Total VBUS capacitance is 2 µF nominal against the 10 µF inrush ceiling, so do not add bulk capacitance on VBUS.
2. **C_OUT_ at pins 10/11 and C_BAT at pins 2/3.** Join each pair of pins at the pads and place each capacitor within about 1–2 mm. Drop each capacitor's GND pad to L2 with one or two vias right at the pad; L2 is only 0.0994 mm below L1.
3. **Current sizing.**
   - Size IN/VBUS for 0.5 A or more.
   - Size OUT (VSYS) and BAT (VBAT_CELL) for the full on-battery system current (about 1 A planning), not the 0.3 A charge current: when USB is absent, the BAT→OUT path carries the whole load.
   - Resistance per 10 mm of length (ρ = 1.724×10⁻⁸ Ω·m at 20 °C, 35 µm copper): 0.3 mm wide ≈ 16.4 mΩ; 0.5 mm ≈ 9.9 mΩ; 0.8 mm ≈ 6.2 mΩ; 1.0 mm ≈ 4.9 mΩ. Halve the copper to 17.5 µm (possible for inner L3; unverified) and the resistance doubles.
   - A 0.8–1.0 mm trunk on 1 oz L1 keeps the drop below about 10 mV per 10–20 mm at 1 A.
   - Use two or more vias at each layer change on these paths. Thin-wall estimates at 1.2 mm length with an assumed 25 µm plating: about 1.3 mΩ per 0.2 mm barrel and about 0.9 mΩ per 0.3 mm barrel.
4. **VSS (pin 8).** Give it its own low-impedance connection to GND: a short trace to the thermal pad and/or a GND via. Do not rely on the EP alone; TI forbids that. Tie CE (4), EN2 (5) and TD (15) to GND with short stubs to GND vias. Do not route traces through the 0.26 mm lead-to-EP gap; that gap is derived from the 2.8 mm span, 0.6 mm leads and 1.68 mm pad.
5. **Programming nodes.**
   - Put RISET at pin 16, R_LIM at pin 12, R_TMR at pin 14 and R_TS_SER at pin 1, each with its pin-side pad within about 1–2 mm of the pin.
   - Take each resistor's GND end by via to the IC-local ground (the EP/VSS area), not into the C_IN_/C_OUT_/C_BAT or TPS631000 return vias. This meets TI's "separate low-current GND" rule without splitting the plane. It also reconciles the old "single-point ground" wording with TI's newer "solid ground plane tied to the thermal pad" wording and with the project's one-GND rule.
   - Keep TMR free of leakage: a short to VSS disables the safety timers.
   - Keep LX, clock and I2C copper away from or under none of these nodes. R_LIM sits between the IN and OUT copper, so its ground return must not share the IN/OUT capacitor return.
6. **Thermal pad.**
   - The current four 0.45/0.2 mm vias are close to TI's example (five Ø0.2 mm vias at 0.58 mm offsets); adding the centre via would match it exactly.
   - SLUA271C's 1.0 mm pitch / 0.3 mm drill starting point would only fit a 2 × 2 array on a 1.68 mm land, so four 0.2 mm vias are consistent with both documents.
   - The deciding items are via treatment and paste. Specify filled/plugged vias (best), or top-tented vias with mask Ø = hole + 0.1 mm = 0.3 mm. Avoid back-side-only tenting.
   - Conflict to resolve with the assembler: the device-specific TI stencil example gives 85 % coverage (1.55 mm square), while SLUA271C's generic figure is 50–70 %. If vias are left open, use a windowed paste pattern that avoids the vias.
   - Keep a routing and via keep-out next to pin 1.
7. **Heat.**
   - Dissipation estimates (IIN at the 0.5 A limit, IBAT 0.30 A): about 0.76 W at VIN 5.0 V and VBAT 3.4 V; about 1.0 W at VIN 5.5 V; up to about 1.17 W at VBAT 3.0 V and VIN 5.5 V.
   - Junction rise is about 35 / 46 / 54 °C at 45.8 °C/W, or about 20–32 °C if the board approaches the EVM's 27 °C/W.
   - That is not a TJ(REG) risk at normal ambient, but about 1 W on an 80 × 45 mm board will warm its neighbours. Keep the AFE and reference parts (INA1–5, U1–U3, the VDiv/VREF components), the 32 kHz crystal and the cell footprint away from UP1.
   - Spread heat: tie the EP vias into L2 and an L4 pour under the IC, and add L1 GND copper around the IC as in Fig. 37. If L3 routing allows, add local GND-net copper on L3 under UP1 (same net, no split).
8. **L3 under UP1.** The EP vias pass through L3. Keep L3 power and signal copper clear of that via field, and do not route sensitive L3 nets through it.

### Gaps
- TI gives no numeric trace widths, capacitor distances, required thermal-via count for this power level, or minimum distance to heat-sensitive circuits. The EVM guide states "8+ vias" but gives no drill size or stack-up. TI's thermal check is empirical (p34) and must be measured on this board.
- The project footprint RGT0016C_V (EP size, paste aperture, via coordinates) was not compared against drawing 4222419/E in this research.
- Two things were not researched: whether the fabricator/assembler can build filled-and-capped 0.2 mm vias, and the actual copper weights of the stack (L1/L4 versus L3).
- The DC-bias effective capacitance of C_IN_ (0402, 1 µF, 16 V, X7S at about 5 V) was not checked against the datasheet's 1 µF minimum.

## 2. GCT USB4105-GF-A (J_USB_C): which pins carry VBUS/GND, shell and stake grounding, copper/vias for the charger input current, keep-outs

### Takeaway
GCT supplies the pinout, a recommended PCB layout (±0.05 mm) and current ratings: VBUS 5 A collectively, GND 6.25 A collectively, 0.25 A per other pin, with at most 30 °C shell temperature rise. It gives no rules for trace width, vias, shell grounding or copper keep-outs.

For this design:
- Both combined VBUS pads and both combined GND pads must be connected.
- All four shell stakes are GND.
- D+/D−/SBU stay isolated.

Because EN2 = GND caps the input at 0.5 A, VBUS/GND copper is sized by IR-drop headroom to VIN-DPM and by keeping ESD return loops local, not by ampacity.

### Cited Findings
- [DATA] Revision status: drawing **USB4105 Rev B4 (18 Dec 2023; drawing date 4 Oct 2019)** and product specification **Rev A3 (27 Feb 2023)**. Both were fetched on 16 Sep 2026 and are current. — [GCT drawing](https://gct.co/files/drawings/usb4105.pdf); [GCT spec](https://gct.co/files/specs/usb4105-spec.pdf)
- [DATA] Pin, signal and mating sequence:
  - A1, A12, B1, B12 = GND (mate first).
  - A4, A9, B4, B9 = VBUS (mate first).
  - A5 = CC1; B5 = CC2.
  - A6/B6 = D+, A7/B7 = D−, A8/B8 = SBU (all mate second).
  - SHELL = GND.

  — [GCT drawing B4, sheet 1 pin table](https://gct.co/files/drawings/usb4105.pdf)
- [REC] Recommended PCB layout (component-side view, tolerance ±0.05 mm):
  - One row of 12 SMT pads, 1.15 mm long, at 0.50 mm signal pitch.
  - Four pads are 0.60 mm wide: combined A1/B12 GND, A4/B9 VBUS, B4/A9 VBUS and B1/A12 GND. The other eight are 0.30 mm wide.
  - Row order: A1B12, A4B9, B8, A5, B7, A6, A7, B6, A8, B5, B4A9, B1A12.
  - Outer centre-to-centre spans: 6.40 mm (GND), 4.80 mm (VBUS), 3.50 mm (outermost signal pads).
  - Two Ø0.65 mm holes, 5.78 mm apart, not hatched as solder area.
  - Four shell-stake slots, 0.60 mm wide in 1.00 mm pads: two slots 1.70 mm long in 2.10 mm pads and two 1.40 mm long in 1.80 mm pads, 8.64 mm apart.
  - A PCB-edge datum is drawn.

  — [GCT drawing B4, "Recommended PCB Layout"](https://gct.co/files/drawings/usb4105.pdf)
- [DATA] Shell-stake length S: blank = 0.95 mm, -060 = 0.60 mm, -120 = 1.20 mm (the drawing shows 0.95 mm). The plug/receptacle mating view gives a 6.5 mm maximum plug dimension and a 1.85 mm minimum dimension. — [GCT drawing B4](https://gct.co/files/drawings/usb4105.pdf)
- [DATA] Ratings:
  - 5.00 A collectively on the VBUS pins; 6.25 A collectively on the GND pins.
  - 1.25 A on A5/B5; 0.25 A on each other pin.
  - 48 V DC.
  - Contact resistance 40 mΩ maximum initially, 50 mΩ after test.
  - −40 to +85 °C; 20,000 mating cycles.

  — [GCT drawing B4](https://gct.co/files/drawings/usb4105.pdf); [GCT spec A3 §4.1, §6.1.1](https://gct.co/files/specs/usb4105-spec.pdf)
- [DATA] Contact current test: 5 A collectively on the VBUS pins (1.25 A on VCONN), returned through the GND pins, with 0.25 A on each other contact. The temperature rise "shall not exceed 30°C at the outside surface of the shell". Revision A1 (October 2019) raised the rating from VBUS 3 A / GND 4.25 A to 5 A / 6.25 A. — [GCT spec A3 p3 §6.1.4, p11](https://gct.co/files/specs/usb4105-spec.pdf)
- [DATA] Reflow qualification profile: peak 255 °C (−0/+5), 60 s above 217 °C, 5 s above 250 °C. — [GCT spec A3 p6 §7.0](https://gct.co/files/specs/usb4105-spec.pdf)
- [PROJECT] Netlist:
  - Both VBUS pads (A4_B9, B4_A9) are on VBUS.
  - A1_B12, B1_A12 and SH1–SH4 are on GND.
  - A6/A7/A8/B6/B7/B8 have no other connection.
  - CC1 (A5) goes to D_CC_ESD.1 and RJ1; CC2 (B5) goes to D_CC_ESD.2 and RJ2.
  - RJ1 and RJ2 are 5.1 kΩ 1 % (RC0402FR-075K1L).

  — [project pin table](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/review_2026-09-16/power_evidence/power_pin_tables.md); [project BOM](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/ASSEMBLY_SNAPSHOT_20260924T023521434Z/MAIN_BOARD_COMPLETE_ASSEMBLY_BOM.csv)
- [PROJECT] USB-C is charge-only:
  - No D+/D− routing; D+/D− and SBU pads stay unconnected.
  - CC1 and CC2 keep independent pull-downs.
  - ESD returns stay local to the connector/power area rather than crossing the AFE.
  - D_CC_ESD, D_VBUS, RJ1/RJ2 and C_VBUS "must follow their pin nodes just inside the connector, with local GND vias".
  - On a board about 1.2 mm thick, the 0.60 mm stakes do not pass through, so a retention review is still open.

  — [Master prompt (early constraints; §12)](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md); [ANALOG_POWER_LAYOUT_BASIS](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/work/analog_power/ANALOG_POWER_LAYOUT_BASIS.md)
- [DATA] Charger input with EN2 = GND is at most 100 mA (USB100) or 500 mA (USB500). VIN-DPM is 4.35–4.63 V. The EVM guide recommends 4.75–5.5 V at the input. — [SLUS937C p5, p7](https://www.ti.com/lit/ds/symlink/bq24072t.pdf); [SLVU274E p3](https://www.ti.com/lit/ug/slvu274e/slvu274e.pdf)
- [REC] The preferred method is a chassis ground connection immediately adjacent to the TVS ground and the connector-shield ground. Where there is no chassis earth, "tightly coupled multiple layer ground planes can help keep ground shifts at Protected ICs to a minimum". — [SLVA680A p3](https://www.ti.com/lit/an/slva680a/slva680a.pdf)
- [N/A] The D+/D−/SBU pads are intentionally unconnected, so USB 2.0 90 Ω differential-pair and length rules and data-line TVS do not apply. The 1.25 A A5/B5 (VCONN) rating is irrelevant because the CC nets carry only pull-down current into RJ1/RJ2 here. — [project pin table](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/review_2026-09-16/power_evidence/power_pin_tables.md); [GCT drawing B4](https://gct.co/files/drawings/usb4105.pdf)

### Inferences
1. **Connect all combined pads.** Both VBUS pads (A4B9, B4A9) and both GND pads carry current in either plug orientation. Leave each used pad straight rearward (away from the PCB-edge datum), at pad width (0.60 mm for VBUS/GND, 0.30 mm for CC), before widening or turning. Pad-to-pad gaps are only 0.20 mm everywhere (derived from the drawing), so put no copper between pads and no vias in the pad row. Check that the 0.20 mm gaps leave a buildable solder-mask web.
2. **CC2 sits next to VBUS.** B5 (CC2) is directly next to the B4A9 VBUS pad, with a 0.20 mm gap. Turn CC2 away from VBUS immediately and inspect for bridges. A5 (CC1) is flanked only by the unconnected B8 and B7 pads.
3. **Unused pads.** Leave A6/A7/A8/B6/B7/B8 as bare pads with no stubs and no GND tie; nothing requires one.
4. **VBUS current and drop.** At 0.5 A, a 0.6 mm × 10–15 mm VBUS lead on 1 oz L1 is about 8–12 mΩ, a 4–6 mV drop. Taking the EVM's 4.75 V lower recommended input as the floor, there is only about 120 mV of headroom above the 4.63 V maximum VIN-DPM. The cable and the 40–50 mΩ contacts use most of that, so keep the PCB share small. Return GND through the L1 pour and several vias into L2 next to the GND pads.
5. **Shell grounding.**
   - Solder all four stake slots and put them on GND.
   - Stitch the L1 GND pour around the slots and GND pads to L2 and L4 with several 0.6/0.3 vias close to the pads.
   - Put the D_VBUS and D_CC_ESD ground vias in the same cluster, so ESD current returns to the connector ground without crossing the board.
   - Keep non-GND exposed copper and untented vias out from under the metal shell/body footprint.
   - With the -060 stake on a board about 1.2 mm thick, the solder joint is inside the slot only. The shell ground bond and mechanical retention need assembler qualification. A -120 variant exists; switching to it is a BOM decision.
6. **Keep-outs.**
   - Clearance around the two Ø0.65 mm holes (project copper-to-NPTH rule 0.50 mm).
   - Board-edge setback per the connector datum.
   - The plug overmold envelope near the board edge.
   - No AFE, clock, I2C or TS routing in the connector-to-TVS zone.
7. **Pad-joining trade-off.** The two VBUS pads are 4.8 mm apart, and CC1/CC2 exit between them. Joining VBUS on L1 directly behind the pad row would force CC through vias before its TVS, which SLVA680A discourages. A reasonable compromise:
   - Route the CC pads to D_CC_ESD on L1 with no vias; CC may via after the TVS.
   - Place D_VBUS on the L1 VBUS segment nearest the charger.
   - Tie the far VBUS pad in through two or more low-inductance vias and inner copper (SLVA680A "Case 3"-type compromise).

   Document whichever arrangement is chosen.

### Gaps
- GCT gives no guidance on trace width, vias, shell grounding (direct connection versus thermal relief), under-body copper keep-out, or plating. The recommendations above are general practice.
- The USB Type-C specification (Rd tolerance, CC capacitance, vSafe5V limits) was not reviewed.
- Whether the Ø0.65 mm holes are plated or unplated is inferred only from the drawing's hatch legend.

## 3. ESD protection layout (D_VBUS = Nexperia PESD5V0S1BA,115 SOD-323; D_CC_ESD = Nexperia PESD5V0X2UTR SOT-23)

### Takeaway
Both Nexperia datasheets and TI SLVA680A agree on the layout:
- Put the TVS as close to the connector as the design rules allow.
- Route the protected line from the connector pin straight onto the TVS pad, with no stub and ideally no via before the TVS.
- Keep unprotected traces out of the connector-to-TVS zone.
- Make the TVS ground as short as possible, with a GND via immediately at the TVS ground pad into a tightly coupled plane. At 8 kV, 0.25 nH of ground inductance adds about 10 V.

No manufacturer gives a numeric distance. There are two design flags (not layout items):
- The PESD5V0S1BA (VRWM 5 V, VBR 5.5–9.5 V) starts conducting inside the charger's 4.35–6.4 V operating range, and pre-empts the charger's 6.6 V OVP and 28 V tolerance.
- The PESD5V0X2UT is a snap-back device that must not be held by an unlimited DC source, and the CC2 pad sits next to a VBUS pad.

### Cited Findings
- [DATA] BOM: D_CC_ESD = **Nexperia PESD5V0X2UTR** (SOT-23, footprint SOT95P230X100-3N). D_VBUS = **PESD5V0S1BA,115** (SOD323). — [project BOM](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/ASSEMBLY_SNAPSHOT_20260924T023521434Z/MAIN_BOARD_COMPLETE_ASSEMBLY_BOM.csv)
- [DATA] Revision status: the PESD5V0S1BA/BB/BL product data sheet is **Rev. 04, 20 August 2009** (with a Nexperia © 2017 footer). It is old, but it is the current Nexperia asset, retrieved 24 Sep 2026. The PESD5V0X2UT product data sheet is dated **3 February 2021 (v.1)**. — [Nexperia PESD5V0S1BA](https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA_BB_BL.pdf); [Nexperia PESD5V0X2UT](https://assets.nexperia.com/documents/data-sheet/PESD5V0X2UT.pdf)
- [DATA] PESD5V0S1BA, per diode:
  - VRWM 5 V; IRM 5 nA typical, 100 nA maximum at 5 V.
  - Clamping voltage V(CL)R: 10 V maximum at IPP 1 A; 14 V maximum at IPP 12 A (8/20 µs).
  - V(BR) 5.5–9.5 V at 1 mA; rdif 50 Ω maximum.
  - Cd 35 pF typical, 45 pF maximum.
  - Bidirectional, protects one line; up to 130 W per line (8/20 µs).

  — [PESD5V0S1BA p5, p8](https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA_BB_BL.pdf)
- [REC] Nexperia "Circuit board layout and protection device placement":
  1. Place the protection device as close to the input terminal or connector as possible.
  2. Minimize the path length between the protection device and the protected line.
  3. Keep parallel signal paths to a minimum.
  4. Avoid running protection conductors in parallel with unprotected conductors.
  5. Minimize all PCB conductive loops, including power and ground loops.
  6. Minimize the length of the transient return path to ground.
  7. Avoid shared transient return paths to a common ground point.
  8. Use ground planes wherever possible; on multilayer boards, use ground vias.

  — [PESD5V0S1BA p8, "Application information"](https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA_BB_BL.pdf)
- [DATA] PESD5V0X2UT:
  - Pinning: pin 1 = K1 (cathode 1), pin 2 = K2 (cathode 2), pin 3 = CA (common anode).
  - VRWM 5 V; VBR 7.2/8.7/11 V at 1 mA; IRM 1 nA typical, 50 nA maximum.
  - Cd 0.76 pF typical, 0.9 pF maximum.
  - VCL 2.4 V at 8 A and 3.4 V at 16 A (TLP); Rdyn 0.12 Ω.
  - IPPM 10 A (8/20 µs); 22 kV IEC 61000-4-2 contact discharge; Tj up to 175 °C.

  — [PESD5V0X2UT pp1–4](https://assets.nexperia.com/documents/data-sheet/PESD5V0X2UT.pdf)
- [HARD] The PESD5V0X2UT uses a snap-back clamp: "Do not connect unlimited DC current sources to the data lines to avoid keeping the ESD protection device in snap-back state after exceeding breakdown voltage … Do not connect the signal lines to unlimited current sources like, for example, a battery." The datasheet also says to "give careful consideration to impedance matching and signal coupling". — [PESD5V0X2UT p6 §10](https://assets.nexperia.com/documents/data-sheet/PESD5V0X2UT.pdf)
- [REC] SLVA680A §2.1:
  - Place the TVS as near the connector as the design rules allow, and the protected IC much farther away (L4 ≫ L1).
  - No stub between the protected line and the TVS: "route directly from the ESD Source to the TVS", ideally with no vias in that path.
  - Minimize the TVS-to-ground inductance (L3), "perhaps … the most predominant parasitic".
  - At 8 kV (IEC 61000-4-2), dI/dt = 4×10¹⁰ A/s, so "even with 0.25 nH of inductance an additional 10 V is presented".

  — [SLVA680A p4](https://www.ti.com/lit/an/slva680a/slva680a.pdf)
- [REC] SLVA680A §2.2:
  - Treat the connector-to-TVS region as a keep-out for unprotected traces, including on any layer that a via in that path crosses.
  - Use straight, short routes; use curves, or 45° corners at most. A 90° corner is a strong EMI source and can arc at radii below about 2.6 mm in air during an 8 kV event.

  — [SLVA680A p5–6](https://www.ti.com/lit/an/slva680a/slva680a.pdf)
- [REC] SLVA680A §2.3: avoid vias between the connector and the TVS. If a via is needed, route from the connector to the TVS pin first and only then take the via. The note ranks Case 1 best, Case 2 worst, and Case 3 an acceptable compromise. — [SLVA680A p6–7](https://www.ti.com/lit/an/slva680a/slva680a.pdf)
- [REC] SLVA680A §2.4:
  - Connect the TVS ground pin to a same-layer ground plane that is coupled to a plane on the immediately adjacent layer, and stitch the planes with vias, "with one VIA immediately adjacent to the ground pin of the TVS" (Fig. 2-8 shows four stitching vias).
  - Make the GND-via pad and drill as large as possible, and do not break the plane near the GND via.
  - Connect to several plane layers.
  - Keep GND-via clearances to non-ground planes small; the extra capacitance lowers impedance.

  — [SLVA680A p7–8](https://www.ti.com/lit/an/slva680a/slva680a.pdf)
- [DATA] BQ24072T: IN tolerates up to 28 V (absolute maximum), with OVP at 6.4–6.8 V and an operating range of 4.35–6.4 V. The device HBM rating is ±2000 V. — [SLUS937C p6–7](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [PROJECT] Keep D_CC_ESD and D_VBUS next to their connector nodes, with short ground returns and nearby vias. Keep ESD return paths local to the connector/power area rather than across the AFE. — [Master prompt §12](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)
- [N/A] SLVA680A's BGA via-in-pad and chassis-screw examples (Figs 2-8/2-9) do not apply: these TVS parts are leaded SOD-323/SOT-23, and the wearable has no chassis earth. — [SLVA680A p8](https://www.ti.com/lit/an/slva680a/slva680a.pdf)

### Inferences
1. **VBUS order.** Route connector VBUS pad(s) → D_VBUS pin 1 (K1) pad, with the trace running onto or through the pad (no T-stub) → C_VBUS → trace → C_IN_ → UP1.13. Take R_TS_TOP's VBUS tap from the C_IN_/UP1.13 end, never from the connector-to-TVS segment.
2. **TVS grounds.**
   - Give D_VBUS pin 2 (K2) and D_CC_ESD pin 3 (CA) each at least one or two 0.6/0.3 GND vias touching or directly adjacent to the pad, into L2. L2 is 0.0994 mm below L1, so this is a very low-inductance path. Use the larger via size, as SLVA680A advises.
   - Tie the L1 GND pour to the connector GND pads and shell slots within a few millimetres.
   - Do not share TVS ground vias with converter or charger return vias, and do not let the ESD return pass through the AFE region.
3. **CC routing.** Route pads A5/B5 to D_CC_ESD pins 1/2 on L1 with no vias, then on to RJ1/RJ2; vias are acceptable after the TVS. Orient the SOT-23 so pins 1/2 face the connector and pin 3 faces the GND via cluster.
4. **Priority.** The CC nets end only in RJ1/RJ2; no IC hangs on CC in this charge-only design. D_CC_ESD therefore mainly limits arcing and coupling, so VBUS protection deserves layout priority where the two conflict.
5. **Snap-back hazard.** The CC2 pad is 0.20 mm from a VBUS pad. A 5 V short alone stays below VBR (7.2 V minimum). But a short combined with an ESD trigger, or any source above about 7.2 V, could hold the diode in snap-back from a multi-amp USB source. Board-level action: inspect B5 to B4A9 for bridges. Design-level: flag for review.
6. **D_VBUS design flag (not layout).** VBR minimum is 5.5 V, below the charger's 6.4 V minimum OVP. For a sustained input above about 5.5 V, the TVS would conduct and dissipate instead of the BQ simply disconnecting; the charger alone would survive up to 28 V. VRWM of 5 V also leaves little margin above a normal 5.0–5.25 V VBUS. Raise this in schematic review.
7. **C_VBUS as a charge sink.** A 1 µF C_VBUS right behind D_VBUS also absorbs ESD charge: 150 pF at 8 kV is 1.2 µC, which is about 1.2 V on 1 µF, ignoring ESL. Give C_VBUS its own adjacent GND via as well.
8. **Corners.** Use 45° corners or arcs on VBUS and CC between the pad and the TVS.

### Gaps
- No manufacturer states a numeric maximum TVS-to-connector distance or a required via count. Nexperia's general ESD application handbook was not reviewed.
- The USB Type-C requirements for CC voltage and capacitance, and for CC-to-VBUS short faults, were not reviewed.
- The exact PESD5V0S1BA ESD-rating table values (air and contact kV) were not captured precisely.

## 4. MAX17048 (UP4): CELL/VDD sensing (Kelvin at the battery terminal, avoiding charge-current IR drop), VDD bypass, exposed pad, I2C pull-ups

### Takeaway
On the MAX17048 the measured voltage is VDD-to-GND at the IC; CELL is not internally connected. The VDD branch and the GND return are therefore the Kelvin sense pair:
- Route VDD (together with CELL) as a dedicated low-current branch from the J_Li-Po VBAT_CELL pin.
- Return UP4 GND and EP to the plane near the battery-negative entry.
- Bypass VDD with 0.1 µF right at pins 3–4.
- Tie EP, CTG and QSTRT to GND.

ADI gives no PCB-layout section, and no rule on pull-up placement beyond "the system must provide pullup circuits".

### Cited Findings
- [DATA] Revision status: the MAX17048/MAX17049 datasheet is **19-6171 Rev 7 (11/16)**, current at ADI's URL on 16 Sep 2026 (the content dates from 2016). The EV kit document is **19-6239 Rev 0 (3/12)**. — [ADI MAX17048](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf); [ADI EV kit](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048EVKIT-MAX17049EVKIT.pdf)
- [HARD] TDFN pin requirements:
  - Pin 1 CTG: "Connect to Ground".
  - Pin 2 CELL: "Connect to the Positive Battery Terminal. MAX17048: Not internally connected."
  - Pin 3 VDD: "Power-Supply Input. Bypass with 0.1µF to GND. MAX17048: Voltage sense input. Connect to positive battery terminal."
  - Pin 4 GND: "Ground. Connect to negative battery terminal."
  - Pin 5 ALRT: open-drain, active-low.
  - Pin 6 QSTRT: "Connect to GND if not used".
  - Pins 7 SCL and 8 SDA: internal pull-downs for sensing disconnection.
  - EP: "Connect to GND."

  — [MAX17048 p6](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf)
- [DATA] "The MAX17048 measures VCELL between the VDD and GND pins." VCELL is the average of four conversions, updated every 250 ms in active mode and every 45 s in hibernate. — [MAX17048 p10](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf)
- [DATA] Electrical limits:
  - VDD 2.5–4.5 V.
  - Voltage error ±7.5 mV/cell at 3.6 V and 25 °C; ±20 mV/cell over −20 to +70 °C.
  - Resolution 1.25 mV/cell.
  - IDD 23 µA typical / 40 µA maximum active; 3–5 µA hibernate; 0.5–2 µA sleep.
  - Bus-low sleep timeout tSLEEP 1.75–2.5 s.
  - SCL/SDA/ALRT −0.3 to +5.5 V.

  — [MAX17048 p2](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf)
- [REC] Application guidance:
  - "In all cases, the system must provide pullup circuits for ALRT (if used), SDA, and SDL [sic]."
  - 1S host-side configuration: VDD powered directly from the battery, QSTRT to GND, ALRT to the system interrupt (Fig. 14, Table 3).
  - The only external part is the 0.1 µF VDD capacitor (p1 simple circuit, "Eliminates Current-Sense Resistor").

  — [MAX17048 p1, p14–15](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf)
- [DATA] Package T822+3; outline 21-0168; land pattern 90-0065. — [MAX17048 p18](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf)
- [REC] EV kit schematic (Fig. 3):
  - C3, 0.1 µF from VDD to GND at the IC.
  - CELL tied to PK+ through R3, which the component list gives as "Not installed, resistors—short (PC trace)"; C4 is open.
  - CTG, QSTRT, GND and EP go to ground.
  - 150 Ω series resistors plus 5.6 V zeners on ALRT/SCL/SDA, toward an off-board connector.
  - A 1 MΩ ALRT pull-up to VDD.

  — [EV kit p1 component list, p7 Fig. 3](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048EVKIT-MAX17049EVKIT.pdf)
- [PROJECT] Project connections:
  - UP4.2 CELL and UP4.3 VDD are on VBAT_CELL, with CU6_1 (100 nF 16 V X5R 0402).
  - UP4.1, UP4.4, UP4.6 and UP4.9 are on GND.
  - SCL/SDA are pulled up by a single pair, R_SCL/R_SDA (4.7 kΩ); ALRT by R_AL (10 kΩ).
  - Place the gauge near the battery connection with a short, quiet cell-sense/VDD route. No shunt is to be added, and the I2C pull-ups stay singular.

  — [project pin table](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/review_2026-09-16/power_evidence/power_pin_tables.md); [project BOM](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/ASSEMBLY_SNAPSHOT_20260924T023521434Z/MAIN_BOARD_COMPLETE_ASSEMBLY_BOM.csv); [Master prompt §12](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)

### Inferences
1. **Sense branch.** Tie pins 2 and 3 together at the IC and run one thin (0.15–0.25 mm) dedicated trace to the J_Li-Po pin-3 pad, or to VBAT_CELL copper at the connector before charger or converter current splits off. Do not tap C_BAT, UP1 BAT copper, or a VSYS/VBAT trunk. The branch carries at most 40 µA, so its own drop is negligible. By contrast, tapping 10 mm of shared 0.5 mm, 1 oz VBAT copper (about 9.9 mΩ) would add about 3 mV during a 0.3 A charge and about 10 mV at a 1 A discharge. That is comparable to the ±7.5 mV VERR.
2. **Ground return.** Return UP4 pin 4 and EP to L2 through a via close to the J_Li-Po pin-1 GND entry, outside the plane region that carries converter and charger return current back to the battery. Tie CTG and QSTRT to the same local ground.
3. **Bypass.** Place CU6_1 directly across pins 3 to 4 (adjacent pins on the same side), with a GND via right at the capacitor.
4. **Exposed pad.** Dissipation is about 0.1 mW, so no thermal-via array is needed. One GND via (tented or plugged to avoid solder wicking), or a top-copper tie to pins 1/4, is enough.
5. **I2C.**
   - One pull-up pair anywhere on the on-board bus is sufficient; near the MCU is typical.
   - The EV kit's 150 Ω/zener protection exists because its bus goes off-board to a cable. It does not apply on-board.
   - Keep SDA/SCL/ALRT away from LX, the antenna and TS.
   - Keep the pull-up rail at 5.5 V or less.
   - If 3V3_DIG collapses, the internal pull-downs hold the bus low and the IC sleeps after tSLEEP. This is a design note, not a layout item.
6. **Limits of Kelvin sensing.** The board can only Kelvin-sense to the connector. Harness and connector resistance still appears in VCELL under load, and layout cannot remove it.

### Gaps
- The MAX17048 datasheet has no layout section.
- Land pattern 90-0065 (EP size, via guidance) was not retrieved.
- The EV kit layout figures are too low-resolution to extract via or trace details.
- ADI makes no statement on I2C pull-up placement.

## 5. TS/NTC sensing: routing the remote 103AT-2 leads and noise on TS

### Takeaway
The BQ24072T TS input is a ratiometric window comparator: hot threshold 12.5 % of VIN, cold threshold 25 % of VIN, 1 % of VIN hysteresis, 50 ms deglitch. It is fed by a divider referenced to VIN, so:
- The divider must reference the IC's own IN and VSS nodes.
- The high-impedance TS pin node must be tiny.

TI gives no guidance on long thermistor leads or a TS filter capacitor. Keep the divider and R_TS_SER at UP1, and route BAT_TEMP with its own quiet ground to the R_TH_BAT pads, out of the USB-ESD and converter/antenna zones. Any filter capacitor would be a schematic change.

### Cited Findings
- [HARD] TS pin: "Connect the TS input to the center tap of a resistor divider from VIN to GND with the NTC in parallel with the bottom resistor." A series resistor (R8) "must be added to protect the IC from 28V inputs" when the top resistor (R6) is below 100 kΩ. The project uses R6 = R_TS_TOP 33.2 kΩ, R8 = R_TS_SER 100 kΩ, R7 = R_TS_BOTTOM 28 kΩ. — [SLUS937C p4, p20 Fig. 18](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [DATA] TS thresholds and behaviour:
  - VHOT 12/12.5/13 % of VIN; VCOLD 24.5/25/25.5 % of VIN; hysteresis 1 % of VIN on each.
  - Deglitch tDGL(TS) = 50 ms.
  - TS is monitored continuously during charging. Outside the VCOLD–VHOT window, charging is suspended and the timers pause; CHG stays low.

  — [SLUS937C p9 EC; p19 §9.3.12](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)
- [DATA] The "T" versions use a voltage-based TS bias; the non-T parts use a current-biased TS. — [SLVU274E p2](https://www.ti.com/lit/ug/slvu274e/slvu274e.pdf)
- [REC] TI's low-current-ground rule (§12.1 item 2) applies to the TS divider return. For the current BQ25185, TI asks that the TS/MR external element's GND be "connected as close to the device as possible". — [SLUS937C p33](https://www.ti.com/lit/ds/symlink/bq24072t.pdf); [SLUSF65B p23](https://www.ti.com/lit/gpn/BQ25185)
- [PROJECT] Remote NTC:
  - Exactly one Semitec 103AT-2 (10 kΩ at 25 °C) is fitted on the cell.
  - Two insulated leads run to R_TH_BAT: pad 1 = GND, pad 2 = BAT_TEMP.
  - J_Li-Po pin 2 is also on BAT_TEMP, but no pack NTC is used in this variant.
  - Route BAT_TEMP/TS quietly, away from LX and clock routes, and keep the 33.2 k / 28 k / 100 k values.

  — [project BOM](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/ASSEMBLY_SNAPSHOT_20260924T023521434Z/MAIN_BOARD_COMPLETE_ASSEMBLY_BOM.csv); [Master prompt §12](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md); [ANALOG_POWER_LAYOUT_BASIS](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/work/analog_power/ANALOG_POWER_LAYOUT_BASIS.md)
- [REC] Keep unprotected traces out of the connector-to-TVS area. BAT_TEMP/TS must not run through the USB ESD zone. — [SLVA680A p5](https://www.ti.com/lit/an/slva680a/slva680a.pdf)

### Inferences
1. **Divider references.** Take R_TS_TOP from the C_IN_/UP1.13 VBUS node and return R_TS_BOTTOM's ground at the UP1 VSS/EP area. The thresholds then track VIN as TI intends. At 5 V VIN, VHOT ≈ 0.625 V and VCOLD ≈ 1.25 V, with 50 mV hysteresis. A few millivolts of ground offset in the plane is small against that, but keep this return out of the battery-current corridor.
2. **TS node.** Keep the R_TS_SER.2 to UP1.1 node about 1–2 mm long. Its 100 kΩ source impedance makes it the most pickup-sensitive node in this section.
3. **BAT_TEMP routing.**
   - At 25 °C the BAT_TEMP node has about 6 kΩ source impedance (33.2 k ‖ 28 k ‖ 10 k) and sits at about 18 % of VIN, mid-window, so pickup is attenuated accordingly.
   - Route BAT_TEMP from the divider to R_TH_BAT pad 2 over unbroken L2, paired with the pad-1 GND return, and put the pad-1 GND via right at the pad.
   - Stay away from L1/LX, the SPI clock, the antenna and the USB connector ESD zone.
   - Avoid a long stub to J_Li-Po pin 2: either put J_Li-Po.2 on the route or keep its branch short.
4. **Harness.** Twist the two leads, run them away from the converter and antenna, and strain-relieve them. This is general practice; no Semitec or TI source was reviewed for it.
5. **Filtering.** Only the 50 ms digital deglitch is specified. Adding a TS capacitor (which would form τ = 100 kΩ × C) is a schematic change that needs approval, and TI gives no value. It is not a layout action.
6. **No battery drain.** The divider is powered from VBUS, so when USB is absent the NTC network draws no battery current.

### Gaps
- No TI source covers long-lead routing, the TS pin's input leakage or bias current (which would set the error across the 100 kΩ R_TS_SER), or a TS filter capacitor for the BQ24072T.
- The Semitec 103AT-2 datasheet (lead insulation, voltage rating) was not reviewed.
