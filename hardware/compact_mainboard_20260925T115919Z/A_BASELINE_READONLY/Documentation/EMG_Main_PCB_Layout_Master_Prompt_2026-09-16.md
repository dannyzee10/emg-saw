# EMG main-board PCB implementation brief — Astra

**Purpose:** implement a native Altium main-board placement checkpoint, with the complete routing plan defined for the following reviewed stage. This is not fabrication authorization.

## 1. Authorization, source revision, and evidence

You are authorized to create and edit the native Altium PCB, its main-board project, controlled local libraries, rules, rooms, mechanical annotations, and necessary test-point additions. Implement the work; do not stop at another generic recommendation report.

Source project:
`C:\Users\PMLS\Desktop\emg-saw\hardware\review_2026-09-16\fixed_revision_remote_ntc\EMG_MainBoard.PrjPcb`

Required assembly variant: `PROTO_1_REMOTE_NTC`.

First read, from that revision:
- `REMOTE_NTC_CHANGE_REPORT.md`
- `REMOTE_NTC_ASSEMBLY_GUIDE.md`
- Latest schematic, component/model inventory, complete-system BOM, automatic-assembly BOM, variant population, warning dispositions, and native connectivity evidence under `release_evidence`.
- The existing BK13 assembly contract and previous electrical-preservation checks.

The reported baseline is 0 active electrical errors, 58 reviewed warnings, 134/134 existing checks and 164/164 remote-NTC checks. Verify the files and rerun applicable tests; do not copy these numbers into a new result without executing them. Preserve the distinction between a compiler Boolean return, diagnostic counts, and completed processing. Read the actual diagnostics.

