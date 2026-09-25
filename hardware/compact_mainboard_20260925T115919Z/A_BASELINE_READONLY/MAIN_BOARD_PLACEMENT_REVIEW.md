# EMG main-board placement checkpoint — 24 September 2026

**Review draft. PLACEMENT INCOMPLETE — the native image package is now complete; the final project save/reopen checkpoint and final hash manifest are still outstanding.**

The native main-board placement exists and the latest completed Altium DRC reports **510 unrouted connections and zero violations in every other reported category**. Full-board routing has deliberately not been started. This document does not authorize fabrication, battery charging, body-connected operation, or population of the optional DRL. It will only change to the requested placement-review status after the remaining checkpoint exports are verified.

## 1. Open this working revision

Project: `C:\Users\PMLS\Desktop\emg-saw\hardware\pcb_layout_2026-09-23_drl\MainBoard\EMG_MainBoard_Layout.PrjPcb`

PCB: `MainBoard/EMG_MainBoard_Layout.PcbDoc`

Variant: **PROTO_1_REMOTE_NTC**.

Current controlled symbol snapshot: `MainBoard/Libraries/EMG_MainBoard_Placement_Frozen_20260924.SchLib`. It was exported natively from the current placed symbols. Its project-local footprint bindings match the current schematic. Older frozen symbols remain for traceability; do not update the design wholesale from an earlier snapshot. This snapshot does not imply that the placed symbols' historical source-library metadata was rebound to the new filename.

The verified full-system schematic baseline remains under `hardware/review_2026-09-16/fixed_revision_remote_ntc`. The preceding layout remains under `hardware/pcb_layout_2026-09-16`. Neither is the present DRL working PCB. Scratch mapping and ECO staging boards are evidence only.

The saved PCB used for the current inventory and DRC is SHA-256 `dd9b38813b487f4b68abf233758c2abaf93ec01159116b74e495af49bc25011f`. Later view-only saves can change native viewport caches; a final hash manifest must distinguish such serialization from design changes.

## 2. Actual physical-board partition and assembly

Only eight main-board sheets are included: `AFE_Channel_1` through `AFE_Channel_5`, `Analog_Shared`, `Power_tree_design`, and `MCU_sheet`. The five DEBs and one generic flex template remain separate physical-board designs. No DEB or flex packages were brought onto this PCB.

The current saved design contains **231 physical packages represented by 240 schematic sections**. Multipart U1/U2/U3 remain three physical packages. All 209 inherited main-board packages are on Top; the 22 optional DRL provisions are on Bottom. There are no component bodies on the internal copper layers.

| Category | Actual count | Assembly meaning |
|---|---:|---|
| Main PCB package/termination provisions | 231 | Includes DNP footprints and the remote-NTC wire termination |
| Not Fitted | 25 | 22 DRL provisions plus the three optional Wi-Fi capacitors |
| Fitted PCB parts | 205 | Excludes the remote thermistor body |
| SMT/mixed automatic-placement candidates | 195 | Review coordinates only; assembler origin/rotation conventions still require approval |
| Entirely through-hole PCB parts | 10 | Separate assembly list |
| Required remote sensor | 1 | SEMITEC 103AT-2, manual cell-mounted assembly |
| Required procurement instances | 206 | 205 PCB parts plus that same single remote sensor |
| Free bare PCB test pads | 15 | Copper features, zero procurement quantity |

The current assembly snapshot is `evidence/ASSEMBLY_SNAPSHOT_20260924T023521434Z/`. Its **522/522 freshly executed checks** compare the saved native schematic/project/variant/PCB against the completed native component inventory. It writes the partition manifest, variant table, all-component X/Y/rotation/side inventory, master procurement view, PCB assembly BOM, machine-candidate BOM/coordinates, through-hole BOM, manual NTC subsection and free-testpad list. These are main-board-subsystem records, not a complete five-DEB/five-flex purchase list.

Exactly one 103AT-2 is purchased and installed manually on the battery cell. Its appearance in the master BOM and manual subsection refers to one procurement group, not two sensors. R_TH_BAT's board coordinates locate the wire terminations, not a sensor body to machine-place. Pad1 remains GND and pad2 BAT_TEMP. J_Li-Po remains 1=GND, 2=BAT_TEMP, 3=VBAT_CELL; do not attach another pack thermistor to pin2 in this variant. The cell-mounted sensor's wire fit, insulation, thermal attachment and independent strain relief remain physical qualification items.

