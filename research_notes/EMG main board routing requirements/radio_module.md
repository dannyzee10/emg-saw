# ST67W611M1A6BTR (integrated PCB antenna) on the EMG main board: manufacturer layout requirements for the antenna, grounding, decoupling, 32.768 kHz crystal and SPI host interface

Labels used throughout:
- **[HARD]**: the manufacturer says "must", "do not" or "never", or the item is an electrical specification limit.
- **[REC]**: a manufacturer recommendation ("recommended", "should", "as close as possible").
- **[REF]**: what ST's own reference or evaluation boards actually do.
- **[GP]**: general good practice from a source other than the module maker.

Page numbers are the PDFs' own "page n/N" labels. Project coordinates come from the task brief and the project's archived footprint decode ([RF_STACK_LAYOUT_BASIS.md](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/work/rf/RF_STACK_LAYOUT_BASIS.md), [ANTENNA_AND_MASK_DRC_DISPOSITION.md](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/work/rf/ANTENNA_AND_MASK_DRC_DISPOSITION.md)):
- Antenna keep-out: x 44.2–56.5 mm, y 54.4–59.4 mm.
- Board edge: y = 55.0 mm.
- Outer edge of pads 25–32: y = 54.4395 mm.

## 1. Datasheet, application note and user manual: antenna keep-out, module location, ground plane, ground under the module, GND vias, decoupling, traces under the module

### Takeaway
ST publishes only two numeric host-board RF dimensions:
- The 12.28 mm × 5 mm antenna portion beyond the antenna-side pad row (DS14784 Fig. 8). AN6316 labels this region "ANTENNA ZONE KEEP OUT AREA".
- A 15 mm × 40 mm "antenna clearance area" drawn with no copper or traces (DS14784 Fig. 17).

There is no number for distance to metal, battery, enclosure or body, and no minimum ground-plane size.

On placement, the datasheet text says "corner". AN6316 (October 2025), the ST wiki and ST's X-NUCLEO board all put the module in the middle of an edge with the antenna beyond the board edge. AN6316 rates a corner "functional, but not optimum".

Grounding and decoupling rules:
- Connect every GND pin directly to a solid GND plane.
- Put a GND via as close as possible to each GND pin.
- Put at least 5 vias under each central pad. ST's reference board uses tented 0.45/0.2 mm vias, and fewer vias are allowed if they are larger.
- Fit one 10 µF capacitor per VDD pin, as close to the pin as possible, each with its own ground via.

### Cited Findings

