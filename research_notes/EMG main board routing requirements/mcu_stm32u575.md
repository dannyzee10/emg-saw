# STM32U575VIT6 (LQFP100, non-SMPS): ST layout and routing requirements for U_MCU1 on the EMG main board

Tags used in these notes: **[HARD]** means a datasheet or application-note "must", a required component characteristic, or an absolute-maximum limit. **[ST-REC]** means an ST recommendation, or what ST's own reference designs do. **[N/A]** means it does not apply to this board. General good practice that does not come from ST appears only under "Inferences" and is marked **[GOOD]**. Page numbers are the printed page numbers of the PDFs that the canonical st.com URLs returned on 2026-09-24. For every document used, the printed page numbers matched the PDF page index. Project facts come from read-only project files and are cited as local file links.

## 1. AN5373 (current revision): decoupling per VDD/VSS pair, VCAP, VDDA/VREF+, VBAT, VDDUSB/VDDIO2, NRST/BOOT0 and the PCB-layout section

### Takeaway
AN5373 Rev 7 (Nov 2023) is still the revision that st.com serves. Together with DS13737 Rev 10, it fixes every part value:
- 100 nF ceramic on each VDD pin, plus one 10 µF (4.7 µF minimum) per package.
- 4.7 µF on VCAP. DS13737 adds ±20 %, ESR < 20 mΩ at 3 MHz, and a rating of at least 10 V.
- 100 nF + 1 µF on VDDA, and another 100 nF + 1 µF on the externally driven VREF+.
- 100 nF on VBAT when it is tied to VDD. VDDUSB goes to VDD (preferred) when USB is unused.
- 100 nF on NRST, placed close to the device. A 10 kΩ resistor holds BOOT0.

Placement rule: capacitors go "as close as possible to, or below, the pins". ST's only layout drawing (AN5373 Fig. 17) shows the order pin → capacitor pad → via. AN5373 gives no numeric trace widths, via rules or distances.

The project BOM matches every ST value. The copper review is therefore about geometry: loop area, via position, and the resistance of the VCAP connection.

