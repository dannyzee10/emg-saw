# Unbroken Planes and Tight Loops Govern Routing

Judge this board's routed copper on four things above all. L2 must be unbroken, and so must L4 under every L3 trace. Every switching and decoupling loop must close on L1 in the order pin → capacitor pad → via. The ST67W611M1 antenna zone must be free of copper on all four layers. And the board must be ordered as the exact JLC04121H-3313 stack-up with a copper-to-edge setback of at least 0.4–0.5 mm. The part makers give almost no numeric routing distances. TI, ADI, ST, Microchip and Murata give no minimum spacing between the switcher and the analog circuits, no limit on LX copper, and no trace widths for these parts. The firm numbers come from three places instead:

- **Component limits.** Examples are the TPS631000 low-side FB resistor ≤ 100 kΩ, VCAP ESR < 20 mΩ at 3 MHz, and TPS7A2030 COUT of 1–200 µF.
- **Land patterns.** Examples are the BK13C's 0.18 mm pads at 0.35 mm pitch and the ST67's 5 mm antenna portion.
- **Fabricator limits.** Examples are 0.09/0.09 mm track and space, and 0.4 mm copper-to-V-cut.

Three fabrication items outrank any single trace:

- **The stack-up must be named on the order.** JLC's default 1.2 mm stack is JLC04121H-7628. If that is built, a 0.161 mm line on L1 designed for 50 Ω comes out at about 71.5 Ω.
- **The 0.254 mm edge rule fails panel assembly.** The 0.35 mm-pitch connectors need Standard PCBA, and on a board only 45 mm wide that means a panel. A V-cut panel needs 0.4 mm copper-to-edge, which the exported rule fails.
- **Exposed-pad vias need a written decision.** The vias under the BQ24072T and the ST67 need a documented fill, tent or paste treatment.

The tables below contain about 100 checks, grouped by board region. Each is graded P0 (stop the line), P1 (performance) or P2 (margin or hygiene), so a reviewer can walk the copper one block at a time, whether it was autorouted or hand-routed. Where sources conflict, the report says which rule governs and why. Examples are ST's datasheet "corner" placement versus AN6316's "middle-edge", and AN2834's split ground planes versus TI's single plane.

**Priority key.** **P0 (stop the line):** the copper breaks a manufacturer "must", a spec limit, a fabricator limit, or a condition for RF function or certification. Fix it before anything else. **P1:** a manufacturer recommendation, or a derived consequence of one, that sets noise, accuracy, EMI or thermal margin. **P2:** margin, rule hygiene or project/general practice with no manufacturer backing. The report marks derived numbers "(derived)". They are calculated from the cited equations and data, not quoted from a manufacturer.

## Ordering the wrong JLC stack would shift impedance by 40 %

The Altium export matches JLC's **JLC04121H-3313** template exactly:

| Layer | Thickness |
|---|---|
| L1 copper | 35 µm |
| 3313 prepreg | 0.0994 mm |
| L2 copper | 15.2 µm |
| Core | 0.865 mm |
| L3 copper | 15.2 µm |
| 3313 prepreg | 0.0994 mm |
| L4 copper | 35 µm |
| **Pressed total** | **1.1642 mm** |

