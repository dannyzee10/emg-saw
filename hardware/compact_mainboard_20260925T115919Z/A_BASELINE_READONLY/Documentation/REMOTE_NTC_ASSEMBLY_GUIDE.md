# Remote battery NTC assembly — PROTO_1_REMOTE_NTC

This prototype requires **one SEMITEC Corporation 103AT-2 thermistor**, manually attached to the battery cell and connected through two insulated wires. The thermistor body is off-board. It must not measure main-PCB temperature and must not be omitted from the complete assembly.

The battery is not selected. This document defines the sensor assembly; it does not approve a battery, charging-temperature range, attachment material, wire, enclosure, or finished product for use.

## Electrical and physical arrangement

```text
MAIN PCB                                              BATTERY CELL

R_TH_BAT terminal 2 / BAT_TEMP ---- insulated wire ----+
                                                     |
                                               ONE 103AT-2
                                           thermally attached
                                            and electrically
                                            insulated at cell
                                                     |
R_TH_BAT terminal 1 / GND --------- insulated wire ----+
```

R_TH_BAT remains a single electrical component between BAT_TEMP and GND in the schematic. Its controlled PCB model represents the two wire terminations, not a sensor body to be installed on the board. The native variant has R_TH_BAT **Fitted / Required**, with manual off-board assembly parameters. The machine-assembly output deliberately excludes its body.

The charger remains BQ24072T. The existing network is preserved: VBUS through 33.2 kΩ to BAT_TEMP; 28 kΩ from BAT_TEMP to GND; and 100 kΩ from BAT_TEMP to UP1 pin 1 TS. The remote NTC is parallel to the 28 kΩ resistor, not a replacement for any of these resistors. R_TS_SER terminal 1 is BAT_TEMP and terminal 2 is the TS node.

| Board termination | Signal | Required connection |
|---|---|---|
| R_TH_BAT pad 1, rectangular | GND | One insulated wire to one NTC lead |
| R_TH_BAT pad 2, round | BAT_TEMP | One insulated wire to the other NTC lead |
| J_Li-Po pin 1 | GND | Battery negative |
| J_Li-Po pin 2 | BAT_TEMP | No additional pack temperature sensor in this assembly |
| J_Li-Po pin 3 | VBAT_CELL | Battery positive |

**PROTO_1_REMOTE_NTC uses the separate 103AT-2 sensor. Do not connect a second pack NTC to J_Li-Po pin 2.** If the eventual battery has an extra wire, identify its function from that supplier's documentation before connection. An extra wire is not proof of an NTC. Do not modify or bypass pack protection circuitry.

## Required sensor and manufacturer limits

The exact selected part is **SEMITEC Corporation 103AT-2**, AT series, nominal 10.0 kΩ at 25°C, resistance tolerance ±1%, B25/85 = 3435 K ±1%. Its resin body is specified as 3.7 × 2.4 × 4.0 mm maximum. The AT-2 leads are 0.5 mm square tin-plated 42-alloy, with nominal 2.54 ±0.25 mm pitch. These are the sensor's own leads; no remote wire gauge has been selected from these dimensions.