### Cited Findings
**Documents and revisions (what st.com served on 2026-09-24)**
- AN5373 "Getting started with STM32U5 MCU hardware development", **Rev 7, November 2023**, 47 pp. The canonical URL returns this revision. It is almost 3 years old, but no newer revision was served. — [AN5373 Rev 7](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- DS13737 (STM32U575xx datasheet), **Rev 10, July 2024**, 346 pp. — [DS13737 Rev 10](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- AN2834 "How to get the best ADC accuracy in STM32 microcontrollers", **Rev 10, October 2024**. This note is generic across all STM32 families. — [AN2834 Rev 10](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)
- AN6316 "How to optimize the PCB layout for ST67W611M1 and STM32U575AI", **Rev 3, October 2025**. — [AN6316 Rev 3](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- UM2861 (NUCLEO-U575ZI-Q, MB1549), **Rev 10, March 2025**. — [UM2861 Rev 10](https://www.st.com/resource/en/user_manual/um2861-stm32u5-nucleo144-board-mb1549-stmicroelectronics.pdf)
- ST wiki "Basics of power supply design for MCU", page revision id 90012. The page shows no date. wiki.st.com refused connections, so the page was read from the wiki.stmicroelectronics.cn mirror. — [ST wiki: power supply design](https://wiki.st.com/stm32mcu/wiki/Basics_of_power_supply_design_for_MCU)

**Variant identification**
- ST names two families: "STM32U575xQ … (with SMPS)" (Fig. 3) and "STM32U575xx … (without SMPS)" (Fig. 4). The version without SMPS has a VCAP pin and only the LDO. The STM32U575VIT6 has no Q suffix, so it is the LDO/VCAP device. — [AN5373 §2.1 Figs. 3–4, pp.7–8](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [HARD] "Packages with and without SMPS are not compatible, in almost all power supply pins." ST's example: a pin that is VDDIO2 on the SMPS package is VSS on the legacy package, so the supply is short-circuited. — [AN5373 §3.3 Table 2 caution, p.24](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- ST boards with the internal SMPS are "identified by '-Q' suffixed boards". — [UM2861 p.2](https://www.st.com/resource/en/user_manual/um2861-stm32u5-nucleo144-board-mb1549-stmicroelectronics.pdf)

**VDD/VSS decoupling**
- [HARD] "VDD pins must be connected to VDD with external decoupling capacitors: a 10 µF (typical value, 4.7 µF minimum) single tantalum or ceramic capacitor for the package, and a 100 nF ceramic capacitor for each VDD pin." — [AN5373 §2.2, p.13](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [HARD] "Each power supply pair (such as VDD/VSS or VDDA/VSSA) must be decoupled with filtering ceramic capacitors … These capacitors must be placed as close as possible to, or below, the appropriate pins on the underside of the PCB to ensure the proper functionality of the device." Figure 24 (without SMPS) shows n × 100 nF + 1 × 10 µF on VDD. — [DS13737 §5.1.6, Fig. 24, pp.150–151](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- [ST-REC] All power and ground connections "(including pads, tracks, and vias) must have the lowest possible impedance". This is "typically achieved with thick track widths and, preferably, the use of dedicated power-supply planes in multilayer PCBs". — [AN5373 §7.4, p.34](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [ST-REC] Each supply pair gets 100 nF ceramic plus about 10 µF (tantalum or ceramic) in parallel. Where several VDD pins share one VSS pin, the capacitors go between each VDD pin and that common VSS pin. Capacitors go "as close as possible to, or below the appropriate pins on the underside of the PCB". Typical values are 10–100 nF. — [AN5373 §7.4, p.34](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [ST-REC] Fig. 17 "Typical layout for VDD/VSS pin pair" (read from the rendered figure):
  - One capacitor straddles the adjacent VDD and VSS pins.
  - Each pin reaches its capacitor pad through a short trace.
  - The "Via to VDD" and "Via to VSS" sit on the outboard side of the capacitor pads, so current flows pin → capacitor pad → via.

  — [AN5373 §7.4 Fig. 17, p.35](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [ST-REC] Decoupling guidance from the ST wiki:
  - The goal is "to minimize the size of current loops".
  - "put a capacitor as close as possible to each VDD/Vss pin pair. If VDD pins are not close to Vss pins, put the capacitor close to VDD and directly to the ground plan[e]".
  - Use low-ESR/ESL ceramic parts, in "the smallest package for a given capacitance".
  - Mix capacitor sizes; capacitors in parallel reduce ESL.

  — [ST wiki: power supply design, decoupling section](https://wiki.st.com/stm32mcu/wiki/Basics_of_power_supply_design_for_MCU)
- [ST-REC] Reference design (LQFP100, Fig. 19): VDD pins 11, 28, 50, 75 and 100 connect to VDD_MCU with C3 = 100 nF ×5 plus C2 = 10 µF. Table 9 describes these as "100 nF … For each external power pin" and "10 µF … Decoupling capacitors required for the package". — [AN5373 §8.2 Table 9 p.37, Fig. 19 p.39](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)

**VCAP (pin 48, LDO-only variant)**
- [HARD] VCAP "is the digital core supply, from the internal LDO regulator … connected to a total of 4.7 µF (typical) external capacitor". It "requires a 4.7 µF (typical) external decoupling capacitor connected to VSS". The two-VCAP UFBGA169 option with 2 × 2.2 µF is **[N/A]**. — [AN5373 §2.1 p.3, §2.2 p.13](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [HARD] "The external capacitor on VCAP pin requires the following characteristics: COUT = 4.7 µF or 2 × 2.2 µF ±20%; COUT ESR < 20 mΩ at 3 MHz; COUT rated voltage [≥] 10 V". The ≥ glyph is lost in text extraction. — [DS13737 §5.1.6, caution under Fig. 24, p.151](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- [HARD] "The LDO generates this voltage on VCAP pin connected to an external capacitor of 4.7 µF typical." — [DS13737 p.35](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- [ST-REC] The VCAP capacitor is required "for the stability of the internal LDO". "When VCAP is available, decoupling capacitors need to be attached as close as possible to VCAP pins." — [ST wiki §3.2.1 and §3.5](https://wiki.st.com/stm32mcu/wiki/Basics_of_power_supply_design_for_MCU)
- The core rail on VCAP runs at about 1.2 / 1.1 / 1.0 / 0.9 V in voltage-scaling ranges 1–4. — [AN5373 §2.1.5, p.13](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- In the reference design, pin 48 connects only to C15 = 4.7 µF to ground. Nothing else is on the net. — [AN5373 Fig. 19, p.39](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)

**VDDA / VREF+ / VREF− / VSSA (pins 22 / 21 / 20 / 19)**
- [HARD] "The VDDA pin must be connected to two external decoupling capacitors: 100 nF ceramic and 1 µF tantalum or ceramic." As an optional extra, "VDDA can be connected to VDD through a ferrite bead". — [AN5373 §2.2, p.13](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [HARD] When VREF+ comes from an external voltage, "an external 100 nF + 1 µF tantalum or ceramic capacitor must be connected on this pin". If the internal VREFBUF drives VREF+ instead, 1 µF is required. — [AN5373 §2.2, p.13](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [HARD] "VREF- must always be equal to VSSA." — [AN5373 §2.1, p.4](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [ST-REC] The analog supply "can be separately filtered and shielded from noise on the PCB", and VSSA provides an "isolated supply ground connection". VDDA may differ from VDD. VDDA-domain peripherals stay isolated until firmware sets the ASV bit. — [AN5373 §2.1.1, p.10](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [ST-REC] "In order to improve analog performance, the user must use separate supply sources for VDD and VDDA, and place the decoupling capacitors as close as possible to the device." — [AN5373 §7.3, p.34](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [ST-REC] Reference-design values:
  - VREF+ (pin 21): C6 = 1 µF + C7 = 100 nF.
  - VDDA (pin 22): C4 = 1 µF + C5 = 100 nF.
  - VSSA (19) and VREF− (20) are drawn to the same ground as VSS pins 10, 27, 49, 74 and 99. There is no separate analog ground.

  — [AN5373 Fig. 19, p.39](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [ST-REC] Use the highest of VDDA, the VDDA booster or VDD to supply the I/O analog switches. VDDA or the booster is preferred because they are "often less noisy". This is a firmware setting (ANASWVDD/BOOSTEN). — [AN5373 §2.1.6, p.13](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)

**VBAT (pin 6)**
- [ST-REC] "If no external battery is used in the application, it is recommended to connect the VBAT pin to VDD with a 100 nF external ceramic decoupling capacitor." The 1 µF value is recommended only when a battery is charged through VBAT's internal 5 kΩ / 1.5 kΩ resistor. — [AN5373 §2.1.4 p.11, §2.2 p.13](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- The reference schematic shows C1 = 1 µF on a separate "VBAT" net, which is the battery case. — [AN5373 Fig. 19, p.39](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- VBAT has no sequencing constraint relative to VDD. — [AN5373 §2.3.2, p.18](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)

**VDDUSB (pin 73) and VDDIO2**
- [ST-REC] "The VDDUSB pin must preferably be connected to the VDD voltage supply when the USB is not used." If VDDUSB is left high-impedance or tied to VSS, the maximum input voltage on "_u" I/Os is reduced. — [AN5373 §2.1, p.3](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [HARD] VDDUSB "must be connected to VDD or VSS pin (preferably to VDD) when the USB is not used". Table 32 allows VDDUSB = 0–3.6 V with USB unused and 3.0–3.6 V with USB used. — [DS13737 p.34; Table 32 p.156](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- In the reference design, VDDUSB (pin 73) has C13 = 100 nF. — [AN5373 Fig. 19, p.39](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [N/A] VDDIO2: the non-SMPS LQFP100 has no VDDIO2 pin. The "m × 100 nF + 4.7 µF" VDDIO2 branch in Fig. 24 therefore does not apply. — [DS13737 Fig. 15 p.96, Fig. 24 p.151](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)

**Supply sequencing (VDDA comes from a separate LDO)**
- [HARD] Sequencing rules:
  - While VDD < 1 V, VDDA, VDDUSB and VDDIO2 must stay below VDD + 300 mV. Above 1 V, all supplies are independent.
  - VDDA, VDDUSB and VDDIO2 "must be switched off before VDD".
  - During power-down, VDD may briefly be lower than the other supplies only if the energy delivered to the MCU stays below 1 mJ. ST's example: 10 µF at 3.3 V gives 0.05 mJ.

  — [AN5373 §2.3.2–2.3.3, pp.18–19](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)

**NRST (pin 14)**
- NRST works in both directions. Every internal reset source drives NRST low, and the pulse generator guarantees at least 20 µs. The internal pull-up RPU is switched off during an internal reset. — [AN5373 §2.4.2, pp.19–20](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [HARD] Fig. 38 "Recommended NRST pin protection" shows 0.1 µF. Its notes say "The user must ensure that the level on the NRST pin can go below the VIL(NRST) max level" and "The external capacitor on NRST must be placed as close as possible to the device". — [DS13737 Fig. 38, p.239](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- Table 100 values:
  - VIL(NRST) ≤ 0.3 × VDD.
  - RPU = 30 / 40 / 50 kΩ (min / typ / max).
  - Pulses of 50 ns or less (tF) are filtered.
  - Pulses of at least 330 ns (tNF) are not filtered (1.71–3.6 V).

  — [DS13737 Table 100, p.238](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- [ST-REC] "To allow tools to reset the applications, the RESET pins must be connected." — [AN5373 §8.1, p.36](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- In the reference design, NRST (pin 14) has C8 = 100 nF, a push-button B1 and an ESD device, and runs to the ST-LINK connector RESET# pin. — [AN5373 Fig. 19 p.39, Table 9 p.37](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)

**PH3-BOOT0 (pin 94)**
- The BOOT0 value comes either from the PH3-BOOT0 pin or from an option bit (nSWBOOT0), which frees the pad for other use. — [AN5373 §5.1, p.28](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [ST-REC] "R1 [10 kΩ] maintains PH3-BOOT0 pin at a logic low or high level." In Fig. 19, R1 runs to SW1, whose default position is ground. — [AN5373 Table 9 p.37, Fig. 19 p.39](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- "When waking up from Standby mode, the BOOT pin is sampled and the user must pay attention to its value." — [AN5373 §8.1, p.36](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- The bootloader can use USART1 (PA9/PA10), USART2 (PA2/PA3), SPI1 (PA4–PA7), SPI2 (PB12–PB15), I2C2 (PB10/PB11) and others. — [AN5373 §5.2, p.29](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)

**PCB-layout section (§7)**
- [ST-REC] "it is best to use a multilayer PCB, with a separate layer dedicated to ground (VSS) and another dedicated to the VDD supply". Separate the board into blocks: high-current, low-voltage, digital, and grouped by EMI contribution. — [AN5373 §7.1–7.2, p.34](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [ST-REC, worded as "must be respected"] Grounding rules:
  - "Ground every block … individually. Return all grounds to a single point. Avoid loops (or ensure they have a minimum area)."
  - Supplies "must be implemented close to the ground line to minimize the area of the supplies loop", because the supply loop "acts as an antenna".
  - "All component-free PCB areas must be filled with additional grounding."

  — [AN5373 §7.3, p.34](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [ST-REC] Interrupt and handshaking strobe signals need "a surrounding ground trace, shorter lengths, and the absence of noisy and sensitive traces nearby". Clocks count as noisy signals and high-impedance nodes as sensitive ones. — [AN5373 §7.5, p.35](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [HARD, satisfied in firmware] Unused I/Os "must not be left floating": set them to analog mode, use a pull resistor, or make them outputs. Unused clock sources must be disabled. — [AN5373 §7.6, p.35](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- The full text of §7 gives no numeric trace width, via size or count, or placement distance. — [AN5373 §7, pp.34–35](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)

**Project data used for the cross-check (read-only)**
- BOM entries:
  - C_MCU_VDD1..5: GRM155R61C104KA88D, 100 nF, X5R, 16 V, 0402.
  - C_MCU_BULK: GCM21BC71E106KE36L, 10 µF, X7S, 25 V, 0805.
  - MCU_VCAP: CL21A475KOFNNNE, 4.7 µF ±10 %, 16 V, X5R, 0805.
  - C1_MCU, C3_MCU: 100 nF 0402. C2_MCU, C4_MCU: GRM155C71C105KE11D, 1 µF, X7S, 16 V, 0402.
  - C_VBAT, C_VDDUSB, C_NRST: 100 nF.
  - R_NRST, R_MCU_BOOT0_PD: 10 kΩ.
  - R_ADC1..5: 330 Ω 0402. C_ADC1..5: GRM1555C1E103JE01D, 10 nF C0G 0402.
  - R_SPI_CS/SCK/MOSI/MISO: 22 Ω 0402.
  - U_MCU1: STM32U575VIT6 on footprint QFP50P1600X1600X160-100N.

  — [MAIN_BOARD_COMPLETE_ASSEMBLY_BOM.csv](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/ASSEMBLY_SNAPSHOT_20260924T023521434Z/MAIN_BOARD_COMPLETE_ASSEMBLY_BOM.csv)
- Pad nets:
  - R_NRST pad 1 is on MCU_NRST and pad 2 on 3V3_DIG, so it is an external pull-up.
  - C1–C4_MCU all sit between 3V0_ANA and GND. The netlist therefore does not show which pair serves VDDA and which serves VREF+.

  — [CURRENT_NATIVE_BOARD_INVENTORY.txt lines 879–881, 1672–1699](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/handoff_2026-09-23_1850/CURRENT_NATIVE_BOARD_INVENTORY.txt)
- The project's sheet specification gives VBAT as "1 uF (AN5373 Fig. 19)", but the BOM fits 100 nF (C_VBAT). — [08_mcu_rf_sheet_spec.md line 64](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/08_mcu_rf_sheet_spec.md)

### Inferences
**BOM against ST requirements**

| Pin(s) | ST requirement | Project part | Result |
|---|---|---|---|
| VDD 11/28/50/75/100 | 100 nF ceramic on each pin | C_MCU_VDD1..5, 100 nF | Matches |
| Package bulk | 10 µF (4.7 µF minimum) | C_MCU_BULK, 10 µF X7S | Matches |
| VCAP 48 | 4.7 µF ±20 %, ESR < 20 mΩ at 3 MHz, rated ≥ 10 V | 4.7 µF ±10 %, 16 V, X5R, 0805 | Value and voltage OK. ESR and effective capacitance at 1.2 V over temperature not verified. |
| VDDA 22, VREF+ 21 | 100 nF + 1 µF on each pin | Two × (100 nF + 1 µF) on 3V0_ANA | Matches. Check that one 100 nF sits physically at pin 21 and one at pin 22. |
| VBAT 6 → 3V3_DIG | 100 nF | C_VBAT, 100 nF | Matches AN5373 §2.2. The spec text (1 µF) is inconsistent with the BOM. |
| VDDUSB 73 → 3V3_DIG | Tie to VDD (preferred); 100 nF in Fig. 19 | C_VDDUSB, 100 nF | Matches |
| NRST 14 | 0.1 µF close to the pin | C_NRST 100 nF, plus a 10 kΩ pull-up | OK. The pull-up is an addition that ST does not require. |
| BOOT0 94 | 10 kΩ holding resistor | R_MCU_BOOT0_PD, 10 kΩ | Matches |

**Geometry from the LQFP100 pinout (DS13737 Fig. 15)**
- Every VDD pin is next to a VSS pin: 10/11, 27/28, 49/50, 74/75 and 99/100. Fig. 17 can therefore be followed exactly for C_MCU_VDD1..5: one capacitor across each pair, and one VDD via plus one GND via outboard of the pads.
- VCAP (48) is next to VSS (49). MCU_VCAP should straddle pins 48 and 49 on L1, with no via in the VCAP path.
- VDDUSB (73) is next to VSS (74).
- VBAT (6) and NRST (14) have no neighbouring VSS pin. Their capacitors need their own GND via to L2 at the capacitor pad (ST wiki rule).
- VSS 49 serves both the VCAP and VDD3 capacitors, and VSS 74 serves both the VDDUSB and VDD4 capacitors. **[GOOD]** Give each capacitor its own GND via rather than one shared via.
- The through vias are 0.6/0.3 mm and the pin pitch is 0.5 mm, so no via fits between pins. All vias must sit beyond the pin toes and capacitor pads, which is the Fig. 17 arrangement.
- On L3, **[GOOD]** make sure the VDD vias land on real 3V3_DIG copper: a pour or a short 0.3–0.4 mm branch.

**VCAP connection resistance (the ESR limit covers the whole loop the LDO sees)**
- Copper resistance per square is ρ/t = 1.72e-8 Ω·m / 35 µm ≈ 0.49 mΩ/□ for 1 oz copper, and ≈ 0.98 mΩ/□ for 0.5 oz. The skin depth at 3 MHz is ≈ 38 µm, about the foil thickness, so the DC estimate roughly holds.
- A 0.3 × 2 mm trace is ≈ 3.3 mΩ. A 0.2 × 5 mm trace is ≈ 12 mΩ, which alone would use most of the 20 mΩ budget.
- **[GOOD] targets:**
  - Capacitor pad edge within about 1–2 mm of the pin-48 toe.
  - Trace as wide as the pad allows (≥ 0.3 mm once clear of the pin).
  - No via, test point or other branch on MCU_VCAP.
  - GND side: a direct short trace to pin 49 plus 1–2 vias to L2 at the capacitor pad.
- AN5373 allows capacitors "below the pins on the underside". For VCAP that would add two vias to the loop, so placing it on top next to the pins is preferable on this board.

**Other cross-checks**
- Symbol and footprint: check that U_MCU1 pins 19–22 are VSSA / VREF− / VREF+ / VDDA and pins 46–50 are PE15 / PB10 / VCAP / VSS / VDD, as on the non-SMPS pinout. On the SMPS LQFP100, pin 48 is VSSSMPS and pin 22 is PA0 (see Q2).
- BOOT0 integrity protects both the ADC pins and the radio bus. If BOOT0 were ever high at reset, the bootloader could probe PA2/PA3 (USART2) and PA4 (SPI1), which are ADC channels 3–5, and PB12–PB15 (SPI2), which is the ST67 bus.
  - **[GOOD]** Keep R_MCU_BOOT0_PD at pin 94 with a short trace.
  - **[GOOD]** Keep the stub to TP_MCU_BOOT0 short.
  - **[GOOD]** Keep SCK and other fast edges away from this net.
- NRST: R_NRST (10 kΩ) in parallel with RPU (30–50 kΩ) gives about 7.5–8.3 kΩ. An open-drain debugger or reset source easily pulls this below 0.3 × VDD, so there is no conflict with Fig. 38. The layout priority is C_NRST right at pin 14, which makes the node low-impedance at HF before the trace runs to J_SWD pin 5 and the test pad.
- Sequencing: 3V0_ANA (VDDA and VREF+) must not stay up while 3V3_DIG collapses, unless the stored energy delivered is below 1 mJ. The LDO is enabled by MCU AFE_EN, so power-up is naturally ordered. Confirm what powers the TPS7A2030 input during power-down. This is a design check, not a copper check.
- Grounding: ST's own U5 reference ties VSSA and VREF− straight to the common ground, and DS13737 limits the difference between any two ground pins to 50 mV (Q2). The project's single GND net with an unbroken L2 plane is consistent with both. The §7.3 "single point" rule is met through placement: digital return currents are kept out of the analog corner. No split plane is needed.

### Gaps
- ST gives no numeric distance limit, via count or trace width for LQFP decoupling. The distance and width targets above are general practice, not ST figures.
- I did not obtain the ESR at 3 MHz, or the DC-bias and temperature capacitance curves, for Samsung CL21A475KOFNNNE. The stack of ±10 % tolerance and X5R temperature drift may approach the −20 % limit. Check against the manufacturer's data.
- AN5373 Rev 7 (Nov 2023) is the revision served, but I did not check the STM32U575VI product-page document list for errata or a newer revision.
- I did not consult reference manual RM0456. Firmware items, such as keeping VREFBUF off in high-impedance mode while VREF+ is driven externally, and ANASWVDD/BOOSTEN, remain unverified.

## 2. DS13737: LQFP100 pinout facts and electrical limits that matter for routing

### Takeaway
On the non-SMPS LQFP100, each of the five VDD pins sits beside a VSS pin, and VCAP (48) sits beside VSS (49). The analog group VSSA / VREF− / VREF+ / VDDA (19–22) is followed directly by PA0–PA3 (23–26), then a digital VSS/VDD pair (27/28), then PA4 (29).

Limits that bind the layout:
- At most 50 mV between any two ground pins, including VREF−.
- At most 50 mV between VDD pins of the same domain.
- VREF+ no more than VDDA + 0.4 V, and at least 2 V for the 14-bit ADC.
- At most 100 mA per VDD pin.
- The NRST filter windows.
- ADC accuracy falls with parasitic input capacitance and with digital activity on adjacent I/Os.

The SMPS LQFP100 has a different pinout, so the footprint and symbol must use the non-SMPS mapping.

### Cited Findings
- Non-SMPS LQFP100 pin numbers (Fig. 15, top view): pins 1–25 run along the first side, 26–50 the second, 51–75 the third and 76–100 the fourth.

  | Group | Pins |
  |---|---|
  | Backup and 32 kHz | VBAT 6, PC14-OSC32_IN 8, PC15-OSC32_OUT 9 |
  | Supply pair | VSS 10, VDD 11 |
  | HSE | PH0-OSC_IN 12, PH1-OSC_OUT 13 |
  | Reset | NRST 14 |
  | GPIO before the analog group | PC0–PC3 15–18 |
  | Analog supply and reference | VSSA 19, VREF− 20, VREF+ 21, VDDA 22 |
  | ADC inputs | PA0 23, PA1 24, PA2 25, PA3 26, PA4 29 |
  | Supply pair | VSS 27, VDD 28 |
  | GPIO after PA4 | PA5 30 |
  | Core supply corner | PB10 47, VCAP 48, VSS 49, VDD 50 |
  | SPI side | PB12 51, PB13 52, PB14 53, PB15 54, PD8 55 |
  | Debug and USB supply | PA13 72, VDDUSB 73, VSS 74, VDD 75, PA14 76, PA15 77 |
  | Other | PB3 89, PB4 90, PH3-BOOT0 94 |
  | Supply pair | VSS 99, VDD 100 |

  — [DS13737 Fig. 15, p.96](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- [N/A, as a warning] The LQFP100_SMPS pinout (Fig. 14) differs:
  - VSSA 19, VREF+ 20 (there is no separate VREF− pin), VDDA 21, PA0 22.
  - VSS 26, VDD 27, PA4 28.
  - VLXSMPS 46, VDDSMPS 47, VSSSMPS 48, VDD11 49, VSS 50, VDD 51, VDD11 98.

  — [DS13737 Fig. 14, p.95](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- [HARD] Table 29 limits:
  - VDDX − VSS, including VDDA, VDDUSB, VBAT and VREF+: −0.3 to 4.0 V.
  - VREF+ − VDDA: at most 0.4 V when VREF+ > VDDA.
  - |ΔVDDx| between VDD pins of the same domain: at most 50 mV.
  - |VSSx − VSS| between all ground pins "(7) Including VREF- pin": at most 50 mV.
  - Note 1: all main power pins (VDD, VDDA, VDDUSB, VBAT) and ground pins (VSS, VSSA) "must always be connected to the external power supply".

  — [DS13737 Table 29, pp.153–154](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- [HARD] Table 30 limits:
  - At most 100 mA into any one VDD pin, or out of any one VSS pin.
  - At most 200 mA in total.
  - 20 mA per I/O; 120 mA for all I/Os together.
  - Injected current on FT, TT and RST pins: −5 / +0 mA.

  — [DS13737 Table 30, p.154](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- [HARD] ADC1 (14-bit) limits and data:
  - VREF+ must lie between 2 V and VDDA when VDDA ≥ 2 V. When VDDA < 2 V, VREF+ = VDDA.
  - fADC = 5–55 MHz.
  - Internal sample-and-hold capacitor CADC = 5 pF typ.
  - The I/O analog-switch booster "must be used when VDDA < 2.4 V".

  — [DS13737 §5.3.19 Table 103, pp.240–242](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- The Table 104 values for the maximum source resistance RAIN are given "without external capacitor". The tolerance is 2 LSB at 14 bits. The worst case is a scan in which channel i sits at VREF+ and channel i+1 at VREF−. — [DS13737 Table 104, pp.242–244](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- Table 105 (14-bit ADC1 accuracy), single-ended:
  - ENOB 11 min / 12 typ bits.
  - SINAD and SNR 68 min / 74 typ dB.
  - THD −84 typ / −80 max dB.

  The values were "Evaluated by characterization for BGA packages … The values for LQFP packages may differ." Footnote 4 reads: "This parameter may degrade in case of digital activity on adjacent I/Os." — [DS13737 Table 105, p.244](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- [ST-REC] Fig. 40 notes and "General PCB design guidelines":
  - Cparasitic is the PCB capacitance "(dependent on soldering and PCB layout quality)" plus the pad capacitance.
  - "A high Cparasitic value downgrades the conversion accuracy. To remedy this, fADC must be reduced."
  - "The 100 nF capacitor must be ceramic (good quality) and must be placed as close as possible to the chip."

  — [DS13737 Fig. 40 notes, p.245](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- I/O pin capacitance CIO = 5 pF. Weak pull-up and pull-down are 30–50 kΩ. — [DS13737 Table 93, pp.228–230](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- SPI master fSCK is at most 80 MHz at VDDIOx = 2.7–3.6 V in voltage range 1. It is 75 MHz (or 50 MHz) at 1.71–2.7 V. — [DS13737 Table 148, pp.332–333](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- [N/A] USB: "No external termination series resistors are required on USB_DP (D+) and USB_DM (D-)". USB data is not used on this board. — [DS13737 p.338](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)

### Inferences
- Corner map (top view):
  - The analog cluster (19–29) wraps one corner: pins 19–25 on side 1, pins 26–29 on side 2.
  - The VCAP/VSS/VDD group (48–50) and the SPI pins (51–55) share the next corner.
  - The debug pins PA13 (72) and PA14 (76) share a corner with VDDUSB/VSS/VDD (73–75), which sit between them.
  - BOOT0 (94) is on side 4, and VSS/VDD 99/100 sit at the pin-1 corner.

  This matches the brief's plan: ADC pins toward the analog corridor, and SPI toward the ST67.
- Pin adjacencies that matter:
  - **VSS/VDD 27/28 sit between ADC_CH4 (PA3, 26) and ADC_CH5 (PA4, 29).** The C_MCU_VDD2 current loop and its vias sit inside the analog pin group. **[GOOD]** Keep that loop minimal, with its vias straight down to L2 at the capacitor. Route the PA3 and PA4 traces away from the capacitor rather than alongside its supply trace.
  - PA0 (23) is next to VDDA (22). This is analog next to analog and is acceptable, but separate the 3V0_ANA feed from the PA0 trace once past the pins.
  - PB10 (47, ST67 CHIP_EN, mostly static) is next to VCAP (48).
  - The SPI pins 51–54 start right after VDD 50. The MCU_VCAP and C_MCU_VDD3 capacitors have first claim on the copper next to pins 48–50. The 22 Ω resistors go just beyond them.
- The 50 mV ground-difference limit is easy to meet with a solid L2 plane and a via at every VSS, VSSA and VREF− pin or capacitor. A split plane, a long ground trace or a solder-bridged analog island would make it harder to meet. This supports the project's single-GND choice.
- The 100 mA per-pin current is small. Supply trace widths are set by inductance and loop area, not by current capacity.
- Error budget: 1 LSB at 14 bits with VREF+ = 3.00 V is ≈ 183 µV. With ENOB of 12 bits typical (BGA-characterized, and LQFP "may differ"), the converter's own noise is about 4 LSB. Layout-coupled noise should stay well below that.
- The 80 MHz SPI capability is not the limit on this board. The ST67 caps the bus at 40 MHz (Q4).

### Gaps
- The GPIO output AC table (rise/fall time per OSPEEDR setting) came out garbled in text extraction. I could not quantify edge rates for the termination analysis.
- The Table 104 RAIN / sampling-time rows are garbled. Only the notes quoted above are reliable.
- Table 105 accuracy is BGA-characterized. I found no LQFP100-specific ADC figures.

## 3. AN2834 and U5 ADC data: analog input routing, separation from digital, RC at the pin, VREF+ decoupling, ground return

### Takeaway
ST's ADC guidance:
- Keep the reference low in impedance and low in inductance, with its capacitors at the pins.
- Keep analog tracks away from digital tracks, and do not let them cross. Shield them with ground.
- Put the R and C with very short leads, and avoid negative injection current.
- A large capacitor at the pin is a valid charge reservoir, provided the time between conversions lets it recharge.

AN2834 is generic, and some of its numbers conflict with the U5-specific documents: 10 nF + 1 µF decoupling, VREF+ ≥ 2.4 V, and separate analog and digital ground planes. Where they conflict, AN5373 and DS13737 take precedence for this device. For the 330 Ω / 10 nF input network at a 2 kHz per-channel rate, the charge-sharing error is under 1 LSB for realistic channel-to-channel differences.

### Cited Findings
- [ST-REC] Noise on the reference changes the result. AN2834's example: a 40 mV peak-to-peak ripple on a 3.3 V reference causes a 15 LSB error at 12 bits. — [AN2834 §3.2.1, p.14](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)
- [ST-REC] The reference "must have a very low output impedance including low inductance". Parasitic inductance can leave the approximation cycle unfinished, or make the LC network oscillate. "Correct decoupling capacitors on the reference voltage located very close to pins provide a low source impedance." — [AN2834 §3.2.3, pp.15–16; §4.2.2, p.22](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)
- [ST-REC] Supply-side guidance:
  - Use a linear regulator for the analog stage when the digital supply is a switcher.
  - Place 0.1 µF plus 1–10 µF close to the source, and ceramic capacitors close to the VDD/VSS and VDDA/VSSA pins.
  - A series ferrite together with the decoupling capacitor forms an LC circuit that "can start to oscillate". Use "small inductances and with ferrite cores, which have losses at high frequencies".

  — [AN2834 §4.2.1, pp.20–21](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)
- [ST-REC] "In most STM32 microcontrollers, the VDD and VSS pins are placed close to each other. So are the VREF+ and VSSA pins. A capacitor can therefore be connected very close to the microcontroller with very short leads." — [AN2834 §4.2.1, p.21](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)
- These generic values conflict with the U5 documents:
  - AN2834 Fig. 20 (100/144-pin packages) shows VDDA 1 µF // 10 nF and VREF+ 1 µF // 10 nF when VREF+ is separate from VDDA, and one 1 µF // 100 nF when they are tied.
  - AN2834 says VREF+ "may range from 2.4 V to VDDA".

  The U5 documents instead require 100 nF + 1 µF on each pin, and give VREF+ ≥ 2 V for ADC1. — [AN2834 §4.2.1 Fig. 20, p.21](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf); contradicted by [AN5373 §2.2 p.13](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf) and [DS13737 Table 103](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- [ST-REC] Source resistance slows the charging of CADC, with time constant (RADC + RAIN) × CADC. Source capacitance plus PCB parasitic capacitance (CAIN + Cp) must be fully charged. "The greater value of (CAIN + Cp), the more limited the source frequency". The limit is FAIN ≤ 1 / (10 × RAIN × (CAIN + Cp)). — [AN2834 §3.2.7–3.2.8 pp.16–17; §4.2.8 p.34](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)
- [ST-REC] Adding "a large external capacitor (Cext) to the input pin" is a valid technique. Cext should be large enough that dumping the sample-and-hold charge onto it raises Cext by no more than 0.5 LSB. Firmware must then allow a recharge time tC = −(Rin × Cext) × ln(…) between conversions of the same channel. Without that wait, Cext is "cyclically charged" and the error builds up. — [AN2834 §4.4.3, pp.44–47](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)
- [ST-REC] Negative injection current on any analog pin, or on "a closely positioned digital input pin", adds leakage into the ADC input, with the adjacent analog channel worst affected. ST recommends a Schottky diode between VSSA and any pin that can produce negative injection. — [AN2834 §3.2.9 p.18; §4.2.10 p.35](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)
- [ST-REC] Crosstalk: "A digital track that crosses an analog input track on the PCB may affect the analog signal". Fig. 18 shows two cases: tracks running close together, and tracks crossing on opposite sides of the board. The fix is "placing ground tracks across it" (Fig. 32). — [AN2834 §3.2.11 pp.18–19; §4.2.11 p.35](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)
- [ST-REC] "Placing ground tracks alongside sensitive analog signals provides shielding", with a ground plane on the other side. Remote signals should arrive on shielded cable, grounded at the receiver end only. — [AN2834 §4.2.12, p.36](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)
- [ST-REC, generic] AN2834's layout recommendations:
  - Separate the analog and digital layouts so that tracks do not cross.
  - "It is recommended to use different planes for analog and digital grounds … The analog ground must be placed below the analog circuitry."
  - Connect the analog and digital grounds "in a star network".
  - On multilayer boards, use separate layers for power and ground. "The analog ground can be connected at one point to this ground plane … close to the power supply."

  — [AN2834 §4.2.13, pp.37–38](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)
- [ST-REC] Placement and firmware practice:
  - "Components like resistors and capacitors must be connected with very short leads."
  - Put SMD decoupling capacitors close to the MCU, and "use wide tracks for power".
  - In firmware, "minimize digital signal changes during sampling and conversion".

  — [AN2834 §4.2.14 and §4.3, p.39](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)
- [ST-REC] On ST's own STM32U575 board, "VDDA and VREFP are analog power supplies which must be decoupled by two capacitors, 1 µF and 100 nF, connected directly to the analog ground pin VSSA". On that board VSSA joins main ground through solder bridge SB38. — [AN6316 §4.4.2 Figs. 15–17, pp.11–12](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [ST-REC] For sensitive applications, supply VDDA from "a low noise and high PSRR LDO". Tying VREF+ to VDDA makes VDDA "more sensitive to noise and accuracy". — [ST wiki §3.2.2](https://wiki.st.com/stm32mcu/wiki/Basics_of_power_supply_design_for_MCU)
- The brief's intended ADC wiring: PA0–PA3 are pins 23–26 and PA4 is pin 29. Each channel goes through 330 Ω with 10 nF at the MCU side. The brief asks to "Keep the 3V0_ANA feed away from the SPI/power corridor". — [Layout brief §10, lines 173–183](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)

### Inferences
**Numbers for the 330 Ω / 10 nF (C0G) network, with CADC = 5 pF and 14 bits at VREF+ = 3.00 V**
- Charge sharing: CADC / (CADC + Cext) ≈ 5.0e-4, which is about 2.7 LSB per volt of step between consecutively sampled voltages.
  - A full-scale step (3 V) gives about 8 LSB.
  - A 0.3 V step gives about 0.8 LSB.
- AN2834's 0.5 LSB criterion for a worst-case full-scale step would need Cext ≥ about 164 nF. The 10 nF works because all five EMG channels sit near the same 1.5 V baseline.
- Recharge: τ = 3.3 µs, and an 8 LSB kick settles to 0.5 LSB in about 2.8 τ ≈ 9 µs. That is far below a 500 µs per-channel interval at 2 kHz. **[GOOD]** Keep this in mind if firmware ever moves to a fast continuous scan.
- FAIN limit from AN2834: 1 / (10 × 330 Ω × 10 nF) ≈ 30 kHz. The RC corner is ≈ 48 kHz. Both are far above the EMG band.
- With 10 nF at the pin, a PCB parasitic of a few pF is negligible. The DS13737 RAIN table does not apply directly, because it assumes no external capacitor.

**Placement**
- **[GOOD]** Put C_ADCn right at its MCU pin: signal pad within about 1–3 mm, on L1, no via between the capacitor and the pin.
- **[GOOD]** Give C_ADCn its own GND via to L2 at the pad. Place these vias toward VSSA/VREF− (19/20), not next to the C_MCU_VDD2 vias at pins 27/28.
- **[GOOD]** Put R_ADCn immediately upstream of the capacitor. The long run from the AFE then sits on the source side of the RC, where the filter cleans up anything it picks up.

**Routing**
- **[GOOD]** Run the ADC traces on L1 over unbroken L2.
- **[GOOD]** Keep L3 digital traces and SPI via fields out of the area under the analog corner and under the ADC corridor. A row of via antipads can slot L2.
- **[GOOD]** Where a ground guard is used between ADC traces and digital traces, stitch it to L2 at both ends and along its length. An unstitched guard is worse than none, as the brief also says.
- **[GOOD]** With L2 between them, a digital trace on L3 crossing under an L1 ADC trace couples much less than in AN2834's two-layer case. Still cross only at 90°, and never under the RC capacitors.

**Pins next to the ADC inputs**
- PC0–PC3 (15–18) and PA5–PA7 (30–32) are the ADC pins' neighbours. Table 105 note 4 says digital activity on adjacent I/Os degrades accuracy, so **[GOOD]** these should be static or slow during conversions.
- PC3 is AFE_EN and is static. The optional VREF_A sense on PA5 is analog.

**VDDA and VREF+ routing**
- **[GOOD]** Place a 100 nF at pin 21 with its GND leg taken to pins 20/19, and a 100 nF at pin 22 with its GND leg taken to pins 19/20. Put a GND via to L2 at those pads.
- **[GOOD]** Put the 1 µF capacitors behind the 100 nF ones.
- **[GOOD]** Split the 3V0_ANA feed at the 1 µF node, so the VDDA current and the VREF+ reference-charge pulses do not share a thin trace. AN2834 §3.2.3 explains why reference inductance matters.
- **[GOOD]** The 3V0_ANA feed to the MCU should be its own branch from the TPS7A2030 output, not a daisy-chain through the AFE. It should not run beside SPI or power traces.
- A ferrite bead, as AN5373 and the wiki allow for a VDD-derived VDDA, is not needed here because VDDA already has a separate LDO. AN2834 warns that a bead can ring with the capacitors.

**Resolving the ground-plane conflict**
AN2834's split-plane and star advice is generic. The U5-specific evidence (the Fig. 19 common ground and the 50 mV limit between any two ground pins) together with the project's single-GND decision favours one solid L2 plane. Keep the analog return area separate by placement. Copying AN6316's solder bridge is **[N/A]**; the brief also forbids it.

**Injection current**
The AFE outputs come from rail-to-rail amplifiers on 3V0_ANA, so no negative excursion is expected. The Schottky diode advice is **[N/A]** unless the AFE supply can collapse before its outputs while signals are present.

### Gaps
- I did not search for a U5-specific ADC application note. The ADC guidance here comes from generic AN2834 plus DS13737. I also did not check whether ST publishes LQFP-specific ADC accuracy data.
- ST gives no numeric spacing, guard-trace or stitching-pitch rule for ADC traces.

## 4. SWD routing and SPI-master routing (series termination, trace length)

### Takeaway
SWD needs no external pull resistors, because SWDIO is pulled up and SWCLK pulled down internally. NRST must reach the debug connector. ST's reference design adds 47 Ω series resistors and 6 V ESD arrays at the connector, but gives no length or impedance rules. For the ST67 SPI, ST's rules are:
- 40 MHz maximum clock.
- Target 50 Ω.
- Coplanar ground between signals.
- Inner layers on 4-layer boards, to limit SCK radiation.
- Short tracks, away from RF and power.
- Care when changing layers.

No ST document found specifies series termination. Placing the 22 Ω resistors at the drivers is general practice. At the likely track lengths, the extra timing from length is negligible, so no length matching is needed.

### Cited Findings
- ST67W611M1 SPI wiki page: revision id 86022. wiki.st.com refused connections, so the page was read from the wiki.stmicroelectronics.cn mirror. — [ST wiki: ST67W611M1 SPI interface](https://wiki.st.com/stm32mcu/wiki/Connectivity:ST67W611M1_spi)
- SWD pins: SWDIO = PA13 and SWCLK = PA14 on all packages. After reset they are debug pins, "immediately usable by the debugger host". After release, SWDIO is an alternate-function pull-up and SWCLK an alternate-function pull-down. "Having embedded pull-up and pull-down resistors removes the need to add external resistors." — [AN5373 §6.3–6.3.1, p.32](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [HARD] "The JTAG input pins must not be floating … Special care must be taken with the SWCLK/TCK pin that is directly connected to the clock of some of these flip-flops." The internal pulls prevent floating. — [AN5373 §6.2.3, p.31](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- The standard SWD connector (Fig. 16) carries VDD, SWDIO/PA13, SWCLK/PA14, NRST and GND. "To allow tools to reset the applications, the RESET pins must be connected." — [AN5373 §6.3.2 Fig. 16 p.33; §8.1 p.36](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [ST-REC] Debug protection in the reference design: R5–R9 = 47 Ω and U1–U3 = "ESD protection 6V1" (ESDALC6V1W5) are "Used for ESD protection" on the debug lines to the ST-LINK connector. There are no capacitors on SWDIO or SWCLK. — [AN5373 Table 9 p.37, Fig. 19 p.39](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [ST-REC] Interrupt and handshake strobes (SPI_RDY, and CS used as a wake signal) need a surrounding ground trace, short length, and no noisy traces nearby. — [AN5373 §7.5, p.35](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- [HARD] ST67W611M1 SPI timing: Tcyc ≥ 25 ns, "a maximum frequency of 40 MHz". MOSI setup 6 ns and hold 6 ns. MISO output delay at most 8 ns. SPI_CS "can also convey a wake-up signal". SPI_RDY is the module's handshake. — [ST wiki: ST67W611M1 SPI interface](https://wiki.st.com/stm32mcu/wiki/Connectivity:ST67W611M1_spi)
- [ST-REC] ST67 SPI hardware rules:
  - "Route these tracks with impedance control targeting 50 Ohms. Exercise caution when changing layers. Use coplanar routing (i.e. to separate these signals with ground) to avoid coupling."
  - Route away from RF and power supplies.
  - "minimize the length of SPI_CLK, SPI_MOSI and SPI_MISO tracks … to reduce propagation delay and skew between SPI_MISO and SPI_CLK at the host side".
  - "On a four-layer board, route SPI signals on inner layers to minimize SPI_CLK radiation."

  — [ST wiki: ST67W611M1 SPI interface §3](https://wiki.st.com/stm32mcu/wiki/Connectivity:ST67W611M1_spi)
- [ST-REC] AN6316 SPI routing:
  - "Coplanar line routing (ground between signals)".
  - Avoid routing across the SMPS area.
  - "Internally route signals (in the first or second inner layer) to prevent SPI_CLK radiation".
  - Keep tracks as short as possible. In ST's design the total length is about 45 mm, "a delay of 300 ps".
  - "There is no impedance control, but it should be as close to 50 Ω as possible". The stack reached 38 Ω.

  — [AN6316 §4.3, pp.9–10](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- The STM32 side can drive SPI much faster: master fSCK is up to 80 MHz at 2.7–3.6 V. — [DS13737 Table 148, p.332](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)
- The project's intent:
  - SPI2 on PB12 = CS (51), PB13 = SCK (52), PB14 = MISO (53), PB15 = MOSI (54), with PD8 = SPI_RDY (55).
  - SWDIO on pin 72, SWCLK on pin 76.
  - The J_SWD header is 1 = VTREF, 2 = SWDIO, 3 = GND, 4 = SWCLK, 5 = NRST.
  - 22 Ω resistors for SCK, MOSI and CS near the MCU, and for MISO near the module.
  - A short L3 SPI corridor, a target of about 50 Ω, and no unnecessary serpentines.

  — [08_mcu_rf_sheet_spec.md lines 199–203, 237–242](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/08_mcu_rf_sheet_spec.md); [Layout brief lines 193, 245](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)

### Inferences
**SPI timing**
- AN6316's figures give about 6.7 ps/mm, so a 60 mm MCU-to-module route adds about 0.4 ns each way.
- At 40 MHz the half-period is 12.5 ns. The MISO path budget (SCK out + 8 ns module delay + MISO back + host setup) has several ns of margin.
- Length matching and serpentines therefore add nothing. Short and direct is the whole requirement, which the brief also says.

**Series termination [GOOD, not ST]**
- A source-series resistor only works when it sits at the driver. Place R_SPI_SCK, R_SPI_MOSI and R_SPI_CS within a few mm of pins 52, 54 and 51, before any via, with R_SPI_MISO likewise next to the module's MISO pad.
- Keep SCK free of test points or stubs between the MCU and the module. If SCK needs probing, use the resistor pad.

**Congestion at pins 48–55**
MCU_VCAP (48/49), C_MCU_VDD3 (49/50) and the three MCU-side 22 Ω resistors (51/52/54) all compete for the same corner. **[GOOD]** Priority order:
1. VCAP capacitor, at the pin.
2. VDD3 capacitor.
3. Resistors.
4. The L1→L3 vias, placed after the resistors.

Do not run SCK alongside the MCU_VCAP trace, or between the VCAP capacitor and pin 48.

**Layer changes**
- An L1→L3 transition keeps L2 as the reference, so return current stays continuous.
- **[GOOD]** Where an L3 trace also takes L4 as its reference, add a GND stitching via next to each signal via. This is how to "exercise caution when changing layers".
- **[GOOD]** Do not let the SPI via row slot L2 under the VCAP/VDD3 loop.

**SPI_RDY and CS**
These are handshake and interrupt lines under AN5373 §7.5. **[GOOD]** Give them a ground neighbour, keep them short, and keep them away from SCK.

**SWD**
- PA13 (72) and PA14 (76) are separated by VDDUSB/VSS/VDD (73–75), whose capacitors need the copper at the pins. **[GOOD]** Route SWDIO and SWCLK around the C_VDDUSB and C_MCU_VDD4 capacitors, not between those capacitors and their pins.
- **[GOOD]** Keep SWCLK, which clocks the debug flip-flops, short and away from the ADC corner and the SPI clock.
- **[GOOD]** Keep J_SWD at the service edge near that corner.
- The brief's "no new capacitors on SWDIO/SWCLK" matches the ST reference.
- The project has no 47 Ω resistors or ESD parts on SWD. That is a design choice, not a layout error. Consider them only if the header will be handled often without ESD precautions.

### Gaps
- I found no ST guidance on series-termination values or placement for STM32U5 SPI, and no SWD trace-length or impedance guidance.
- I did not retrieve the GPIO driver output impedance or rise time per speed setting, which would be needed to check that 22 Ω plus the driver impedance is close to 50 Ω. The datasheet AC table extraction was garbled.
- I do not know the SPI clock the firmware will actually use.

## 5. ST reference hardware: how decoupling and VCAP are actually placed on 4-layer boards

### Takeaway
ST's only non-SMPS STM32U575 LQFP100 reference is a schematic: AN5373 Fig. 19. I found no ST layout that shows a VCAP capacitor.

The two ST boards examined both use the SMPS variant, so they have VDD11 capacitors instead of VCAP:
- NUCLEO-U575ZI-Q uses the STM32U575ZIT6Q.
- AN6316's 4-layer STM32U575AI board uses the SMPS variant.

AN6316 still shows ST's 4-layer practice: all parts on top, 100 nF capacitors hugging the package, 10 µF on the supply branches, a VDD_MCU star of 400 µm tracks, and VDDA/VREF+ 1 µF + 100 nF returned directly to VSSA. Its BGA micro-via rules, SMPS parts and analog solder bridge do not apply here.

### Cited Findings
- The AN5373 Fig. 19 schematic (STM32U575 LQFP100, no SMPS) is summarised in Q1. It is a schematic only; AN5373 contains no layout images of it. — [AN5373 Fig. 19, p.39](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)
- AN6316 B2413 board:
  - Four layers, FR-4 (εr 4.5), 34 × 20.32 mm, 0.7 mm thick, 35 µm copper.
  - Micro vias only because of the UFBGA169 package. Other parts use standard through vias.
  - All components on the top side.
  - 120 µm clearance. Tracks connected to BGA balls are at most 200 µm for power and 150 µm for signals **[N/A: BGA escape]**.

  — [AN6316 §2 p.3, §3.1 p.4, §4.2 pp.8–9](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [ST-REC] "All VDDs of the chip are regrouped in one single VDD MCU in a star distribution". Fig. 15 shows the 100 nF capacitors spread around the package perimeter at the supply balls, and the 10 µF capacitors on the star branches (read from the rendered figure). "Power supply track width = 400 µm." — [AN6316 §4.4.2 Fig. 15, pp.10–11](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [ST-REC] Analog supply on the AN6316 board:
  - VDDA and VREFP each get 1 µF + 100 nF, "connected directly to the analog ground pin VSSA".
  - Fig. 17 shows the capacitors on a local "A GND" copper area that joins the VSSA pad.
  - That area connects to main ground through solder bridge SB38. This is **[N/A]**: a development-board measurement feature, which the brief tells us not to copy.

  — [AN6316 §4.4.2 Figs. 16–17, pp.11–12](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [N/A] The AN6316 board runs the SMPS, whose "1.2 V … two LDOs … are decoupled by 2 × 2.2 µF". Its placement rule (U5 oriented so the SMPS sits on the side away from the ST67, "a noisy source that can affect RF performances") does not apply to the LDO-only device. — [AN6316 §3.1 p.4, §4.4.2 p.11](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- NUCLEO-U575ZI-Q uses the STM32U575ZIT6Q (SMPS, LQFP144), so it has no VCAP. VDDA and VREF+ are set by solder bridges:
  - SB55 ON / SB54 OFF: "VDDA/VREF follows 1V8 to 3V3 VDD_MCU".
  - SB55 OFF / SB54 ON: "VDDA/VREF fixed to 3V3".

  Either way VDDA and VREF+ are tied together, as on the EMG board. — [UM2861 pp.2–3, p.24](https://www.st.com/resource/en/user_manual/um2861-stm32u5-nucleo144-board-mb1549-stmicroelectronics.pdf)

### Inferences
- With no ST VCAP layout to copy, the VCAP review rests on three things: DS13737's capacitor characteristics (ESR < 20 mΩ at 3 MHz), the generic Fig. 17 pin → capacitor → via pattern, and the wiki's "as close as possible to VCAP pins".
- AN6316's 400 µm star suggests a width floor for 3V3_DIG branches feeding the five VDD pins. On this board, an L3 3V3_DIG pour or short 0.3–0.4 mm branches from the bulk capacitor to each VDD capacitor via are equivalent.

**Consolidated review checklist for the routed copper around U_MCU1**

Tags: H = hard, R = ST recommendation, G = general practice.

1. **(H)** Footprint and symbol use the non-SMPS LQFP100 map: 19–22 = VSSA / VREF− / VREF+ / VDDA; 48 = VCAP; 49/50 = VSS/VDD; no pin of the SMPS package.
2. **(H/R)** Each C_MCU_VDDn straddles its pair (10/11, 27/28, 49/50, 74/75, 99/100) on L1. The path is pin → pad → via, with its own VDD and GND vias outboard. No long shared return traces. C_MCU_BULK sits on the 3V3_DIG entry to the MCU.
3. **(H)** MCU_VCAP (4.7 µF) straddles 48/49 on L1. No via, test point or branch on the VCAP net. **(G)** Trace ≤ about 2 mm and ≥ 0.3 mm (budget from ESR < 20 mΩ at 3 MHz). **(G)** 1–2 GND vias to L2 at the pad, separate from the VDD3 capacitor's via.
4. **(H/R)** One 100 nF + 1 µF at VREF+ (21) and one at VDDA (22), 100 nF nearest the pin. GND legs go to VREF−/VSSA (20/19) with vias to L2. VREF− and VSSA each tie to GND. **(G)** Split the 3V0_ANA feed at the 1 µF node, as a dedicated branch from the TPS7A2030. It must not run parallel to SPI or switcher traces.
5. **(R)** C_VBAT (100 nF) at pin 6 and C_VDDUSB (100 nF) at 73/74, each with a GND via at the pad.
6. **(H/R)** C_NRST (100 nF) at pin 14 with a GND via. R_NRST nearby. NRST reaches J_SWD pin 5. No fast aggressor runs beside the NRST trace.
7. **(R)** R_MCU_BOOT0_PD at pin 94 with a short trace. The TP_MCU_BOOT0 stub is short. **(G)** No clock or SPI trace runs along it.
8. **(R)** For each of R_ADC/C_ADC1..5:
   - **(G)** C within about 1–3 mm of its pin, with no via between.
   - **(G)** Its own GND via in the analog corner.
   - **(R)** Tracks run over solid L2, with no digital crossings on L1 and no L3 digital traces or via rows under the ADC corridor.
   - **(G)** Any guard trace is stitched.
   - **(R)** The C_MCU_VDD2 loop at 27/28 is kept tight inside the analog pin group.
9. **(R)** SPI:
   - **(G)** The 22 Ω resistors sit at their drivers: SCK, MOSI and CS at MCU pins 52/54/51; MISO at the module.
   - **(R)** Short inner-layer (L3) corridor, about 50 Ω, with coplanar ground.
   - **(G)** Stitching vias at layer changes where L4 is also a reference.
   - **(R)** Away from the analog bank, VCAP, NRST, BOOT0 and the switching cell.
   - **(G)** No SCK stubs or test points. No serpentines.
10. **(R)** SWD: PA13/PA14 go to J_SWD with no added capacitors or pull resistors. **(G)** Route around the 73–75 decoupling capacitors, keep lines short, and keep SWCLK away from the ADC corner.
11. **(R/H)** Unused PH0/PH1 (12/13) and PC14/PC15 (8/9) are left unrouted and set to analog mode in firmware. No floating copper stubs on them.
12. **(R)** L2 has no slots under the MCU. Free areas on L1, L3 and L4 are filled with GND and stitched. Supply traces run next to their ground return to keep loop area small.

### Gaps
- I did not retrieve the NUCLEO-U575ZI-Q (MB1549) schematic pack, Gerbers, or any Discovery-kit layout. Their exact capacitor positions and via patterns are unverified, and they use SMPS parts anyway.
- I found no ST layout with the non-SMPS U575 VCAP. VCAP geometry above is inferred from generic ST guidance.
- The AN6316 figure descriptions come from low-resolution rendered images. Exact capacitor-to-ball distances are not stated in the text.