JLC's live API lists this template as enabled, but **not as the default**. The default 1.2 mm stack is JLC04121H-7628, with 0.2104 mm prepreg and a 0.6 mm core ([JLC impedance-template API](https://cart.jlcpcb.com/api/overseas-shop-cart/v1/shoppingCart/getImpedanceTemplateSettings); [JLC stack-up page](https://jlcpcb.com/impedance)). The researcher field-solved both stacks using JLC's published parameters: prepreg Dk 4.1, core Dk 4.6, and 1.2/0.6 mil solder mask at Er 3.8 ([JLC calculator guide](https://jlcpcb.com/help/article/User-Guide-to-the-JLCPCB-Impedance-Calculator)). On the 3313 stack, 50 Ω needs **≈0.161 mm on L1 with solder mask**, or 0.15 mm beside a stitched GND pour at a 0.2 mm gap. On L3 it needs **≈0.136 mm**. On the default 7628 stack the same 0.161 mm L1 line becomes about 71.5 Ω (derived).

The geometry has a less obvious consequence. **L3 is 0.0994 mm from L4 but 0.865 mm from L2, so L4, not L2, is L3's real return plane.** An L3 trace over a void in L4 rises to about 112–119 Ω (derived). The project brief already states that "L3 signals must not depend on a fragmented L4 return" ([layout brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)).

The exported rules sit comfortably inside JLC's multilayer limits. JLC allows **0.09/0.09 mm** track and space, a via ring of 0.05 mm minimum and 0.075 mm preferred, 0.2 mm from via hole to track, 0.2 mm via hole-to-hole, and ±20 % track-width tolerance ([JLC PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)). The problems are in a few specific values:

- **Edge setback.** The exported edge rule is **0.254 mm**, although the brief intends 0.50 mm ([RULES.txt](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/NATIVE_FINAL_20260924T015854610Z/RULES.txt)). JLC requires ≥ 0.2 mm to a routed edge and **≥ 0.4 mm to a V-cut edge** ([JLC PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)).
- **Why V-cut is likely.** Only Standard PCBA places 0.35 mm-pitch parts. Economic PCBA stops at 0.4 mm pitch. Standard PCBA needs a single board of at least 70 × 70 mm, or a panel with rails and fiducials ([JLC PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)). An 80 × 45 mm board therefore gets panelised, probably with V-cut, which is exactly the case the 0.254 mm rule fails.
- **Via-in-pad.** JLC cannot ink-plug a via that sits in a pad or within 0.35 mm of one ([JLC via covering](https://jlcpcb.com/help/article/pcb-via-covering)). Filled-and-capped vias (POFV) are extra-cost on 4-layer boards ([JLC POFV](https://jlcpcb.com/news/free-via-in-pad-6-20-layer-pcbs-pofv)). The exposed-pad vias under the BQ24072T and the ST67 therefore need a decision written into the order.
- **Current is not the binding constraint.** JLC's plating is **18 µm on average**. On that basis a 0.3 mm via barrel carries about 1.3–1.4 A at a 10 °C rise (derived) ([smps.us IPC-2152 fit](https://www.smps.us/pcb-calculator.html); [Altium via current](https://resources.altium.com/p/pcb-current-carrying-capacity-how-hot-too-hot)). Temperature rise almost never limits a 0.6 A board. Millivolts of IR drop and loop inductance do.

**Table F: fabrication and stack-up checks**

| ID | Pri | What to verify in the copper, rules or order | Source |
|---|---|---|---|
| F1 | P0 | The order names **JLC04121H-3313** (1.2 mm; 1 oz outer, 0.5 oz inner). Remove the spurious 0.32 mm FR-4 layer below L4 from the Altium stack. Add solder-mask layers so the impedance solver is not ≈3 Ω high. | ([JLC API](https://cart.jlcpcb.com/api/overseas-shop-cart/v1/shoppingCart/getImpedanceTemplateSettings); [STACK.txt](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/NATIVE_FINAL_20260924T015854610Z/STACK.txt)) |
| F2 | P0 | Copper-to-edge is **≥ 0.50 mm** everywhere (V-cut needs ≥ 0.4, routed edge ≥ 0.2). Re-run DRC after changing the 0.254 mm rule. | ([JLC PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)) |
| F3 | P0 | The assembly tier matches the parts. The 0.35 mm BK13C needs Standard PCBA, so plan a panel with 5 mm rails, 1 mm fiducials placed 3.85 mm from the panel edge, and 2 mm tooling holes. | ([JLC PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities); [JLC process edges](https://jlcpcb.com/help/article/specifications-for-adding-process-edges-and-positioning-holes)) |
| F4 | P0 | Every via in or within 0.35 mm of a pad has a treatment written in the order notes: POFV (charged), plugged, or tented plus windowed paste. Tents are guaranteed only for holes ≤ 0.4 mm. Filled vias need ≥ 0.35 mm to other mask openings. | ([JLC via covering](https://jlcpcb.com/help/article/pcb-via-covering); [JLC POFV](https://jlcpcb.com/news/free-via-in-pad-6-20-layer-pcbs-pofv)) |
| F5 | P1 | The 0.10–0.125 mm pad-to-pad exceptions apply only inside manufacturer land patterns, never to routed copper. JLC's stated SMD pad-to-pad is 0.15 mm, so flag these for DFM. | ([JLC PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)) |
| F6 | P1 | The mask sliver rule of 0.10 mm is exactly JLC's green-mask limit and fails black or white mask (0.13 mm). With +0.05 mm mask expansion, any pad gap under 0.20 mm becomes one ganged opening. | ([JLC PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)) |
| F7 | P1 | 0.6/0.3 mm vias carry no surcharge. **0.45/0.2 mm vias sit exactly on the surcharge threshold**, so never shrink the pad below 0.45 mm. Via hole-to-hole must be ≥ 0.2 mm and inner-layer hole-to-copper ≥ 0.2 mm. The HoleToHole rule was exported without a value, so set it. | ([JLC PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities); [RULES.txt](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/NATIVE_FINAL_20260924T015854610Z/RULES.txt)) |
| F8 | P1 | SPI class widths. L1: 0.16 mm, or 0.15 mm with a stitched GND pour at ≥ 0.2 mm. L3: **0.14 mm** (≈49 Ω, needs a scoped exception to the 0.15 mm minimum) or 0.15 mm (47.7 Ω). The current preferred 0.18 mm is 47 Ω on L1 but **43.5 Ω on L3** (derived). | ([JLC calculator guide](https://jlcpcb.com/help/article/User-Guide-to-the-JLCPCB-Impedance-Calculator); [JLC stack-up](https://jlcpcb.com/impedance)) |
| F9 | P1 | No long 0.15 mm neck on L3 (15.2 µm copper) carries more than about 0.44 A, the 10 °C limit from the IPC-2152 generic fit. At 0.6 A, 0.9 mm × 20 mm on L3 drops about 15 mV (derived). Size power copper by the mV budget. | ([smps.us IPC-2152 fit](https://www.smps.us/pcb-calculator.html)) |
| F10 | P2 | Rule hygiene. Delete the default Width rule (0.254 mm min = max, priority 10), which forces unclassed nets to 0.254 mm. Delete the default RoutingVias rule (1.27/0.71 mm). Confirm the −0.35 mm via-tenting rule exists; it is absent from the export. | ([RULES.txt](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/NATIVE_FINAL_20260924T015854610Z/RULES.txt)) |

## Every return path depends on an unbroken L2 and L4

The strongest piece of evidence is ADI's AN-139. A solid plane on the next layer "is one of the most effective ways to reduce EMI". With 0.13 mm of insulation between loop and plane, loop inductance falls from **187 nH to 13 nH**. The note's instruction is blunt: "Keep the layer 2 shield solid. Place vias away from the hot loop for connections to GND planes you want to keep quiet" ([ADI AN-139](https://www.analog.com/media/en/technical-documentation/application-notes/an139f.pdf)). This board's L1–L2 prepreg is 0.0994 mm, thinner than AN-139's example. L2 is therefore an excellent image plane, but only while it stays continuous.

The sources disagree on splitting ground:

- **For splitting.** ST's generic AN2834 recommends separate analog and digital planes joined at one star point ([ST AN2834](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)). ADI MT-031 says "when in doubt" start split, but also that "there is no single grounding method which will guarantee optimum performance 100% of the time" ([ADI MT-031](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf)).
- **Against splitting.** TI's biopotential ADC datasheets say splitting "is not necessary when analog, digital and power supply components are properly placed", and that "a single ground plane for analog and digital avoids ground loops" ([TI ADS1298](https://www.ti.com/lit/ds/symlink/ads1298.pdf); [TI ADS1299](https://www.ti.com/lit/ds/symlink/ads1299.pdf)).

For this MCU the device-specific evidence settles it. ST's own STM32U575 reference schematic ties VSSA and VREF− to the common ground ([ST AN5373](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)). The datasheet allows at most **50 mV between any two ground pins, including VREF−** ([ST DS13737](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)). The project's single GND net is therefore the right choice. But it makes placement and plane continuity the only isolation the board has.

MT-031 adds a warning aimed squarely at this workflow: autorouting "will generally lead to a layout disaster on a mixed-signal board, so manual intervention is highly recommended" ([ADI MT-031](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf)).

**Table G: ground-system checks (whole board)**

| ID | Pri | What to verify | Source |
|---|---|---|---|
| G1 | P0 | **L2 carries no traces, slots or merged antipad chains.** Check with particular care under the switching cell, the AFE, the ADC corridor, the BK13 escapes, the ST67 body, the 32 kHz crystal and the MCU. The brief's rule: prove the problem and propose six layers before cutting L2. | ([ADI AN-139](https://www.analog.com/media/en/technical-documentation/application-notes/an139f.pdf); [TI ADS1298](https://www.ti.com/lit/ds/symlink/ads1298.pdf); [layout brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)) |
| G2 | P0 | **L4 GND is continuous under the whole length of every L3 trace**, above all the SPI corridor. A void under an L3 trace sends it to about 112–119 Ω (derived). | ([JLC API stack](https://cart.jlcpcb.com/api/overseas-shop-cart/v1/shoppingCart/getImpedanceTemplateSettings); [layout brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)) |
| G3 | P1 | No isolated GND islands or skinny necks on the L1, L3 or L4 pours. Every fill is stitched to L2. Where holes must break up a plane, a row of holes is better than a long slot. | ([ADI MT-031](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf); [TI ADS1299](https://www.ti.com/lit/ds/symlink/ads1299.pdf); [TI SZZA009](https://www.ti.com/lit/an/szza009/szza009.pdf)) |
| G4 | P1 | There is one GND net with no AGND/PGND split, ferrite link or bridge. Do not import the split-plane advice in AN2834, MT-031, SLVAFJ3 §2.6 or AN2867. Converter and radio return currents close near their sources, not under the AFE-to-ADC path. | ([TI ADS1298](https://www.ti.com/lit/ds/symlink/ads1298.pdf); [ST DS13737](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)) |
| G5 | P1 | Every L1↔L3 signal via that has L4 as a reference has a GND via within about 1 mm, so return current can move between L2 and L4. | ([ST wiki SPI](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_spi&oldid=86022)) |
| G6 | P1 | Each analog-critical or ADC net routed by the autorouter has been reviewed by hand against Tables A, D and M. | ([ADI MT-031](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf)) |

## The 2 MHz buck-boost must close both hot loops on L1

The TPS631000 data sheet gives only two layout sentences:

1. Place the input and output capacitors "as close as possible to the IC", with "wide and direct traces".
2. "The sense trace connected to FB is signal trace. Keep these traces away from LX1 and LX2 nodes."

([TI TPS631000 SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)). The actual geometry comes from the data sheet's Fig 7-24 and from the EVM:

- The inductor sits directly beside the VIN–LX1–LX2–VOUT pin row, with no other copper between it and the IC.
- A GND band with about three vias runs under the package, between the two pin rows. It joins CIN ground, GND pin 7 and COUT ground.
- The GND pad of each capacitor has a 2×3 via array.
- The FB divider sits on the far side from the inductor, and it senses VOUT beyond COUT.

([TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf); [TI SLVUC09 EVM](https://www.ti.com/lit/pdf/slvuc09)).

Pin 7 is on the opposite row from VIN and VOUT. Both the buck loop (CUP4_1 → VIN → FETs → pin 7) and the boost loop (CUP4 → VOUT → pin 7) therefore close through the GND copper that crosses to pin 7. **A GND return that detours around the package, necks down, or relies on one via is the main defect to look for** (derived).

Under-body vias need care. The DRL land pattern leaves only **0.81 mm between the pin rows**. A 0.6 mm via centred there leaves about 0.105 mm to each pad row (derived), so it must either shrink or move outside the package.

The pin mapping below comes from the data sheet ([TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)):

| Row | Pins |
|---|---|
| Power row | VOUT 1, LX2 2, LX1 3, VIN 4 |
| Control row | EN 5, MODE 6, GND 7, FB 8 |

Currents set the copper, not the 0.6 A average. At 3.0 V input the boost-mode peak is **≈0.80 A** by TI's Eq. 3 and up to **≈1.01 A** at tolerance corners by TI's SLVA535B method (derived). The switch current limit is **2.6–3.35 A**, higher in operation ([TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf); [TI SLVA535B](https://www.ti.com/lit/pdf/slva535)). A 1.0 A design current is therefore sensible for VSYS and 3V3_DIG. TI's rules of thumb for that current are ≥ 15 mil (0.381 mm) per ampere and "one standard via per 200 mA" at a layer change ([TI SNVA021C / AN-1149](https://www.ti.com/lit/pdf/snva021)).

No manufacturer gives a numeric distance between a switcher and analog circuits. The only numbers are the project's own: a ≥ 0.5–1.0 mm lateral-separation floor, and a placement goal of "several millimetres" ([layout brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)). One physical point supports keeping sensitive nets out from under the inductor even behind L2: at 2 MHz, copper's skin depth is about **47 µm**, three times the 15.2 µm L2 foil. L2 therefore shields the switching fundamental magnetically only in part, although it shields the edge harmonics well (derived).

### LDO and supervisors

The TPS7A2030 limits are hard and specific:

- CIN ≥ 1 µF.
- COUT 1–200 µF with **ESR ≤ 100 mΩ**.
- VIN ≥ VOUT + 0.3 V.
- An input "well regulated and free of spurious noise".
- PSRR near 1 MHz of only **45 dB at 20 mA and 40 dB at 300 mA**.

([TI TPS7A20 SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)). ADI's AN101 shows why layout matters here: wideband switching spikes "pass directly from input to output", and "stray layout capacitance provides additional unwanted feedthrough paths" ([ADI AN101](https://www.analog.com/media/en/technical-documentation/application-notes/an101f.pdf)).

The 3.30 V → 3.00 V headroom is already at TI's 0.3 V minimum. The TPS631000's ±1 % FB tolerance alone can cut it to 0.267 V (derived). IR drop between CUP4 and UP3's IN pin comes straight out of that margin.

For the TPS3808, keep parasitic capacitance on the open CT pin minimal: 100 pF or more is detected as a timing capacitor. The RESET pull-up must be ≥ 10 kΩ ([TI TPS3808 SBVS050N](https://www.ti.com/lit/ds/symlink/tps3808.pdf)). The LTC2954 data sheet has no layout section. Its guidance is electrical: a 5.1 kΩ + 0.1 µF R-C "close to the PB pin", and ±3 µA ONT/PDT timing nodes ([ADI LTC2954](https://www.analog.com/media/en/technical-documentation/data-sheets/2954fb.pdf)).

**Table P: power-conversion checks (UP2 TPS631000, UP3 TPS7A2030, U_UV1 TPS3808, U_EN1 LTC2954)**

| ID | Pri | What to verify | Source |
|---|---|---|---|
| P1 | P0 | CUP4_1 is the part nearest VIN pin 4 and pin 7, and CUP4 the part nearest VOUT pin 1 and pin 7. Both connect on L1 with short, wide copper. The GND return from both capacitors to pin 7 is wide L1 copper (TI's band under the body), not a detour or a single via. No other VSYS or 3V3_DIG capacitor stands in for them. | ([TI SLVSFH3C §7.4.1, Fig 7-24](https://www.ti.com/lit/ds/symlink/tps631000.pdf)) |
| P2 | P0 | LX1 and LX2 are on L1 only, running pin to inductor pad (about 1 mm, flared from the 0.3 mm pad). They have **no vias, no test pads and no pours on other layers**, and there is no unrelated copper between the IC and the inductor. | ([TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf); [TI SLVAFJ3](https://www.ti.com/lit/pdf/slvafj3); [layout brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)) |
| P3 | P0 | RUP_3, RUP_4 and CUP4_FB are within a few mm of FB pin 8, on the side away from the inductor. RUP_3 senses from the CUP4 VOUT pad or downstream of it, never from copper between the IC and COUT. The FB trace is kept away from LX; if it changes layer, it goes to L3 under solid L2. RUP_4 must be ≤ 100 kΩ (it is exactly 100 kΩ). | ([TI SLVSFH3C §6.3.3, §7.4.1](https://www.ti.com/lit/ds/symlink/tps631000.pdf); [TI SLVAFJ3](https://www.ti.com/lit/pdf/slvafj3); [TI SNVA021C](https://www.ti.com/lit/pdf/snva021)) |
| P4 | P0 | EN (pin 5) and MODE (pin 6) are both connected, since each "must not be left floating". They escape on the pin 5/6 side, away from the LX row. | ([TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)) |
| P5 | P0 | L2 is unbroken under UP2, the inductor, CUP4, CUP4_1, the LX copper and the path from the capacitor grounds to pin 7. | ([ADI AN-139](https://www.analog.com/media/en/technical-documentation/application-notes/an139f.pdf)) |
| P6 | P1 | GND via clusters sit at the GND pads of CUP4_1 and CUP4 (TI's figure shows 2×3 at each), with 2 vias near pin 7 and a separate via for RUP_4's ground. Under-body vias are either omitted or reduced so they clear both pad rows in the 0.81 mm gap. | ([TI SLVSFH3C Fig 7-24](https://www.ti.com/lit/ds/symlink/tps631000.pdf)) |
| P7 | P1 | No FB, 3V0_ANA, VREF, AFE, CT, PB, ONT/PDT, crystal or SPI copper runs on L3 or L4 directly under the inductor, the LX nodes or the hot loops. Quiet-ground vias stay outside the hot-loop via field. | ([ADI AN-139](https://www.analog.com/media/en/technical-documentation/application-notes/an139f.pdf); [TI SNVA021C](https://www.ti.com/lit/pdf/snva021)) |
| P8 | P1 | VSYS and 3V3_DIG trunks are sized for 1.0 A: a polygon or 0.8–1.0 mm on L1 (the minimum is 0.38 mm), and ≥ 0.7 mm or a polygon on L3. Any 1 A layer change has 3–5 vias. | ([TI SNVA021C](https://www.ti.com/lit/pdf/snva021); [smps.us](https://www.smps.us/pcb-calculator.html)) |
| P9 | P2 | Lateral separation from sensitive nets is at least 0.5–1.0 mm, with no parallel runs next to LX or the inductor. This is a project rule, not a manufacturer rule. | ([layout brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)) |
| P10 | P2 | The CUP4_FB (10 pF) footprint sits across RUP_3 at the FB end. TI's EVM leaves this position unfitted, so check loop response on the bench. | ([TI SLVUC09](https://www.ti.com/lit/pdf/slvuc09); [TI SNVA021C](https://www.ti.com/lit/pdf/snva021)) |
| P11 | P0 | UP3's CIN is at IN pin 1 and its COUT at OUT pin 5. Both share L1 GND copper at pin 2, with vias to L2 there (TI Fig 7-7). | ([TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)) |
| P12 | P1 | UP3 is fed by a short 3V3_DIG branch taken at or near CUP4, not from the far end of the digital or radio distribution. Budget ≤ about 10 mV of IR drop, because headroom is only 0.3 V. | ([TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)) |
| P13 | P1 | 3V3_DIG (the LDO input) and 3V0_ANA (its output) never run side by side. 3V0_ANA stays away from LX, the inductor, the hot loops and the SPI corridor. | ([ADI AN101](https://www.analog.com/media/en/technical-documentation/application-notes/an101f.pdf); [layout brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)) |
| P14 | P1 | Total capacitance on 3V0_ANA, including the AFE, VDDA/VREF+ and the electrode boards reached through the flexes, stays ≤ 200 µF with ESR ≤ 100 mΩ. | ([TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)) |
| P15 | P1 | U_UV1: CT (pin 4) has no trace, stub or test pad. C_UV_BYPASS sits at VDD pin 6 with a short via. The RESET pull-up is ≥ 10 kΩ. SENSE is tapped at a quiet point, not in the CIN/LX area. | ([TI SBVS050N](https://www.ti.com/lit/ds/symlink/tps3808.pdf)) |
| P16 | P1 | U_EN1: the ONT and PDT capacitors sit at pins 3 and 7 with the shortest loop to GND pin 4. The PB R-C is at the PB-pin end. The PB, EN, INT and KILL traces run neither parallel to nor on the LX side of UP2. | ([ADI LTC2954](https://www.analog.com/media/en/technical-documentation/data-sheets/2954fb.pdf)) |

## Charger, USB-C and ESD belong in one connector-edge power zone

**BQ24072T.** TI's charger layout rules are qualitative:

- The IN and OUT capacitors go "as close as possible" to the IC, with short runs to the thermal pad.
- "All low-current GND connections should be kept separate from the high-current charge or discharge paths".
- High-current paths are sized for the maximum current.

Two statements are firm: VSS "must be connected to ground at all times", and "Do not use the thermal pad as the primary ground input for the device" ([TI BQ24072T SLUS937C](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)). ISET and ILIM must be connected, because leaving ILIM open "disables all charging". IN capacitance must stay **below 10 µF**, because USB inrush is not limited.

TI's RGT0016C example uses a **1.68 mm thermal land with five Ø0.2 mm vias** and 85 % paste. It says vias under paste "be filled, plugged or tented". SLUA271C adds three points ([TI SLUA271C](https://www.ti.com/lit/an/slua271c/slua271c.pdf)):

- A top tent needs a mask opening of hole + 0.1 mm.
- Exposed-pad paste is typically 50–70 %.
- Keep a routing and via keep-out next to pin 1.

EN2 is tied to GND, so the input is capped at 0.5 A. **OUT and BAT copper must still carry the whole system load on battery**, about 1 A at planning level (derived). Charger dissipation is about **0.76–1.0 W**. At the JEDEC RθJA of 45.8 °C/W that is a 35–46 °C junction rise (derived), so heat-sensitive analog parts should stay away from UP1.

**USB-C.** The GCT USB4105 drawing fixes the pins:

| Function | Pins |
|---|---|
| GND | A1, A12, B1, B12 |
| VBUS | A4, A9, B4, B9 |
| CC | A5, B5 |
| Shell | GND |

The recommended layout uses 0.60 mm combined pads and 0.30 mm signal pads at 0.50 mm pitch. That leaves only about 0.20 mm between pads (derived) ([GCT USB4105 drawing](https://gct.co/files/drawings/usb4105.pdf)). GCT gives no rules on trace width, vias or shell grounding.

**ESD.** TI's SLVA680A gives the governing geometry ([TI SLVA680A](https://www.ti.com/lit/an/slva680a/slva680a.pdf)):

- The TVS goes as near the connector as the design rules allow.
- Route "directly from the ESD Source to the TVS" with no stub and ideally no via.
- Put "one VIA immediately adjacent to the ground pin of the TVS", because **0.25 nH of ground inductance adds about 10 V** at an 8 kV discharge.

Nexperia's datasheets repeat the same list, including "avoid shared transient return paths to a common ground point" ([Nexperia PESD5V0S1BA](https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA_BB_BL.pdf)).

**Fuel gauge.** The MAX17048 "measures VCELL between the VDD and GND pins", and CELL is "not internally connected" ([ADI MAX17048](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf)). The VDD branch and the GND return therefore form the Kelvin pair. The gauge's ±7.5 mV accuracy is easily spoiled by tapping a charge-current trunk: 10 mm of 0.5 mm, 1 oz copper adds about 3–10 mV between 0.3 A and 1 A (derived).

**Table C: charger, USB-C, ESD, fuel-gauge and battery-NTC checks**

| ID | Pri | What to verify | Source |
|---|---|---|---|
| C1 | P0 | UP1 VSS (pin 8) has its own low-impedance connection to GND (a trace to the EP and/or a via); the EP is not the only ground. CE (4), EN2 (5) and TD (15) go to GND with short stubs. | ([TI SLUS937C](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)) |
| C2 | P0 | C_IN_ is within about 1–2 mm of IN pin 13. C_OUT_ is at pins 10/11 and C_BAT at pins 2/3, with each pin pair joined at the pads. Each capacitor's GND pad has its own via to L2. | ([TI SLUS937C §12.1, Fig 37](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)) |
| C3 | P0 | RISET (pin 16), R_LIM (pin 12), R_TMR (pin 14) and R_TS_SER (pin 1) are connected and sit within about 1–2 mm of their pins. Their ground ends return to the IC's local EP/VSS ground, not into the capacitor or TPS631000 return vias. | ([TI SLUS937C](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)) |
| C4 | P1 | OUT (VSYS) and BAT (VBAT_CELL) copper is sized for about 1 A on-battery load (0.8–1.0 mm on L1). IN/VBUS is sized for 0.5 A. There are at least 2 vias at every layer change. | ([TI SLUS937C](https://www.ti.com/lit/ds/symlink/bq24072t.pdf); [layout brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)) |
| C5 | P1 | EP vias match TI's pattern: 4–5 × Ø0.2 mm at 0.58 mm offsets. They are filled, plugged, or top-tented (mask Ø = hole + 0.1 mm), never tented from the bottom only. Paste is windowed away from open vias. No trace runs through the 0.26 mm lead-to-EP gap (derived). There is a routing and via keep-out at pin 1. | ([TI SLUS937C RGT0016C](https://www.ti.com/lit/ds/symlink/bq24072t.pdf); [TI SLUA271C](https://www.ti.com/lit/an/slua271c/slua271c.pdf)) |
| C6 | P1 | The EP vias tie into L2 and an L4 pour for heat spreading. L3 power and signal copper stays clear of the UP1 via field. The AFE, reference parts and 32 kHz crystal are placed away from the ≈1 W source. | ([TI SLUS937C §12.3](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)) |
| C7 | P2 | No bulk capacitance is added on VBUS: the total must stay under 10 µF. | ([TI SLUS937C §9.4.1](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)) |
| U1 | P0 | Both VBUS pad pairs (A4B9, B4A9) and both GND pairs (A1B12, B1A12) are connected, and all four shell stakes are on GND. D+, D− and SBU (A6/A7/A8/B6/B7/B8) are bare pads with no stubs. | ([GCT USB4105 drawing](https://gct.co/files/drawings/usb4105.pdf); [project pin table](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/review_2026-09-16/power_evidence/power_pin_tables.md)) |
| U2 | P0 | There is no copper and no via between pads in the USB-C pad row (0.20 mm gaps). CC2 (B5) turns away from the adjacent VBUS pad B4A9 immediately; inspect that gap for bridges. | ([GCT USB4105 drawing](https://gct.co/files/drawings/usb4105.pdf)) |
| U3 | P1 | The L1 GND around the shell slots and GND pads is stitched to L2 and L4 with several 0.6/0.3 mm vias. The VBUS lead from connector to charger drops only a few mV at 0.5 A, because only about 120 mV separates the 4.75 V recommended input from the 4.63 V maximum VIN-DPM (derived). | ([TI SLVA680A](https://www.ti.com/lit/an/slva680a/slva680a.pdf); [TI SLVU274E](https://www.ti.com/lit/ug/slvu274e/slvu274e.pdf)) |
| E1 | P0 | Each connector pad runs straight onto its TVS pad, with the trace passing through the pad (no T-stub) and **no via before the TVS**. CC1/CC2 reach D_CC_ESD pins 1/2 on L1; vias are allowed only after the TVS. | ([TI SLVA680A §2.1–2.3](https://www.ti.com/lit/an/slva680a/slva680a.pdf); [Nexperia PESD5V0S1BA](https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA_BB_BL.pdf)) |
| E2 | P0 | The ground pads of D_VBUS (pin 2) and D_CC_ESD (pin 3) each have a GND via touching or immediately beside the pad, going into L2. These vias are not shared with converter or charger returns, and the ESD return path never crosses the AFE. | ([TI SLVA680A §2.4](https://www.ti.com/lit/an/slva680a/slva680a.pdf); [Nexperia PESD5V0S1BA](https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA_BB_BL.pdf)) |
| E3 | P1 | VBUS runs in the order connector → D_VBUS → C_VBUS (with its own GND via) → C_IN_ → UP1.13. R_TS_TOP taps VBUS at the C_IN_/UP1 end. No unprotected trace enters the connector-to-TVS zone on any layer. Corners there are 45° or arcs. | ([TI SLVA680A §2.2](https://www.ti.com/lit/an/slva680a/slva680a.pdf)) |
| FG1 | P1 | UP4 CELL (2) and VDD (3) are tied at the IC and run as one thin, dedicated branch to the J_Li-Po VBAT_CELL pin. The branch is not tapped from C_BAT, the UP1 BAT copper or a VSYS/VBAT trunk. CU6_1 (0.1 µF) sits directly across pins 3 and 4 with a GND via. | ([ADI MAX17048](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf)) |
| FG2 | P1 | UP4 GND (4) and the EP return through a via near the J_Li-Po GND entry, outside the charge and converter return corridor. CTG and QSTRT tie to that same local ground. SDA, SCL and ALRT stay away from LX, the antenna and TS. There is only one I2C pull-up pair on the board. | ([ADI MAX17048](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf); [ADI MAX17048 EV kit](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048EVKIT-MAX17049EVKIT.pdf)) |
| T1 | P1 | The TS divider references UP1's own IN node and VSS/EP ground; the thresholds are 12.5 % and 25 % of VIN. The node from R_TS_SER.2 to UP1.1 (100 kΩ source) is about 1–2 mm long. BAT_TEMP runs over unbroken L2 alongside its pad-1 GND return, away from LX, SPI, the antenna and the USB ESD zone. | ([TI SLUS937C](https://www.ti.com/lit/ds/symlink/bq24072t.pdf); [TI SLVA680A](https://www.ti.com/lit/an/slva680a/slva680a.pdf)) |

## A 205× gain makes VREF taps as sensitive as electrode inputs

The AD8237 data sheet gives four layout rules ([ADI AD8237](https://www.analog.com/media/en/technical-documentation/data-sheets/ad8237.pdf)):

- "closely match the impedance of each path" into +IN and −IN, and place added source resistance "close to the in-amp inputs";
- place 0.1 µF "as close as possible to each supply pin";
- "tie REF to the appropriate local ground";
- BW: "Do not leave this pin floating."

On this board REF is driven by the servo integrator, as in AD8237 Fig. 77, and REF is a gained input: VOUT = (VREF + V+IN − V−IN)(1 + R2/R1). Two consequences follow for routing (derived):

- **VREF_A differences between taps count as signal.** Any in-band difference in VREF_A between channel n's RL return and its servo IN+ is amplified by about **25.4 × 8.06 ≈ 205**, the same as the EMG signal.
- **The Vservo trace is an input net.** Anything the Vservo trace to pin 6 picks up is treated as signal too.

RF is the larger threat than 50 Hz. ADI warns that once an in-amp rectifies RF, "no amount of low-pass filtering at the in-amp output will remove the error" ([ADI AN-671](https://www.analog.com/media/en/technical-documentation/application-notes/AN-671.pdf)). With Wi-Fi on the same board, compact input loops over solid L2 are the defence.

The MCP6404 needs **0.01–0.1 µF within 2 mm** of VDD and a bulk capacitor ≥ 1 µF within 100 mm. It also needs a series isolation resistor when the load exceeds about **100 pF at G = +1**. That matters for U1C, which drives VREF_A with no isolation resistor ([Microchip MCP640x DS20002229E](https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP6401-Data-Sheet-DS20002229.pdf)). Guard rings matter only "where low input bias current is critical". The worst leakage here works out to microvolts (derived), so guard rings are optional and L2 should stay whole under the op-amps.

**ADC input RC.** ST describes the physics: an external capacitor "to the input pin" acts as the charge reservoir for the 5 pF sample-and-hold, and PCB parasitic capacitance "downgrades the conversion accuracy" ([ST AN2834](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf); [ST DS13737](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)). TI states the placement rule explicitly: RC filters "are placed immediately next to the input pins" ([TI ADS8860](https://www.ti.com/lit/ds/symlink/ads8860.pdf)). With 330 Ω and 10 nF, charge sharing costs at most about 8 LSB on a full-scale channel-to-channel step, and it settles in about 9 µs against a 500 µs per-channel interval (derived).

**BK13C connectors.** Hirose's drawing for the BK13C fixes the lands:

- 0.18 mm signal pads at 0.35 mm pitch;
- 0.75 mm power pads;
- 0.215 × 1.04 mm end tabs;
- a cross-hatched **"INSULATION AREA"** between the pad rows.

([Hirose BK13C06-10DS drawing](https://www.hirose.com/en/product/document?clcode=CL0480-0720-0-95&documentid=BK13C06-10DS2-0.35V%28895%29_4800720095_2D_ENG&documenttype=2DDrawing&lang=en&productname=BK13C06-10DS%2F2-0.35V%28895%29&series=BK13C)). Hirose's sister-series guidelines give the meaning of such an area. The BM28 guideline requires solder resist on any routing there, and warns that patterns under the connector can push it up off its solder joints ([Hirose BM28 guideline](https://www.hirose.com/en/product/document?clcode=CL0673-5048-0-51&productname=BM28B0.6-6DS%2F2-0.35V%2851%29&series=BM28&documenttype=Guideline&lang=en&documentid=0001442212)). The DF40 guideline says patterns, via holes and resist beneath the connector "may cause solder defects" ([Hirose DF40 guideline](https://www.hirose.com/en/product/document?clcode=CL0684-4032-1-51&productname=DF40C-100DP-0.4V%2851%29&series=DF40&documenttype=Guideline&lang=en&documentid=0001442210)). The connector "has no polarity" ([Hirose BK13 catalog](https://www.hirose.com/en/product/document?clcode=CL0480-0720-0-95&documentid=en_BK13C_CAT&documenttype=Catalog&lang=en&productname=BK13C06-10DS%2F2-0.35V%28895%29&series=BK13C)).

**Table A: AFE, ADC-input RC and BK13C checks**

| ID | Pri | What to verify | Source |
|---|---|---|---|
| A1 | P0 | Each INA's BW (pin 1) and −VS (pin 4) go straight to GND vias; BW is never floating. | ([ADI AD8237](https://www.analog.com/media/en/technical-documentation/data-sheets/ad8237.pdf)) |
| A2 | P0 | Each AD8237 +VS (pin 5) has its own 0.1 µF right at the pin. Each MCP6404 VDD (pin 4) has 0.01–0.1 µF within **2 mm**. The GND via sits at the capacitor pad, with **no via between pin and capacitor**. MCP6404 VSS (pin 11) has a direct via to L2. | ([ADI AD8237](https://www.analog.com/media/en/technical-documentation/data-sheets/ad8237.pdf); [Microchip MCP640x §4.4](https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP6401-Data-Sheet-DS20002229.pdf); [TI ADS1299](https://www.ti.com/lit/ds/symlink/ads1299.pdf)) |
| A3 | P1 | The RDD resistors sit at INA pins 2/3, and the −IN junction is made at the pin. The post-RDD +IN and −IN nets are short and geometrically alike. Va/Vb/Vc and the INA inputs run as a tight group on L1 over unbroken L2. | ([ADI AD8237 p.23](https://www.analog.com/media/en/technical-documentation/data-sheets/ad8237.pdf); [ADI AN-671](https://www.analog.com/media/en/technical-documentation/application-notes/AN-671.pdf)) |
| A4 | P1 | For each channel, RL_n's VREF_A end and servo_n's IN+ come from one local VREF_A point, with no other channel's current flowing between them. Each Vservo_n trace (op-amp output to INA pin 6) is short, on L1 over L2, and away from digital and switching copper. | ([ADI AD8237 Figs. 70, 77](https://www.analog.com/media/en/technical-documentation/data-sheets/ad8237.pdf); [analog pin audit](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/review_2026-09-16/analog_pin_audit.md)) |
| A5 | P1 | **No capacitor and no large pour is tied to VREF_A** (keep it well under 100 pF). U1C has no isolation resistor on that output. | ([Microchip MCP640x §4.3](https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP6401-Data-Sheet-DS20002229.pdf)) |
| A6 | P1 | VREF_B is a star: U1 pin 14 → five R_VREFn (68 Ω) → a private trace to each J_FPCn pin 8. After routing, VREF_B_FPC1 to 5 must still be **five distinct nets**, with no shared pour, via or test point. Copper fan-out before the resistors is ≪ 100 pF. | ([BK13 contract](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/BK13_ASSEMBLY_CONTRACT_SOURCE.md); [Microchip MCP640x §4.3](https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP6401-Data-Sheet-DS20002229.pdf)) |
| A7 | P1 | Summing nodes are short: Rservo_n and Cservo_n at the servo IN−, and RGN, RG and CH at the gain-stage IN−. Long runs go on the low-impedance side (INA_OUT, VOUT). RH spans pins 7–8 and RL sits at FB, so they share temperature. | ([ADI in-amp guide](https://www.analog.com/media/en/training-seminars/design-handbooks/designers-guide-instrument-amps-complete.pdf); [ADI AN-671](https://www.analog.com/media/en/technical-documentation/application-notes/AN-671.pdf)) |
| A8 | P1 | Analog-critical nets (Va/Vb/Vc, INA inputs, Vservo, VREF_A taps, summing nodes, VOUT) are on **L1 only**. Digital nets cross them only on L3, at 90°, and never under the RC capacitors. | ([ADI MT-031](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf); [TI ADS1298](https://www.ti.com/lit/ds/symlink/ads1298.pdf)) |
| A9 | P2 | Guard rings are optional. If used: guard = VREF_A for the inverting servo and gain stages, and guard = IN− for the U1C/U1D followers. The unfitted DRL copper stubs are short and kept away from INA inputs. | ([Microchip MCP640x §4.6](https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP6401-Data-Sheet-DS20002229.pdf)) |
| D1 | P1 | **Each C_ADCn (10 nF C0G) is at its MCU ADC pin**: about 1–3 mm away, on L1, with no via between capacitor and pin. Its own GND via points toward VSSA/VREF− (pins 19/20), not beside the C_MCU_VDD2 vias at pins 27/28. | ([TI ADS8860](https://www.ti.com/lit/ds/symlink/ads8860.pdf); [ST AN2834](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf); [ST DS13737 Fig. 40](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)) |
| D2 | P1 | R_ADCn sits immediately upstream of C_ADCn. The VOUT runs are on L1 over L2. They may run parallel to each other, but never alongside SPI, SWD, clocks, switch nodes or RF feeds, and no digital trace crosses them on L1 or L4. | ([ST AN2834 §3.2.11](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf)) |
| K1 | P0 | Each J_FPC land pattern matches drawing EDC3-633002-95: signal pads 0.18 mm at 0.35 mm pitch, power pads 0.75 mm, end tabs 0.215 × 1.04 mm, overall 4.245 mm. | ([Hirose BK13C drawing](https://www.hirose.com/en/product/document?clcode=CL0480-0720-0-95&documentid=BK13C06-10DS2-0.35V%28895%29_4800720095_2D_ENG&documenttype=2DDrawing&lang=en&productname=BK13C06-10DS%2F2-0.35V%28895%29&series=BK13C)) |
| K2 | P0 | **Nothing is inside the insulation area** (about 3.815 × 1.63 mm between the pad rows): no vias, test points or exposed copper. There are no vias in the 0.18 mm pads. Preferably no trace runs under the body; any that does is fully mask-covered and mounting-tested. | ([Hirose BM28 guideline](https://www.hirose.com/en/product/document?clcode=CL0673-5048-0-51&productname=BM28B0.6-6DS%2F2-0.35V%2851%29&series=BM28&documenttype=Guideline&lang=en&documentid=0001442212); [Hirose DF40 guideline](https://www.hirose.com/en/product/document?clcode=CL0684-4032-1-51&productname=DF40C-100DP-0.4V%2851%29&series=DF40&documenttype=Guideline&lang=en&documentid=0001442210)) |
| K3 | P0 | No trace passes between adjacent signal pads; the copper gap is only 0.17 mm (derived). Each pad escapes straight outward on L1, and vias sit outside the body outline (±0.95 mm), clear of the pads (±1.05 mm). | ([Hirose BK13C drawing](https://www.hirose.com/en/product/document?clcode=CL0480-0720-0-95&documentid=BK13C06-10DS2-0.35V%28895%29_4800720095_2D_ENG&documenttype=2DDrawing&lang=en&productname=BK13C06-10DS%2F2-0.35V%28895%29&series=BK13C)) |
| K4 | P0 | The P1 (3V0_ANA) and P2 (GND) lands and all signal nets follow the DS↔DP contract exactly. The connector has no polarity, so a 180° flip swaps 3V0_ANA and GND. | ([Hirose BK13 catalog](https://www.hirose.com/en/product/document?clcode=CL0480-0720-0-95&documentid=en_BK13C_CAT&documenttype=Catalog&lang=en&productname=BK13C06-10DS%2F2-0.35V%28895%29&series=BK13C); [BK13 contract](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/BK13_ASSEMBLY_CONTRACT_SOURCE.md)) |
| K5 | P1 | GND contacts 1, 3, 5, 7, 9 and 10 and the three P2 lands each have their own vias into L2, never one shared via. The P1 lands have a short, wide connection. | ([ADI MT-031](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf); [TI ADS1298](https://www.ti.com/lit/ds/symlink/ads1298.pdf)) |
| K6 | P2 | Each connector sits near board support, to hold the 0.02 mm warpage limit. The FPC swing zone is free of tall parts. The SIG1 and power marks stay visible after mating. | ([Hirose BK13C drawing](https://www.hirose.com/en/product/document?clcode=CL0480-0720-0-95&documentid=BK13C06-10DS2-0.35V%28895%29_4800720095_2D_ENG&documenttype=2DDrawing&lang=en&productname=BK13C06-10DS%2F2-0.35V%28895%29&series=BK13C); [Hirose BM28 guideline](https://www.hirose.com/en/product/document?clcode=CL0673-5048-0-51&productname=BM28B0.6-6DS%2F2-0.35V%2851%29&series=BM28&documenttype=Guideline&lang=en&documentid=0001442212)) |

## The radio needs bare antenna copper and a solid ground body

**Placement.** ST's documents disagree:

- **DS14784 text:** place the module "in the corner of the PCB". Yet its own Fig. 17 shows a mid-edge module with a 15 × 40 mm clearance strip ([ST DS14784](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)).
- **AN6316:** placement "must be in the middle-edge of the board … irrespective of the dimensions of the board". It rates a corner "functional, but not optimum" and a module with PCB all around its antenna "not functional" ([ST AN6316](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)).

AN6316 is newer, the ST wiki agrees with it, and ST's own X-NUCLEO board follows it with the antenna overhanging an 82 mm edge ([ST UM3449](https://www.st.com/resource/en/user_manual/um3449-wifibluetooth802154-connectivity-expansion-board-based-on-the-st67w611m1-module-for-stm32-nucleo-boards-stmicroelectronics.pdf)). **Middle-edge governs.** The project's centred placement on the 80 mm edge is correct.

**Keep-out.** The project keep-out is x 44.2–56.5 mm, y 54.4–59.4 mm. It matches ST's 12.28 mm-wide, 5 mm-deep antenna portion. About 0.56 mm of it lies on the board and about 4.44 mm overhangs ([RF layout basis](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/work/rf/RF_STACK_LAYOUT_BASIS.md)). The datasheet's hard rule is "Do not cover the antenna clearance area with copper or traces" ([ST DS14784](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)).

**Grounding.** Connect "all GND pins directly to a solid GND plane", with "GND vias as close as possible to the GND pin" ([ST DS14784](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)). Put "at least 5 vias on each central PAD" ([ST wiki power and grounding](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_Power_supplies_and_grounding&oldid=86021)). ST's reference board uses tented 0.45/0.2 mm vias and "if bigger vias are used, then a smaller amount is allowed" ([ST AN6316](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)).

**Decoupling.** Use "one 10 μF decoupling capacitor per VDD pin", placed "as close as possible" with "a dedicated via" for its ground ([ST wiki power and grounding](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_Power_supplies_and_grounding&oldid=86021)).

**Numbers ST does not give.** ST gives no distance to metal, the battery, the enclosure or the body, and no minimum ground-plane size. The reactive near field at 2.45 GHz reaches about 19.5 mm (derived physics estimate). That is the same order as Fig. 17's 15 mm depth, so treat 15–20 mm around the antenna as the detuning zone.

**32.768 kHz crystal.** The ST wiki requires the crystal to be "as close as possible to the module pins and shielded by ground planes", and advises avoiding "routing high-speed signals or sensitive power below the crystal". It also asks for load-capacitor footprints to be provisioned against the module's internal "8 pF equivalent" ([ST wiki 32 kHz](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_32KHz_management&oldid=80818)). Epson's FC-135 footprint marks the area between the pads: "Do not design any circuit patterns in the shaded area" ([Epson FC-135 spec](https://download.epsondevice.com/td/pdf/td_xtal_32khz/FC-135_Q13FC13500003_en.pdf)). ST's AN2867 adds a grounded guard ring, short symmetric paths, few test points, and cleaning and coating against humidity ([ST AN2867](https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8afals-stm32-mcus-and-mpus-stmicroelectronics.pdf)). Each extra pF of trace capacitance pulls the crystal about **17 ppm** (derived).

**SPI.** The ST67 SPI runs at up to **40 MHz**, which is exactly what ST's host code uses ([X-CUBE-ST67W61 CLI .ioc](https://github.com/STMicroelectronics/x-cube-st67w61/blob/main/Projects/NUCLEO-U575ZI-Q/Applications/ST67W6X/ST67W6X_CLI/ST67W6X_CLI.ioc)). ST's routing rules are:

- target 50 Ω;
- coplanar ground between the lines;
- inner layers on a 4-layer board, "to minimize SPI_CLK radiation";
- "exercise caution when changing layers";
- a dedicated bus with no other slave.

([ST wiki SPI](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_spi&oldid=86022)). ST's reference board ran 45 mm at 38 Ω without impedance control ([ST AN6316](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)). Trace length is therefore not the binding timing limit. The module's MISO delay of ≤ 8 ns inside a 12.5 ns half-period is.

**Table R: ST67W611M1 antenna, ground, decoupling, crystal and SPI checks**

| ID | Pri | What to verify | Source |
|---|---|---|---|
| R1 | P0 | **No copper on L1, L2, L3 or L4 inside x 44.2–56.5 mm, y ≥ 54.44 mm**, including the 0.56 mm band that lies on the board. That means no pours, plane fill, traces, stitching vias, pads, parts or hardware. Read each layer back to confirm that L2 plane or polygon voids really honour the keep-out. | ([ST DS14784 §6.2](https://www.st.com/resource/en/datasheet/st67w611m1.pdf); [RF layout basis](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/work/rf/RF_STACK_LAYOUT_BASIS.md)) |
| R2 | P0 | The module is centred on the edge (centre near x 50.35 on the 80 mm edge) with its antenna portion overhanging. It is not in a corner and not inboard. | ([ST AN6316 §5](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)) |
| R3 | P0 | All six perimeter GND pads (10, 15, 18, 26, 30, 32) connect **directly**, not through thermal spokes, to an L1 GND pour that fills under the module body. Each has its own via right beside the pad. | ([ST DS14784 §6.2](https://www.st.com/resource/en/datasheet/st67w611m1.pdf); [ST AN6316 Fig. 8](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)) |
| R4 | P0 | RESERVED pins 1, 2, 4–8, 11, 12, 19 and 20, and NC pin 31, are left unconnected: no GND tie and no net. | ([ST DS14784 Table 1](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)) |
| R5 | P0 | Each of the four central lands has ≥ 5 vias. Their treatment (tented, plugged or filled) is agreed with the assembler and written into the order notes. | ([ST wiki power and grounding](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_Power_supplies_and_grounding&oldid=86021); [JLC via covering](https://jlcpcb.com/help/article/pcb-via-covering)) |
| R6 | P1 | L2 is unbroken under the whole module body, with no merged antipads from SPI escape vias. The L4 pour under the module is continuous and stitched to L1 and L2 all around the module perimeter. | ([ST wiki power and grounding](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_Power_supplies_and_grounding&oldid=86021)) |
| R7 | P1 | Each of VDD pins 9, 16 and 25 has a 10 µF capacitor as close as possible, with its own GND via. The supply via lands on the capacitor pad, so current passes the capacitor before the pin (DS Fig. 16). The capacitors for pin 25 sit beside or inboard of the module, never beyond the pad-row line. | ([ST DS14784 Fig. 16](https://www.st.com/resource/en/datasheet/st67w611m1.pdf); [ST AN6316 Fig. 14](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)) |
| R8 | P1 | The module supply is copper sized for about 0.38 A peak (377 mA during Wi-Fi Tx) and is fed from 3V3_DIG. VDD33 has a 2.97 V minimum, so a 3.00 V rail would leave only 30 mV. | ([ST DS14784 Tables 2, 14](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)) |
| R9 | P1 | There is no switcher or inductor, battery or battery wiring, connector shell, screw, test pad or EMG input within about 15 mm deep × ±20 mm along the edge around the antenna. | ([ST DS14784 Fig. 17](https://www.st.com/resource/en/datasheet/st67w611m1.pdf); [ST wiki antenna](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_Antenna_and_RF&oldid=77652)) |
| R10 | P1 | SPI_MOSI (27), SPI_CLK (28) and SPI_MISO (29) sit on the antenna-side row. Their escapes turn inboard immediately and never head outward into the keep-out. | ([ST DS14784 Table 1](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)) |
| R11 | P2 | A GND stitching fence runs along the ground edge **outside** the keep-out at ≤ about 3 mm pitch (λ/20 in FR-4). This is general practice, not an ST rule. | ([Infineon AN91445](https://www.infineon.com/dgdl/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf?fileId=8ac78c8c7cdc391c017d073e054f6227)) |
| X1 | P0 | **No copper pattern lies between the FC-135 pads**: no trace or via in the gap. | ([Epson FC-135 spec](https://download.epsondevice.com/td/pdf/td_xtal_32khz/FC-135_Q13FC13500003_en.pdf)) |
| X2 | P1 | X_WIFI_32K is within a few mm of pins 13/14, on the crystal-side row away from the antenna, with the 0 Ω links inline. The traces are short and of equal length, with no stubs or test points on the 32 kHz nets. The DNP load-capacitor pads sit right at the crystal. | ([ST wiki 32 kHz](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_32KHz_management&oldid=80818); [ST AN2867](https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8afals-stm32-mcus-and-mpus-stmicroelectronics.pdf)) |
| X3 | P1 | No SPI, UART, switching or supply trace runs on L3 beneath the crystal, the links or the 32 kHz traces. L2 under them is unbroken. An L1 GND guard around the 32 kHz nets ties to module GND pin 15 and is stitched to L2. | ([ST wiki 32 kHz](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_32KHz_management&oldid=80818); [ST AN2867 Fig. 13](https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8afals-stm32-mcus-and-mpus-stmicroelectronics.pdf)) |
| S1 | P1 | SPI is point-to-point on L3 over continuous L4, with GND between the lines. It is as short as practical (ST's reference board used about 45 mm). It never crosses the switching cell, the antenna neighbourhood or the area under the crystal. | ([ST wiki SPI](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_spi&oldid=86022); [ST AN6316 §4.3](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)) |
| S2 | P1 | The 22 Ω series resistors sit at their drivers, before any via: SCK, MOSI and CS within about 2–3 mm of MCU pins 52, 54 and 51; MISO at module pin 29. There are no stubs or test points on SCK, and no serpentines. | ([ST wiki SPI](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_spi&oldid=86022)) |
| S3 | P1 | Each SPI signal via has a GND via within about 1 mm. SPI_RDY and CS (strobe and wake signals) are short and have a ground neighbour. | ([ST wiki SPI](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_spi&oldid=86022); [ST AN5373 §7.5](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)) |

## The MCU rewards the pin-capacitor-via order

**Part values.** ST's STM32U5 hardware guide and datasheet fix the part values, and the project BOM matches all of them:

| Pin | Required parts |
|---|---|
| Each of the five VDD pins | 100 nF each, plus one 10 µF for the package |
| VCAP | 4.7 µF, "±20 %; ESR < 20 mΩ at 3 MHz; rated ≥ 10 V" |
| VDDA | 100 nF + 1 µF |
| VREF+ | 100 nF + 1 µF |
| VBAT (tied to VDD) | 100 nF |
| NRST | 100 nF, "as close as possible to the device" |

([ST AN5373](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf); [ST DS13737](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)). Capacitors must sit "as close as possible to, or below, the appropriate pins". ST's only layout drawing (AN5373 Fig. 17) shows current flowing pin → capacitor pad → via, with the vias outboard.

**Geometry.** On the non-SMPS LQFP100 every VDD pin sits next to a VSS pin: 10/11, 27/28, 49/50, 74/75 and 99/100. VCAP (48) sits next to VSS (49). Fig. 17 can therefore be copied exactly. The pins are at 0.5 mm pitch, so no 0.6 mm via fits between them (derived).

**VCAP.** The VCAP loop is the part most at risk from an autorouter. A 0.2 mm × 5 mm trace on 1 oz copper is already about 12 mΩ, most of the 20 mΩ ESR budget (derived). The SMPS package differs in "almost all power supply pins" and can short a supply ([ST AN5373](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)), so the footprint mapping itself is a P0 check.

**ADC accuracy.** The datasheet notes that ADC accuracy "may degrade in case of digital activity on adjacent I/Os" ([ST DS13737](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)). Its error budget is tight: 1 LSB at 14 bits with VREF+ = 3.00 V is about 183 µV (derived).

**Table M: STM32U575VIT6 (LQFP100, no SMPS) checks**

| ID | Pri | What to verify | Source |
|---|---|---|---|
| M1 | P0 | The footprint and symbol use the **non-SMPS** LQFP100 map: 19–22 = VSSA / VREF− / VREF+ / VDDA; 48 = VCAP; 49/50 = VSS/VDD. No SMPS-package pin such as VLXSMPS or VDD11 appears. | ([ST DS13737 Figs. 14–15](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf); [ST AN5373 §3.3](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)) |
| M2 | P0 | **MCU_VCAP (4.7 µF) straddles pins 48/49 on L1.** The VCAP net has no via, test point or branch. The trace is ≤ about 2 mm long and ≥ 0.3 mm wide. The capacitor has its own 1–2 GND vias, separate from the VDD3 capacitor's via. | ([ST DS13737 §5.1.6](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf); [ST wiki power supply](https://wiki.st.com/stm32mcu/wiki/Basics_of_power_supply_design_for_MCU)) |
| M3 | P0 | Each C_MCU_VDDn (100 nF) straddles its pin pair (10/11, 27/28, 49/50, 74/75, 99/100) on L1. Current flows pin → pad → via, with its own VDD and GND vias outboard of the pads. There are no long shared return traces. | ([ST AN5373 §7.4, Fig. 17](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf); [ST DS13737 Fig. 24](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)) |
| M4 | P0 | VREF+ (21) and VDDA (22) each have 100 nF (nearest the pin) plus 1 µF. Their GND legs run to VREF−/VSSA (20/19). VREF− and VSSA each tie to GND with vias to L2. | ([ST AN5373 §2.2](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf); [ST AN6316 §4.4.2](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)) |
| M5 | P1 | 3V0_ANA reaches the MCU as its own branch from the TPS7A2030, not daisy-chained through the AFE. It splits at the 1 µF node into the VDDA and VREF+ feeds, and never runs parallel to SPI or switcher copper. | ([ST AN2834 §3.2.3](https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf); [ST wiki power supply](https://wiki.st.com/stm32mcu/wiki/Basics_of_power_supply_design_for_MCU)) |
| M6 | P1 | C_VBAT (pin 6), C_VDDUSB (pins 73/74) and C_NRST (pin 14) each have a GND via at the capacitor pad. Pins 6 and 14 have no neighbouring VSS pin. C_MCU_BULK (10 µF) sits at the 3V3_DIG entry to the MCU. | ([ST AN5373](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf); [ST DS13737 Fig. 38](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)) |
| M7 | P1 | The C_MCU_VDD2 loop at pins 27/28 is tight, because it sits between ADC pins PA3 (26) and PA4 (29). The PA3 and PA4 traces leave away from that capacitor. | ([ST DS13737 Fig. 15, Table 105](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf)) |
| M8 | P1 | Around pins 48–55, placement priority is: VCAP capacitor, then VDD3 capacitor, then the 22 Ω SPI resistors, then the L1→L3 vias. SCK never runs beside the VCAP trace or between the VCAP capacitor and pin 48. The SPI via row does not slot L2 under the VCAP/VDD3 loop. | ([ST DS13737](https://www.st.com/resource/en/datasheet/stm32u575ag.pdf); [ST AN5373](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)) |
| M9 | P1 | NRST reaches J_SWD pin 5. SWDIO (72) and SWCLK (76) route around the capacitors at pins 73–75, not between those capacitors and their pins, with no added capacitors or pull resistors. SWCLK is short and kept away from the ADC corner. | ([ST AN5373 §6.3, §8.1](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)) |
| M10 | P1 | R_MCU_BOOT0_PD sits at pin 94 on a short trace, and the stub to TP_MCU_BOOT0 is short. No clock or SPI trace runs alongside it. If BOOT0 is high at reset, the bootloader probes PA2–PA4 (ADC pins) and SPI2. | ([ST AN5373 §5](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)) |
| M11 | P2 | 3V3_DIG reaches the VDD pins through an L3 pour or through 0.3–0.4 mm branches; ST's reference board uses a 400 µm star. The unused PH0/PH1 and PC14/PC15 pins have no floating stubs. L1, L3 and L4 free areas are filled with GND and stitched. | ([ST AN6316 §4.4.2](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf); [ST AN5373 §7.3](https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf)) |

## Six schematic issues that no amount of routing can fix

Several findings in the notes are design issues, not copper issues. They should go to schematic review alongside the layout sign-off:

- **D_VBUS breakdown is below the charger's OVP.** The PESD5V0S1BA's minimum breakdown voltage is **5.5 V**, below the BQ24072T's 6.4 V minimum OVP ([Nexperia PESD5V0S1BA](https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA_BB_BL.pdf); [TI SLUS937C](https://www.ti.com/lit/ds/symlink/bq24072t.pdf)). A sustained overvoltage would load the TVS before the charger simply disconnects.
- **The CC TVS is a snap-back part next to VBUS.** The PESD5V0X2UT "must not" be connected to unlimited DC sources ([Nexperia PESD5V0X2UT](https://assets.nexperia.com/documents/data-sheet/PESD5V0X2UT.pdf)), yet CC2's pad sits 0.20 mm from a VBUS pad.
- **CUP4_1 is below TI's recommendation.** It is 10 µF where TI recommends 22 µF. It must still provide ≥ 4.2 µF effective at the VSYS DC bias ([TI SLVSFH3C](https://www.ti.com/lit/ds/symlink/tps631000.pdf)).
- **The LDO runs at its minimum headroom.** The TPS7A2030 works at exactly its 0.3 V minimum. There, TI's curves show PSRR of only about 27–30 dB around 1–2 MHz at 300 mA ([TI SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)).
- **The AD8237 output load is too heavy.** The in-band load of about 7.4 kΩ (derived) is below ADI's "(R1 + R2) ‖ RL ≥ 10 kΩ" recommendation for best output swing and linearity ([ADI AD8237](https://www.analog.com/media/en/technical-documentation/data-sheets/ad8237.pdf)).
- **The radio's certification assumes 20 cm separation.** The ST67 modular grant assumes "a separation distance of 20cm or more" from persons ([ST DS14784](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)). A wearable does not meet that condition, which makes this a regulatory item, not a routing item.

The notes also report two conflicting VSYS ranges, 3.0–4.2 V and 3.0–5.0 V ([power-tree doc](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/01_power_tree_design.md)). The buck-mode peak current, and therefore the LX and VIN copper sizing, depends on which one is true.

## Stop-the-line checks in review order

Check the P0 items in the order below. Each step, if it fails, can invalidate everything checked after it.

| Order | IDs | One-line pass condition |
|---|---|---|
| 1 | F1, F2, F3, F4 | JLC04121H-3313 named on the order; edge ≥ 0.5 mm; Standard-PCBA panel planned; in-pad via treatment written. |
| 2 | G1, G2 | L2 has no trace, slot or antipad chain; L4 is solid under every L3 trace. |
| 3 | R1, R2, R3, R4, R5 | Antenna zone bare on all four layers; module mid-edge; GND pads direct with vias; reserved pins open; ≥ 5 central-land vias. |
| 4 | P1–P5, P11 | Both converter hot loops tight on L1; LX has no vias or extras; FB sensed at COUT and away from LX; EN/MODE tied; L2 whole under the cell; LDO capacitors share pin-2 ground. |
| 5 | M1–M4 | Non-SMPS pin map; VCAP straddles 48/49 with no via; five VDD pairs follow pin → capacitor → via; VDDA/VREF+ decoupled at the pins. |
| 6 | C1–C3, U1, U2, E1, E2 | Charger VSS grounded independently; charger capacitors and programming resistors at their pins; all USB-C power and shell pads connected; nothing between USB pads; TVS inline with a GND via at its ground pad. |
| 7 | A1, A2, K1–K4, X1 | INA BW tied; AFE bypass capacitors at the pins; BK13 lands per the drawing, with nothing in the insulation area, nothing between pads and the mapping per contract; nothing between the crystal pads. |

## Conclusion

The literature shows how little the manufacturers constrain the routed copper directly. Almost none of them give a routing distance, so a reviewer who hunts for millimetre rules will find mostly project conventions. The enforceable content is topological: which pad a via lands on, which layer carries a return current, which copper must not exist at all. The checklist therefore works best as a connectivity and continuity audit before it becomes a DRC exercise. A 0.20 mm clearance violation matters far less than an L4 void under the SPI corridor, a via in the VCAP net, or a VREF_A tap shared across channels. None of those three trips a standard DRC, which is the concrete danger of autorouting this board.

Some items cannot be proven from copper and datasheets alone:

- effective capacitance at DC bias for CUP4_1 and MCU_VCAP;
- MCP6404 stability into 330 Ω/10 nF;
- the TPS631000 loop with the 10 pF feed-forward fitted;
- 32 kHz frequency error;
- antenna detuning by the body and enclosure.

These should be handed to bench and HIL tests as named acceptance items, not assumed from a clean layout review. Two cross-checks are the cheapest insurance on the fabrication side. First, run JLC's own impedance calculator against the 0.136–0.161 mm field-solver widths before locking the SPI rule. Second, get a written answer from JLC on in-pad via treatment for the 0.2 mm holes.