## 3. Changes and preservation

The existing eight-sheet platform, common GND, AFE, ADC, MCU, radio, charger and power-control architectures were retained. The following are the deliberate additions/corrections in this working revision:

- Added 22 optional DRL components to Analog_Shared and the main PCB, with all 22 Not Fitted in PROTO_1_REMOTE_NTC. The fifteen buffered Va/Vb/Vc signals use same-name global ports to reach the new sense resistors; the saved flattened result proves the connections rather than relying on label appearance.
- Transferred the new packages through native ECO in two passes, including the four new DRL nets and 47 new terminals. The bottom-side placement was verified against mirrored native pad geometry.
- Resolved inherited managed-library identity conflicts using controlled project-local libraries and placed source identities. No shared/global vendor library was edited and the proposed bulk footprint replacements were not executed.
- Corrected physical body placement/envelopes, silkscreen/assembly artwork, individual component clearances and the real ground-polygon copper. Earlier failing DRC and partial native-run evidence remains available.
- Added native representative maximum body envelopes to fourteen exact GRM155C71C105KE11D instances and their selected local pattern. These are explicitly labeled datasheet envelopes, not fabricated manufacturer STEP models.

The verified AFE networks were not redesigned: RDD 10k/5k/10k, AD8237 26.1k/1.07k gain network, 2M/3.3µF servo, 10k/820nF high-pass, and 80.6k/3.9nF C0G post stage remain. Five independent 68Ω VREF branches remain distinct. DEB bias/protection/buffer circuits remain on the separate DEBs.

The five 330Ω/10nF ADC networks remain in series with their own channels. MCU VCAP is isolated from the external supply rails, MCU VREF+ remains 3V0_ANA, WIFI_BOOT remains separate from MCU_BOOT0, and SYS_EN remains separate from KILL_CTRL. TPS3808 CT remains open. BQ24072T, MAX17048, TPS631000, TPS7A2030 and LTC2954 are retained. USB-C remains charge-only.

The optional DRL uses fifteen 1MΩ buffered sense branches, MCP6401 U_DRL1, 1.5MΩ feedback, 1nF compensation, 100nF local bypass, two 470kΩ output resistors and a removable 0Ω selection link to the existing reference-electrode path. The passive R_ref remains fitted in the default build. A future experimental populated-DRL assembly must remove R_ref and fit the DRL circuit as one separately controlled population change; the present variant does not enable both drivers. This is a future bench option; loop stability, recovery, electrode faults and system/body current paths have not been validated by the placement work. Do not populate it merely because footprints exist.

## 4. Verification evidence and its dates

| Check | Actual result | Evidence and scope |
|---|---|---|
| Native placement DRC completed 24 September, 10:29:13 local | 510 Un-Routed Net Constraint; zero all other reported categories | `evidence/DRC07_PLACEMENT_CHECKPOINT_RESULT.md` and native HTML/parsed JSON |
| Native inventory/rules/classes/legacy stack export, current saved PCB | COMPLETE | `evidence/NATIVE_FINAL_20260924T015854610Z/`; read context Modified=False |
| Current saved PCB terminal and frozen-symbol verification | 1479/1479 PASS, rerun against the fresh 24 September compile | `evidence/FINAL_CHECKPOINT_CONNECTIVITY_20260924T030756297Z.json` |
| Current assembly/variant/coordinates | 522/522 PASS, run 24 September | `evidence/ASSEMBLY_SNAPSHOT_20260924T023521434Z/` |
| Fresh native schematic compile, 24 September at 11:07:00 local | 0 active errors, 39 active warnings, 3 inherited suppressed diagnostics | `evidence/CHECKPOINT_CLOSE_20260924T025659139Z/NATIVE_COMPILE_FINAL_SEP24.txt`; REPORT COMPLETE, NeedsCompile=False, InCompilation=False |
| Original terminal-partition, interface and baseline-hash preservation | 658/658 PASS, rerun 24 September | `evidence/PRESERVATION_FRESH_20260924T030755428Z/`; original 743 terminals/210 partitions preserved after removing the authorized 47 new terminals; all 266 original baseline file hashes unchanged |
| Native ECO acceptance after controlled identity repair | Zero component, footprint, net or pad changes proposed | `images/NATIVE_ECO_ZERO_COMPONENT_NET_PAD_CHANGES.png`; only PCB-only class removal proposals remained, and were not executed |
| Controlled footprint-source identity repair | 988/988 library checks; 1109/1109 immediate PCB checks | `evidence/MANAGED_IDENTITY_NORMALIZATION_VERIFIED.md`; geometry-preserving correction at that recorded stage |
| Native polygon direct rebuild | 255/255 preservation checks | `evidence/POLYGON_DIRECT_REBUILD_DELTA_VERIFICATION.json` |
| Final R_TMR 0.10mm translation | 250/250 preservation checks | `evidence/R_TMR_DRC06_SAVED_DELTA_VERIFICATION.json` |

