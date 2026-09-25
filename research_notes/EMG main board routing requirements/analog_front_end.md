# Analog front-end PCB layout and routing requirements: AD8237 / MCP6404 / MCP6401 / VREF distribution / ADC-input RC / Hirose BK13C (5-ch sEMG main board)

Legend used in every finding: **[HARD]** is a manufacturer "must / do not" statement or a drawing/spec limit. **[MFR]** is a recommendation for that exact part. **[PRACTICE]** is manufacturer app-note/tutorial guidance that carries over to this board. **[ANALOG]** is guidance from a sister Hirose series, not BK13 itself. **[N/A]** marks guidance that does not apply to this build (one common GND by design; DRL not fitted). "Derived" marks my own arithmetic or interpretation. Source status (checked 24–25 Sep 2026): the AD8237 and MCP640x PDFs downloaded again from the official URLs are byte-identical (SHA-256 `1022ed7d…` / `7be1e00c…`) to the 16 Sep archive in `hardware/pcb_layout_2026-09-16/sources/analog_power/` ([index][idx]). So **AD8237 Rev. 0 (Aug 2012)** and **MCP640x DS20002229E (Rev. E, Mar 2023)** are still current. TI `symlink` and ST `resource` URLs serve the latest revision (listed below). Documents older than about 2012 are marked "(old)". Their content is still what the manufacturer serves.

## Q1. AD8237 datasheet layout guidance: input symmetry, FB/gain-network parasitics, REF drive and routing, bypassing, input RC/protection, guard/shield

### Takeaway
The AD8237 datasheet (Rev. 0, the only revision) gives just four layout rules:
- match the source impedance of the +IN and −IN paths and put any series resistance right at the input pins;
- place 0.1 µF as close as possible to each supply pin (10 µF can sit farther away and be shared);
- refer REF and the output to the correct local reference;
- never leave BW floating.

Unlike classic in-amps, REF resistance does not affect CMRR, but REF is a gained input. In this servo topology (Fig. 77 style), the Vservo trace to REF and the per-channel VREF_A taps at RL/servo are as noise-critical as the electrode inputs (derived below).

### Cited Findings
**Pins and hard limits**
- [HARD] Pinout (RM-8/MSOP-8): 1 BW, 2 +IN, 3 −IN, 4 −VS, 5 +VS, 6 REF, 7 FB, 8 VOUT. BW: "For high bandwidth mode, connect this pin to +VS, or for low bandwidth mode, connect this pin to −VS. **Do not leave this pin floating.**" — [AD8237 Rev. 0, p.8, Table 6][ad8237]
- [HARD] Absolute max voltage at −IN, +IN, FB or REF = +VS + 0.5 V. — [AD8237 p.7, Table 4][ad8237]
- BW to +VS is only for G ≥ 10 (1 MHz GBP). Otherwise BW goes to −VS (200 kHz GBP). — [AD8237 p.20][ad8237]
- Package is RM-8, JEDEC MO-187-AA, 0.65 mm pitch. — [AD8237 p.27][ad8237]

**Input-path symmetry, input RC and protection**
- [MFR] "Poor layout can cause some of the common-mode signal to be converted to a differential signal before reaching the in-amp. This conversion can occur when the path to the positive input pin has a different frequency response than the path to the negative input pin. For best CMRR vs. frequency performance, closely match the impedance of each path. Place additional source resistance in the input path (for example, for input protection) close to the in-amp inputs to minimize interaction between the resistors and the parasitic capacitance from the printed circuit board (PCB) traces." — [AD8237 p.23, "Layout / Common-Mode Rejection Ratio over Frequency"][ad8237]
- [MFR] Input protection: put series resistors in each input to limit current to 5 mA. Example: +VS = 3 V with a 10 V overload needs ≥ (10 V − 3 V)/5 mA = 1.4 kΩ (Fig. 68). — [AD8237 p.22][ad8237]
- [MFR] The on-chip RFI filter "is sufficient for a majority of applications". Optional external RFI filter (Fig. 69):
  - R = 10 kΩ 1 %, CC = 1 nF 5 % (each input to ground), CD = 10 nF across the inputs;
  - f_diff = 1/(2πR(2CD + CC)); f_CM = 1/(2πR·CC). — [AD8237 p.22][ad8237]