Follow the AT-2 limits in the [official SEMITEC AT datasheet](https://www.semitec-global.com/uploads/2022/01/P12-13-AT-Thermistor.pdf), including the handling illustrations. In particular:

- Start lead bending at least 3 mm from the sensor head. Do not load the head/lead seal.
- Observe the illustrated maximum 2 N load and maximum 0.3 mm deflection; the force direction matters. These component limits are not a permitted service load for the finished harness.
- Solder at least 5 mm from the head, at no more than 340°C for 7 seconds using the specified 50 W iron condition. These are upper limits, not a recommendation to heat a battery assembly to those conditions.
- Do not apply the different parenthesized AT-5 limits to the AT-2.

Prepare and inspect lead splices before attaching the sensor to the cell, keeping soldering heat away from the battery. The datasheet does not select a LiPo attachment adhesive or insulation system. That choice must satisfy both sensor and selected battery instructions and be qualified on the actual assembly.

## Termination and strain relief

The retained copper termination provision consists of two plated through-hole pads at 2.54 mm pitch. Each has a nominal 0.65 mm drill/hole definition and 1.15 mm top/mid/bottom copper size; nominal geometric annulus is 0.25 mm. Pad 1 is rectangular and pad 2 is round. These dimensions do not approve direct insertion of the sensor's square leads; this variant requires insulated remote wires. See [REMOTE_NTC_PAD_ASSESSMENT.md](release_evidence/REMOTE_NTC_PAD_ASSESSMENT.md) for the geometry evidence and qualification limits.

No wire gauge, finished-hole tolerance, anchor dimensions, flex radius, or pull-test load has been invented. Before releasing the harness, check that the selected prepared/tinned conductor fits the **finished** hole with suitable clearance without forcing or damaging the plating, and that the resulting joint has adequate solder access and insulation spacing. If it does not, stop and qualify a documented termination change.

Provide an independent harness strain-relief anchor and a compliant service segment. Solder joints, sensor leads, and cell attachment must not carry normal handling or repeated cable loads. Inspect soldering, exposed strands, insulation, and splice coverage. The existing pads are not automatically qualified for repeated wire loading merely because they can be soldered.

## Cell attachment and wiring

1. Confirm the selected protected battery's identity, polarity, allowed charge current and temperature range, dimensions, connector/harness compatibility, and protection requirements. Those selections remain open.
2. Use a suitable electrically insulating thermal attachment method approved for the sensor and selected battery construction. Keep the sensor thermally associated with the cell rather than with the charger, converter, or radio.
3. Insulate both sensor leads and all splices. Prevent contact with conductive pouch surfaces, terminals, adjacent conductors, or enclosure hardware.
4. Provide the qualified strain relief described above. Do not puncture, crush, abrade, or solder onto a LiPo pouch. Do not use attachment pressure or lead forming that damages the cell or sensor.
5. Connect the two insulated wires to the marked R_TH_BAT termination pads. Use exactly one connected sensor. Leave J_Li-Po pin 2 unused by the battery harness for this variant.
6. Inspect attachment, wire routing, insulation, termination polarity/net identity, and continuity before enabling battery charging. Inspection must include the actual battery assembly, not only an unloaded PCB.

## Procurement and assembly reconciliation

| Record | R_TH_BAT quantity | Purpose |
|---|---:|---|
| [COMPLETE_SYSTEM_BOM.csv](release_evidence/COMPLETE_SYSTEM_BOM.csv) / [PDF](release_evidence/COMPLETE_SYSTEM_BOM.pdf) | 1 | Master system procurement requirement |
| [REMOTE_NTC_MANUAL_ASSEMBLY_BOM.csv](release_evidence/REMOTE_NTC_MANUAL_ASSEMBLY_BOM.csv) | 1, already counted above | Manual/harness assembly subsection; **zero additional procurement quantity** |
| [PCB_AUTOMATIC_ASSEMBLY_BOM.csv](release_evidence/PCB_AUTOMATIC_ASSEMBLY_BOM.csv) / [PDF](release_evidence/PCB_AUTOMATIC_ASSEMBLY_BOM.pdf) | 0 sensor bodies | Exclude remote sensor from machine assembly; retain PCB terminations |

The common procurement identifier `REMOTE_NTC_R_TH_BAT` reconciles the master and manual records. Do not sum the manual subsection as a second order. The two wire lengths, insulation/splice materials, thermal attachment, strain relief, and battery are still to be specified; their quantities and MPNs have not been invented.

The actual saved **PROTO_1_REMOTE_NTC** variant leaves only C_WIFI_X32_OUT, C_WIFI_X32_IN, and C_WIFI_BULK Not Fitted. Required decoupling and protection remain fitted. The native population export and [population table](release_evidence/VARIANT_POPULATION_TABLE.md) are the source of the assembly states.

No production PCB placement coordinates exist in this schematic package. [The placement status](release_evidence/PCB_AUTOMATIC_PLACEMENT_STATUS.md) and [exclusion manifest](release_evidence/PCB_PLACEMENT_FILTER_MANIFEST.csv) explicitly exclude the remote sensor body and all three DNP items. The native mapping test board is not a manufacturing placement source. Verify the eventual production placement export with `work/verify_machine_placement.mjs`; no sensor body may be machine-placed at R_TH_BAT.

## Installation and charger checks

Use the [TS calculation report](release_evidence/REMOTE_NTC_TS_CALCULATION.md) for the expected electrical behavior, tolerances, open/short behavior, and calculation limits. Calculated trip temperatures are not measured limits or an approved battery charging window.

- With the sensor electrically isolated from the board, compare its measured resistance at a known stable temperature to the manufacturer's R/T information and tolerance. At 25°C, the selected resistance tolerance corresponds to 9.90–10.10 kΩ before accounting for instrument error or test-temperature uncertainty. Do not measure resistance on a powered circuit.
- Verify that the harness connects only one NTC between BAT_TEMP and GND. With it connected, an ohmmeter across the board terminals also sees the 28 kΩ network and potentially other board paths; that reading is not the sensor resistance alone.
- Before charger operation, inspect sensor continuity, insulation, physical cell contact, and the absence of any second pack sensor connection. A detached but electrically connected sensor can appear valid while measuring the wrong temperature. Confirm battery polarity and compatibility independently.
- On a suitable bench setup with no person connected, characterize TS-node voltage and charger response at ambient, cold, and hot conditions, and during sensor disconnect and short faults. Use a safe controlled qualification method; do not drive a real battery beyond its manufacturer limits to force a trip.
- Confirm measured threshold and recovery behavior over relevant VBUS, component tolerances, and installation conditions. Establish sufficient margin to the selected battery's specified charging range before approving charging.
- Do not use a fixed resistor as the released sensor substitute. A charging LED does not prove that the temperature sensor, its cell attachment, or the fault response is valid; the BQ24072T keeps CHG low during a TS fault, as described in the linked calculation report and TI datasheet.

Battery and sensor installation require inspection and testing. Adding this remote thermistor does not establish battery safety, medical compliance, or permission for charging/debugging while worn. Body-connected operation remains battery-only until external-interface isolation and safety are formally validated; do not connect grounded USB, SWD, UART, or oscilloscope equipment to a person-worn unit.

## Open qualification items

Battery MPN/capacity/protection/charge limits/temperature limits/connector compatibility; actual wire and finished-hole fit; insulation and thermal attachment; strain-relief geometry and load testing; sensor R/T and installed thermal response; TS electrical thresholds and hysteresis on hardware; harness inspection criteria; enclosure and body/external-interface safety remain open. This assembly definition is not fabrication or battery-charging approval.