Counts from separate stages are not combined into an invented total. Earlier full-system 134/134, 164/164 or 624-pin reports are historical baseline evidence, not fresh results for this board. The fresh native compiler returned False, but completed processing and reports no active errors; the Boolean and the actual diagnostic list are recorded separately. Exact comparison against the 23 September post-placement report finds all 214 named terminal partitions and all 42 diagnostic rows unchanged, with no new or removed warnings. See `CHECKPOINT_CLOSE_20260924T025659139Z/COMPILE_VS_PRIOR_COMPARISON.json`.

The preceding native project-only save refreshed twelve existing controlled-library document IDs and registered the generated DRC HTML. All eight SchDoc hashes, the PCB disk hash, source-document membership, compile settings and variant sections stayed unchanged. Its project hash is now `51f2271bd6afe3028fb3f196e572150fc22cf7a79dba21affda8ea54e261be63`; exact changes are recorded in the closure folder's `PROJECT_SAVE_DIFF.json` and `PROJECT_SAVE_DISPOSITION.md`.

The current saved-file check compares all **790 logical terminal identities on 214 compiled nets** with **808 physical PCB pads on 136 connected PCB nets**. The difference is explained by 78 preserved intentional singleton/open terminals, 15 free bare test pads and inherited extra mechanical/duplicate pad records. It proves every compiled terminal's assigned pad/net and each exact connected terminal set; it does not prove completed routed copper continuity. The current PCB remains intentionally unrouted in many places.

The 39-warning report keeps the new DRL_SUM no-driver warning visible. It is a resistor-fed analog summing node with exactly the expected 18 terminals; ERC does not infer a driven input through those passive branches. This warning disposition is not a DRL loop-stability test. No blanket No-ERC or global diagnostic suppression was added.

The twelve repaired interfaces remain VOUT_1–5, FG_ALRT, USB_PGOOD_N, MCU_PWR_INT_N, AFE_EN, MCU_SHUTDOWN, I2C_SCL and I2C_SDA. Their fresh full terminal sets are recorded in `evidence/PRESERVATION_FRESH_20260924T030755428Z/DRL_F01_CONNECTIVITY_PROOF.json` and verified against the current PCB terminal assignments. All five VREF_B_FPCn branches, ADC resistors, SPI series links and the crystal links remain electrically distinct as intended.

## 5. Placement, stack and rule decisions

The main-board outline is the inherited rounded **80×45mm trial**, not a validated enclosure or battery fit. The organized edge arrangement retains five actual BK13 DS sockets in channel order along the long lower edge, quiet AFE/reference circuits behind them, power/service circuitry toward the upper left, MCU/ADC toward the right, and the ST67 integrated PCB antenna facing outward at the upper edge. The 22 DNP DRL provisions occupy a reviewed bottom-side area; their connection trials and eventual routing must preserve the common-ground references.

Exact current origins, rotations, sides and source UIDs are in the fresh component inventory and assembly snapshot. These are real saved coordinates. The report does not infer package bounds, connector mating envelopes or antenna approval from an origin coordinate alone.

There is **one electrical GND**, with no added AGND/DGND split, ferrite ground link or narrow star bridge. Ground remains below the module circuit body; the antenna exclusion is a separate physical keepout. The native L4 ground polygon was rebuilt after DRL placement: generated holes changed from 53 to 99, clearing all 45 non-GND DRL pads. The previous 45 shorts and associated clearances are absent in DRC07.

The current native stack export shows:

| Copper layer | Copper thickness | Following interlayer dielectric |
|---|---:|---|
| L1 TOP | 0.035mm | 0.0994mm 3313 prepreg, nominal Dk4.1 |
| L2 GND | 0.0152mm | 0.865mm core, nominal Dk4.6 |
| L3 POWER SIGNAL | 0.0152mm | 0.0994mm 3313 prepreg, nominal Dk4.1 |
| L4 BOTTOM GND | 0.035mm | Bottom external surface |