Preserve the entire verified source revision unchanged. Work under a NEW directory, proposed:
`C:\Users\PMLS\Desktop\emg-saw\hardware\pcb_layout_2026-09-16\`

Save a main-board project and PCB under `MainBoard`, for example:
`EMG_MainBoard_Layout.PrjPcb` and `EMG_MainBoard_Layout.PcbDoc`.

Preserve UIDs/designators and use controlled, traceable source/model copies. Record source hashes and changes. Never turn the scratch mapping PCB into the production layout. First demonstrate a native PCB save/reopen/readback using the installed Altium version. If an automation function fails, identify it explicitly and continue only with operations that can be verified; do not manufacture success screenshots or rename another file format to PcbDoc.

## 2. Source priority and interpretation of the two concept images

Use the two supplied white concept images only for broad organization: “INTEGRATED MAIN BOARD: TOP PLACEMENT” and “FOUR LAYERS, ONE COMMON GROUND.”

Priority is: verified circuit connectivity and actual component models; applicable manufacturer requirements; explicit project requirements; then concept images. If these conflict, document the conflict rather than silently changing a circuit.

Corrections to the pictures:
- The ST67-B version has an integrated PCB antenna, not a ceramic or stick antenna.
- The EMG signal arrow goes from AFE toward the MCU ADC, not backward.
- No component bodies are mounted on L2 or L3 in this conventional PCB.
- Five real BK13 sockets replace the generic illustrated FFC connectors.
- USB-C is charge-only. Do not add USB D+/D− routing.
- 80 × 45 mm is a trial outline, not a validated minimum or enclosure fit.
- Discard generic ground-splitting, trace-width, and antenna-clearance numbers from all other generated posters.

Consult current primary documents and archive their URLs, revisions, relevant figures, and downloaded-file hashes. Relevant sources are listed at the end. AN6316 contains a different STM32 package/reference-board implementation: borrow applicable layout principles, not its BGA pin numbers, microvias, SMPS circuit, or analog-ground solder bridge. This project retains its verified LQFP100 non-SMPS MCU and common GND.

## 3. Physical-board partition: do this BEFORE PCB transfer

The requested MAIN PCB contains exactly these eight schematic sheets:
`AFE_Channel_1` through `AFE_Channel_5`, `Analog_Shared`, `Power_tree_design`, and `MCU_sheet`.

The five `DEB_Channel_*` sheets and `BTB_RIBBON` describe OTHER physical boards. Do not import their components onto this main PCB. They remain part of the system documentation and later separate PCB work. One flex template represents five physical flexes, not five extra components on the main board.

Use a dedicated main-board PrjPcb containing the eight main-board sheets and required local dependencies. Keep an unchanged full-system reference project. If the installed Altium workflow instead uses a supported multi-board structure, prove the board-assignment isolation. Do not import everything and merely move unwanted DEB parts outside the outline: the next ECO would remain wrong.

Generate `BOARD_PARTITION_MANIFEST.csv` with designator, UID, source sheet, physical board, footprint, and population/assembly category. Treat multipart U1/U2/U3 as three packages, not separate components for each amplifier section.

Record the original resolved Net Identifier Scope. Preserve all intended connectivity during project partitioning; do not rely on Automatic scope behaving identically after sheets are removed. In particular, prove all twelve repaired interfaces and five VREF branches still work.

Compare each main-board net's terminal set against the full-system baseline projected onto the main-board component set. Allow only documented added test-point terminals. Do not globally rename local nets or merge different channels. Preserve the physical connector mappings at the boundaries; connectors, not matching names across separate PCBs, define the inter-board harness.

Verify the automatic-assembly BOM is restricted to MAIN-board items. Whole-system part counts are not the main-board component count.

## 4. Execution stages and the stopping point for THIS task

Execute now:
A. Native main-board project/PCB creation, library resolution, stack/rule setup, board partition and native ECO.
B. Placement of ALL main-board footprints, DNP provisions and wire terminations; actual antenna/connector keepouts; critical local connection trials; placement DRC; native visual evidence.

Route short local decoupling, oscillator, feedback, or switching connections when needed to prove placement feasibility, and label their scope. Save an unrouted placement checkpoint before these trials. Do not run a full-board autorouter or proceed into all remaining routing without the placement checkpoint being reviewed.

Also prepare the full routing sequence and acceptance checks below so the next stage is ready. End THIS pass with a native placement package for review, not manufacturing files. A DRC containing expected unrouted connections is normal at this stage; shorts, invalid footprints, overlaps and keepout violations are not.

## 5. Board shape, mechanics, and fabrication basis

Start with a rounded rectangular 80 × 45 mm placement trial. Use the long bottom edge for five sensor flexes. Prefer this organized edge arrangement over a triangular board for this revision. Do not force the outline smaller by crowding feedback circuits or erasing clearances.

Use provisional mounting/strain-relief envelopes only where mechanics are undefined; do not drill arbitrary final screw holes. Reserve tool, screw-head, connector mating, wire-soldering and enclosure access. No metal mounting hardware within antenna clearance.

Preferred initial process: rigid FR-4, four copper layers, ENIG, conventional through vias. Evaluate a 1.2 mm standard factory stack first, subject to actual connector/enclosure support and manufacturability. Do not invent prepreg/core thicknesses or assume all layers have identical copper weight. Record the actual selected JLCPCB or chosen fabricator stack and tolerances. If it cannot be established, mark stack/impedance provisional and do not call controlled-impedance routing finalized.

No blind/buried/microvias by default. Our LQFP100 does not require copying a BGA reference-board HDI process. Do not buy/order anything or release fabrication outputs.

Unknown battery dimensions must remain an explicit mechanical envelope TBD. Do not place an imaginary battery on top of the circuit and declare it fits.

## 6. Four-layer assignment and common-ground policy

Proposed starting stack:
- L1 TOP: nearly all components; critical analog, feedback and local decoupling/switching connections; short digital escapes.
- L2 GND: continuous common GND reference. No long signal routes, arbitrary analog/digital split or narrow star bridge.
- L3 POWER/SIGNAL: defined VBAT_CELL/VSYS/3V3_DIG/3V0_ANA regions as needed, plus a reserved short digital/SPI corridor. Do not create enormous VBUS or switched-node planes.
- L4 BOTTOM: mostly GND, test access and limited auxiliary routing. Keep uninterrupted ground beneath the L3 SPI corridor.

The detailed stack must provide close L1-to-L2 coupling and a defined reference for L3 signals, usually the nearby L4 ground in a conventional four-layer stack. Evaluate actual dielectric distances and coplanar clearances with Altium's impedance solver. L3 signals must not depend on a fragmented L4 return.

If routing density prevents continuous references, demonstrate the problem and propose six layers before cutting L2 apart. A candidate six-layer allocation is L1 critical signals/components, L2 GND, L3 digital signals, L4 power, L5 GND, L6 auxiliary signals/test access. Do not upgrade without documenting necessity and process impact.

Use ONE electrical `GND` net for analog, digital and power returns on the main PCB. Do not create AGND/DGND nets, a ferrite link in ground, or a single narrow joining bridge. Separate placement and current paths, not ground islands. Quiet reference/ADC returns must not share narrow copper necks carrying converter or radio current.

Local regulator/charger small-signal/Kelvin return arrangements must follow the device layout guidance. These are not permission to split the entire system ground. Preserve low-impedance local connections to the IC ground/reference point.

Ground exists below the ST67 circuit body. Remove copper/vias only from the actual antenna exclusion and other specifically justified keepouts. Inspect footprint keepout primitives so a generic module courtyard does not accidentally remove all ground under the module.

## 7. Initial Altium width, clearance and via rules

The following are PROJECT STARTING TARGETS, not component guarantees, medical insulation distances, or universal current ratings. Verify against actual footprints, copper thickness, stack, fabrication process and thermal/voltage-drop calculations. Save actual Altium rule scopes/priorities, not only a written table.

| Net class | Preferred starting width | Starting clearance / treatment |
|---|---|---|
| Ordinary UART/I2C/GPIO/SWD | 0.20 mm; 0.15 mm local escape | 0.20 mm generally |
| Buffered analog Va/Vb/Vc, INA/post paths | 0.20 mm; 0.15 mm short escape | 0.25 mm to unrelated copper where feasible |
| VOUT1–5 / ADC_EMG1–5 | 0.20 mm | 0.25 mm generally; ADC-side segment very short |
| VREF_A / VREF_B source and branches | 0.25–0.40 mm where practical | Quiet routing; no noisy parallel neighbor |
| Main VBUS/VBAT/VSYS/3V3 trunks | Polygon or 0.8–1.0 mm starting corridor | 0.25 mm generally; calculate actual drop/heating |
| Local lower-current power branches | 0.30–0.50 mm where practical | Short pin neckdowns permitted after review |
| SPI nets | Width from approximately 50-ohm profile | Reference-backed, spaced/ground-shielded; not a fixed generic width |
| LX1/LX2 | Compact geometry from regulator layout | Dedicated keepout from sensitive wiring; not a generic signal trace |

Do not force a 0.20/0.25 mm global rule between fine-pitch device pads when their verified geometry cannot support it. Add narrowly scoped breakout exceptions, typically around 0.10–0.125 mm only if supported by actual fabrication and pad spacing. Preserve wider rules outside the escape region; do not relax the whole board. Verify solder-mask webs too.

Start with conventional via pad/hole 0.60/0.30 mm. Permit 0.45/0.20 mm only for justified dense escape and verified fabrication. These are nominal CAD dimensions, not guaranteed finished-hole dimensions. Respect annular rings, drill-to-drill, hole tolerances and actual plating.

Start ordinary copper-to-routed-edge setback at 0.50 mm, with explicit manufacturer-defined connector/antenna exceptions. Start copper-to-NPTH-edge setback at 0.50 mm, and separately reserve the larger screw/washer/tool envelope. Component-body/edge clearance comes from actual mechanics, not one universal number.

For clocks/power versus analog, seek at least 0.5–1.0 mm lateral routing separation where space permits and avoid long parallel runs; keep the switching cell several millimetres away from the quiet analog bank as a placement goal. These are not sufficient proof of noise rejection. Prefer placement changes over marginal spacing.

Do not impose unnecessary serpentine equal-length routing on low-frequency EMG signals. Preserve analog symmetry and short routes. For SPI, verify timing/skew and return geometry; do not add a 50-ohm shunt resistor because the trace target is 50 ohms. Retain the existing 22-ohm series resistors.

## 8. Overall top-side floorplan

Use these flexible zones; final coordinates follow actual footprints and routing feasibility:

BOTTOM LONG EDGE: J_FPC1…J_FPC5, one row, all five sensor flexes exiting the same side. Keep channel order 1→5 and consistent mated orientation. Connector pitch is determined by the actual flex width, stiffeners, mating/tool clearance and keepouts, not illustration spacing.

LOWER/MIDDLE QUIET BANK: INA1…INA5 and RDD/input networks closest behind their respective sockets; U1/U2/U3 and feedback/servo components immediately behind or between their served channels. Reserve a quiet output corridor to the MCU.

LOWER LEFT QUIET EDGE: J_REF and R_ref; VDiv/VREF components near U1, away from the USB shield and power hot spots.

UPPER LEFT POWER/SERVICE ZONE: USB-C at the left edge; CC/VBUS protection immediately inside; BQ24072T, battery connector/service termination, gauge and TPS631000 in a compact power block. The pushbutton and charge LED must remain usable through the eventual enclosure.

POWER/ANALOG BOUNDARY: TPS7A2030 with its own close input/output capacitors, feeding an analog distribution path toward the AFE and MCU analog corner. Do not put the analog reference divider beside the inductor just to shorten its supply wire.

UPPER EDGE: ST67 antenna facing outward. Prefer an edge-centred placement trial following ST's antenna wiki; compare the applicable datasheet figure/reference-board arrangement before locking position. Document any edge-centre/corner wording discrepancy; do not derive a universal clearance from either a generated image or prose alone.

RIGHT/CENTRE-RIGHT: STM32 with ADC pins toward the quiet analog-output corridor and practical SPI escapes toward ST67. Evaluate legal package rotations using real pad locations. Do not swap MCU functions or amplifier sections merely to improve artwork without a separately verified circuit change.

RIGHT/LOWER SERVICE EDGE: SWD, UART recovery links/test access and boot access, outside antenna clearance and flex-mating envelopes.

BOTTOM SIDE: initially no large ICs, connector bodies or inductor. Prefer GND and flat probe access. Add bottom components only with documented placement benefit, assembly access and return-path review. No battery/enclosure-fit claim is allowed without real dimensions.

## 9. AFE and shared-reference placement details

Preserve actual physical package sharing:
U1 A/B = CH1 post/servo; U1 C/D = shared reference buffers.
U2 A/B = CH2; U2 C/D = CH3.
U3 A/B = CH4; U3 C/D = CH5.

Do not create five copies of U1–U3, split one package between rooms, or mechanically apply identical replicated-channel placement to shared packages. Use package-aware placement rooms/groups and report their membership.

For each channel, route:
BK13 buffered Va/Vb/Vc outputs → local RDD 10k/5k/10k → AD8237 → post/servo network → VOUT_n → ADC RC.

Place RDD components and RH/RL gain-setting resistors close to their actual amplifier pins. Put CH_n 3.9 nF across RG_n 80.6 kΩ with a compact loop. Place the CL_n/10 kΩ high-pass and 2 MΩ/3.3 µF servo components near the associated MCP6404 section. Minimize inverting/summing-node copper and leakage paths. Keep component supply bypasses beside the physical package power pins, not scattered according to schematic sheet positions.

Keep the 2 MΩ servo input node particularly short; avoid a large test pad, long via stub or clock route there. Do not automatically surround every high-impedance node with a GND guard or flooded top copper; guard potential and parasitic capacitance require circuit-specific justification. Do not solve this by cutting a long slot in L2.

Important: the main-board connector receives BUFFERED electrode signals. The fifteen 99.8 kΩ/22 MΩ/BAV199 high-impedance electrode interfaces reside on the DEBs and are not to be relocated to the main board.

Put RV1/RV2 and their capacitors next to U1's reference inputs. Preserve VREF_A separately from VREF_B_SRC and from MCU VREF+. Keep the five 68-ohm branches distinct, preferably isolating them close to the source before long connector runs. Never bridge them with a common downstream pour. Route each to its own J_FPCn pin8.

J_REF contacts remain the documented biased reference path through R_ref, not an audio jack or direct GND. Retain its verified net mapping. Reserve physical mating clearance; flag unselected production connector identity.

## 10. STM32 and ADC details

Maintain the existing pin assignments, packages and component values. Place 100 nF VDD bypasses with short pin-to-cap-to-ground loops, plus the existing bulk. VBAT/VDDUSB bypasses remain local. Give each critical bypass an adjacent GND via rather than a long shared return trace.

Place the dedicated 4.7 µF VCAP capacitor very close to pin48 and its ground return. MCU_VCAP must remain a small isolated net, never a power-distribution plane or test-power output.

Place the VDDA/VREF+ bypasses at pins22/21 with short returns near VSSA/VREF− pins19/20, into the common ground. Keep the 3V0_ANA feed away from the SPI/power corridor.

ADC physical mapping is PA0/23, PA1/24, PA2/25, PA3/26 and PA4/29 for CH1…5. Place each 330-ohm/10 nF network beside its ADC pin, capacitor on the ADC side. Route the longer path as VOUT_n before the resistor, not as the ADC-side node after it. No bypass of any series resistor. This RC is not a validated primary anti-alias filter.

Keep R_NRST/C_NRST near pin14 and preserve SWD access. Do not load SWDIO/SWCLK with new capacitors. Preserve separate MCU_BOOT0 and WIFI_BOOT. Unused oscillator pins remain open; do not add another MCU crystal for layout symmetry.

## 11. ST67, SPI, crystal, and antenna

Use actual ST67W611M1A6BTR geometry. Create a real all-copper-layer antenna keepout and a mechanical no-metal/no-battery envelope based on the applicable ST drawing. Prefer antenna overhang where mechanically supported; all circuit-body lands must still have valid host-board support. Account for enclosure, battery foil, flexes, probes, screws and panel rails. Do not put stitching vias in the antenna exclusion or remove ground beneath the whole module.

Retain ground pads 10/15/18/26/30/32 and library centre pads33–36 on GND. Start from the ST multi-via central-land recommendation, commonly five vias per land, and adapt only with documented pad/thermal/assembly justification. Do not interpret a changed numerical ordering between example central GND lands as a need to renumber the verified library.

Place the three existing 10 µF plus 100 nF supply pairs close to pins9/16/25, with very short local ground returns. Prefer the smaller bypass nearest the pin without making the larger capacitor remote. Keep the DNP 47 µF C_WIFI_BULK footprint near the radio supply entry, not inside antenna clearance.

Prefer a short L3 SPI corridor over uninterrupted L4 GND; retain L2. Target about 50 ohms using the chosen stack. Place SCK/MOSI/CS 22-ohm resistors near MCU drivers, MISO resistor near the module driver. Keep both resistor-side nets separate and correctly assigned. Avoid long clock test stubs and ground-guard traces that are not actually stitched to GND. No SPI path through the analog bank or switching cell. No unnecessary tight serpentine matching.

Keep radio UART test points on the MODULE side of removable zero-ohm links. Preserve active-high CS pull-down, BOOT and CHIP_EN circuits. Group recovery access so a probe/cable does not intrude on antenna clearance.

Place Q13FC13500003 and both zero-ohm links close to ST67 pins13/14, using short quiet traces. Preserve crystal pin1/pad1 and pin2/pad2 mapping. Keep C_WIFI_X32_IN/OUT footprints but Not Fitted. No 100 nF load capacitors and no large direct oscillator test pads. Follow oscillator guidance for ground shielding and avoid digital/power wiring underneath its sensitive local routing.

## 12. USB, charger, converter, gauge, and remote NTC

USB-C: reserve actual plug insertion and shell-anchor geometry. Keep D_CC_ESD and D_VBUS next to their connector nodes with short ground returns and nearby vias, not long branches into the board. Preserve independent CC1/CC2 pull-downs. D+/D− and SBU pads remain unconnected. Keep ESD return paths local to the connector/power area rather than across the AFE.

BQ24072T: put IN/OUT/BAT bypass parts close to their respective pins and ground/thermal pad. Use adequate thermal copper and an assembly-qualified thermal-via/stencil pattern. Keep TS/ISET/ILIM/TMR networks away from charge-current copper drops; reference their quiet returns to the IC's ground region as directed by TI. Do not replace this with a board-wide AGND/DGND split. Check thermal gradients toward the AFE; no unverified cell over the charger.

TPS631000: place UP2, L1, CUP4_1 and CUP4 as one compact cell. Preserve L1=DFE21CCN1R0MELL and CUP4=47 µF. Keep VIN/CIN and VOUT/COUT paths short and wide. Keep LX1/LX2 compact; no large switching-node pour, long layer excursion, test loop or unrelated trace under the switching cell. Route FB from a quiet output-sense point, with the divider/feed-forward capacitor near FB and away from LX nodes. Use TI's layout example rather than the concept rendering's pad geometry. Do not invent a thermal pad for an IC/package that has none.

Size current-carrying copper and vias from calculated operating and transient currents. The preceding audit used a provisional 0.6 A 3.3 V load-step target; treat this as a planning case, not a guaranteed maximum. Evaluate low-battery current, converter peak inductor/switch currents, neckdowns, copper weight, allowable voltage drop and temperature rise. LX routing is not sized merely from the average radio current.

MAX17048: place near the battery electrical connection with a short quiet cell-sense/VDD route and decoupling. Avoid sensing through unnecessary high-current trace drop. Do not add a shunt/current-sense amplifier: it is not in the verified circuit. Keep I2C pull-ups singular.

LTC2954/TPS3808 and shutdown: put small timing/control components close to their ICs and away from LX/SPI. Preserve SYS_EN versus KILL_CTRL; CT stays intentionally open. Place the button where the enclosure can actuate it, with local controller routing, and the existing LED where visible. Do not invent extra LEDs and their firmware circuits.

Remote NTC: put the R_TH_BAT two-pad termination in the battery-service area, with solder/tool access and provisional space for an independent harness anchor. Keep pad1=GND and pad2=BAT_TEMP. Retain the controlled termination-only footprint, not a local sensor body. Route BAT_TEMP/TS quietly away from LX and clock routes. Preserve 33.2k/28k/100k values. Exactly one 103AT-2 is required manually on the cell, excluded from machine placement. J_Li-Po remains 1=GND, 2=BAT_TEMP, 3=VBAT_CELL; no additional pack sensor on pin2 in this variant. Wire fit, strain relief and battery compatibility remain open checks.

## 13. Copper pours, vias, and return paths

Use real GND-connected copper and inspect it after repour. Remove floating islands and unintended slivers; avoid narrow necks around signal antipads. Do not hide unrouted ground connections with a visual fill that is not actually connected.

Place GND vias at decoupler ground pads, IC ground clusters, USB/ESD return regions, connector GND groups, module centre lands and sensible top/bottom ground-stitching locations. Start ordinary stitching at roughly 2–5 mm where helpful, then adjust to actual geometry and return-current needs. This is not a universal RF fence specification.

At an L1→L3 digital signal transition, place an adjacent GND stitching via, preferably within about 1 mm if geometry permits, tying the L2/L4 reference grounds. Both must be the SAME GND net. A nearby via does not cure a split/void directly beneath the trace.

Use multiple power vias for current paths as calculated; do not assign a universal amperage rating to a via. Prefer short same-layer connections for converter loops and small analog feedback loops.

Ordinary signal/ground vias should not be open via-in-pad under small SMT components by default. For ST67/BQ thermal lands, use a manufacturer/assembler-qualified filled/capped or approved tented/plugged/stencil arrangement. Open barrels can wick solder; tenting is not equivalent to filling. Do not assume all vias need expensive filling or that no thermal via can be in a pad.

No stitching inside antenna clearance. No arbitrary ground slit around analog circuits. Any local copper pullback for oscillator, summing-node capacitance or switching-node coupling must be specifically justified and must not create an unreferenced signal path.

## 14. Test access and connector serviceability

Preserve existing verified SWD/UART/BOOT access and actual selected testpoint models. Existing 5021 components are physical testpoints, not imaginary flat pads; account for their height and access. Do not silently change their footprints.

Add compact bare-pad access where absent and justified, preferably one 1.0 mm round exposed pad with no paste opening. Verify mask clearance and use larger spacing/access if hand probing requires it. Prefer about 2.0–2.54 mm centres in service groups when practical; do not force this spacing onto tightly coupled critical circuits.

Required candidate nodes:
- VBUS, VBAT_CELL, VSYS, 3V3_DIG, 3V0_ANA.
- VREF_A, VREF_B_SRC.
- VOUT_1…VOUT_5, BEFORE each 330-ohm ADC resistor.
- Nearby local GND pads in power, analog and digital service areas, ALL on GND.

Use existing accessible pads for reset, boot, UART, AFE_EN, SYS_EN and KILL_CTRL where adequate; add extra service pads only when access is missing. Avoid large direct test pads on INA inputs, servo summing nodes, LX1/LX2, the raw crystal nets or VCAP. Adjacent component pads may provide necessary specialist probing without long stubs.

Any new test point must be a schematic-backed one-pin component with a controlled footprint or an explicitly documented native PCB testpoint assignment. Update schematic/PCB consistency and record allowed added terminals. Do not create a PCB-only pad on a guessed net. Do not delete existing pins/nets to simplify verification.

Place labels CH1…CH5, signal-pin-1 orientation and service pin legends where readable. J_SWD remains 1=VTREF, 2=SWDIO, 3=GND, 4=SWCLK, 5=NRST; it is a custom header, not a universal adapter pinout. VTREF is not intended to power the complete board. Ground test pads named by physical zone must not create separate ground nets.

## 15. BK13 mechanical contract

Use all five actual DS sockets, correct footprints, and the existing mating contract. Their buffered signal pins remain 2/4/6 and reference pin8, with intended GND and grouped power lands unchanged. Do not renumber DS/DP contacts to make their schematic pictures look identical.

All sockets should share a consistent, documented mating orientation. Mark MAIN/DEB and signal pin1 clearly; do not confuse signal pin1 with the P1 power-contact group. Reserve flex-plug body, stiffener, bend, unplugging and strain-relief envelopes.

A standard rectangular courtyard alone does not prove a flex can mate or exit. Do not rotate one socket 180 degrees to shorten a trace without rechecking the full mechanical/electrical harness transform. If the existing fold/keying dimensions are missing, retain an explicit placement constraint and qualification gate rather than inventing a compliant assembly.

Do not route any flex, battery wire or connector metal across antenna clearance. Keep the five DEB PCBs and flex design separate from this main-board deliverable.

## 16. Following routing stage: sequence and checks

Prepare this sequence now; execute full-board routing only after the placement checkpoint is reviewed:
1. Resolve fixed connector/radio/mechanical placement, then local converter/charger and decoupling connections.
2. Route small analog feedback/servo/gain networks, crystal loop and ADC-side RC connections.
3. Route connector-to-INA buffered analog signals and references without noisy parallel paths.
4. Route VOUT signals to MCU through the quiet corridor.
5. Route SPI inside the defined reference-backed digital corridor, then UART/SWD/I2C/control.
6. Complete power distribution and GND stitching, inspect via currents and return paths.
7. Repour, inspect every layer, correct islands/clearances and compare actual copper connectivity to the schematic.
8. Finish silkscreen, test access, assembly/3D clearance, BOM/placement filtering and DRC.

If a step requires crowding a critical path, revise placement before accepting convoluted routing. Do not connect endpoints by geometry alone or use a generic autorouter result as analog/RF signoff.

## 17. Verification and honest acceptance criteria

For the current checkpoint prove:
- Native project and PcbDoc save/reopen; all selected footprints resolve.
- Correct main-board-only inventory, including DNP footprints and remote sensor termination, excluding DEB/flex packages.
- Actual schematic-to-PCB ECO and UID/pad/net consistency, not a handmade scratch assignment alone.
- Projected baseline terminal partitions preserved; explicitly account for added testpoints and main-only boundary changes.
- All twelve cross-sheet interfaces intact; five distinct VREF branches; zero-ohm/330-ohm/22-ohm links not bypassed.
- WIFI_BOOT != MCU_BOOT0, SYS_EN != KILL_CTRL, VREF+ =3V0_ANA, VCAP isolated from external supplies.
- No unintended shorts, component overlaps, invalid layers, mirror errors, missing pads or antenna violations.
- Meaningful stack, rule priority/scope, differential/single-ended profiles only where applicable, and documented unresolved process choices.

Report ERC and PCB DRC separately. At placement stage give unrouted connection counts openly; do not suppress them or claim a zero-unrouted board. After routing, all required connections must be routed and checked against copper connectivity. A green screenshot is not proof of DRC or electrical performance.

The radio's existing certifications are not automatic approval of a body-worn product. Review the ST67 integration/RF-exposure conditions, including the FCC/ISED separation language in its datasheet, for final intended use. Battery, body/external-interface safety, EMI, ESD and first-hardware EMG performance remain qualification tasks. No fabrication, charging or body-use approval is granted by this placement.

## 18. Deliverables: produce REAL Altium images

Save a placement checkpoint plus its native project/libraries, then generate:
- `MAIN_BOARD_TOP_PLACEMENT.png` with legible designators.
- `MAIN_BOARD_BOTTOM_PLACEMENT.png`.
- `MAIN_BOARD_3D_TOP.png` and `MAIN_BOARD_3D_BOTTOM.png`; identify missing 3D bodies instead of inventing them.
- Separate actual L1, L2, L3 and L4 views.
- Closeups: AFE/shared references; ADC RC/MCU bypass/VCAP; USB/BQ/power; TPS631000 switching cell/FB; ST67 ground/antenna/crystal; five sockets/mating envelopes; NTC/SWD/UART/test access.
- Annotated versions may explain zones and current paths but must retain the underlying real CAD image. Distinguish these annotations from actual routed copper.
- `BOARD_PARTITION_MANIFEST.csv`, actual component X/Y/rotation/side inventory, stack report, Altium rules export, placement DRC, applicable electrical-preservation tests, variant/BOM/testpoint reports and before/after hashes.
- `MAIN_BOARD_PLACEMENT_REVIEW.md` with decisions, measured clearances/distances, source references, unresolved mechanical constraints, routing plan and exact open-project instructions.

Do not issue manufacturing-ready Gerbers or fabricate pick-and-place coordinates for components that are not actually placed. Review images must come from the saved PCB, not an image generator or a renderer using invented parts.

Final status must be one of:
`PLACEMENT CHECKPOINT READY FOR REVIEW — NOT FABRICATION RELEASE`
or
`PLACEMENT INCOMPLETE — [specific unresolved native/mechanical blockers]`.

IMPLEMENT stages A and B now. Preserve the verified source. Stop at the review checkpoint before full-board routing. The next user decision should be based on actual CAD placement, not another generic PCB concept image.

## Primary reference starting points

Retrieve the actual current documents; record the versions used. These sources support requirements/principles, not universal endorsement of every proposed dimension above.

- ST67 datasheet: https://www.st.com/resource/en/datasheet/st67w611m1.pdf
- ST67 antenna: https://wiki.st.com/stm32mcu/wiki/Connectivity:ST67W611M1_Antenna_and_RF
- ST67 supplies/grounding: https://wiki.st.com/stm32mcu/wiki/Connectivity:ST67W611M1_Power_supplies_and_grounding
- ST67 SPI: https://wiki.st.com/stm32mcu/wiki/Connectivity:ST67W611M1_spi
- ST67 stack: https://wiki.st.com/stm32mcu/wiki/Connectivity:ST67W611M1_PCB_stack-up_options
- ST67 32 kHz: https://wiki.st.com/stm32mcu/wiki/Connectivity:ST67W611M1_32KHz_management
- ST AN6316: https://www.st.com/resource/en/application_note/an6316-how-to-optimize-the-pcb-layout-for-st67w611m1-and-stm32u575ai-stmicroelectronics.pdf
- STM32U5 AN5373: https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf
- TPS631000: https://www.ti.com/lit/ds/symlink/tps631000.pdf
- BQ24072T: https://www.ti.com/lit/ds/symlink/bq24072t.pdf
- AD8237: https://www.analog.com/media/en/technical-documentation/data-sheets/ad8237.pdf
- Mixed-signal layout: https://www.analog.com/en/resources/analog-dialogue/articles/what-are-the-basic-guidelines-for-layout-design-of-mixed-signal-pcbs.html
- JLCPCB capabilities: https://jlcpcb.com/capabilities/pcb-capabilities
- Altium multi-board workflow: https://www.altium.com/documentation/altium-designer/multi-board-design

Also consult the actual selected MCP6404, MAX17048, TPS7A20, LTC2954, TPS3808, Hirose BK13, GCT USB4105, Epson crystal and passive-package manufacturer drawings before their final local placement.