**Document currency (checked 2026-09-24/25)**
- DS14784 **Rev 5, dated 04-May-2026**, is the current ST67W611M1 datasheet. The live st.com file downloaded on 2026-09-24 has the same SHA-256 (217A53014DEB…) as the project copy archived on 2026-09-16 — [DS14784 datasheet](https://www.st.com/resource/en/datasheet/st67w611m1.pdf); [project download manifest](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/sources/rf/DOWNLOAD_MANIFEST.json)
- AN6316 **Rev 3, dated 21-Oct-2025** ("How to optimize the PCB layout for ST67W611M1 and STM32U575AI") is current. The live file is byte-identical (SHA-256 E35C486D…) to the archive. Earlier revisions: Rev 1 on 28-May-2025 and Rev 2 on 11-Sep-2025 — [AN6316](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- UM3449 **Rev 2, April 2026** is the X-NUCLEO-67W61M1 user manual — [UM3449](https://www.st.com/resource/en/user_manual/um3449-wifibluetooth802154-connectivity-expansion-board-based-on-the-st67w611m1-module-for-stm32-nucleo-boards-stmicroelectronics.pdf). DB5558 **Rev 3, October 2025** is the data brief for the STDES-67W61xx-U5 reference designs — [DB5558](https://www.st.com/resource/en/data_brief/stdes-67w61bu-u5.pdf)
- None of DS14784's revision-history entries lists §6.2 "RF layout guideline" as changed; only §6.1 "Power layout guideline" appears. The "corner" wording therefore dates from the 2025 releases (Rev 1 19-Mar-2025 … Rev 3 16-Jun-2025 first public; Rev 4 10-Sep-2025) — [DS14784 revision history, pp. 33–34](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)

**Module and landing-pattern geometry (-B version)**
- The module measures 12.28 × 17.28 mm, 2.37 mm maximum height. It has a shielded "COMPONENT AREA" of 11.98 × 11.98 mm and a "PCB ANTENNA AREA" at one end, 5.3 mm deep in the side view — [DS14784 §5.1.1 Fig. 7, p. 16](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- Landing pattern:
  - 32 perimeter pads, 0.847 ± 0.05 mm square, 1.27 mm pitch.
  - Four central ground pads. Fig. 7 dimensions each as 3 mm; Fig. 8 gives 3.3 mm dimensions for the array.
  - The module outline extends **5 mm** beyond the outer edge of the antenna-side pad row (pins 25–32), drawn as a dashed 12.28 mm-wide region with no lands.
  - [DS14784 §5.1.1 Figs. 7–8, p. 16](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- **Conflict (height):** UM3449 lists the module as "12.28 x 17.28 x 2.2 mm". DS14784 Fig. 7 says 2.37 mm max and DB5558 says 2.37 mm — [UM3449 §8.5, p. 25](https://www.st.com/resource/en/user_manual/um3449-wifibluetooth802154-connectivity-expansion-board-based-on-the-st67w611m1-module-for-stm32-nucleo-boards-stmicroelectronics.pdf); [DB5558 p. 1](https://www.st.com/resource/en/data_brief/stdes-67w61bu-u5.pdf)

**Antenna keep-out, clearance and module location**
- [HARD] "Do not cover the antenna clearance area with copper or traces." — [DS14784 §6.2 item 2, p. 21](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- [REC; conflicts with AN6316 and the wiki] "Place ST67W611M1 in the corner of the PCB as shown in Figure 17." Figure 17 itself does not show a corner:
  - A shaded clearance strip **15 mm** deep runs the full **40 mm** length of one board edge. The drawing is not to scale.
  - The module's hatched "COMPONENT AREA" sits just inboard of the strip, about midway along the 40 mm.
  - The module's antenna end lies inside the shaded strip, with more shaded board between the antenna tip and the board edge.
  - [DS14784 §6.2 item 1 and Fig. 17, p. 21](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- [REC] "Keep the antenna area as far away as possible from the power supply and metal components." (item 3) and "Use a good layout method to avoid excessive noise coupling with signal lines or supply voltage lines." (item 6) — [DS14784 §6.2, p. 21](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- [HARD wording] "The placement of the module must be in the middle-edge of the board with respect to where the antenna is placed, irrespective of the dimensions of the board." [REC] "No copper or metallic plane should be placed under or close to the antenna" — [AN6316 §5, p. 16](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- AN6316 Fig. 26 ("recommended antenna placement") shows the module centred on an edge, the dotted "Board edge" at the antenna/body boundary, the antenna beyond the edge, and the label "Area with no PCB" on both sides of the antenna. Fig. 27 shows two rejected placements:
  - Corner, with the antenna overhanging: "This configuration is functional, but not optimum".
  - Module inboard, so the antenna sits over PCB with board all around it: "This configuration is not functional".
  - [AN6316 §5 Figs. 26–27, p. 16](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [REF] The footprint in AN6316 Fig. 7 labels the region beyond pins 25–32 "ANTENNA ZONE KEEP OUT AREA" — [AN6316 §4.1 Fig. 7, p. 7](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- Regulatory context:
  - Modular grant: FCC ID YCP-67W611M1A01, IC 8976A-67W611M1A01; "The module is limited to OEM installation ONLY"; "Trace antenna: Not applicable".
  - RF exposure: "a separation distance of 20cm or more should be maintained between the antenna of this device and persons during operation … This transmitter must not be co-located or operating in conjunction with any other antenna or transmitter."
  - [DS14784 §12, p. 28](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)

**Ground plane, ground under the module and GND vias**
- [HARD/REC] "Connect all GND pins directly to a solid GND plane." (item 4) and "Place GND vias as close as possible to the GND pin." (item 5) — [DS14784 §6.2, p. 21](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- [REC] "The recommendation is to have the maximum number of vias under the QFN PAD to ensure acceptable current return path (including RF) and an optimal power dissipation. The amount of vias depends on the class of the PCB. In this design, five standard vias are placed under each Exposed PAD. If bigger vias are used, then a smaller amount is allowed" — [AN6316 §4.1, p. 7](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [REF] B2413 via pattern (AN6316 Fig. 8, "VIAs GND PAD"):
  - Five vias per central pad: four corners plus the centre.
  - Top-layer GND copper fills the area between the perimeter pads and the central pads.
  - Further vias sit beside several perimeter pads; their nets cannot be identified from the image.
  - [AN6316 Fig. 8, p. 7](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [REF] Via definition (Fig. 9, "Thru hole standard type"): net GND, template "Thru 1:4", pad diameter **0.45 mm**, hole **0.2 mm**, solder mask "Tented" ticked on top and bottom. It is "standard for all the boards except for the BGA package, for which micro vias are used" — [AN6316 §4.1 Fig. 9, p. 8](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [REF] B2413 board: 4-layer FR-4 (εr 4.5), 34 × 20.32 mm, 0.7 mm thick, 35 µm Cu, ENIG, 0.2 mm minimum hole, µvias, no buried vias. For RF current return (stated for the -P RF path), "the first inner layer is preferentially dedicated for the GND signal" — [AN6316 §2 p. 3; §4.5.2 p. 13](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)

**Decoupling and supply**
- [REC] DS14784 §6.1 text: "1. Place the capacitor as close as possible to the chip and the power pin. 2. Use a capacitor to decouple the power supply from the chip. 3. Use capacitors to prevent noise from coupling back to the power plane." — [DS14784 §6.1, p. 21](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- [REC] DS14784 Fig. 16, marked with a green tick as correct: the chip pin runs by a short trace to the capacitor's VCC pad, the VCC via is at that capacitor pad, and a separate GND via is directly at the capacitor's GND pad — [DS14784 Fig. 16, p. 21](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- [REF] "For certain 10 µF-0402, the placement is near to the VDD PADs: VDD_IO1, VDD_IO2, and VDD33. The connection to the board PAD is as short as possible." Fig. 14 marks the 10 µF parts beside the VDD pads, all outside the "ANTENNA ZONE KEEP OUT AREA". No 100 nF part is shown for the module — [AN6316 §4.4.1 Fig. 14, p. 10](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- VDD33 operating range is 2.97 V minimum, 3.3 V typical, 3.63 V maximum. VDD33 and VDDIO absolute maximum is 3.63 V — [DS14784 Tables 2 and 4, p. 9](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- Load currents at 3.3 V and 25 °C:
  - Continuous WLAN Tx up to **377 mA** (11b 11 Mbps at 22 dBm; 372 mA at 11b 1 Mbps).
  - BLE continuous Tx at +10 dBm: **167 mA**.
  - [DS14784 Table 14 p. 14; Table 16 p. 15](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- Power-on sequence:
  - "VDD33 and VDDIO can be independent. Both must have reached there minimal value to start communication with host."
  - The internal POR starts when PU_CHIP (CHIP_EN) reaches 0.7 × VDD33.
  - The BOOT bootstrap must be valid from t3.1 ≥ 0 ms before VDDCORE and hold for t3.2 ≥ 2 ms.
  - Typical timings: t1 (POR) 3 ms, t2 1 ms, t4 (40 MHz XTAL start) 1 ms.
  - [DS14784 §4.4 Fig. 5 / Table 6, p. 10](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- Shutdown occurs when PU_CHIP falls below V_RST (0.1 × VDD33 typical, 0.3 × VDD33 maximum) for t_RST ≥ 1 ms — [DS14784 §4.5 Table 7, p. 11](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)

**Pin rules that affect copper**
- [HARD] "RESERVED pins must be left NC." On the -B version these are pins 1, 2, 4, 5, 6, 7, 8, 11, 12, 19 and 20; pin 31 is NC. GND pins are 10, 15, 18, 26, 30 and 32 — [DS14784 Table 1, p. 8](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- The antenna-side row (pins 25–32) carries VDDIO 25, GND 26, SPI_MOSI 27, SPI_CLK 28, SPI_MISO 29, GND 30, NC 31 and GND 32. XTAL32K_OUT 13 and XTAL32K_IN 14 sit on the opposite row, between RESERVED 12 and GND 15 — [DS14784 Table 1, p. 8](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- **Conflict (reserved pins):** UM3449 uses pin 1 (GPIO0) for the X-NUCLEO user button, whereas DS14784 requires RESERVED pins to be NC — [UM3449 §7.7, p. 16](https://www.st.com/resource/en/user_manual/um3449-wifibluetooth802154-connectivity-expansion-board-based-on-the-st67w611m1-module-for-stm32-nucleo-boards-stmicroelectronics.pdf); [DS14784 Table 1, p. 8](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)

### Inferences
- **Placement conflict resolution.** AN6316 is newer and uses "must", the wiki agrees with it, and ST's own X-NUCLEO board follows it (see §3). AN6316 also rates a corner "functional, but not optimum". The datasheet's "corner" text is legacy and even disagrees with its own Fig. 17. The project's centred placement on the upper edge, antenna facing outward and overhanging, therefore matches ST's preferred arrangement.
- **The project keep-out matches ST's defined antenna portion exactly.** It is 12.3 mm wide (module width 12.28 mm) and runs 5.0 mm from the outer edge of pads 25–32 (54.44 → 59.44 mm).
  - About 0.56 mm of it lies on the board (y 54.44–55.00 mm) and about 4.44 mm overhangs.
  - This is the AN6316 Fig. 26 geometry ("Board edge" at the antenna/body boundary) to within about 0.6 mm.
- **DS Fig. 17 mapped onto an overhanging antenna.** Beyond the antenna tip and alongside the antenna, the shaded strip becomes free space. The only on-board remnant is the thin band between the pad-row line and the board edge.
  - With the project's 0.50 mm copper-to-edge setback, lateral copper within ±20 mm of the module centre already ends at y ≤ 54.50 mm, only 0.06 mm outboard of the pad-row line.
  - So the Fig. 17 intent is effectively met without extra voids, provided nothing metallic (connectors, screws, battery, test points, flex) sits in that ±20 mm × 15 mm neighbourhood.
- For scale, the reactive near field of a 2.45 GHz radiator reaches roughly λ0/2π ≈ 122 mm / 6.28 ≈ 19.5 mm (physics estimate, not an ST number). This is the same order as Fig. 17's 15 mm depth and ±20 mm span. Treat about 15–20 mm around the antenna as the zone where metal, battery foil and body tissue will detune it.
- **Ground-plane size is not a concern.** AN6316 says "irrespective of the dimensions of the board". ST's certification-checked B2413 is only 20.32 mm wide, and X-NUCLEO puts the module on an 82 mm edge. The 80 × 45 mm board brackets both.
- **Central-pad vias.** Five 0.6/0.3 mm vias per land meet the wiki's "at least 5" and exceed ST's reference 5 × 0.45/0.2 mm (AN6316 allows fewer if larger).
  - ST's reference vias are drawn tented top and bottom. Open 0.3 mm barrels under a 3 × 3 mm LGA land can wick solder.
  - Use filled/capped vias, or an assembler-approved plug or tent plus stencil scheme. This is an assembly decision; ST gives no fill requirement.
- **Checklist A: antenna region (review routed copper).**
  1. No copper on L1, L2, L3 or L4 anywhere inside x 44.2–56.5 mm, y ≥ 54.44 mm (the 0.56 mm on-board band included): no polygon or plane fill, no traces, no vias (including stitching), no pads, no components, no mounting hardware.
     - Confirm by layer-by-layer readback. In Altium, verify that L2 plane or polygon voids actually honour the keep-out, since split planes do not always follow keep-out objects.
  2. The keep-out's inner boundary coincides with the outer edge of pads 25–32. Copper on the antenna side of that line may exist only as the pads themselves.
  3. The module centre (x ≈ 50.35 mm) is near the midpoint of the 80 mm upper edge.
  4. No switching regulator (for example the TPS631000 cell), inductor, battery, battery or flex wiring, connector shell, screw, test pad or EMG front-end input within the Fig. 17 neighbourhood of the antenna, taken as about 15 mm deep × ±20 mm along the edge.
  5. Decoupling capacitors for pin 25, which sits on the antenna-side row, are placed beside or inboard of the module, never beyond the pad-row line.
- **Checklist B: ground under the module and GND vias.**
  1. L1 GND pour fills under the module body between pads, as in AN6316 Fig. 8.
  2. All six perimeter GND pads (10, 15, 18, 26, 30, 32) connect directly to that pour and each has its own via immediately beside the pad. ST says "directly", so do not use thin thermal-relief spokes.
  3. Four central lands with at least 5 vias each, via treatment agreed with the assembler.
  4. L2 is unbroken under the whole module body. Check that antipads of the SPI escape vias do not merge into a slot.
  5. The L4 pour under the module is continuous and stitched to L1/L2 with multiple vias around the module perimeter (wiki: "Drill multiple ground vias on the top and bottom layers").
  6. RESERVED pads and NC pin 31 are not tied to GND or any other net.
- **Checklist C: decoupling.**
  1. For each of pins 9, 16 and 25: 100 nF nearest the pin and 10 µF also close. ST's own reference uses only a 10 µF 0402 right at the pad, and the project's 10 µF parts are 0805, so check they are not pushed remote.
  2. Each capacitor ground pad has its own via, per the wiki's "dedicated via".
  3. The supply via lands at the capacitor pad so current passes the capacitor before the pin (DS Fig. 16).
  4. The supply trace or pour to the module is sized for about 0.38 A peak Tx current.
  5. The DNP 47 µF sits at the supply entry, outside the antenna neighbourhood.
  6. Confirm the module is fed from the 3.30 V rail (3V3_DIG), not a 3.00 V rail. VDD33 minimum is 2.97 V, so a 3.00 V feed would leave only 30 mV for IR drop and ripple.

### Gaps
- ST gives **no numeric** clearance to metal, battery, enclosure plastic or the human body, and **no minimum ground-plane size**. The only numbers are the 5 mm antenna portion and the not-to-scale 15 × 40 mm sketch. I found no ST radiation-efficiency or detuning data versus host ground size or enclosure.
- DS14784 Fig. 17 does not say whether its 15 mm is measured from the board edge or from the module, or whether the shaded area must be free of board material or only of copper. The text says only "copper or traces".
- ST does not specify via fill, plug or cap for vias in the central lands. The reference CAD only shows "Tented".
- I found no ST statement forbidding inner-layer (L3) routing or power copper under the module **body**. ST prohibitions apply to the antenna area; for the body ST says only "solid GND plane" and good noise practice.
- The per-pad GND via count for perimeter pads is not specified beyond "as close as possible".
- ST's downloadable B2413 and X-NUCLEO Gerbers/EDA files (UM3449 §3.1 says they are on the product page) were not retrieved. The st.com product pages timed out, so via pitch, stitching and exact pullbacks were not measured from Gerbers.
- Body-worn use: the modular grant's 20 cm RF-exposure condition does not cover a wearable. The additional SAR/permissive-change route was not researched; it is a regulatory item, not a layout item.

## 2. ST wiki "Connectivity:ST67W611M1_Antenna_and_RF" and related ST wiki pages: every layout rule, figure and dimension, and any statement about stitching vias near the antenna

### Takeaway
The ST wiki pages are short and qualitative:
- The antenna page says to put the module in the middle of one edge with no copper underneath, and to keep it away from the power supply, metal and sensitive components near the antenna end. It gives no dimensions.
- The grounding page gives the only via numbers: at least 5 vias per central pad, multiple top/bottom ground vias, and a dedicated ground via per decoupling capacitor.
- No wiki page mentions stitching vias at the antenna boundary.

The live wiki was unreachable from this environment on 2026-09-24 and 2026-09-25, so the quotes below come from the project's text captures of 2026-09-16, identified by immutable oldid.

### Cited Findings
- **Access note:** wiki.st.com returned timeouts or "socket hang up" to curl and WebFetch on 2026-09-24/25. Text was taken from the project's captures, which are text extractions (not HTML) captured 2026-09-16 (09:17–09:20 UTC). Wiki figures were **not** captured — [project capture files](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/sources/rf/ST67_antenna_web_capture.json)
- **Antenna and RF considerations (oldid 77652; "Last edited one year ago" at capture):**
  - "This page provides a brief overview of the main recommendations. You can also refer to the implementation guidelines defined in this document" (link to st.com; the target was not captured).
  - §1 Module and host placement: "RF modules are typically placed at the edge of the board due to antenna radiation or to minimize the RF path length to the antenna. The host can be placed close to the module (coexistence has been validated), but the orientation of the host is important, particularly the pins connected to the SMPS or clock sources, which could affect RF performances."
  - §1, recommended placement of STDES-67W611BU-U5 (board B2413): "the SMPS coil is placed on the opposite side of the module, and the crystals do not face the edge of the module."
  - §2 Placement of the -B module: "To optimize antenna performance, place the module in the middle of one edge of the PCB with no copper underneath." This is followed by an "optimal placement" figure and "Some not recommended placement" figures, not captured.
  - "Keep the antenna area as far as possible from the power supply and metal components."
  - "Avoid placing any metallic materials near the antenna, as they can affect its performance."
  - "When the PCB antenna is operating, the ground or signal network near the end of the antenna experiences voltage fluctuations due to electromagnetic coupling. It is recommended to avoid placing sensitive components near the end of the antenna."
  - No dimension appears anywhere in the page text.
  - [ST wiki Antenna and RF, oldid 77652](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_Antenna_and_RF&oldid=77652)
- **Power supplies and grounding (oldid 86021; "Last edited 5 months ago" at capture):**
  - "The analog domain is supplied through VDD33 (16) pin and the digital domain through VDDIO (9 and 25) pins."
  - VDD33 3.3 V typical, range 2.97–3.63 V. VDDIO is either 3.3 V (2.97–3.63 V) or 1.8 V (1.62–1.98 V).
  - "Warning: Unlike the other ST67W611M1 I/Os which are VDDIO I/Os, CHIP_EN is a 3.3 V analog input pin."
  - "Current consumption figures are provided in the datasheet to help select the right LDOs/bucks and size the power tracks."
  - §3 Grounding: [HARD/REC] "Connect all GND pins directly to a solid GND plane. Place at least 5 vias on each central PAD to ensure a good power dissipation. Drill multiple ground vias on the top and bottom layers to minimize the current return path."
  - §4: "It is necessary to make sure the supply voltages are clean with minimum ripple and, in all cases, that they never go outside the specified ranges. Additional care must be given in the case of the buck layout." "When using 3.3 V for VDDIO, a single power supply source can be used for both VDD33 and VDDIO."
  - §4: [REC] "It is recommended to use one 10 μF decoupling capacitor per VDD pin." [HARD] "Decoupling capacitors must be placed as close as possible to their corresponding pins with the ground pad of each capacitor connected to the board ground through a dedicated via."
  - [ST wiki Power supplies and grounding, oldid 86021](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_Power_supplies_and_grounding&oldid=86021)
- **PCB stack-up options (oldid 77664; "Last edited one year ago"):**
  - "The ST67W611M1 module can be soldered on a mother PCB with the following characteristics": FR4 εr = 4.5; 4-layer board; "PCB thickness: 12/10" (1.2 mm); Cu 35 μm; ENIG; minimum hole 0.2 mm; "μVias, no buried vias."
  - "Customers targeting a different stack-up are advised to make the necessary studies, simulations, and characterizations and contact STMicroelectronics support, if necessary." (The page's B2413 stack table was not captured as text.)
  - [ST wiki PCB stack-up options, oldid 77664](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_PCB_stack-up_options&oldid=77664)
- **Conflict (reference thickness):** the wiki's generic mother board is 1.2 mm ("12/10"), while AN6316's B2413 is 0.7 mm thick — [ST wiki stack-up, oldid 77664](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_PCB_stack-up_options&oldid=77664); [AN6316 §2, p. 3](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- **Conflict (VDDIO minimum):** the wiki says 1.62 V for the 1.8 V range, while DS14784 Table 4 gives 1.65 V — [ST wiki power, oldid 86021](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_Power_supplies_and_grounding&oldid=86021); [DS14784 Table 4, p. 9](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- The SPI and 32 kHz wiki pages (oldids 86022 and 80818) are covered in §5 and §4 below.
- **Stitching vias:** no captured ST wiki text mentions stitching or fence vias at the antenna keep-out boundary. The only via statements are the grounding-page items above.
- [GP] Non-ST general antenna guidance (Cypress/Infineon AN91445 Rev *H, ©2014–2018, older and generic):
  - "Never place any component, planes, mounting screws, or traces in the antenna keep-out area across all layers."
  - "There must not be any ground directly below the antenna."
  - "The battery cable or mic cable must not cross the antenna trace."
  - "No metal is allowed in the antenna near-field."
  - Plastic near the antenna "increases the electrical length of the antenna trace and reduces the resonant frequency."
  - "Always verify the antenna matching network with the final plastic enclosure in place."
  - [AN91445 §12, p. 23](https://www.infineon.com/dgdl/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf?fileId=8ac78c8c7cdc391c017d073e054f6227)
- [GP] AN91445 via guidance:
  - "Use plenty of vias spaced not more than one-twentieth of the wavelength of the RF signals between ground fillings at the top layer and inner ground layer."
  - "Place ground vias immediately next to pins/pads in the top layer."
  - "Never share a via with multiple pins or pads."
  - "Allow a good number of vias for the central ground pad in the QFN package."
  - "Fill the unused area in the top and bottom layers with ground and connect it with the ground plane with many vias spaced not more than one-twentieth of the wavelength."
  - "Use separate vias to ground for each decoupling capacitor. Do not share vias."
  - [AN91445 §18–§20, pp. 47–48](https://www.infineon.com/dgdl/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf?fileId=8ac78c8c7cdc391c017d073e054f6227)
- [GP] **Conflict:** AN91445 says "Always place the antenna in a corner of the PCB". That is generic advice for Cypress's own PCB antennas and is superseded for this module by ST's middle-edge guidance — [AN91445 §12, p. 23](https://www.infineon.com/dgdl/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf?fileId=8ac78c8c7cdc391c017d073e054f6227)

### Inferences
- **"With no copper underneath"** on the wiki refers to the antenna. The same page family, the datasheet (§6.2 item 4) and AN6316 Fig. 8 all require solid GND under the module **body**. Only the antenna portion is voided.
- **Stitching-via pitch.** Applying AN91445's λ/20 rule at 2.45 GHz gives λ0/20 ≈ 6.1 mm in air, and about 58 mm/20 ≈ 2.9 mm inside FR-4 at εr ≈ 4.5 (λ0/√εr ≈ 58 mm).
  - A fence along the host ground edge **outside** the keep-out and along the board edge near the module, at ≤ 3 mm pitch, ties the L1/L2/L4 ground edges together.
  - This is good practice, not an ST requirement, and none of it may enter the keep-out.
- **"End of the antenna."** The page does not say which side of the -B antenna is its open end. Treat both lateral ends of the 12.3 mm antenna zone as sensitive for the EMG analog front end and its electrode or flex inputs.
- **Host orientation.** The project's STM32U575 is LQFP100 without SMPS. For this board, "SMPS or clock sources" means:
  - Keep the MCU's clock pins and any MCU crystal from facing the module edge (the brief says no MCU crystal is fitted).
  - Keep the TPS631000 switching cell and inductor on the far side of the board from U_WIFI1.

### Gaps
- The wiki figures (optimal and not-recommended placements, the STDES board placement image, the B2413 stack table) were not retrievable. If they contain dimensions, those are missing here.
- The target of the antenna page's "implementation guidelines defined in this document" link is unknown; it is likely DS14784 or AN6316 but was not verified.
- Wiki versions newer than the 2026-09-16 captures (oldids 77652, 86021, 86022, 80818, 77664) could not be checked on 2026-09-24/25.

## 3. ST reference and evaluation boards using ST67W611M1 (STDES-67W61BU-U5 / B2413; X-NUCLEO-67W61M1 / MB2230): what their layout does around the module

### Takeaway
Both ST boards put the module at an edge, not in a corner, with the antenna portion outside the board outline. Both keep solid ground under the module body. B2413 uses five tented 0.45/0.2 mm through vias in each central pad, top-layer GND fill with extra vias round the perimeter pads, and a 10 µF 0402 capacitor at each VDD pad. It routes SPI on inner layers with ground between the lines, keeps the SMPS on the opposite side of the host, and places the chips 5.8 mm apart. X-NUCLEO sits the external 32 kHz crystal right next to the module. ST's Gerbers were not retrieved, so fence-via pitch and exact pullbacks are unknown.

### Cited Findings
- **STDES-67W61BU-U5 = B2413** (PCB-antenna or MHF4 variant), with B2414/B2415 as -P variants. Four-layer FR-4 boards compatible with the STM32U575AI BGA: B2413 is 20.32 × 34 mm (B2414 20.32 × 44.91 mm, B2415 20.32 × 48.65 mm). ST says:
  - The goal is "to recommend layouts and associated BOMs for dedicated applications".
  - "Performance has been assessed and FCC and CE certification checks" were done.
  - "Utilizing the reference designs for user applications helps achieve suitable RF performance and aids in passing certification."
  - [DB5558 Rev 3, pp. 1–3](https://www.st.com/resource/en/data_brief/stdes-67w61bu-u5.pdf)
- [REF] B2413 placement: "All the components are located on the TOP side. The orientation of the U5 is determined by the SMPS component, which must be located on the U5 side opposite to the ST67W611M1 module. The SMPS is a noisy source that can affect RF performances." "the distance between the two chips is equal to 5.8 mm (~230 mil)." — [AN6316 §3.1, p. 4](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [REF] B2413 host-interface resistors: "Most of the signals can be disconnected from the board pins because serial resistors are used." — [AN6316 §3.2, p. 6](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [REF] B2413 ground and vias: five standard vias under each central pad (Fig. 8), through vias of 0.45 mm diameter / 0.2 mm hole, tented top and bottom (Fig. 9), and top-layer GND pour under and around the module. Footprint annotation: "ANTENNA ZONE KEEP OUT AREA" beyond pins 25–32 (Fig. 7) — [AN6316 §4.1, pp. 7–8](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [REF] B2413 SPI (§4.3):
  - "Coplanar line routing (ground between signals)".
  - "Avoid placing the SPI routing toward U5 across the SMPS area".
  - "Internally route signals (in the first or second inner layer) to prevent SPI_CLK radiation".
  - "Track length must be as short as possible … In this reference design, the total length is about 45 mm that represents a delay of 300 ps."
  - "There is no impedance control, but it should be as close to 50 Ω as possible … In that layer stack, the impedance of the lines is equal to 38 Ω."
  - Fig. 13 shows top, first-inner and second-inner layer views with the module's antenna zone at the top edge of the board.
  - [AN6316 §4.3, pp. 9–10](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [REF] B2413 decoupling: one 10 µF 0402 at each of VDD_IO1, VDD_IO2 and VDD33, with the "connection to the board PAD … as short as possible" (Fig. 14) — [AN6316 §4.4.1, p. 10](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [REF] B2413 32 kHz options:
  - Internal RC: "X3, R22, R23, R31, and R32 are not populated (in that case pins 13 and 14 can be left unconnected)".
  - External clock from the MCU PA2 into pin 13 (XTAL32K_OUT): R31 populated.
  - Crystal ("XO 32 kHz"): "X3, R22, and R23 are populated. R31 and R32 are not populated."
  - So B2413 also uses series links between crystal and module, like the project's 0 Ω links.
  - [AN6316 §3.3 Fig. 5, p. 6](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [REF] X-NUCLEO-67W61M1 (MB2230A):
  - Fig. 4 (top) and Fig. 5 (bottom) photos show module U1 at the board's lower edge with its antenna portion protruding beyond the board outline. The "32 kHz crystal (X1)" is placed immediately adjacent to the module — [UM3449 §7.1 Figs. 4–5, p. 9](https://www.st.com/resource/en/user_manual/um3449-wifibluetooth802154-connectivity-expansion-board-based-on-the-st67w611m1-module-for-stm32-nucleo-boards-stmicroelectronics.pdf)
  - The Fig. 6 mechanical drawing shows an 82 × 68 mm board, with the module's antenna region drawn outside the lower board edge at a position away from the corners — [UM3449 §7.2 Fig. 6, p. 10](https://www.st.com/resource/en/user_manual/um3449-wifibluetooth802154-connectivity-expansion-board-based-on-the-st67w611m1-module-for-stm32-nucleo-boards-stmicroelectronics.pdf)
  - "An RF U.FL connector is also implemented on the module to allow conducted measurements" (mating cable, for example Murata MXHQ87WJ3000) — [UM3449 §8.5, p. 25](https://www.st.com/resource/en/user_manual/um3449-wifibluetooth802154-connectivity-expansion-board-based-on-the-st67w611m1-module-for-stm32-nucleo-boards-stmicroelectronics.pdf)
  - "All board design resources, including schematics, EDA databases, manufacturing files, and the bill of materials, are available from the X-NUCLEO-67W61M1 product page" — [UM3449 §3.1, p. 4](https://www.st.com/resource/en/user_manual/um3449-wifibluetooth802154-connectivity-expansion-board-based-on-the-st67w611m1-module-for-stm32-nucleo-boards-stmicroelectronics.pdf)

### Inferences
- **Overhang measured from UM3449 Fig. 6** (scaled from the 82.00 mm width; about ±0.5 mm reading error):
  - The pad row nearest the antenna ends about 1 mm inside the board edge, and about 4.5 mm of the 5 mm antenna portion overhangs.
  - The module centre is about 7 mm right of the board's centre line, about 28 mm from the right edge.
  - This closely matches the project geometry (0.56 mm on board, 4.44 mm overhang, 80 mm edge). ST's own ~80 mm-edge board therefore validates the project's "mostly overhanging, edge-centred" arrangement.
- ST's reference boards put no 100 nF next to the module. The project's added 100 nF parts are harmless as long as they do not push the 10 µF parts away from the pins.
- A certification-checked ST board uses only 5 × 0.45/0.2 mm tented vias per central land. The project's 5 × 0.6/0.3 mm is electrically equal or better; the open question is assembly (wicking), not RF.
- B2413's 45 mm, 38 Ω, untuned SPI worked at ST's 40 MHz setting (see §5). This indicates, but does not guarantee, that tight impedance control is not critical for a short run.

### Gaps
- The B2413 and X-NUCLEO Gerbers, ODB++ and schematic packs were not downloaded or inspected. The st.com product pages timed out, and the UM and AN contain only images. Unmeasured:
  - stitching-via pitch along ground edges,
  - distance from host ground edge to antenna,
  - whether any copper exists on inner layers under the antenna band,
  - the X-NUCLEO 32 kHz crystal's guard, via and load-cap arrangement (C12/C13) and its crystal part number.
- The body-worn and enclosure performance of the reference boards is not published.

## 4. 32.768 kHz crystal layout (Epson FC-135 Q13FC13500003 on ST67 pins 13/14): trace length, guard ring grounding, no signals underneath, parasitic capacitance

### Takeaway
ST's module-specific rules:
- Put the crystal "as close as possible to the module pins".
- Shield it "by ground planes".
- Avoid "routing high-speed signals or sensitive power below the crystal".
- Provision load-capacitor footprints, since the module has an "equivalent" 8 pF built in.

Epson adds "Do not design any circuit patterns in the shaded area" between the FC-135 pads. AN2867 (Rev 24) adds keeping tracks short, a grounded guard ring, a local ground plane underneath, symmetry, few test points, coating in humid environments, and flux cleaning. The crystal is 9 pF CL, ±20 ppm, 70 kΩ ESR max, 0.5 µW max drive. Each pF of load mismatch shifts it about 17 ppm.

### Cited Findings
- [HARD/REC] ST 32 kHz wiki page (oldid 80818; "Last edited 11 months ago" at capture):
  - The module "embeds an RC oscillator … the low accuracy (± 5%) of this RC oscillator may be insufficient to enable certain low-power modes"; "an accurate low-frequency clock is mandatory to enable low-power Bluetooth® LE".
  - On-board crystal (Option 2): "The crystal must be connected to ST67W611M1 XTAL32K_IN (14) and XTLA32K_OUT (13) pins. The ST67W611M1 integrates matched capacitances with an equivalent capacitance value of 8 pF capacitances. Adding load capacitances on the board may therefore be unnecessary, but it is recommended to provision them on the board to match the selected crystal."
  - Table in §3: "Load capacitance must be provisioned in case the integrated 8 pF equivalent capacitance is insufficient. The crystal must be placed as close as possible to the module pins and shielded by ground planes to prevent long traces that may be affected by external interference. It is also recommended to avoid routing high-speed signals or sensitive power below the crystal."
  - Internal RC mode: "Both XTAL32K_IN (14) and XTLA32K_OUT (13) pins must be left open." External single-ended clock: "Must be connected to the XTLA32K_OUT (13) pin. It must have a 3.3 V voltage swing and be routed with a proper shielding."
  - Firmware must select the source: `W6X_CLOCK_MODE` (1 = internal RC, 2 = external passive crystal, 3 = external active crystal) in `ST67W6X/Target/w6x_config.h`.
  - [ST wiki 32 kHz management, oldid 80818](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_32KHz_management&oldid=80818)
- Pins 13 (XTAL32K_OUT) and 14 (XTAL32K_IN) are in the **VDD33** domain. "32.768 kHz quartz is optional. 32.768 kHz coming from host processor can be provided on this pin" (pin 13) — [DS14784 Table 1, p. 8](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- [REF] X-NUCLEO: "By the onboard 32 kHz crystal (X1). To do that, SB37 and SB38 must be ON, and SB52 remains OFF. In addition, adjust the C12 and C13 external load capacitor values if needed." — [UM3449 §7.7, p. 16](https://www.st.com/resource/en/user_manual/um3449-wifibluetooth802154-connectivity-expansion-board-based-on-the-st67w611m1-module-for-stm32-nucleo-boards-stmicroelectronics.pdf)
- **Epson FC-135 Q13FC13500003xx spec sheet** (3 pages, no revision number printed; PDF metadata shows created 2025-06-11, modified 2025-07-16):
  - Load capacitance CL 9.0 pF; tolerance ±20 × 10⁻⁶ at +25 °C with DL = 0.1 µW.
  - Motional resistance R1 max 70 kΩ; C1 3.4 fF typical; C0 1 pF typical; L1 7.1 kH typical.
  - Drive level 0.1 µW typical, 0.5 µW maximum (absolute maximum 0.5 µW).
  - Turnover 25 ± 5 °C; B ≤ −0.04 × 10⁻⁶/°C²; aging ±3 × 10⁻⁶ first year; operating −40 to +85 °C.
  - Package 3.2 × 1.5 × 0.8 mm.
  - Recommended footprint: two pads 1.0 × 1.8 mm with a 2.5 mm dimension (drawn pad-centre to pad-centre). The area between the pads is hatched with the note "*Do not design any circuit patterns in the shaded area."
  - Reflow peak 260 °C.
  - [Epson FC-135 Q13FC13500003 spec sheet, p. 1–3](https://download.epsondevice.com/td/pdf/td_xtal_32khz/FC-135_Q13FC13500003_en.pdf)
- [GP; STM32 guide, applied by analogy] **AN2867 Rev 24 (23-Feb-2026)** §7.1 "PCB design guidelines":
  - "Avoid high values of stray capacitance and inductances … Reducing the stray capacitance also decreases startup time and improves oscillation frequency stability."
  - "Mount the crystal as close as possible to the MCU/MPU, to keep tracks short, and to reduce inductive and capacitive effects. A guard ring around these connections, connected to the ground, is essential to avoid capturing unwanted noise … Long tracks/paths behave as antennas."
  - "Any path conveying high-frequency signals must be routed away from the oscillator paths and components."
  - "The oscillator PCB must be underlined with a dedicated underneath ground plane, distinct from the application PCB ground plane. The oscillator ground plane should be connected to the nearest MCU/MPU ground."
  - "Leakage current can increase startup time and even prevent the oscillator start. If the device operates in a severe environment (high moisture/humidity ratio), an external coating is recommended."
  - [AN2867 §7.1, p. 45](https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8afals-stm32-mcus-and-mpus-stmicroelectronics.pdf)
- [GP] AN2867 Fig. 13 ("Recommended layout for an oscillator circuit") shows the "Ground shield" ring around the crystal and CL1/CL2, "VSS paths", and a "Local ground plane (other layer)". Its Warning: "It is highly recommended to apply conformal coatings to the PCB area shown in Figure 13, especially for the LSE quartz, CL1, CL2, and paths to the OSC_IN and OSC_OUT pads as a protection against moisture, dust, humidity, and temperature extremes that may lead to startup problems." — [AN2867 Fig. 13, p. 46](https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8afals-stm32-mcus-and-mpus-stmicroelectronics.pdf)
- [GP] AN2867 §7.2 examples:
  - Bad layout: "no ground planes around the oscillator component", "too long paths", "no symmetry between oscillator capacitances", "high crosstalk / coupling between paths", "too many test points".
  - Fixed layout: "guard ring connected to the GND plane around the oscillator", "symmetry", "less test points", "no coupling between paths".
  - §7.3: "PCB cleaning is recommended to obtain the maximum performance by removing flux residuals from the board after assembly (even when using 'no-clean' products in ultra-low power applications)."
  - [AN2867 §7.2–7.3, pp. 47–51](https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8afals-stm32-mcus-and-mpus-stmicroelectronics.pdf)
- [GP] Load and pull formulas:
  - Load: CL = CL1·CL2/(CL1+CL2) + Cs, where Cs is "stray capacitance, sum of the device pin (OSC_IN and OSC_OUT) and the PCB (a parasitic) capacitances". AN2867's own example: CL = 15 pF with Cs = 5 pF gives CL1 = CL2 = 20 pF.
  - Pullability (ppm/pF) = Cm·10⁶ / (2·(C0+CL)²).
  - [AN2867 §3.1 p. 12 (Cs definition), §3.3 p. 12, §3.7 p. 17](https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8afals-stm32-mcus-and-mpus-stmicroelectronics.pdf)
- **Conflict (ground-plane philosophy):** AN2867 asks for an oscillator ground plane "distinct from the application PCB ground plane". The ST67 wiki says only "shielded by ground planes". The project has deliberately chosen one continuous GND net — [AN2867 §7.1, p. 45](https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8afals-stm32-mcus-and-mpus-stmicroelectronics.pdf); [ST wiki 32 kHz, oldid 80818](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_32KHz_management&oldid=80818)

### Inferences
- **Frequency sensitivity.** Using the Epson C1 = 3.4 fF and C0 = 1 pF with CL = 9 pF, AN2867's pullability formula gives 0.0034 × 10⁶ / (2 × 10²) ≈ **17 ppm per pF** of load error.
  - ST describes the module's built-in load as "8 pF equivalent". If that is the effective series load the crystal sees, board stray of about 1 pF (pads of two 0 Ω links, two DNP cap pads and short traces) brings it close to the crystal's 9 pF.
  - The resulting error would be a few ppm to a few tens of ppm, which is why fitting load capacitors by default is unnecessary but the footprints are kept.
  - Every extra pF of routing adds about 17 ppm, so short traces matter for accuracy as well as noise.
- **Adapting AN2867's "distinct ground plane" to a continuous-GND 4-layer board.** L2 is a solid GND only 0.0994 mm below L1, so it is the "local ground plane (other layer)".
  - On L1, surround the crystal, the two 0 Ω links and the DNP capacitor pads with a GND guard ring or pour. Tie it to module GND **pin 15**, which is adjacent to XTAL32K_IN pin 14, and via-stitch it to L2 at several points.
  - Return both DNP capacitor grounds to that same guard rather than to distant vias.
  - This follows the ST wiki "shielded by ground planes" wording without splitting the board ground.
- **Checklist D: 32 kHz crystal (review routed copper).**
  1. X_WIFI_32K sits within a few mm of pins 13/14, on the module's crystal-side row, well away from the antenna end, with the two 0 Ω links inline between the pins and the crystal.
     - Trace lengths are as short and as equal as practical, with no stubs and no test points on the 32 kHz nets (AN2867: "too many test points").
     - Pad 1 and pad 2 mapping is preserved.
  2. No copper pattern on L1 between the FC-135 pads (Epson note), meaning no trace or via in the 1.5 mm gap.
  3. No SPI, UART, switching or supply trace on **L3** beneath the crystal, links or 32 kHz traces (ST: "avoid routing high-speed signals or sensitive power below the crystal"). L2 under the crystal is unbroken GND with no antipad clusters.
  4. A GND guard is present around the 32 kHz nets on L1, tied to pin 15 and stitched to L2. The guard must not run between the crystal pads.
  5. Both 32 kHz nets stay clear of SPI_CLK (pin 28), which is on the opposite row.
  6. DNP C_WIFI_X32_IN/OUT footprints sit right at the crystal pads with short ground returns.
  7. Assembly note: clean flux residue and consider conformal coating of the crystal area, because a wearable sees sweat and humidity (AN2867 leakage warning).
- The ST67's 32 kHz oscillator transconductance and drive-level setting are not published, so AN2867's gain-margin check cannot be done on paper. Verify start-up and frequency on hardware across temperature.

### Gaps
- ST does not say whether "8 pF equivalent" is the per-pin capacitance or the effective load CL, and gives no ST67 pin or stray capacitance. ST publishes no oscillator gm, critical gm or drive level for the module, and no list of recommended 32 kHz crystals or maximum ESR for the ST67.
- The X-NUCLEO X1 part number and its C12/C13 values were not found in UM3449 text. The schematic was not retrieved.
- Epson application notes on crystal circuit layout (beyond the spec-sheet shaded-area note) were not retrieved.
- The BLE sleep-clock accuracy the ST67 firmware actually requires was not found.

## 5. SPI host interface: clock frequency used by the ST host stack, series termination, trace length and impedance, return path; UART, BOOT and CHIP_EN notes

### Takeaway
- **Clock:** 40 MHz is the specification maximum, and ST's reference host code runs exactly 40 MHz (SPI mode 0, MSB first, software chip select).
- **Chip select:** active-high. The host raises SPI_CS, waits for SPI_RDY, then clocks. SPI_RDY is a module output that the host watches on both edges.
- **Routing:** ST asks for about 50 Ω, coplanar ground between the SPI lines, inner-layer routing on 4-layer boards, the shortest practical length (the reference board uses about 45 mm), a dedicated bus, and no path near RF or supply noise.
- **Series termination:** ST documents never specify it. The project's 22 Ω source-end resistors are ordinary signal-integrity practice.
- **Timing:** the binding limit is MISO output delay ≤ 8 ns within a 12.5 ns half-period, not trace delay.

### Cited Findings
- [HARD] "The SPI bus is configured in full-duplex slave mode with three signals (SPI_CLK, SPI_MOSI, SPI_MISO). It is not recommended to connect additional SPI slave devices to the same bus as the ST67W611M1. The SPI_RDY pin is present and used by the ST67W611M1 as an interrupt towards the host processor. The SPI_CS pin can also be used as a wake-up signal from the host processor. Maximum SPI frequency : 40 MHz." — [DS14784 §2.2, p. 5](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- UART: "Full-duplex asynchronous communication; Data bit length: 8 bits; Stop bit length: 1 bit; Parity: None; Hardware flow control (RTS/CTS): None; Baud rate: 2000000 bauds" — [DS14784 §2.1, p. 4](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- ST SPI wiki page (oldid 86022), bus rules:
  - "It is recommended to use a dedicated SPI bus for the ST67W611M1 … Adding another slave on the same SPI bus could lead to data loss or, in the worst case, uncontrolled deadlock situations."
  - Five signals: SPI_CS (24) input, SPI_CLK (28) input, SPI_MOSI (27) input, SPI_MISO (29) output, SPI_RDY (21) output.
  - [HARD] "All SPI signals must use VDDIO logic levels."
  - [ST wiki SPI, oldid 86022](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_spi&oldid=86022)
- Transfer sequence, which shows **CS is active high**:
  - "When the SPI controller has data to transfer, it raises SPI_CS and waits for the readiness of the target … Once the module raises SPI_RDY, the controller enables SPI_CLK … The host stops SPI_CLK and lowers SPI_CS when the transfer is completed. Note that SPI_CS can be lowered only after SPI_RDY is de-asserted."
  - "the controller must wait until SPI_RDY is deasserted before asserting SPI_CS again … Failing to comply may cause the module to enter an error state."
  - [ST wiki SPI §2.1, oldid 86022](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_spi&oldid=86022)
- [HARD] Timing: T_cyc (SPI_CLK period) ≥ 25 ns ("a maximum frequency of 40 MHz"); MOSI setup ≥ 6 ns; MOSI hold ≥ 6 ns; MISO output delay T_vld ≤ 8 ns — [ST wiki SPI §2.3, oldid 86022](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_spi&oldid=86022)
- [REC] Hardware implementation (§3):
  - "Signal integrity: Route these tracks with impedance control targeting 50 Ohms. Exercise caution when changing layers. Use coplanar routing (i.e. to separate these signals with ground) to avoid coupling. Ensure SPI signals are routed away from sensitive or noisy signals, such as RF signals or power supply sources."
  - "SPI maximum frequency: … To achieve this frequency, integrators must minimize the length of SPI_CLK, SPI_MOSI and SPI_MOSI [sic] tracks on their boards to reduce propagation delay and skew between SPI_MISO and SPI_CLK at the host side."
  - "EMC: … On a four-layer board, route SPI signals on inner layers to minimize SPI_CLK radiation. For other board stack-ups, perform EMC simulations or measurements."
  - "It is recommended to refer to ST's ST67W611M1 reference designs for implementation guidelines."
  - [ST wiki SPI §3, oldid 86022](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_spi&oldid=86022)
- Software configuration and start-up (§4):
  - "Data size = 8 bits; POL = 0; PHA = 0; First bit = MSB".
  - Start-up: "1. The host sets the CHIP_EN pin high. 2. The host waits for the module to assert the SPI_RDY pin. … 4. The module transmits 'ready' …"
  - [ST wiki SPI §4, oldid 86022](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_spi&oldid=86022)
- [REF] **ST host stack clock (X-CUBE-ST67W61, GitHub main, retrieved 2026-09-24), NUCLEO-U575ZI-Q `ST67W6X_CLI` project**, `.ioc` file:
  - `RCC.SPI1Freq_Value=160000000`, `SPI1.BaudRatePrescaler=SPI_BAUDRATEPRESCALER_4`, `SPI1.CalculateBaudRate=40.0 MBits/s`.
  - SCK, MISO and MOSI pins (PA5/PA6/PA7) at `GPIO_SPEED_FREQ_VERY_HIGH`; SPI_CS on PD14 as a GPIO at `GPIO_SPEED_FREQ_HIGH`.
  - [ST67W6X_CLI.ioc](https://github.com/STMicroelectronics/x-cube-st67w61/blob/main/Projects/NUCLEO-U575ZI-Q/Applications/ST67W6X/ST67W6X_CLI/ST67W6X_CLI.ioc)
- [REF] Same project, `main.c`:
  - SPI: `CLKPolarity = SPI_POLARITY_LOW`, `CLKPhase = SPI_PHASE_1EDGE`, `NSS = SPI_NSS_SOFT`, `FirstBit = MSB`.
  - SPI_RDY pin: `GPIO_MODE_IT_RISING_FALLING`, `GPIO_NOPULL`.
  - BOOT and CHIP_EN are push-pull outputs, both written `GPIO_PIN_RESET` (low) at initialisation.
  - [main.c](https://github.com/STMicroelectronics/x-cube-st67w61/blob/main/Projects/NUCLEO-U575ZI-Q/Applications/ST67W6X/ST67W6X_CLI/Core/Src/main.c)
- [REF] `spi_port.c`: "Powering up the NCP using GPIO CHIP_EN" is done by setting CHIP_EN high; the module is switched off by driving it low — [spi_port.c](https://github.com/STMicroelectronics/x-cube-st67w61/blob/main/Projects/NUCLEO-U575ZI-Q/Applications/ST67W6X/ST67W6X_CLI/ST67W6X/Target/spi_port.c)
- [REF] Release notes: "Update the SPI Baudrate from 50 to 40MBits/s of NUCLEO-H7S3L8 projects to comply with ST67W611M specification" — [X-CUBE-ST67W61 Release_Notes.html](https://github.com/STMicroelectronics/x-cube-st67w61/blob/main/Release_Notes.html)
- [REC/REF] AN6316 §4.3 SPI routing recommendations (coplanar, avoid the SMPS area, inner layers, as short as possible, about 45 mm = 300 ps, as close to 50 Ω as possible, 38 Ω achieved without impedance control) — [AN6316 §4.3, pp. 9–10](https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf)
- [HARD] CHIP_EN: "CHIP_EN is a 3.3 V analog input pin. Ensure that CHIP_EN signal uses 3.3 V logic levels even when VDDIO is set to 1.8 V" — [ST wiki power, oldid 86021](https://wiki.st.com/stm32mcu/index.php?title=Connectivity:ST67W611M1_Power_supplies_and_grounding&oldid=86021)
- UM3449 caution for VDDIO = 1.8 V: drive CHIP_EN from a 3.3 V-tolerant open-drain host pin with a 33 kΩ pull-up to VDDRF (3.3 V). This "increases current consumption by 100 µA in shutdown mode" — [UM3449 §7.4.2, pp. 13–14](https://www.st.com/resource/en/user_manual/um3449-wifibluetooth802154-connectivity-expansion-board-based-on-the-st67w611m1-module-for-stm32-nucleo-boards-stmicroelectronics.pdf)
- BOOT (pin 3, VDDIO domain): "Select boot from SPI or from UART." It is the bootstrap pin, sampled at power-up (valid ≥ 2 ms, t3.2). CHIP_EN (pin 17): "Chip power on. VDD33 domain signal." — [DS14784 Table 1 p. 8; Table 6 p. 10](https://www.st.com/resource/en/datasheet/st67w611m1.pdf)
- [REF] The NCP_Loader utility "aims to flash the ST67W611M binaries and to execute the Manufacturing test over STM32 UART link", using "The BOOT, CHIP_EN, SPI_RDY and UART TX/RX signals" — [NCP_Loader README](https://github.com/STMicroelectronics/x-cube-st67w61/blob/main/Projects/NUCLEO-U575ZI-Q/Utilities/NCP/NCP_Loader/README.md)
- [GP] Return-path practice (non-ST): "Do not have traces running across the RF trace in the ground plane"; "Allow a wide ground plane beneath the RF trace"; ground vias next to pads — [AN91445 §18, §20, pp. 47–48](https://www.infineon.com/dgdl/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf?fileId=8ac78c8c7cdc391c017d073e054f6227)

### Inferences
- **Timing budget at 40 MHz, mode 0.** The module changes MISO on the SCK falling edge and the host samples on the next rising edge, which leaves about 12.5 ns. That must cover:
  - SCK flight (host → module),
  - T_vld ≤ 8 ns,
  - MISO flight (module → host),
  - RC delay of the 22 Ω series resistors (about 22 Ω × 5–10 pF ≈ 0.1–0.2 ns each),
  - the STM32U575 SPI master input setup time.
  
  At about 6.7 ps/mm (AN6316: 45 mm ≈ 300 ps), even 60 mm each way costs only about 0.8 ns round trip. That leaves roughly 3–4 ns before the host setup time. Length is not the limiting factor below a few tens of mm, and 40 MHz is feasible.
  
  If margin proves thin on hardware, the firmware can drop to 20 MHz (prescaler /8). Community reports cited by search found /8 reliable where /2 failed on other hosts, but this was not verified.
- **Series resistors.** ST gives no termination value. Placing 22 Ω at each driver (SCK/MOSI/CS at the MCU, MISO at the module) is the correct source-termination topology, because the host GPIOs run at "VERY_HIGH" slew in ST's code.
  - Keep each resistor within about 2–3 mm of its driving pin, so there is no unterminated stub between driver and resistor.
  - The module's MISO output impedance is unpublished, so check the 22 Ω value with a scope for overshoot and ringing.
- **Return path on this stack.** SPI on L3 is referenced to L4, which is only 0.0994 mm away; L2 is the reference for L1 escape stubs.
  - At every L1↔L3 transition, put a GND via within about 1 mm of the signal via so return current can move between L2 and L4 (both GND). This is ST's "exercise caution when changing layers".
  - Keep L4 unbroken under the whole SPI corridor.
  - Put GND copper or guard traces between SCK, MOSI and MISO on L3, per ST's "coplanar" wording, and keep SCK farthest from the 32 kHz nets and the analog front end.
- **Escape from the antenna-side row.** SPI_MOSI 27, SPI_CLK 28 and SPI_MISO 29 sit on the antenna-side pad row. Their escapes must turn inboard immediately, under the module body or sideways, and never outward into the keep-out.
  - If escape vias sit under the module body, they must be tented or plugged under the LGA, and their L2 antipads must not merge into a slot under the module.
- **Checklist E: SPI and control (review routed copper).**
  1. SPI is point-to-point (no other slave on the bus) and routed on L3 over continuous L4 with ground between signals.
  2. Total length is as short as practical. Treat the reference board's 45 mm as a benchmark, not a limit.
  3. No SPI trace crosses the TPS631000 switching area, the antenna neighbourhood, or beneath the 32 kHz crystal.
  4. The 22 Ω parts are at their driver ends.
  5. The CS pull-down holds CS inactive (low) while the host is in reset, which is consistent with active-high CS.
  6. SPI_RDY (pin 21) goes to an EXTI-capable MCU pin, with no pull in ST's code.
  7. CHIP_EN: host-driven, 10 kΩ pull-down keeps the module off during host reset, 3.3 V logic. Shutdown needs CHIP_EN held below 0.1–0.3 × VDD33 for ≥ 1 ms.
  8. BOOT: pull-down plus header or override, low for normal SPI operation (ST's code drives BOOT low). The level must be stable before CHIP_EN rises and for ≥ 2 ms after.
  9. UART recovery test points (2 Mbaud) sit on short stubs on the module side of the 0 Ω links and outside the antenna neighbourhood.
  10. VDDIO and all SPI/UART/BOOT levels are on the same rail as the MCU I/O (VDDIO logic).

### Gaps
- No ST statement on SPI series-termination values, maximum trace length, or skew limits beyond "minimize".
- The MISO driver strength or impedance and the input capacitance of the module pins are not published.
- The STM32U575 SPI master MISO setup and hold times at 40 MHz were not pulled from its datasheet. The project should add them to the timing budget above.
- The BOOT level-to-mode mapping (which level selects UART download) is not stated in the documents read. ST's code only shows BOOT held low for normal SPI operation. The ST wiki boot/NCP-loader pages were unreachable.
- The community report that prescaler /2 fails and /8 works came from a search-result summary of an ST Community thread on non-U5 hosts. It was not opened or verified.