This is the inherited JLC04121H-3313 nominal 1.2mm candidate, 1.1642mm copper-plus-three-dielectric sum before solder mask. The legacy API also prints an FR-4 0.32004mm property after L4; it is disclosed in STACK.txt and is not silently added as a fourth interlayer gap. Current fabricator availability/tolerance and an actual native impedance-solver profile still need confirmation. No finalized 50Ω SPI trace width is asserted. Retain the existing 22Ω source resistors; do not add a shunt termination merely because the trace target is 50Ω.

The full saved rule scopes and priorities are in `NATIVE_FINAL_20260924T015854610Z/RULES.txt`. Fine-pitch and local connection exceptions are confined to named pads/tracks/regions, while the general rules remain active. The board-edge rule's nine explicit OutlineEdge matrix cells are approximately 0.50mm; the older scalar property still reads 0.254mm, as explicitly documented in the saved matrix evidence. Do not treat the scalar-only API dump as the complete matrix. The rules are placement/design starting constraints, not patient insulation distances or thermal current ratings.

The class export contains six duplicate component-class pairs and nine duplicate net-class pairs with equal membership/settings and distinct UIDs. They are PCB-only placement/routing groups and feed current rule scopes. Native ECO proposes removing both objects because the schematic does not generate these classes. Those proposals were not executed. Deduplicating to one equivalent class per name is optional housekeeping; deleting all classes would damage the rule organization. Four DRL-only nets currently use the applicable general rules and should be explicitly categorized when DRL routing is undertaken. This is not a missing electrical connection.

The latest DRC reports 111 rule-summary rows: one contains all 510 unrouted diagnostics; the other 110 report zero. It closes reported shorts, copper/component clearance, silk and board-edge violations under the saved rules. It does not establish unmodeled plug access, final material processing, radio performance or body safety.

## 6. Mechanical/body representation and measured corrections

R_TMR was moved from x=27.3 to **27.4mm at y=47.6mm**, resolving the observed 0.225mm pad-to-TP_VBUS clearance against its 0.25mm rule. C_VBUS was moved to **(18.7,44.2)mm** for physical clearance. The exact delta reports preserve other component poses and pad/net identities for those transactions.

The fourteen selected Murata GRM155 parts now have a **1.1×0.6×0.6mm maximum datasheet envelope**, checked against the official exact-MPN drawing. These are labeled representative native bodies, not vendor STEP models. Existing imported bodies and other missing-body limitations must remain visible in the final 3D inventory. A visually convincing solid is not proof of a selected connector's actual mating geometry.

The native bottom-placement check initially measured at least 1.500000mm from new DRL pads to the screened existing bottom/through copper and 0.350002mm between new different-net pad bounds. Those are scoped intermediate pad-bound results, not final all-component assembly clearances. The later DRC07 and final saved placement are the authoritative rule evaluation after subsequent corrections.

BK13 signal pins remain 2/4/6 for Va/Vb/Vc and pin8 for the independent VREF branch. Existing DS/DP transformed numbering and power groups 11/12/15 and 13/14/16 are retained. A schematic pin-number comparison cannot prove mating orientation. Main/DEB end labels, signal-pin1 identification, fold/keying/strain-relief geometry and continuity inspection remain required. Do not confuse signal pin1 with a P1 power-contact group.

## 7. Source basis and inherited evidence

Current DRL, MCP6401/package, passive, AD8237-body and Murata body-envelope sources and download hashes are archived under `work/design_basis/`, including `DRL_OPTION_DESIGN_BASIS.md`, `ARCHIVED_DATASHEET_HASHES.json`, `BODY_GEOMETRY_CORRECTION_BASIS.md` and `GRM155_CLEARANCE_ENVELOPE_BASIS.md`. Those contain the applied source versions and dimensions. The GRM155 body correction uses Murata drawing GRM155C71C105KE11-01A, dated 24 June 2026.

The original layout source archive under `hardware/pcb_layout_2026-09-16/sources/` and its `work/rf/` basis remain inherited evidence, not a fresh download claim. In particular, the ST67 requirements, antenna/power/SPI/32kHz guidance, STM32U5 hardware guidance, TPS631000 and BQ24072T local layout guidance, Hirose BK13 drawings and the selected factory stack basis continue to govern the next routing stage. Applicable principles were used without copying an unrelated STM32 BGA/SMPS reference design into this LQFP100 non-SMPS board.

## 8. Remaining qualification gates