- [MFR] Input bias current needs a DC return path (Fig. 74). — [AD8237 p.23][ad8237]
- [PRACTICE] ADI in-amp guide on RFI filters:
  - "The RFI filter should be built using a PC board with ground planes on both sides. All component leads should be made as short as possible. The input filter common should be connected to the amplifier common using the most direct path."
  - Avoid separate boards, because the extra lead length "can create a loop antenna. Instead, physically locate the filter right at the in-amp's input terminals." — [A Designer's Guide to Instrumentation Amplifiers, 3rd ed. 2006 (old), p.5-14 (PDF p.67)][inamp]
- [PRACTICE] AN-671 on RFI filters and rectification:
  - Any mismatch between the time constants of C1a/R1a and C1b/R1b "will unbalance the bridge and reduce high frequency common-mode rejection". Use matched resistors and 5 % capacitors; C2 ≈ 10 × C1 gives about 20× less mismatch error.
  - Build the filter on a board "with ground planes on both sides".
  - RF rectification: "even the best in-amps have virtually no common-mode rejection at frequencies above 20 kHz… Once rectified, no amount of low-pass filtering at the in-amp output will remove the error… If the RF interference is of an intermittent nature, this can lead to measurement errors that go undetected." — [AN-671 Rev. 0, 08/2003 (old), pp.1–2][an671]

**Gain network at FB (the AD8237 has no RG pins; G = 1 + R2/R1 around FB)**
- [MFR] "Unlike most instrumentation amplifiers, the relative match of the two gain setting resistors determines the gain accuracy… two 1% resistors can cause approximately 2% maximum gain error at high gains." TCR tracking sets gain drift. — [AD8237 p.21][ad8237]
- [MFR] "If the parallel combination of R1 and R2 is greater than about 30 kΩ, the resistors start to contribute to the noise. For best output swing and linearity, keep (R1 + R2) || RL ≥ 10 kΩ." — [AD8237 p.20][ad8237]
- [MFR] "For the best performance, keep the two input pairs (+IN and −IN, and FB and REF) at similar dc and ac common-mode potentials." — [AD8237 p.21][ad8237]
- [PRACTICE] For gain drift, a gain resistor's "physical position relative to other resistors in the same gain network, and even its physical orientation (vertical or horizontal)" matter (thermal gradients). — [In-amp guide p.5-9 (PDF p.62)][inamp]
- The datasheet says nothing about parasitic capacitance at FB (see Gaps).

**REF drive and REF routing**
- [MFR] "Traditional instrumentation amplifier architectures require the reference pin to be driven with a low impedance source… With the AD8237 architecture, resistance at the reference pin has no effect on CMRR." REF resistance does change gain: G = 1 + (R2 + RREF)/R1 (Fig. 71). A divider can drive REF if its resistance is constant (Fig. 72). — [AD8237 pp.22–23][ad8237]
- [MFR] REF has gain.
  - "Because the reference pin is functionally no different from the positive input, it can be used with gain": VOUT = (VREF + V+IN − V−IN)(1 + R2/R1) (Fig. 70).
  - This is useful for "dc removal servo loops, which typically use an inverting integrator to drive REF… This requires special attention to the input range (especially at REF) and the output range. All three input voltages are referred to the one ground shown, which may need to be a low impedance midsupply." — [AD8237 p.22][ad8237]
- [MFR] ECG front end (Fig. 77): "If the REF pin is left unconnected to the gain setting network, a low frequency inverting integrator can be connected from the output to the REF pin". The figure uses a 2 MΩ / 3.3 µF integrator (the same values as this board's Rservo/Cservo). "Proper decoupling is not shown." — [AD8237 p.26][ad8237]
- [MFR] "The output voltage of the AD8237 is developed with respect to the potential on the reference terminal. Take care to tie REF to the appropriate local ground." (Fig. 73 shows supply decoupling, REF and output referred to local ground.) Reference pins also "provide a means of physically separating the input and output grounds to reject ground bounce common to the inputs." — [AD8237 pp.22–23][ad8237]
- [PRACTICE] For classic in-amps: put an op-amp buffer between a divider and REF. "Many other solutions are possible, as long as the impedance driving the reference terminal is kept very low" (Figs. 5-7/5-8). The CMR part is **[N/A]** to the AD8237; the gain part still applies. — [In-amp guide p.5-4 (PDF p.57)][inamp]

**Supply bypass and chopper**
- [MFR] "Place a 0.1 μF capacitor as close as possible to each supply pin. As shown in Figure 73, a 10 μF tantalum capacitor can be used farther away from the part… can usually be shared by other precision integrated circuits. Keep the traces between these integrated circuits short to minimize interaction of the trace parasitic inductance with the shared capacitor. If a single supply is used, decoupling capacitors at −VS can be omitted." — [AD8237 p.23][ad8237]
- [MFR] The inputs are chopped at about 27 kHz. Clock ripple is "typically 100 μV RTI when the bandwidth is greater than the clock frequency". It is worst in high-bandwidth mode, and extra filtering after the AD8237 may be needed. — [AD8237 p.21][ad8237]

**Guard/shield**
- The AD8237 datasheet has no guard-ring or cable-shield guidance (theory, applications and layout text, pp.20–26, reviewed). — [AD8237][ad8237]

**Project facts used below**
- INAn:
  - +IN comes from one 5 kΩ RDD (RDD2/5/8/11/14, AR02BTC5001).
  - −IN is the junction of two 10 kΩ RDD (ERA2ARB103X).
  - FB joins RH 26.1 kΩ (to VOUT) and RL 1.07 kΩ (to **VREF_A**).
  - REF is Vservo_n (servo op-amp output, also Cservo).
  - BW and −VS go to GND; +VS goes to 3V0_ANA.
- INA_OUT_n drives:
  - RH;
  - CL (820 nF, GRM21BR71C824KA01L) in series with RGN 10 kΩ into the gain-stage IN−;
  - Rservo 2 MΩ into the servo IN−.
- The servo IN+ and the gain-stage IN+ both connect to VREF_A. — [pin audit 16 Sep 2026][pinaudit]; [BOM][bom]

### Inferences
1. **Input symmetry is designed in; routing must keep it.**
   - Both inputs see about 5 kΩ Thevenin (5 kΩ vs 10 k‖10 k).
   - Per p.23, the RDD resistors belong at INA pins 2/3. The post-RDD nets (NetINAn_2, NetINAn_3) should be the short, geometrically similar side. Make the −IN junction at the pin, not as a long stub.
   - Let the long runs be the low-impedance buffered Va/Vb/Vc from the connector. If fixed placement put RDD near J_FPC instead, flag the long 5 kΩ post-RDD traces.
   - Mains CMRR is not the concern (derived): a 1 pF imbalance at 5 kΩ converts common mode to differential at 50 Hz by 2π·50·5k·1p ≈ 1.6×10⁻⁶ (about −116 dB).
   - The real concern is RF (on-board Wi-Fi, converter harmonics), which AN-671 says cannot be filtered out after rectification. So route +IN/−IN, and Va/Vb/Vc upstream, as a tight group on one layer over unbroken L2. Interference then arrives as common mode.
2. **REF and VREF_A taps are "input-class" nets (derived from Fig. 70 with R1 returned to VREF_A, plus the pin audit).**
   - INA_OUT = V_A(RL) + G·(Vd + V_REFpin − V_A(RL)), with G = 1 + 26.1/1.07 ≈ 25.4.
   - The integrator output follows its own IN+ in-band: V_REFpin = V_A(servo IN+) + V_Cservo.
   - Two consequences:
     - (a) VREF_A noise common to all taps nets to about 1× at VOUT (input-referred ≈ 1/205).
     - (b) Any in-band **difference** between VREF_A at RL_n's return and at servo_n's IN+, and any pickup on the **Vservo_n trace** to INA pin 6, is amplified by G × 8.06 ≈ 205, the same as the EMG signal (input-referred 1:1).
   - Rule: for each channel, take RL_n's VREF_A end and the servo IN+ (U1.5, U2.5, U2.12, U3.5, U3.12) from one local VREF_A point, with no other channel's current flowing between them.
   - Route Vservo_n (op-amp output to pin 6) short, on L1 over unbroken L2, away from digital/switching nets.
   - A difference at the gain-stage IN+ tap only gets about 9× (input-referred ≈ 0.044), so it is lower priority.
   - The shared-trace error is small but real: about 1 µA of signal current per channel × 0.1 Ω of shared VREF_A copper ≈ 0.1 µV.
3. **FB parasitic capacitance is not critical (derived).** The FB node impedance ≈ RH‖RL ≈ 1.03 kΩ, so 1 pF puts a pole near 150 MHz. Keep RH across pins 7–8 and RL at FB mainly to minimise pickup loop area and to keep RH/RL at the same temperature (in-amp guide p.5-9).
4. **Bypass checklist.**
   - Each INA pin 5 gets its own 0.1 µF right at the pin, with its GND via at the capacitor pad.
   - Pins 4 (−VS) and 1 (BW) go straight to GND vias. No −VS decoupling is needed (single supply).
   - Five unsynchronised ~27 kHz choppers share 3V0_ANA. Use short, wide 3V0_ANA distribution to limit supply-borne interaction, echoing ADS1298's "wide power-supply traces or dedicated power-supply planes to minimize… crosstalk" ([ADS1298][ads1298]).
5. **[N/A]** Fig. 69 external RFI filter and Fig. 68 protection resistors are not in this design. The 5/10 kΩ RDD resistors already limit fault current to well under 5 mA (derived: ≈3.5 V/5 kΩ ≈ 0.7 mA). The FB-bias-cancel resistor in series with REF (Fig. 66) is N/A because REF is servo-driven.
6. **Outside routing scope, for the hardware engineer (derived):** the in-band INA_OUT load is (RH + RL) 27.17 kΩ ‖ (RGN + CL ≈ 10.2 kΩ at 100 Hz) ‖ 2 MΩ ≈ 7.4 kΩ. That is below the datasheet's "(R1 + R2) || RL ≥ 10 kΩ" best-swing/linearity recommendation. Impact is probably small at EMG amplitudes.

### Gaps
- ADI publishes no AD8237 PCB layout example beyond schematic Fig. 73. The EVAL-AD8237 user guide/board files were not reviewed.
- There is no manufacturer statement on FB parasitic capacitance, guard rings or shield driving for the AD8237.
- Microphonic (piezoelectric) noise from Class II MLCCs in the gained path (Cservo 3.3 µF X7R 1206; CL 820 nF X7R 0805) could matter in a wearable. It was not researched here, and no source is cited.

## Q2. MCP6404 (U1–U3, quad, from BOM) and MCP6401 (U_DRL1, not fitted): bypassing, summing-node capacitance, guard rings, ground pour near high-impedance nodes

### Takeaway
Microchip gives concrete numbers:
- 0.01–0.1 µF within **2 mm** of VDD, and bulk ≥ 1 µF within **100 mm** (shareable);
- a series RISO when load capacitance exceeds about **100 pF at G = +1**;
- guard rings only "where low input bias current is critical" (≈10¹² Ω surface leakage gives 5 pA at 5 V).

No node in this AFE is leakage- or capacitance-critical enough to need guard rings or plane cut-outs (derived). A continuous GND plane under the op-amps is correct. The real layout duties are per-package bypass, short summing nodes, isolation-resistor placement and no added capacitance on VREF_A.

### Cited Findings
- Part identity:
  - U1, U2, U3 = **MCP6404T-E/ST** (TSSOP-14, footprint TSSOP-ST14_N).
  - U_DRL1 = MCP6401T-E/OT (SOT-23-5), **Not Fitted**. — [BOM][bom]
- Currency: DS20002229E covers MCP6401/1R/1U/2/4/6/7/9. Revision E (March 2023) updated the AEC-Q100 features, the spec tables and the packaging. — [MCP640x DS20002229E, Appendix A][mcp]
- [MFR] §4.4 Supply bypass: "the power supply pin (VDD for single-supply) should have a local bypass capacitor (i.e., 0.01 μF to 0.1 μF) **within 2 mm** for good high frequency performance. It can use a bulk capacitor (i.e., 1 μF or larger) **within 100 mm** to provide large, slow currents. This bulk capacitor can be shared with other analog parts." §3.3: "VDD will need bypass capacitors." — [MCP640x pp.16, 18][mcp]
- [MFR] §4.3 Capacitive loads:
  - A unity-gain buffer is the most sensitive. "When driving large capacitive loads with these op amps (e.g., **> 100 pF when G = +1 V/V**), a small series resistor at the output (RISO…) improves the feedback loop's phase margin."
  - Fig. 4-5 gives recommended RISO vs CL/GN (GN = noise gain). Check peaking/overshoot by bench test or SPICE. — [MCP640x p.18][mcp]
- [MFR] §4.5: an unused op-amp in a quad should be configured per Fig. 4-6, to stop output toggling and crosstalk. — [MCP640x p.18][mcp]
- [MFR] §4.6 PCB surface leakage:
  - "Under low humidity conditions, a typical resistance between nearby traces is 10¹² Ω. A 5V difference would cause 5 pA of current to flow; which is greater than the… bias current at +25°C (±1.0 pA, typical). The easiest way to reduce surface leakage is to use a guard ring around sensitive pins (or traces). The guard ring is biased at the same voltage as the sensitive pin."
  - Non-inverting / unity-gain: guard ring to **VIN−**, with VIN+ reached by a wire that does not touch the PCB surface.
  - Inverting / transimpedance: guard ring to **VIN+** ("same reference voltage as the op amp (e.g., VDD/2 or ground)"), with VIN− reached by a wire that does not touch the PCB (Fig. 4-7). — [MCP640x p.19][mcp]
- Specs: IB = 1 pA typ, 100 pA max at 25 °C; 30 pA typ at 85 °C; 800 pA typ at 125 °C. IOS = 1 pA typ. ZCM = ZDIFF = 10¹³ Ω ‖ 6 pF. GBWP = 1 MHz typ. — [MCP640x pp.1, 3–4][mcp]
- [MFR] Input protection (Figs. 4-2/4-3): min(R1, R2) > (VSS − min(V1, V2))/2 mA, and > (max(V1, V2) − VDD)/2 mA. — [MCP640x p.17][mcp]
- TSSOP-14 land pattern (Microchip drawing C04-2087 Rev E): pitch 0.65 BSC; pad-row spacing C = 5.90; pad width X ≤ 0.45; pad length Y ≤ 1.45; pad-to-pad gap G ≥ 0.20 mm. — [MCP640x p.41][mcp]
- MCP6401 SOT-23-5 (C04-2091-OT Rev H, per project basis): pitch 0.95; opposing centres 2.80; pads 0.60 × 1.10 mm. Pins: 1 VOUT, 2 VSS, 3 VIN+, 4 VIN−, 5 VDD. — [DRL option basis][drl]
- [PRACTICE] ADI (Analog Dialogue 39-09, Sept 2005, old):
  - "High speed op amps will perform better if the ground plane is removed from under the input and output pads. The stray capacitance introduced by the ground plane at the input… lowers the phase margin".
  - Otherwise: "Best results will occur when the entire plane is unbroken. Resist the temptation to remove areas of the ground plane for routing other signals".
  - Guarding: "completely surround the sensitive node with a guard conductor that is kept at, or driven to (at low impedance), the same potential as the sensitive node". — [AD 39-09 pp.4, 6][ad3909]
- [PRACTICE] "All decoupling capacitors must connect directly to a low impedance ground plane in order to be effective. Short traces or vias are required". The HF decoupling capacitor "must be as close to the chip as possible" (Fig. 6). — [MT-101 Rev. 0, 03/09 (old) pp.2, 6–7][mt101]
- [PRACTICE] "Do not place vias between bypass capacitors and the active device. Placing the bypass capacitors on the same layer as close to the active device yields the best results." — [ADS1299 SBAS499C §12.1 p.72][ads1299]
- [PRACTICE] Kelvin bypassing: "The supply current flows through the bypass capacitor pin first and then to the supply pin". — [ADS1298 SBAS459K p.98][ads1298]
- Project section roles (all 12 sections used):
  - Inverting gain stages: U1A, U2A, U2C, U3A, U3C.
    - Outputs VOUT_1..5.
    - IN− node NetCH_n_2: RGN 10 kΩ, RG 80.6 kΩ ‖ CH 3.9 nF C0G.
    - IN+ = VREF_A.
  - Servo integrators: U1B, U2B, U2D, U3B, U3D.
    - IN− = NetCservo_n_1 (Rservo 2 MΩ, Cservo 3.3 µF).
    - IN+ = VREF_A.
    - OUT = Vservo_n, to INAn pin 6.
  - U1C is the VREF_A follower: IN+ = VDiv (RV1/RV2 100 kΩ, Cdiv_10uF, Cdiv_1); output pin 8.
  - U1D is the VREF_B_SRC follower: output pin 14, to R_ref 100 kΩ and R_VREF1..5 (68 Ω). — [pin audit][pinaudit]; [BOM][bom]
- DRL option (all 22 parts Not Fitted):
  - U_DRL IN− = DRL_SUM: 15 × 1 MΩ from the buffered Va/Vb/Vc nets; feedback 1.5 MΩ ‖ 1 nF.
  - IN+ = VREF_B_SRC, taken before the 68 Ω branches.
  - 100 nF between pins 5 and 2, adjacent to the package.
  - DNP 0 Ω link to J_REF. — [DRL option basis][drl]

### Inferences
1. **Bypass checklist.**
   - U1/U2/U3 pin 4 (VDD): one 0.1 µF each within 2 mm, with its GND via at the capacitor pad (no pin-cap via, no long ground trace).
   - Pin 11 (VSS): a direct via to L2.
   - One ≥ 1 µF bulk within 100 mm can be shared with the AD8237 10 µF bulk; both datasheets allow sharing.
   - Check autorouted segments for vias inserted between pin and capacitor.
2. **Summing-node capacitance is irrelevant here, so do not cut L2 (derived).**
   - Servo: feedback factor β ≈ Cservo/(Cservo + Cp) ≈ 1 for any pF-scale Cp.
   - Gain stage: CH = 3.9 nF ≫ Cp.
   - The MCP6404 is a 1 MHz part, not the "high-speed op amp" case of AD 39-09. Keep L2 continuous under U1–U3.
3. **Leakage is not critical, so guard rings are optional (derived).**
   - A 3 V neighbour through 10¹² Ω gives 3 pA:
     - × 2 MΩ (servo) = 6 µV at INA_OUT;
     - × 50 kΩ (VDiv Thevenin) = 0.15 µV.
   - Worst-case IB 100 pA × 2 MΩ = 200 µV DC at INA_OUT, and the second stage is AC-coupled (≈19 Hz). All negligible.
   - If guards are used anyway, follow §4.6:
     - inverting servo and gain stages: guard = VREF_A (their IN+);
     - VREF followers U1C/U1D: guard = their IN− (= output).
   - For a wearable, humidity/sweat contamination can lower surface resistance by orders of magnitude. Cleanliness/coating is the relevant control; see Gaps.
4. **Ground pour next to high-impedance nodes is acceptable.** No reviewed Microchip, TI or ADI source forbids it for low-speed precision nodes. The only warning (AD 39-09) is about high-speed phase margin, which is N/A. Pour at 0 V beside a 1.5 V node leaks about 1.5 pA (derived), which is negligible.
5. **Keep summing nodes physically short.**
   - The Rservo_n and Cservo_n pads on NetCservo_n_1 should sit at the op-amp IN− pin. Any long run should be on Rservo's INA_OUT end, which is low impedance.
   - The same applies to RGN/RG/CH at each gain-stage IN−.
   - MCP6404 inputs have no specified on-chip RFI filter. Compact input loops reduce Wi-Fi rectification (AN-671 mechanism).
6. **Isolation resistors.**
   - U1D drives five flexes/DEBs. Each R_VREFn (68 Ω) is that branch's RISO. The fan-out copper before the resistors, from U1 pin 14, must stay small (sum ≪ 100 pF). Put the long trace and flex capacitance beyond each resistor.
   - Each gain stage drives 330 Ω + 10 nF. Above the CH corner (≈506 Hz) the noise gain tends to 1, so the most sensitive G = +1 case of §4.3 applies. Whether 330 Ω is enough RISO for 10 nF must be read from Fig. 4-5 or simulated (not verified here).
7. **Do not add capacitance to VREF_A.** U1C drives VREF_A directly with no RISO. A layout-time "decoupling" capacitor or large pour tied to VREF_A (>100 pF) risks instability per §4.3.
8. **[N/A] MCP6401 guidance applies only to the experimental DRL population.** With it not fitted:
   - DRL_SUM, DRL_OUT and DRL_LIMIT_* are floating copper. Keep them short and away from INA input nets (general practice, no source).
   - Keep the 15 tap stubs from Va/Vb/Vc to the 1 MΩ pads short, and similar on each channel.
   - Keep the J_REF DNP link pad on the J_REF net as a short stub.
   - If the DRL is ever populated:
     - DRL_SUM is an inverting 1 MΩ/1.5 MΩ node: §4.6 case 2 applies, with guard = VREF_B_SRC.
     - Fit 100 nF within 2 mm.
     - Loop stability depends on the output resistors plus cable capacitance. TI notes this pole "can be as small as 2 kHz" ([SBAA188 p.5][sbaa188]).
9. §4.5 (unused op-amps) is N/A: all 12 sections are used.

### Gaps
- The Fig. 4-5 RISO values are graphical and could not be extracted, so 330 Ω/10 nF and 68 Ω/flex loads are not verified against it.
- MCP6404 noise density and closed-loop output impedance vs frequency were not extracted.
- No manufacturer source gives surface resistance for humid or sweat-contaminated boards (10¹² Ω is Microchip's "low humidity" figure). The need for conformal coating was not researched.

## Q3. Primary-source biopotential/mixed-signal board guidance: single vs split ground, reference-distribution topology, separation from digital/switching/RF, return-path continuity

### Takeaway
The sources disagree on ground splitting:
- ADI MT-031 leans towards "start split" and ST AN2834 recommends separate planes joined at one star point.
- TI's biopotential ADC datasheets (ADS1298/ADS1299) say a split "is not necessary" and a single plane "avoids ground loops" if placement partitions analog/digital/power. ADI itself says "no single grounding method" always wins.

The project's single common GND is therefore defensible, but only with strict partitioning and an unbroken L2. No source gives a numeric analog-to-digital spacing. The guidance is qualitative: partition, never cross digital over analog, keep the return path continuous, interleave connector grounds, and do not trust an autorouter on mixed-signal boards.

### Cited Findings
**Ground strategy**
- [PRACTICE] TI ADS1298 datasheet:
  - "dedicate an entire PCB layer to a ground plane and route no other signal traces on this layer… When using vias to connect to the ground layer, use multiple vias in parallel".
  - "…separating the ground planes is not necessary when analog, digital and power supply components are properly placed. Proper placement of components partitions the analog, digital and power supply circuitry into different PCB regions to prevent digital return currents from coupling into sensitive analog circuitry. If ground plane separation is necessary, then make the connection at the ADC. Connecting individual ground planes at multiple locations creates ground loops, and is not recommended. A single ground plane for analog and digital avoids ground loops." — [ADS1298 SBAS459K (rev. Aug 2015), Layout Guidelines p.98, Fig. 108][ads1298]
- [PRACTICE] TI ADS1299 datasheet:
  - Separate analog parts ("ADCs, amplifiers, references, DACs, and analog MUXs") from digital ones ("microcontrollers, CPLDs, FPGAs, **RF transceivers**, USB transceivers, and **switching regulators**").
  - "Route digital lines away from analog lines."
  - "The ground plane can be split into an analog plane (AGND) and digital plane (DGND), but is not necessary."
  - "Fill void areas on signal layers with ground fill."
  - "Provide good ground return paths… If the ground plane is cut or has other traces that block the current from flowing right next to the signal trace, then the current must find another path… Sensitive signals are more susceptible to EMI interference." — [ADS1299 SBAS499C (rev. Jan 2017) §12.1 p.72, Fig. 79][ads1299]
- [PRACTICE] ADI MT-031:
  - "It is mandatory that at least one layer of the PC board be dedicated to ground plane!"
  - "It is difficult to predict whether the 'multi-point' (single ground plane) or the 'star' ground… will give best overall system performance… When in doubt, it is always better to start out with a split analog and digital ground plane".
  - "There is no single grounding method which will guarantee optimum performance 100% of the time!"
  - Amplifiers and references "are always referenced and decoupled to the analog ground plane". — [MT-031 Rev. A, 10/08 (old) pp.7, 14–15][mt031]
- [MFR] ST AN2834:
  - "It is recommended to use different planes for analog and digital grounds… The analog ground must be placed below the analog circuitry."
  - Connect analog and digital grounds "in a star network… at only one point".
  - "When using a switching-type power supply for the digital circuitry, it is recommended to use a separate linear supply for the analog circuit." — [AN2834 Rev 10 (Oct 2024) §4.2.13 pp.37–38][an2834]
- **[N/A] by project decision:** the split/star advice of MT-031 and AN2834 is not adopted (one common GND). The separate linear analog supply (3V0_ANA from an LDO) does match AN2834.
- [PRACTICE] MT-031 on stack-up and ground-plane checks:
  - A simple 4-layer board has "internal ground and power plane layers with the outer two layers used for interconnections". "Placing the power and ground planes adjacent… provides additional inter-plane capacitance."
  - Check there are "no isolated ground 'islands'" and no "'skinny' connections".
  - "…auto-routing board layout techniques will generally lead to a layout disaster on a mixed-signal board, so manual intervention is highly recommended." — [MT-031 p.4][mt031]
- [PRACTICE] ADI Analog Dialogue 39-09: "Best results will occur when the entire plane is unbroken. Resist the temptation to remove areas of the ground plane for routing other signals"; "Analog and digital circuitry, including grounds and ground planes, should be kept separate when possible." — [AD 39-09 p.4][ad3909]
- [PRACTICE] TI SZZA009 (Nov 1999, old): "Avoid buried traces in the ground plane. If you have to use them, put them in the +V plane"; "Breaking up the plane with a row of holes is much better than having a long slot." — [SZZA009 p.10][szza009]
- [PRACTICE] TI ADS8860: "at least four layers is recommended to keep all critical components on the top layer and interconnected to a solid (low inductance) analog ground plane at the subsequent inner layer… Avoid crossing digital lines with the analog signal path and keep the analog input signals and the reference input signals away from noise sources." — [ADS8860 SBAS569B (rev. Feb 2019) §12.1 p.38][ads8860]

**Separation / partitioning**
- [PRACTICE] "High level analog signals should be separated from low level analog signals, and both should be kept away from digital signals… The ground plane can act as a shield where sensitive signals cross." — [MT-031 p.15][mt031]
- [PRACTICE] TI ADS1298:
  - "Route digital circuit traces (such as clock signals) away from all analog pins… Keep digital signals as far as possible from the analog input signals".
  - Digital traces go "directly above the ground plane with minimal use of vias".
  - "route differential signals as pairs to minimize the loop area".
  - "make short, direct interconnections on analog input lines and avoid stray wiring capacitance… Leakage currents between the PCB traces can exceed the input bias current… if shielding is not implemented." — [ADS1298 p.98][ads1298]
- [MFR] ST AN2834:
  - "A digital track that crosses an analog input track on the PCB may affect the analog signal" (Fig. 18). — [AN2834 §3.2.11 p.18][an2834]
  - "Placing ground tracks alongside sensitive analog signals provides shielding on the PCB" (written for 2-layer boards). — [AN2834 §4.2.12 p.36][an2834]
- [PRACTICE] TI SBAA188: a Faraday shield over the ECG front end reduces power-line interference; the isolation capacitance between device ground and patient ground affects CMR. — [SBAA188 (July 2011, old) p.4][sbaa188]
- No reviewed source (ADS1298, ADS1299, ADS8860, AN2834, MT-031, AD 39-09, AD8237, MCP640x) gives a numeric trace-to-trace or zone separation distance. They do give decoupling distances (e.g., ADS8860: supply capacitor within 0.2 in, <5 nH; REF capacitor within 0.1 in, <2 nH [ADS8860 p.38][ads8860]).

**Reference distribution**
- [PRACTICE] MT-031 Fig. 1: digital return current sharing the analog return impedance "creates error voltages"; the remedy is separate return paths to one reference point ("star"/single-point). — [MT-031 pp.2–3][mt031]
- [PRACTICE] TI ADS1298: route the reference return and the supply separately, "ideally, as a star connection at the AVSS pin"; "If multiple ADCs are on the same PCB, use wide power-supply traces or dedicated power-supply planes to minimize the potential of crosstalk". — [ADS1298 p.98][ads1298]
- [PRACTICE] ADI MT-087: "The output of a buffered reference is the output of an op amp, and therefore the source impedance is a function of frequency… rises at 6 dB/octave… nominally about 10 Ω at a few hundred kHz"; Kelvin sensing is used "to ensure accurate voltages at the load". — [MT-087 Rev. 0, 10/08 (old) p.14][mt087]
- [MFR] Per-branch series resistance isolates capacitive loads (RISO). — [MCP640x §4.3 p.18][mcp]
- Project rule and facts:
  - Five **separate** 68 Ω branches (R_VREF1..5, ERA2AEB680X) run from VREF_B_SRC (U1 pin 14), one to each J_FPCn pin 8 (VREF_B_FPCn), never joined downstream.
  - The DEB reference input is the connector side of a 10 kΩ RC.
  - R_ref 100 kΩ from VREF_B_SRC is the body/J_REF path. — [BK13 contract][bk13c]; [pin audit][pinaudit]; [DRL basis][drl]

**Connector grounding**
- [PRACTICE] At a connector "all signal conductors must run in parallel—it is therefore imperative to separate them with ground pins (creating a faraday shield) to reduce coupling… perhaps 30-40% of all the pins… should be ground pins". — [MT-031 p.15][mt031]
- Project: BK13 DS pins 1, 3, 5, 7, 9, 10 are GND, interleaved with Va (2), Vb (4), Vc (6) and VREF_B (8). Power contact P1 (3 lands) is 3V0_ANA; P2 (3 lands) is GND. — [BK13 contract][bk13c]

### Inferences
1. **With one GND, placement is the isolation.**
   - The pulsed return currents of the Wi-Fi module and the switching converter must close near their sources, not under or through the AFE-to-MCU-ADC area.
   - Common-impedance drops between the VDiv/Cdiv reference ground and MCU VSSA reach VOUT at about 1× (input-referred about 1/205), so they are tolerable.
   - RF picked up and rectified at an amplifier input is input-referred directly and cannot be filtered afterwards (AN-671). Wi-Fi burst/beacon envelopes fall inside the 20–500 Hz EMG band. Distance and compact input loops are the main defence (derived).
2. **L2 continuity audit, most important in autorouted areas:**
   - no traces on L2 (ADS1298, AD 39-09);
   - no chains of via antipads forming slots under analog traces (SZZA009);
   - no islands or skinny necks (MT-031);
   - L4 GND pour stitched to L2 around the AFE, with no floating fragments (ADS1299 "ground fill"; MT-031 islands);
   - every analog trace on L1 has L2 directly beneath for its whole length, including the BK13 escapes and the ADC corridor.
3. **Layer use.**
   - Put analog-critical nets (Va/Vb/Vc, NetINA*, Vservo, VREF_A taps, summing nodes, VOUT) on L1 over L2.
   - Digital/SPI on L3 below the AFE is shielded from L1 by L2 ("ground plane… as a shield where sensitive signals cross"). Do not route analog-critical nets on L3, where they sit next to power shapes and above a partial L4 pour (derived).
4. **VREF_B topology.**
   - Star from U1 pin 14 to each R_VREFn, then one private trace to each J_FPCn pin 8.
   - No pour, via, test point or shared copper between branches downstream of the resistors. Verify by connectivity that VREF_B_FPC1..5 are five distinct nets after autorouting.
   - Keep R_VREFn placement consistent: at the U1 end (minimal shared fan-out) or at the connector end (then five pre-resistor traces load U1D, still ≪ 100 pF).
   - For VREF_A, use the per-channel tap pairing (RL_n + servo IN+) from Q1, inference 2. A chain of taps between channels is acceptable because differences between channels only reach VOUT at about 1× (derived).
5. **Connector grounds.** Give the six GND signal contacts and the three P2 lands short, individual connections into L2 (multiple vias, not one shared via), per ADS1298 "multiple vias in parallel" and MT-031 "ground pins… directly to the ground plane".
6. **Numeric spacing is not manufacturer-sourced.** Any rule the team uses (e.g., "3W" or ≥ x mm from digital/switch node/antenna) must be documented as internal practice, not attributed to these manufacturers.

### Gaps
- No manufacturer numeric keep-out between AFE copper and the switch node, the Wi-Fi antenna/module or digital buses was found in AFE sources. The module and converter datasheets (other researchers' scope) may have one.
- No EMG-specific primary layout guidance was found. The TI ADS129x guidance targets ECG/EEG.
- The ADI EVAL-AD8237 and TI ADS1299EEG-FE board layouts were not reviewed.

## Q4. ADC-input RC (330 Ω + 10 nF): placement and routing of VOUT_n to the STM32U575 ADC pins

### Takeaway
Put the 10 nF C0G **at the STM32 ADC pin**, with its ground via at the capacitor pad. It is the charge reservoir for the 5 pF internal sample-and-hold. The 330 Ω is the op-amp's isolation resistor. It works electrically at either end of the VOUT run, but the run must stay on L1 over unbroken L2 and never cross or parallel digital tracks.
- ST supplies the physics (external capacitor "to the input pin", RAIN limits quoted "without external capacitor", PCB parasitic capacitance) but no explicit placement sentence.
- TI's SAR-ADC datasheet states the RC "is placed immediately next to the input pins".

### Cited Findings
- Project parts:
  - R_ADC1..5 = 0402WGF3300TCE (330 Ω, 0402).
  - C_ADC1..5 = GRM1555C1E103JE01D (10 nF, C0G, 25 V, 5 %, 0402).
  - VOUT_n are MCP6404 gain-stage outputs (U1.1, U2.1, U2.8, U3.1, U3.8). — [BOM][bom]; [pin audit][pinaudit]
- [HARD] STM32U575 14-bit ADC1 (Table 103):
  - RAIN max = 1000 Ω at 14-bit and 12-bit (Tj = 130 °C), 4.7 kΩ at 10-bit, 22 kΩ at 8-bit.
  - CADC (internal sample-and-hold) = 5 pF typ.
  - Table 104 (max RAIN vs sampling time), note 3: "Values without external capacitor".
  - 12-bit ADC4: RAIN max 2.2 kΩ (12-bit), CADC 5 pF. — [DS13737 Rev 10 (Jul 2024) pp.240, 242–243, 246][ds13737]
- [MFR] DS13737 Fig. 40, note 2: "Cparasitic represents the capacitance of the PCB (dependent on soldering and PCB layout quality) plus the pad capacitance… A high Cparasitic value downgrades the conversion accuracy. To remedy this, fADC must be reduced." General PCB guideline: "The 100 nF capacitor must be ceramic (good quality) and must be placed as close as possible to the chip." — [DS13737 p.245][ds13737]
- [MFR] AN2834 §4.2.8: the analog signal period must be ≥ 10 × RAIN × (CAIN + Cp). Example: 25 kΩ, 7 pF and 3 pF give ≤ 400 kHz. — [AN2834 p.34][an2834]
- [MFR] AN2834, "Workaround for extra high impedance sources":
  - "The hardware change consists in adding a large external capacitor (Cext) to the input pin." Size it so the Csh charge moves the voltage by < 0.5 LSB (example: Csh 16 pF gives Cext = 150 nF at 12-bit).
  - Repeated fast conversions can charge Cext cumulatively (Fig. 41).
  - Include pin and "PCB path capacitance" in parallel with Cext. — [AN2834 pp.43–45][an2834]
- [MFR] AN2834:
  - A digital track crossing an analog input track (§3.2.11, Fig. 18).
  - Negative injection current: the effect "is greater if a digital input is close to the analog input being converted" (§4.2.10).
  - Reference decoupling capacitors "located very close to pins".
  - "a 0.1 µF and a 1 to 10 µF capacitor must be placed close to the power source". — [AN2834 pp.16, 18, 20, 22, 35][an2834]
- [MFR] STM32U5 supply schemes: VDDA 100 nF + 1 µF; VREF+ 100 nF + 1 µF. — [AN5373 Rev 7 (Nov 2023) §2, figures pp.14–17][an5373]
- [PRACTICE] TI ADS8860:
  - "The fly-wheel RC filters are placed **immediately next to the input pins**. Among ceramic surface-mount capacitors, COG (NPO) ceramic capacitors provide the best capacitance precision."
  - "Avoid placing vias between the supply pin and its decoupling capacitor".
  - "Avoid crossing digital lines with the analog signal path". — [ADS8860 SBAS569B §12.1 p.38][ads8860]
- [PRACTICE] ADI Analog Dialogue 46-12 (Walsh, Dec 2012; content obtained through a page summarizer):
  - If the series resistor is too small, "the amplifier phase margin will be degraded, potentially causing the amplifier output to ring or become unstable".
  - Use NP0 capacitors for low voltage coefficient; "1 nF to 3 nF" suits that SAR example.
  - The article gives no physical placement guidance. — [AD 46-12][ad4612]
- [MFR] Capacitive loads above ~100 pF at G = +1 need a series RISO. — [MCP640x §4.3 p.18][mcp]

### Inferences
1. **Placement rule.**
   - C_ADC_n pad directly at the MCU ADC pin (≈ 1–2 mm trace), with its GND via at the capacitor pad into L2 near the MCU's VSSA/VREF− region.
   - R_ADC_n in series before it. At the MCU end, the long VOUT run is the op-amp-driven low-impedance side (preferred). At the op-amp end, the long run is the RC node, which is also low impedance at HF.
   - Stability does not depend on R position: the trace capacitance ahead of R (a few pF) is ≪ 100 pF. "C at the pin" is the rule that matters (ADS8860 statement; AN2834 Cext physics) (derived).
2. **Kickback is small (derived).**
   - 5 pF/10 nF gives a charge-sharing step of at most ≈0.05 % of the voltage difference between consecutively sampled channels. That is ≈8 LSB at 14-bit only for a full-scale jump.
   - It recovers with τ = 330 Ω × 10 nF = 3.3 µs.
   - All VOUT_n idle near VREF_A (~1.5 V), so real steps are small.
   - The cumulative charging of AN2834 Fig. 41 does not occur, because R_ADC keeps re-driving C_ADC.
3. **Bandwidth is fine (derived).** The AN2834 rule gives a maximum source frequency of 1/(10 × 330 Ω × 10 nF) ≈ 30 kHz, and the RC corner is ≈ 48 kHz. Both are far above the ≈ 506 Hz (CH) EMG band edge.
4. **MCU side.**
   - VDDA and VREF+ each get 100 nF + 1 µF at the pins, with no via between pin and capacitor.
   - Where pin assignment allows, avoid ADC channels next to fast-toggling I/O (AN2834 §3.2.11).
   - No digital trace should cross VOUT_n on L1 or L4. A crossing on L3 is shielded by L2.
5. **VOUT neighbours.** VOUT traces may run parallel to one another: they are low-impedance sources and the in-band mutual coupling is negligible. They must not run parallel to SPI, SWD, clock, switch-node or RF-feed copper. AN2834's ground guard tracks are optional on this 4-layer board with solid L2.
6. **Injection risk is low (derived; depends on the final rails).** The op-amp runs from the 3.0 V AFE rail, so VOUT cannot go below 0 V or above the (3.3 V) MCU VDDA.

### Gaps
- No ST document with an explicit "place the input capacitor next to the ADC pin" sentence was found. The rule rests on TI ADS8860 plus the charge-reservoir reasoning.
- The ADC instance (ADC1 14-bit vs ADC4 12-bit), sampling time and scan order are firmware choices and were not reviewed.
- MCP6404 stability with 330 Ω/10 nF (Fig. 4-5) was not verified.

## Q5. Hirose BK13C06-10DS/2-0.35V(895): land pattern, insulation area/keep-out, traces/vias under the connector, fine-pitch escape, board-edge placement, mechanical/solder constraints

### Takeaway
Hirose drawing **EDC3-633002-95** (released 5 Oct 2020, no revisions) fixes the lands:
- signal pads 0.18 mm wide at 0.35 mm pitch;
- power pads 0.75 mm wide;
- 0.215 × 1.04 mm end tabs;
- 4.245 mm overall.

It cross-hatches the whole region between the pad rows as an **"INSULATION AREA"**. Hirose's sister-series guideline says routing in such an area must be under solder resist, and that patterns under the connector can lift it. The safe routing rule is: escape every pad outward, no vias and preferably no traces inside the insulation rectangle, L2 intact underneath. Hirose gives no board-edge distance. The connector has no polarity.

### Cited Findings
- Parts: J_FPC1..5 = BK13C06-10DS/2-0.35V(895), HRS No. CL0480-0720-0-95, 1,000 pcs/reel. — [BOM][bom]; [BK13 catalog p.8][bk13cat]
- Drawing identity: EDC3-633002-95 (Hirose Korea). Drawn, checked, approved and released 2020-10-05; revision block empty; 3 sheets (sheet 3 is packaging only). — [BK13C06-10DS drawing, sheets 1–3][bk13dwg]
- [HARD] "Recommended PCB layout" (sheet 2, all mm):
  - overall 4.245 ± 0.02; signal pitch 0.35 ± 0.02; signal pad-centre span 1.4 ± 0.02; signal pad width 0.18 ± 0.02;
  - pad-row outer extent 2.1 (+0.05/0); signal-row inner gap 1.45 (0/−0.05);
  - power pad width 0.75 ± 0.02; gap between the left and right power pads 2.12 ± 0.02; power-pad inner gap 1.63 (0/−0.05);
  - end-tab width 0.215 ± 0.02; end-tab length 1.04 (+0.05/0);
  - a cross-hatched "**INSULATION AREA**" between the pad rows.
  - Note 5: "Please contact us in case you will make different settings from our recommendation."
  - Metal mask: same outline, **80 µm** thick. — [drawing sheet 2][bk13dwg]
- Catalog DS layout table (10DS): B = 1.40, D = 4.245, E = 2.12. — [BK13 catalog p.9][bk13cat]
- [HARD] Solder process:
  - N₂ reflow; peak ≤ 250 °C; > 220 °C for ≤ 60 s; preheat 150–180 °C for 90–120 s; ≤ 2 reflow cycles; O₂ ≥ 1000 ppm when using N₂.
  - Manual soldering 340 ± 10 °C, ≤ 3 s; "do not apply flux which will cause solder wicking".
  - Mask 0.08 mm with 100 % aperture. Cleaning "Not recommended".
  - "PCB Warpage: A maximum of 0.02mm at the center of the connector with reference to both ends of the connector." — [drawing sheet 2 note 4][bk13dwg]; [catalog p.13][bk13cat]
- Body (sheet 1): 3.98 ± 0.1 mm (4 ± 0.3) × 1.9 ± 0.1 mm; receptacle height 0.55 ± 0.1; mated height 0.6 ± 0.1; lead coplanarity ≤ 0.08; pick-and-place area 0.41. — [drawing sheet 1][bk13dwg]
- Catalog notes: "BK13C06-6DS/2-0.35V and BK13C06-10DS/2-0.35V have a **metal reinforcement in the center** of the product"; "This connector has **no polarity**." — [catalog pp.6–9][bk13cat]
- Ratings (BK13C):
  - Signal 0.3 A, power 5 A (total signal 12 A); 50 V AC/DC.
  - Contact resistance ≤ 50 mΩ signal / ≤ 15 mΩ power.
  - Insulation resistance ≥ 50 MΩ at 100 V DC; 150 V AC for 1 min; −55 to +85 °C.
  - Three solder points per power contact, "significantly improving PCB peeling strength". — [catalog pp.1–4][bk13cat]
- Mechanical:
  - "Avoid supporting the PCB only with the connectors."
  - "Secure the mated connectors to the board with housings and cushioning materials."
  - FPC stiffener: glass epoxy ≥ 0.3 mm or stainless steel ≥ 0.2 mm.
  - Unmate perpendicular to the board, or diagonally along the pitch direction, never towards the width direction. — [catalog pp.13–15][bk13cat]
- [ANALOG] Hirose BM28 Series Guideline ETAD-H1016-00 (hybrid board-to-FPC, 0.35 mm pitch, 0.6 mm stack, 5 A power; approved 2021-03-31):
  - §1.2.1: "For the routing on the indicated PCB surface, apply solder resist in order for the insulation treatment."
  - §1.2.3: "If there is not enough clearance on the inner side of PWB pattern, there is a possibility that the connector is pushed up by solder paste. In case those patterns are designed under a connector, there is a possibility to cause solder failure if there are physical height… please conduct mounting test".
  - §1.1.1: put buffer material between the connector and the cover case.
  - §1.1.3: "Please do not locate any material which may affect on connector mating around the connectors."
  - §1.1.4: mark the mating position on the PWB, along the FPC outline. — [BM28 guideline pp.3–7][bm28]
- [ANALOG] Hirose DF40 Series Guideline ETAD-H1015-00: "Although standoff is provided, interference to the connector body by pattern, via hole and solder resist beneath the connector may cause solder defects and poor fillet formation"; "Keep connector warpage within 0.02 mm". — [DF40 guideline pp.6, 8][df40]
- Project facts:
  - Native DS signal pads at X = −0.700…+0.700 mm, Y = ±0.8875 mm.
  - P1 (3V0_ANA) and P2 (GND) each have three lands.
  - Mandatory SIG1 / "POWER P1 — 3V0_ANA" marks; reversal protection must be mechanical. — [BK13 contract][bk13c]
- The project's archive index already reads the insulation area as "insulated surface beneath exposed connector metal", which "does not require splitting system GND". — [source index][idx]

### Inferences
1. **Land coordinates derived from sheet 2** (origin at the footprint centre, X along the long axis):
   - signal pads 0.18 × 0.325 mm at X = 0, ±0.35, ±0.70; Y = ±0.8875;
   - power pads 0.75 × 0.235 mm at X = ±1.435, Y = ±0.9325;
   - end tabs 0.215 × 1.04 mm at X = ±2.015, Y = 0;
   - insulation rectangle ≈ 3.815 × 1.63 mm, bounded by the end-tab inner edges and the power-pad inner edges; the signal pads intrude 0.09 mm into it.
   - The project's DS signal-pad centres (±0.8875) match. Check the native HIROSE_BK13C06-10DS/2-0.35V(895) power-pad and end-tab positions and all pad sizes against these numbers (derived).
2. **Escape.** The copper gap between adjacent signal pads is 0.35 − 0.18 = 0.17 mm, so no trace can pass between pads at normal fab rules.
   - Escape each signal pad straight outward, away from the centreline, on L1.
   - Place vias outside the body outline: the body reaches ±0.95 mm and the pads ±1.05 mm in Y.
   - No via-in-pad on 0.18 mm pads.
   - Route Va/Vb/Vc/VREF_B away as a group over L2 (derived).
3. **Insulation area.**
   - No exposed copper: no vias (tented vias still add height, per the DF40/BM28 cautions), no test points, no bare pads.
   - If a trace must pass under the body, it must be fully solder-mask covered (BM28 §1.2.1) and the assembly mounting-tested (BM28 §1.2.3). Preferably route nothing there: the centre metal reinforcement sits above it.
   - The requirement concerns the surface only. L2 stays continuous beneath (consistent with the project index) (derived).
4. **Contacts.**
   - Connect GND contacts 1, 3, 5, 7, 9, 10 individually to L2 (MT-031 ground-pin guidance).
   - Connect all three P2 lands to L2 with multiple vias.
   - Give the P1 lands (3V0_ANA) a short, wide connection.
   - Do not let pads on different nets share one via or a copper neck inside the insulation rectangle.
5. **Edge and mechanics.** Hirose gives no edge distance for BK13 (derived conclusions):
   - Keep the mated-FPC swing and cover-buffer zone free of tall parts (BM28 §1.1.3, analogous).
   - Place near board support/stiffening so the 0.02 mm warpage limit holds.
   - Do not rely on the connectors for retention.
   - Keep silkscreen SIG1 and power-side marks visible after mating (project contract; BM28 §1.1.4).
6. **No polarity.** Routing of P1/P2 and signal nets must follow the contract's DS↔DP mapping exactly; a 180° flip swaps 3V0_ANA and GND (project contract).

### Gaps
- No BK13-specific Hirose design guideline (ETAD) was found. The meaning of the "INSULATION AREA" and the rules for patterns under the connector are inferred from the BM28 (closest sister series) and DF40 guidelines.
- BK13 has no stated board-edge distance, mated-FPC keep-out envelope or bend-radius guidance in the drawing or catalog.
- It is not stated whether the centre metal reinforcement or the housing metal is electrically connected to any contact. That affects coupling to copper beneath it.
- No revision or date field was established for the BK13 catalog. The drawing is dated 2020-10-05 with no listed revisions.

[ad8237]: https://www.analog.com/media/en/technical-documentation/data-sheets/ad8237.pdf "Analog Devices AD8237 data sheet, Rev. 0 (08/2012), D10289-0-8/12(0); current as of 24 Sep 2026"
[mcp]: https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP6401-Data-Sheet-DS20002229.pdf "Microchip MCP6401/1R/1U/2/4/6/7/9 data sheet DS20002229E (Rev. E, March 2023)"
[inamp]: https://www.analog.com/media/en/training-seminars/design-handbooks/designers-guide-instrument-amps-complete.pdf "ADI, A Designer's Guide to Instrumentation Amplifiers, 3rd ed., Kitchin & Counts, 2006"
[an671]: https://www.analog.com/media/en/technical-documentation/application-notes/AN-671.pdf "ADI AN-671 Reducing RFI Rectification Errors in In-Amp Circuits, Rev. 0, 08/2003"
[mt031]: https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf "ADI MT-031 Grounding Data Converters and Solving the Mystery of AGND and DGND, Rev. A, 10/08"
[mt101]: https://www.analog.com/media/en/training-seminars/tutorials/MT-101.pdf "ADI MT-101 Decoupling Techniques, Rev. 0, 03/09"
[mt087]: https://www.analog.com/media/en/training-seminars/tutorials/MT-087.pdf "ADI MT-087 Voltage References, Rev. 0, 10/08"
[ad3909]: https://www.analog.com/media/en/analog-dialogue/volume-39/number-3/articles/high-speed-printed-circuit-board-layout.pdf "Ardizzoni, A Practical Guide to High-Speed PCB Layout, Analog Dialogue 39-09, Sept 2005"
[ad4612]: https://www.analog.com/en/resources/analog-dialogue/articles/front-end-amp-and-rc-filter-design.html "Walsh, Front-End Amplifier and RC Filter Design for a Precision SAR ADC, Analog Dialogue 46-12, Dec 2012"
[ads1299]: https://www.ti.com/lit/ds/symlink/ads1299.pdf "TI ADS1299 data sheet SBAS499C (Jul 2012, rev. Jan 2017), §12.1 p.72"
[ads1298]: https://www.ti.com/lit/ds/symlink/ads1298.pdf "TI ADS129x data sheet SBAS459K (Jan 2010, rev. Aug 2015), Layout Guidelines p.98"
[sbaa188]: https://www.ti.com/lit/an/sbaa188/sbaa188.pdf "TI SBAA188 Improving Common-Mode Rejection Using the Right-Leg Drive Amplifier, July 2011"
[szza009]: https://www.ti.com/lit/an/szza009/szza009.pdf "TI SZZA009 PCB Design Guidelines for Reduced EMI, Nov 1999"
[ads8860]: https://www.ti.com/lit/ds/symlink/ads8860.pdf "TI ADS8860 data sheet SBAS569B (May 2013, rev. Feb 2019), §12.1 p.38"
[an2834]: https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf "ST AN2834 How to optimize the ADC accuracy in the STM32 MCUs, Rev 10, Oct 2024"
[ds13737]: https://www.st.com/resource/en/datasheet/stm32u575ag.pdf "ST STM32U575xx datasheet DS13737 Rev 10, July 2024"
[an5373]: https://www.st.com/resource/en/application_note/an5373-getting-started-with-stm32u5-mcu-hardware-development-stmicroelectronics.pdf "ST AN5373 Getting started with STM32U5 MCU hardware development, Rev 7, Nov 2023"
[bk13dwg]: https://www.hirose.com/en/product/document?clcode=CL0480-0720-0-95&documentid=BK13C06-10DS2-0.35V%28895%29_4800720095_2D_ENG&documenttype=2DDrawing&lang=en&productname=BK13C06-10DS%2F2-0.35V%28895%29&series=BK13C "Hirose BK13C06-10DS/2-0.35V(895) drawing EDC3-633002-95, released 2020-10-05 (archived Hirose_BK13_DS.pdf, pages rendered p1-p3)"
[bk13cat]: https://www.hirose.com/en/product/document?clcode=CL0480-0720-0-95&documentid=en_BK13C_CAT&documenttype=Catalog&lang=en&productname=BK13C06-10DS%2F2-0.35V%28895%29&series=BK13C "Hirose BK13 series catalog (revision field not established)"
[bm28]: https://www.hirose.com/en/product/document?clcode=CL0673-5048-0-51&productname=BM28B0.6-6DS%2F2-0.35V%2851%29&series=BM28&documenttype=Guideline&lang=en&documentid=0001442212 "Hirose BM28 Series Guideline ETAD-H1016-00 (approved 2021-03-31)"
[df40]: https://www.hirose.com/en/product/document?clcode=CL0684-4032-1-51&productname=DF40C-100DP-0.4V%2851%29&series=DF40&documenttype=Guideline&lang=en&documentid=0001442210 "Hirose DF40 Series Guideline ETAD-H1015-00"
[bom]: file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/ASSEMBLY_SNAPSHOT_20260924T023521434Z/MAIN_BOARD_COMPLETE_ASSEMBLY_BOM.csv "Project BOM snapshot 2026-09-24"
[pinaudit]: file:///C:/Users/PMLS/Desktop/emg-saw/hardware/review_2026-09-16/analog_pin_audit.md "Project compiled analog pin audit, 16 Sep 2026"
[drl]: file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/work/design_basis/DRL_OPTION_DESIGN_BASIS.md "Project DRL option design basis, 2026-09-23"
[bk13c]: file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/BK13_ASSEMBLY_CONTRACT_SOURCE.md "Project BK13 flex assembly contract, 2026-09-12"
[idx]: file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/sources/analog_power/SOURCE_READING_INDEX.md "Project official-source reading index (archive + SHA-256), fetched 16 Sep 2026"