These do not justify inventing new circuits or mechanical identities. They require the actual physical selections or measurements:

- Protected battery MPN, capacity, allowed charge current/temperature, protection behavior, dimensions and mating connector remain unselected. The TS divider is not silently retuned to an unknown battery.
- Remote NTC wire fit, solder/tool access, insulation, strain relief and cell thermal attachment remain subject to battery/sensor instructions and assembly inspection. Exactly one sensor must be connected; a charging LED is not evidence of valid sensing.
- J_REF, J_SWD, J_Li-Po and other provisional mechanical parts require frozen orderable identities and mating/access checks. The SWD mapping is custom 1=VTREF, 2=SWDIO, 3=GND, 4=SWCLK, 5=NRST; VTREF is not an instruction to power the whole board.
- BK13 flex fold, physical pin transform, stiffener/bend/tool envelope and protection against reversed mating need a real assembly contract and unpowered continuity inspection. Electrode hardware and the separate DEB/flex layouts remain separate deliverables.
- Antenna keepout versus battery foil, enclosure, flexes, wires, screws, probes and panel rails requires complete mechanical review. ST67 module certification alone does not approve this wearable's RF exposure or end product.
- Thermal/central-land vias and stencil/filled-capped/tented arrangements need assembler agreement. An open via barrel is not interchangeable with a filled/capped land.
- Effective MLCC capacitance, VCAP requirements, input-resistor pulse behavior, thermal margin, low-battery converter transients and the selected charging-temperature limits remain qualification items.
- The optional populated DRL requires phantom testing of stability, common-mode rejection, electrode loss, output saturation/recovery and current paths before any body testing. DNP placement is not proof of performance.
- Native DRC does not validate EMG noise/crosstalk, alias rejection, ADC settling, Wi-Fi burst coupling or battery-temperature operation; those require first-hardware measurement.

**Body-connected operation remains battery-only until external-interface isolation/safety is formally validated. Do not connect grounded USB, SWD, UART or oscilloscope equipment to a person-worn unit.** No medical certification, charging approval or body-use approval follows from this placement checkpoint.

## 9. Routing plan after placement review

1. Resolve fixed connector/radio/mechanical placement and obtain the user's placement review. Complete compact charger/converter/bypass connections with appropriate local returns.
2. Route small analog feedback/gain/servo loops, the ST67 crystal loop and ADC-side RC connections. Keep high-impedance/summing nodes compact; do not add large probe stubs.
3. Route buffered BK13-to-INA signals and each independent VREF branch, avoiding long parallel clock/switch-node paths.
4. Route VOUT_1–5 through the quiet corridor to the resistor input sides. Keep the ADC-side nodes short.
5. Route SPI in the documented reference-backed digital corridor, then UART/SWD/I2C/control. Maintain continuous reference copper and nearby return vias at layer transitions; no arbitrary analog/digital ground slit.
6. Complete power distribution and GND stitching, checking actual copper/via current paths, local sense returns and voltage drop. Keep LX nodes compact.
7. Repour and inspect every copper layer, clear islands/slivers, and compare actual routed copper against the schematic terminal partitions. Reach zero required unrouted connections only at the routing-stage release gate.
8. Finish silkscreen, test/service access, complete 3D/mating review, assembly filters and final DRC. Obtain the required physical/qualification decisions before fabrication outputs.

No full-board autorouter or manufacturing-ready Gerber package is part of this checkpoint.

## 10. Deliverable status

| Deliverable | Current disposition |
|---|---|
| Native main-only project/PCB and controlled libraries | Present; current identity/net/pad checks pass |
| Native ECO evidence | Present; component/footprint/net/pad comparator categories empty after identity repair |
| Main partition, variant/DNP, BOM and actual coordinate inventories | Present in fresh assembly snapshot |
| Native rule/class/stack export | Present in NATIVE_FINAL_20260924T015854610Z |
| Placement DRC | Present: DRC07, 510 unrouted only |
| Schematic terminal/preservation evidence | Present; fresh 24 September compile, 658/658 preservation and 1479/1479 saved-pad/frozen-symbol checks complete |
| Native Top/Bottom placement, 3D Top/Bottom, L1–L4 views | Present: eight named views in `images/`, indexed and hashed in `evidence/IMAGE_PACKAGE_20260924/` |
| Required local closeups | Present: five named closeups (AFE channel 1, power/charger, ST67 RF, MCU/SWD/test points, BK13 flex row) |
| Final project close/reopen/readback and final hash manifest | Pending final checkpoint closure |
| Full routing/manufacturing outputs | Intentionally not performed |

## 11. Native image package — 24 September 2026

Thirteen named views were captured from the live Altium 22.5.1 session on the saved
`EMG_MainBoard_Layout.PcbDoc`, variant `PROTO_1_REMOTE_NTC`. The package index, per-file SHA-256
manifest, capture recipe and the full View Configuration readback are in
[`evidence/IMAGE_PACKAGE_20260924/`](evidence/IMAGE_PACKAGE_20260924/).

| View | Image |
|---|---|
| Top placement, 2D | [`images/NATIVE_TOP_PLACEMENT_2D.png`](images/NATIVE_TOP_PLACEMENT_2D.png) |
| Bottom placement, 2D, viewed from bottom | [`images/NATIVE_BOTTOM_PLACEMENT_2D.png`](images/NATIVE_BOTTOM_PLACEMENT_2D.png) |
| 3D top | [`images/NATIVE_3D_TOP.png`](images/NATIVE_3D_TOP.png) |
| 3D bottom | [`images/NATIVE_3D_BOTTOM.png`](images/NATIVE_3D_BOTTOM.png) |
| L1 TOP | [`images/NATIVE_LAYER_L1_TOP.png`](images/NATIVE_LAYER_L1_TOP.png) |
| L2 GND | [`images/NATIVE_LAYER_L2_GND.png`](images/NATIVE_LAYER_L2_GND.png) |
| L3 POWER SIGNAL | [`images/NATIVE_LAYER_L3_POWER_SIGNAL.png`](images/NATIVE_LAYER_L3_POWER_SIGNAL.png) |
| L4 BOTTOM GND | [`images/NATIVE_LAYER_L4_BOTTOM_GND.png`](images/NATIVE_LAYER_L4_BOTTOM_GND.png) |
| Closeup — AFE channel 1 (J_REF, INA1, R_ref, RH_2, Cdiv_1, RDD1–3, J_FPC1, U1) | [`images/NATIVE_CLOSEUP_AFE_CH1.png`](images/NATIVE_CLOSEUP_AFE_CH1.png) |
| Closeup — USB-C, BQ24072T charger, TPS631000 converter, MAX17048, J_Li-Po | [`images/NATIVE_CLOSEUP_POWER_CHARGER.png`](images/NATIVE_CLOSEUP_POWER_CHARGER.png) |
| Closeup — ST67W611M1 module land, thermal via field, 32 kHz branch | [`images/NATIVE_CLOSEUP_ST67_RF.png`](images/NATIVE_CLOSEUP_ST67_RF.png) |
| Closeup — STM32U575VIT6, J_SWD, TP_GND and WiFi/MCU test points | [`images/NATIVE_CLOSEUP_MCU_SWD_TESTPOINTS.png`](images/NATIVE_CLOSEUP_MCU_SWD_TESTPOINTS.png) |
| Closeup — BK13 flex connector row J_FPC1–J_FPC5 | [`images/NATIVE_CLOSEUP_BK13_FLEX_ROW.png`](images/NATIVE_CLOSEUP_BK13_FLEX_ROW.png) |

**Provenance.** Every view is display-only. `IMAGE_PACKAGE_MODIFIED_CHECK_SEP24.txt`, read after the
last capture, records `PCBDOC_MODIFIED=False` and `PRJPCB_MODIFIED=False`. No component, net, pad,
rule or geometry was changed, and nothing was saved, to produce these images.

**Read them with these limits.**

- Connection lines and DRC/violation markers are switched off in the View Configuration so the
  placement is legible. The board still contains 570 connection objects and the 510 unrouted-connection
  violations reported by DRC07. Hiding markers is a display choice and clears nothing.
- The four copper-layer views show pads, vias and the L2/L4 plane pours only. The absence of routing is
  the real state of this checkpoint.
- The 3D bottom view shows bottom-side pads with no component bodies: the 22 bottom-side components
  carry no 3D body geometry on the bottom mechanical layer pair. Close that CAD gap before any
  enclosure, flex-fold or mating review that depends on bottom-side height.
- The 2D bottom placement view is dominated by the L4 GND pour, which is the actual bottom copper.

The package supports placement review only. It is not fabrication approval, not a routing release, and
not evidence of DRL, charging, RF-exposure or body-contact qualification.

The next user decision should be based on the completed native image package and this saved CAD. The current draft must not be read as final fabrication or populated-DRL approval.
