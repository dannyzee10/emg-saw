# Fabrication & stack-up limits for the 4-layer JLCPCB EMG main board (80 × 45 mm, FR-4, ENIG, through vias)

Scope: JLCPCB 4-layer fabrication/assembly limits, the exact stack-up, 50 Ω geometry, and copper/via current capacity, each compared with the project's exported rules. All web sources were accessed 2026-09-24. JLC capability pages show only "© 2026" and no revision number. Project files were read only: [RULES.txt](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/NATIVE_FINAL_20260924T015854610Z/RULES.txt), [STACK.txt](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/NATIVE_FINAL_20260924T015854610Z/STACK.txt), [layout brief](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md). The impedance and current numbers in the "Inferences" sections are my own calculations. Their methods and assumptions are stated there, and they are not JLC calculator output.

## Q1 — JLCPCB published 4-layer capabilities vs the project's rules

### Takeaway
Every routing dimension the project uses is within JLC's published 4-layer capability, most with large margin: 0.15 mm tracks vs a 0.09 mm minimum, 0.20 mm clearance vs 0.09 mm, and 0.6/0.3 vias with a 0.15 mm ring and no surcharge. Five exported rule values need attention:
- The edge rule is 0.254 mm, not the intended 0.50 mm. That passes a routed edge but fails a V-cut edge (0.4 mm).
- The solder-mask sliver rule (0.10 mm) is exactly at JLC's limit for green mask and fails for black/white.
- The in-footprint 0.10–0.125 mm pad-to-pad exceptions are below JLC's stated "SMD pad to pad 0.15 mm". They are still above the 0.09 mm spacing limit.
- The −0.35 mm via-tenting rule described in the brief does not appear in the export.
- The 0.45/0.2 mm via sits exactly on JLC's surcharge threshold.

### Cited Findings
**Tracks/spacing**
- Minimum track/spacing, multilayer, 1 oz: "0.09 / 0.09 mm (3.5 / 3.5 mil). 3 mil is acceptable in BGA fan-outs". For 1–2 layers it is 0.10/0.10 mm. With 2 oz copper it is 0.15/0.15 mm (multilayer) and 0.16/0.16 mm (2-layer). Track width tolerance is ±20%. — [JLCPCB, "PCB Manufacturing & Assembly Capabilities"](https://jlcpcb.com/capabilities/pcb-capabilities)
- The page gives no separate trace/space figure for **inner 0.5 oz** copper in the extracted text; the multilayer 0.09/0.09 mm row is the applicable limit. Finished copper options are outer 1 oz/2 oz and inner 0.5 oz (default)/1 oz/2 oz. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)

**Vias and holes**
- Minimum via: "0.15 mm hole size / 0.25 mm via diameter" (multilayer). Cost rule: "0.15mm hole size with any size via diameter, and 0.2mm or 0.25mm hole size with via diameter less than 0.45mm, will cost more." The page also gives a recommended minimum via hole of 0.2 mm. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- Via annular ring: "Via diameter should be 0.1mm (0.15mm preferred) larger than Via hole size", i.e. a ring of 0.05 mm minimum and 0.075 mm preferred. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities). This matches the POFV rule "0.05 mm minimum, 0.075 mm preferred" in [JLCPCB news, "Free Via-in-Pad on 6-20 Layer PCBs with POFV" (2022-11-02)](https://jlcpcb.com/news/free-via-in-pad-6-20-layer-pcbs-pofv).
- Via hole-to-hole spacing is 0.2 mm; pad (PTH) hole-to-hole spacing is 0.45 mm. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- Via **hole** to track is 0.2 mm. Inner-layer via hole to copper is 0.2 mm. Inner-layer PTH hole to copper is 0.3 mm. PTH to track is 0.28 mm (0.35 mm recommended). NPTH to track is 0.2 mm. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- PTH annular ring (1 oz multilayer) is "≧0.20mm" recommended with an absolute minimum of 0.15 mm; 2 oz needs 0.254 mm or more. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- Drill: range 0.15–6.3 mm (multilayer); through-hole tolerance +0.13/−0.08 mm; hole position ±0.05 mm; "Average Hole Plating Thickness: 18μm". — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)

**Pads**
- Pad-to-track is minimum 0.1 mm ("stay well above if possible"). SMD pad-to-pad (different nets) is 0.15 mm. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- BGA: minimum pad 0.2 mm (the extraction says this requires ENIG). BGA pad to trace is ≥0.1 mm (0.09 mm minimum on multilayer). — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)

**Solder mask and via covering**
- Solder-mask bridge (dam), 1 oz: minimum 0.10 mm for green/red/yellow/blue/purple and 0.13 mm for black/white; 2 oz needs 0.20 mm. The page lists solder-mask expansion as "1:1" and says to keep "at least 0.09 mm" mask clearance from traces (exact meaning ambiguous in the extraction). — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- Via covering options on the capabilities page are soldermask-filled (plugged), "Epoxy Filled & Capped" and "Copper paste Filled&Capped". Epoxy/paste filling is "compatible with via diameters from 0.15 to 0.55 mm". Filled vias need "≥ 0.35 mm clearance from other soldermask openings". Epoxy-filled & capped "is the default for 6-layer and above". — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- Via-covering article (last updated 2026-09-09):
  - Plugged/filled via holes "should not be larger than 0.5 mm".
  - Tented vias should ideally be "0.4 mm or less and no larger than 0.5 mm"; "No complaints are accepted for this problem."
  - "Vias with a distance less than 0.35mm from the pad cannot be plugged with ink. Such vias can be plugged with epoxy or copper"; the same applies to holes in pads.
  - Which vias to plug can be specified by note, image, or "which via diameters should be plugged".
  — [JLCPCB help, "Via Covering: Tented, Untented, Plugged, Epoxy-Filled and Copper-epoxy-filled"](https://jlcpcb.com/help/article/pcb-via-covering)
- POFV is free and default on 6–20 layers; "POFV for 4-layer PCBs still requires charges"; POFV via hole range is 0.2–0.5 mm; POFV vias should be "placed more than 0.45 mm from regular PTHs or NPTHs". — [JLCPCB news (2022-11-02)](https://jlcpcb.com/news/free-via-in-pad-6-20-layer-pcbs-pofv)

**Board edge and outline**
- Copper to routed board edge is "≧0.2 mm"; copper to V-cut edge is "≧0.4 mm". Routed-edge tolerance is ±0.2 mm (regular) or ±0.1 mm (high precision); V-cut tolerance is ±0.4 mm. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- Board thickness range is 0.4–4.5 mm (standard values include 1.2 mm). Tolerance is ±10% for boards ≥1.0 mm. The 4-layer maximum size is 663 × 593 mm. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- Castellated holes need ≥0.5 mm diameter and ≥1 mm to the edge. Silkscreen needs line width ≥0.15 mm, text height ≥1.0 mm, and 0.15 mm pad-to-silk. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)

**Impedance control and materials**
- Impedance tolerance is "±10%" as standard, with "±5%" available on request. Listed FR-4 Dk values: 7628 = 4.4, 3313 = 4.1, 2116 = 4.16 (2-layer: 4.5). — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)

**Project values (from the exports and brief)**
- Clearance rules:
  - `CLR_GENERAL_020` 0.20 mm; `CLR_POWER_025` and `CLR_ANALOG_025` 0.25 mm.
  - In-component pad–pad 0.10 mm for U_MCU1, UP1, UP2, UP4 and J_FPC1–5.
  - Pad–pad 0.125 mm for C_ADC1–5.
  - Local track–pad 0.15–0.20 mm and track–track 0.175 mm.
  - GND via to U_MCU1-31 pad 0.175 mm.
- Width rules: min 0.15 mm on all classes; preferred SPI 0.18 mm and POWER 0.9 mm (max 3 mm).
- Vias: `VIA_STD_060_030` pad 0.6/hole 0.3 (priority 1, All). The default `RoutingVias` 1.27/0.7112 is still present at priority 2.
- Board edge: `EDGE_050_GENERAL_PROVISIONAL` BOARD_EDGE_GAP = **0.254 mm**.
- Mask: `MinimumSolderMaskSliver` 0.1 mm; only one `SolderMaskExpansion` rule, **+0.05 mm, scope All**.
- Paste: `PasteMaskExpansion` 0.
- Other: `HoleToHoleClearance` is exported with no value. The default `Width` rule is 0.254/0.254/0.254 at priority 10 (All).
- Source: [RULES.txt](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/NATIVE_FINAL_20260924T015854610Z/RULES.txt)
- The brief sets starting targets: "copper-to-routed-edge setback at 0.50 mm", via 0.60/0.30 with 0.45/0.20 "only for justified dense escape and verified fabrication", and fine-pitch exceptions "around 0.10–0.125 mm only if supported by actual fabrication". — [layout brief §7](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)

**Values JLC lists differently between pages**
- POFV/filled-via hole range:
  - 0.15–0.55 mm on the [capabilities page](https://jlcpcb.com/capabilities/pcb-capabilities)
  - 0.2–0.5 mm in the [2022 POFV news](https://jlcpcb.com/news/free-via-in-pad-6-20-layer-pcbs-pofv)
  - "not larger than 0.5 mm" in the [via-covering article](https://jlcpcb.com/help/article/pcb-via-covering)
- Within the capabilities page, "SMD pad to pad 0.15 mm" sits alongside "pad to track 0.1 mm" and "min spacing 0.09 mm". JLC does not explain why pads are held to a larger gap than tracks. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)

### Inferences
Project rule vs JLC limit (my comparison of the values cited above):

| Item | Project value | JLC limit | Verdict |
|---|---|---|---|
| Min track | 0.15 mm | 0.09 mm | Project is looser (safe, 0.06 mm margin) |
| General / power-analog clearance | 0.20 / 0.25 mm | 0.09 mm | Looser (safe) |
| Local track–pad 0.15, track–track 0.175 | — | pad–track 0.10, spacing 0.09 | OK |
| In-footprint pad–pad 0.10 mm (MCU, UP1/2/4, FPC) and 0.125 mm (C_ADCx) | 0.10–0.125 mm | "SMD pad to pad 0.15 mm" | **Tighter than JLC's stated pad–pad value** (above 0.09 spacing). Acceptable only as manufacturer-footprint geometry; JLC PCBA lists 0.35 mm IC pitch, so such gaps are built routinely. Flag for DFM review. |
| Via 0.6/0.3 | ring 0.15 mm | ≥0.05 (0.075 preferred); surcharge only for 0.15 mm holes, or 0.2/0.25 mm holes with dia <0.45 | OK, no surcharge |
| Via 0.45/0.2 (exposed pads) | ring 0.125 mm | surcharge if 0.2 mm hole with dia **<0.45** | OK **exactly at threshold**. Do not shrink the pad below 0.45 mm. |
| Via hole–track | ≥0.35 mm hole–track (0.2 rule from 0.6 pad) | 0.2 mm from hole | OK |
| GND via to MCU pad 0.175 mm | hole–pad ≈0.325 mm | via hole–track 0.2 | OK for tented/open. **Not** ink-pluggable (<0.35 mm from pad); a filled via needs ≥0.35 mm to other mask openings |
| Hole-to-hole | not exported | 0.2 mm (vias), 0.45 mm (PTH pads) | **Verify the Altium value** |
| Copper to edge | **0.254 mm** (rule named "050"; brief intends 0.50) | routed ≥0.2, V-cut ≥0.4 | Passes a routed edge only. **Fails if the board is V-cut panelised** (likely for Standard PCBA, see Q5). Set to 0.50 mm as the brief intends. |
| Mask sliver | 0.10 mm | 0.10 green, 0.13 black/white | At the limit (green); fails for black/white mask |
| Mask expansion | +0.05 mm all | "1:1"; dam ≥0.10 | With +0.05 mm per side, pad gaps <0.20 mm leave a web <0.10 mm, which JLC will remove (ganged opening). That covers 0.10–0.15 mm pad gaps at fine pitch and the C_ADC pads. |
| Via tenting | "−0.35 mm expansion" per the task brief | tent holes ≤0.4 (≤0.5) mm, not guaranteed | Both 0.3 and 0.2 mm holes are tentable. **The rule is absent from RULES.txt**; confirm it exists or use via tenting properties. |
| Silk | silk–silk 0.254, silk–mask 0.254 | pad–silk 0.15, line ≥0.15, text ≥1.0 | OK (widths not exported) |
| Rule hygiene | default Width 0.254 min=max (priority 10); default RoutingVias 1.27/0.71 | — | Unclassed nets are forced to exactly 0.254 mm. Stale defaults should be cleaned up. |

- Inner-layer antipads: with 0.6 mm via pads kept on inner layers plus a 0.20–0.25 mm pour clearance, hole-to-copper is 0.35–0.40 mm, which clears JLC's 0.2 mm. If unused inner pads are removed and the pour clearance is measured from the hole, the 0.20 mm rule sits exactly at JLC's 0.2 mm minimum.
- The 0.10 mm in-component rules are only safe inside footprints whose copper came from the manufacturer's land pattern. They should never be allowed to apply to routed copper.

### Gaps
- ENIG Ni/Au thickness is not stated on the capabilities page.
- A separate inner-0.5 oz trace/space figure was not found. I assumed the multilayer 0.09/0.09 mm row applies.
- The exact meaning of "Soldermask expansion 1:1" and "keep at least 0.09 mm clearance" was not resolved from the extracted text.
- Whether JLC's order-form "Via Covering: Tented" option overrides the Gerber mask openings was not verified.
- Whether 4-layer impedance control itself carries a fee was not verified.
- The export does not include the Altium HoleToHole value, the silk-width values, or any via-tenting rule. These need to be read in Altium.

## Q2 — Which JLC 4-layer stack-up matches the Altium export

### Takeaway
The export matches **JLC04121H-3313** exactly: 1.2 mm nominal, outer 1 oz / inner 0.5 oz, pressed laminate 1.1642 mm, stack table below. JLC's live API still lists it (enabled, zero fee fields), but it is **not** JLC's default 1.2 mm 4-layer stack. The default is JLC04121H-7628, with 0.2104 mm prepreg and a 0.6 mm core, which would change every impedance on the board. The order must name JLC04121H-3313 explicitly. The Altium stack also carries a spurious 0.32 mm FR-4 dielectric below L4.

### Cited Findings
- Live JLC API response (queried 2026-09-24 with 4 layers, 1.2 mm, 1 oz outer, 0.5 oz inner) for **JLC04121H-3313**:
  - Layers: Top Cu 0.035 mm / prepreg "3313*1" 0.09940 mm / core "0.9mm H/HOZ with copper" = Cu 0.0152 + core 0.865 + Cu 0.0152 mm / prepreg "3313*1" 0.09940 mm / Bottom Cu 0.035 mm.
  - compressionThickness 1.1642 mm; enableFlag true; defaultFlag false; fixedFee 0; coefficient 0.
  - The default template (defaultFlag true) is **JLC04121H-7628**: Cu 0.035 / 7628 0.2104 / core 0.6 mm (Cu 0.0152 each side) / 7628 0.2104 / Cu 0.035, pressed 1.1212 mm.
  - Other enabled 1.2 mm templates: JLC04121H-1080 (1080 0.0764 mm, 0.865 core; non-zero fee fields 110/55), 1080A (non-zero fee fields 330/110), 1080B, 2116A, 2116B, 7628A (non-zero fee fields 330/110).
  — [JLC impedance-template API endpoint](https://cart.jlcpcb.com/api/overseas-shop-cart/v1/shoppingCart/getImpedanceTemplateSettings) (POST `{"cuprumThickness":1,"insideCuprumThickness":0.5,"stencilLayer":4,"stencilPly":1.2}`). I found the endpoint in [gsuberland/jlcpcb_autogenerated_stackups `generate_stackups.linq`](https://github.com/gsuberland/jlcpcb_autogenerated_stackups).
- A third-party archive of the same API (last updated 2025-05-09) has the identical JLC04121H-3313 table. Its normalised file assigns this core **Dk 4.43** from Nan Ya NP-155F datasheet data, not JLC data. — [gsuberland/jlcpcb_autogenerated_stackups](https://github.com/gsuberland/jlcpcb_autogenerated_stackups)
- JLC's stack-up page gives prepreg Dk 7628 = 4.4, 3313 = 4.1, 1080 = 3.91, 2116 = 4.16, and **core Dk 4.6**. Solder mask is 1.2 mil above substrate, 0.6 mil above trace, 1.2 mil between traces, Er 3.8. Copper options are outer 1/2 oz and inner 0.5/1/2 oz. The page defaults to the 1.6 mm JLC04161H family, which includes JLC04161H-3313. — [JLCPCB, "Controlled Impedance PCB Layer Stackup"](https://jlcpcb.com/impedance)
- JLC's impedance-calculator guide (last updated 2026-09-16) makes these modelling assumptions:
  - Nan Ya NP-155F material for 4–8 layers.
  - Copper thickness 1.6 mil for outer 1 oz, 0.6 mil for inner 0.5 oz, 1.2 mil for inner 1 oz.
  - Trapezoidal traces: "Trace top width – Trace base width – 0.7 mil".
  - Mask 1.2/0.6/1.2 mil, Er 3.8.
  — [JLCPCB help, "User Guide to the JLCPCB Impedance Calculator"](https://jlcpcb.com/help/article/User-Guide-to-the-JLCPCB-Impedance-Calculator)
- Finished-thickness tolerance is ±10% for boards ≥1.0 mm, i.e. 1.08–1.32 mm for 1.2 mm. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- The project export lists: L1 0.035 / JLC3313 prepreg 0.0994 Dk 4.1 / L2 GND 0.0152 / JLC core 0.865 Dk 4.6 / L3 "POWER SIGNAL" 0.0152 / JLC3313 prepreg 0.0994 Dk 4.1 / L4 BOTTOM GND 0.035. **Then an extra `DIELECTRIC|FR-4|MM=0.32004|DK=4.8` below L4.** — [STACK.txt](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/NATIVE_FINAL_20260924T015854610Z/STACK.txt)
- The brief requires recording "the actual selected JLCPCB or chosen fabricator stack and tolerances" and says "L3 signals must not depend on a fragmented L4 return". — [layout brief §5–6](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)

### Inferences
- The layer table is 0.035 + 0.0994 + 0.0152 + 0.865 + 0.0152 + 0.0994 + 0.035 = 1.1642 mm. This equals JLC's pressed thickness and the export's ≈1.16 mm. The nominal 1.2 mm finished board includes mask and plating.
- **Discrepancies:**
  - The extra 0.32 mm FR-4 layer under L4 does not exist in JLC04121H-3313. It makes Altium's stack about 1.48 mm, which distorts via length, 3D and drill reports. It has little effect on L1–L3 impedance. Remove it, or replace it with a solder-mask layer of about 0.015–0.03 mm at Er 3.8.
  - The export has no solder-mask layers, so Altium's impedance solver would report uncoated values, about 3 Ω high (see Q3).
  - Outer copper appears as 0.035 mm in JLC's stack table but 1.6 mil (0.0406 mm) in JLC's calculator. The effect on 50 Ω width is about 0.003 mm (Q3).
  - Core Dk is 4.6 on JLC's page but 4.43 in the third-party normalised data. The export's 4.6 matches JLC.
- Geometric consequence: L1 is 0.0994 mm above L2, which gives the tight L1–L2 coupling the brief asks for. **L3 is 0.0994 mm from L4 but 0.865 mm from L2, so L4 is L3's real reference.** Any L4 void, slot or split under an L3 signal breaks its impedance (Q3: about 112–119 Ω over a voided L4).
- The inner planes and L3 copper are 15.2 µm (half of outer). L3 power routing therefore has about 2.3× the sheet resistance of L1 (Q4).
- If an order leaves "Specified stackup" at the default, the fab builds JLC04121H-7628. A 0.161 mm L1 line becomes about 71.5 Ω and the 50 Ω width becomes about 0.357 mm (my field-solver results, Q3).

### Gaps
- JLC's API returns no per-layer Dk, so the core Dk (4.6 per JLC's page vs 4.43 NP-155F-derived) cannot be confirmed from the API.
- The currency/meaning of the fee fields (fixedFee/coefficient) is undocumented. "Zero fee" for 3313 is inferred from the field values.
- The JLC stack page's 1.2 mm view could not be rendered by the fetch tool (it showed the 1.6 mm family), so the stack was confirmed through the API.

## Q3 — 50 Ω single-ended geometry on JLC04121H-3313

### Takeaway
My 2D field-solver calculations with JLC's published parameters give these 50 Ω widths:
- **L1 microstrip over L2: ≈0.16 mm with solder mask** (0.161 mm with 35 µm copper, 0.158 mm with JLC's 1.6 mil), or 0.18 mm without mask.
- **L1 with coplanar GND pour: ≈0.145/0.153/0.156 mm at 0.15/0.20/0.25 mm gaps.**
- **L3 referenced to L4: ≈0.136 mm** (0.123–0.132 mm with a coplanar L3 GND pour).

The project's 0.18 mm SPI width gives ≈47 Ω on L1 (inside ±10%) but ≈43.5 Ω on L3 (13% low). On L3, use about 0.14 mm (49 Ω, needs a scoped exception to the 0.15 mm minimum) or 0.15 mm (47.7 Ω). Without impedance control, JLC's ±20% width tolerance alone spreads any 50 Ω design to about 42–60 Ω.

### Cited Findings
- JLC inputs used:
  - 3313 prepreg Dk 4.1 and 0.0994 mm; core Dk 4.6 and 0.865 mm; inner Cu 0.0152 mm; outer Cu 0.035 mm — [JLC stack page](https://jlcpcb.com/impedance) and the [JLC API](https://cart.jlcpcb.com/api/overseas-shop-cart/v1/shoppingCart/getImpedanceTemplateSettings)
  - Mask 1.2 mil over substrate and 0.6 mil over trace, Er 3.8; trapezoid top = base − 0.7 mil; outer Cu 1.6 mil in the calculator — [JLC calculator guide](https://jlcpcb.com/help/article/User-Guide-to-the-JLCPCB-Impedance-Calculator)
- JLC's calculator offers "Coplanar Single Ended", "Coplanar Differential Pair", "Single Ended (Non-coplanar)" and "Differential Pair (Non-coplanar)" models. — [JLC calculator guide](https://jlcpcb.com/help/article/User-Guide-to-the-JLCPCB-Impedance-Calculator)
- Fab tolerances: impedance ±10% standard (±5% on request); track width ±20%; board thickness ±10%. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- Closed-form cross-check model: Hammerstad & Jensen microstrip equations with finite-thickness correction — [E. Hammerstad, Ø. Jensen, "Accurate Models for Microstrip Computer-Aided Design," IEEE MTT-S 1980](https://doi.org/10.1109/MWSYM.1980.1124303)
- The brief says SPI width should come "from approximately 50-ohm profile", with the existing 22 Ω series resistors kept and "no 50-ohm shunt". — [layout brief §7/§11](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)

### Inferences
**Method.** I used my own quasi-static 2D finite-volume Laplace solver on a non-uniform grid (2 µm cells near the conductors), with Z0 = 1/(c·√(C·C_air)).
- Validation against Hammerstad–Jensen for an uncoated rectangular trace (h 0.0994 mm, Er 4.1, t 35 µm): 60.17 vs 60.17 Ω at w 0.12 mm, 49.28 vs 49.22 Ω at 0.18 mm, and 40.87 vs 40.80 Ω at 0.25 mm. Agreement is within 0.2%.
- Assumptions:
  - JLC trapezoid (top narrower by 0.7 mil).
  - Conformal mask 30.5 µm on the laminate and 15.2 µm on copper, Er 3.8.
  - Coplanar pours are 1.2 mm wide and ideally stitched to L2.
  - The L3 narrow face points toward L4, and prepreg resin (Dk 4.1) fills beside L3 traces.
  - Lossless and quasi-static, which is adequate at tens of MHz.

**L1 microstrip over L2 (h 0.0994 mm):**

| Case | 50 Ω width (mm) | Z at 0.10 / 0.127 / 0.15 / 0.16 / 0.18 / 0.20 / 0.25 / 0.30 mm |
|---|---|---|
| Uncoated, t 35 µm | **0.180** | 66.5 / 59.7 / 55.0 / 53.2 / 50.0 / 47.1 / 41.3 / 36.9 |
| Mask-coated, t 35 µm | **0.161** | 61.6 / 55.8 / 51.7 / 50.2 / 47.3 / 44.8 / 39.5 / 35.4 |
| Uncoated, t 40.6 µm (JLC calc) | 0.177 | 65.7 / 59.1 / 54.5 / 52.7 / 49.6 / 46.8 / 41.1 / 36.6 |
| Mask-coated, t 40.6 µm | 0.158 | 60.9 / 55.2 / 51.2 / 49.7 / 46.9 / 44.4 / 39.2 / 35.2 |

- Effective permittivity is 3.30 coated (6.06 ps/mm) and 2.97 uncoated (5.75 ps/mm).

**L1 coplanar with ground (coated, t 35 µm):**

| Gap to GND pour | 50 Ω width | Z at w = 0.15 / 0.18 / 0.20 mm |
|---|---|---|
| 0.15 mm | 0.145 mm | 49.2 / 45.1 / 42.8 |
| 0.20 mm | 0.153 mm | 50.4 / 46.1 / 43.7 |
| 0.25 mm | 0.156 mm | 51.0 / 46.6 / 44.1 |
| 0.30 mm | 0.158 mm | 51.3 / 46.9 / 44.4 |

- With the 0.2 mm general clearance to a stitched GND pour, **0.15 mm on L1 is about 50 Ω**. Pours pull Z down by only 0.5–2 Ω because h (0.1 mm) is much smaller than the gap.

**L3 (L4 at 0.0994 mm below, prepreg Dk 4.1; L2 at 0.865 mm above, core Dk 4.6; t 15.2 µm):**
- 50 Ω width is **0.136 mm**. Effective permittivity is 4.25 (6.88 ps/mm).
- Z at 0.09 / 0.10 / 0.11 / 0.127 / 0.14 / 0.15 / 0.18 / 0.20 / 0.25 mm = 59.9 / 57.4 / 55.1 / 51.7 / 49.3 / 47.7 / 43.5 / 41.1 / 36.2 Ω.
- With a coplanar GND pour on L3 at gaps 0.15 / 0.20 / 0.25 mm, the 50 Ω width is 0.123 / 0.129 / 0.132 mm.
- **With L4 voided under the trace** (only L2 as reference), Z is 119 Ω at 0.15 mm and 112 Ω at 0.20 mm. Continuous L4 GND under the L3 SPI corridor is mandatory, consistent with the brief.

**Sensitivity (L1 coated, nominal 0.161 mm = 50.0 Ω):**
- Width −20% gives 55.5 Ω; +20% gives 45.6 Ω.
- Prepreg −10% gives 47.0 Ω; +10% gives 52.8 Ω.
- Dk 3.9 gives 51.0 Ω; Dk 4.3 gives 49.1 Ω.
- No mask gives **53.0 Ω (mask ≈ −3 Ω)**; double mask thickness gives 48.7 Ω.
- Stacked corners (w ±20%, h ±10%, Dk 3.9–4.3): 41.9–59.5 Ω for 0.161 mm and 39.4–56.6 Ω for 0.18 mm.
- For L3 at 0.136 mm the corners are 42.4–59.1 Ω (core Dk 4.4–4.8).
- Ordering "impedance control" makes JLC hold ±10% (±5% on request) by adjusting width. Without it, the ±20% width tolerance dominates.

**Recommendations for the SPI class:**
- L1: 0.16 mm microstrip, or 0.15 mm with a stitched GND pour at ≥0.2 mm.
- L3: 0.14 mm, which needs a scoped width exception because the global minimum is 0.15 mm. Alternatively accept 0.15 mm (47.7 Ω, −4.6%).
- The current preferred 0.18 mm is fine on L1 (47.3 Ω) but low on L3 (43.5 Ω).

**Default-stack risk.** On JLC04121H-7628 (0.2104 mm 7628, Dk 4.4), L1 coated 0.161 / 0.18 mm gives 71.5 / 68.5 Ω and 50 Ω needs 0.357 mm. L3 at 0.136 / 0.15 mm gives 65.2 / 62.8 Ω. The stack must be ordered as JLC04121H-3313.

**Delay.** At 6–7 ps/mm, a 50 mm SPI route has a one-way delay of about 0.3–0.35 ns.

### Gaps
- JLC's own calculator output for JLC04121H-3313 could not be retrieved; the calculator is interactive and no calculation API was found. Cross-check these widths in JLC's calculator or in Altium's Layer Stack Manager, with solder mask added, before locking the SPI rule.
- IPC-2141A closed forms were not used or retrieved (the standard is paywalled). The field solver was cross-checked with Hammerstad–Jensen instead.
- How JLC models inner-layer trapezoid orientation and resin-rich Dk beside L3 traces is not documented. I assumed prepreg Dk 4.1; a lower resin-pocket Dk would raise the L3 Z slightly.

## Q4 — Current capacity of tracks and vias (IPC-2152 basis), voltage drop, multiple vias

### Takeaway
At the 0.6 A 3.3 V planning load, temperature rise is not the constraint:
- The conservative generic IPC-2152 chart needs only about 0.11 mm on 35 µm L1 or 0.26 mm on 15.2 µm L3 for a 10 °C rise.
- Voltage drop and converter-loop inductance should size the 0.9 mm power corridors.
- For a charger path at 1.5 A, use ≥0.6 mm (L1, 10 °C) or ≥1.4 mm (L3, 10 °C). At 2 A, use ≥1.0 mm on L1 or ≥2.3 mm on L3.

A 0.3 mm via with JLC's 18 µm average plating has a barrel of about 0.016–0.018 mm², about 1.15–1.3 mΩ, and roughly 1.3–1.4 A (10 °C) or 1.8–1.9 A (20 °C) by the barrel-area method. Use 2–4 vias per current transition.

### Cited Findings
- IPC-2152 generic-chart curve fit: A[mil²] = (117.555·ΔT^−0.913 + 1.15) · I^(0.84·ΔT^−0.108 + 1.159), with I the RMS current in A and ΔT in °C. It checks within 3% of IPC data (10 A/20 °C: IPC 500 mil², fit 513.1). — [L. Rozenblat, "PCB Trace Width Calculator and Equations" (smps.us)](https://www.smps.us/pcb-calculator.html)
- The generic IPC-2152 charts represent "polyimide boards 0.070" thick with 3 ounce copper in still air". Modifiers exist for copper weight, board thickness, plane area and distance to plane.
  - "The old PCB design standard overstated current carrying capacity of external tracks."
  - For internal tracks, "the legacy recommendations … happened to be conservative".
  - The new standard suggests "the same copper size for all board's layers".
  — [smps.us](https://www.smps.us/pcb-calculator.html)
- JLC via plating: "Average Hole Plating Thickness: 18μm". — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- Brooks & Adam measurements (Signal Integrity Journal, summarised by Altium):
  - "thin traces tend to run hotter than the via connected to them, with a temperature difference of only a few °C". With wide (200 mil) traces the via is the warmer part by a few °C.
  - "The rules for sizing traces are often applied to sizing vias."
  - A "0.5 A rule of thumb sometimes seen on forums" is overly conservative. With "a less-conservative limit of 1 A per via … to supply 5 A … 5 large vias with thick plating should be fine".
  — [Z. Peterson, Altium, "PCB Via Current-Carrying Capacity: Is My PCB Too Hot?" (updated Sept 2025)](https://resources.altium.com/p/pcb-current-carrying-capacity-how-hot-too-hot)
- The brief says: "Use multiple power vias for current paths as calculated; do not assign a universal amperage rating to a via". It also says LX routing "is not sized merely from the average radio current" and that 0.6 A is "a planning case, not a guaranteed maximum". — [layout brief §12–13](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)

### Inferences
**Track widths** from the smps.us IPC-2152 generic fit (no modifiers, so conservative), width = area ÷ physical copper thickness. Thicknesses: 35 µm = 1.378 mil (L1/L4 outer); 17.5 µm (nominal 0.5 oz); 15.2 µm = 0.598 mil (JLC inner 0.5 oz, L2/L3).

| ΔT | I (A) | Area (mil²) | 35 µm outer | 17.5 µm | 15.2 µm inner |
|---|---|---|---|---|---|
| 10 °C | 0.5 | 4.4 | 0.08 mm | 0.16 mm | 0.19 mm |
| 10 °C | 1.0 | 15.5 | 0.29 mm | 0.57 mm | 0.66 mm |
| 10 °C | 1.5 | 32.4 | 0.60 mm | 1.19 mm | 1.37 mm |
| 10 °C | 2.0 | 54.5 | 1.01 mm | 2.01 mm | 2.32 mm |
| 20 °C | 0.5 | 2.6 | 0.05 mm | 0.10 mm | 0.11 mm |
| 20 °C | 1.0 | 8.8 | 0.16 mm | 0.32 mm | 0.37 mm |
| 20 °C | 1.5 | 18.0 | 0.33 mm | 0.66 mm | 0.76 mm |
| 20 °C | 2.0 | 29.9 | 0.55 mm | 1.10 mm | 1.27 mm |

- Comparison with the older IPC-2221 formula (I = k·ΔT^0.44·A^0.725, with k = 0.048 external / 0.024 internal as reproduced by online calculators; not fetched in this session):

  | ΔT | Outer 35 µm, 0.5 / 1 / 1.5 / 2 A | Inner 15.2 µm, 0.5 / 1 / 1.5 / 2 A |
  |---|---|---|
  | 10 °C | 0.12 / 0.30 / 0.53 / 0.78 mm | 0.69 / 1.80 / 3.15 / 4.68 mm |
  | 20 °C | 0.08 / 0.20 / 0.35 / 0.51 mm | 0.45 / 1.18 / 2.07 / 3.07 mm |

  IPC-2221's internal widths are about 2–3.7× wider than IPC-2152's, matching smps.us's point that the legacy internal rule was conservative.
- **Reverse check of project widths** (generic fit):
  - 0.9 mm EMG_POWER on L1: about 1.9 A at 10 °C and 2.6 A at 20 °C. The same width on L3: about 1.2 A at 10 °C and 1.65 A at 20 °C.
  - The 0.15 mm minimum-width neck on L1: about 0.70 A at 10 °C. On L3: about 0.44 A at 10 °C. **A 0.15 mm neck on L3 carrying the 0.6 A rail exceeds 10 °C by the generic chart.** Short necks are thermally benign, but review any long L3 power necks.
  - The planning 0.6 A needs about 6.1 mil² (0.11 mm on L1, 0.26 mm on L3) at 10 °C.
- These widths are conservative. The generic chart assumes a 1.78 mm polyimide board with no planes, while this board has solid GND copper 0.1 mm from L1 and L3. IPC-2152 plane modifiers would lower the rise substantially, but the modifier charts were not available here.
- **Voltage drop** (ρ = 1.724 µΩ·cm at 20 °C, annealed copper; an assumption): sheet resistance is 0.493 mΩ/□ for 35 µm and 1.134 mΩ/□ for 15.2 µm. At 0.6 A:
  - 20 mm × 0.9 mm on L1 → 10.9 mΩ, 6.6 mV.
  - 20 mm × 0.5 mm on L1 → 19.7 mΩ, 11.8 mV.
  - 20 mm × 0.9 mm on L3 → 25.2 mΩ, 15.1 mV.
  - 5 mm × 0.3 mm neck on L1 → 8.2 mΩ, 4.9 mV.
  - Budget copper by millivolts, which dominates well before heating does.
- **Via barrels** (length 1.2 mm; area range spans finished-hole-equals-nominal vs drilled-hole-equals-nominal). "Barrel-area method" means treating the barrel as a conductor of equal area in the IPC-2152 generic fit, the approach Altium describes; the IPC-2221 external formula gives similar values (e.g. 1.35–1.48 A at 10 °C for 0.3 mm/18 µm).

  | Via | Barrel area | R (full barrel) | I at 10 °C | I at 20 °C |
  |---|---|---|---|---|
  | 0.3 mm hole, 18 µm (JLC average) | 0.0159–0.0180 mm² (24.7–27.9 mil²) | 1.15–1.30 mΩ | 1.29–1.38 A | 1.80–1.92 A |
  | 0.3 mm hole, 20 µm | — | 1.03–1.18 mΩ | 1.36–1.47 A | — |
  | 0.3 mm hole, 25 µm | — | 0.81–0.96 mΩ | — | — |
  | 0.2 mm hole, 18 µm | 0.0103–0.0123 mm² | 1.68–2.01 mΩ | 1.02–1.12 A | 1.40–1.55 A |

  Per Brooks/Adam, the attached thin traces, not the via, are usually the hot spot. An L1→L2 or L1→L3 transition uses only part of the barrel length, so its resistance is lower.
- **Guidance for converter and charger paths:**
  - For 1.5 A paths (USB-C VBUS → charger IN, charger OUT/BAT, TPS631000 VIN/VOUT), 2 × 0.3 mm vias meet the 10 °C barrel limit.
  - Use **3–4 vias per layer change** (≈0.3–0.4 mΩ combined), roughly ≤0.5 A per via. This gives margin for the unverified converter peak currents, lower loop inductance, and plating-void redundancy.
  - For 0.6 A 3V3 transitions, use ≥2 vias.
  - Keep switching-loop (LX, CIN/COUT) currents on one layer where possible, as the brief prefers.
  - The 0.2 mm in-pad vias are thermal paths. Do not count on them for current.

### Gaps
- IPC-2152 itself (charts and modifiers) and the Saturn PCB Toolkit documentation were not retrieved. Plane, board-thickness and copper-weight modifiers were therefore not applied.
- The primary Brooks & Adam Signal Integrity Journal article was not fetched; the Altium summary was used.
- Whether JLC's 18 µm average plating meets IPC-6012 Class 2 averages was not verified.
- Charger ILIM maximum (BQ24072T) and TPS631000 peak switch/inductor currents were not verified in this session. Size LX and VIN/VOUT copper from the datasheets' peak currents, not the average load.
- No source was found for a JLC-specific current chart.

## Q5 — JLC assembly (PCBA) rules that affect routing: via-in-pad, paste, fiducials, edges

### Takeaway
Size limits force a choice between the two JLC assembly tiers:
- **Standard PCBA** handles 0.35 mm-pitch parts and 0201s, but it needs a single board of at least 70 × 70 mm (this board's 45 mm side is too small) and it requires edge rails and fiducials.
- **Economic PCBA** accepts an 80 × 45 mm single board with no rails or fiducials, but only down to 0.4 mm pitch and 0402.

Standard PCBA therefore means panelising with 5 mm rails. If that panel is V-cut, copper must stay ≥0.4 mm from the V-cut edge, which the current 0.254 mm edge rule fails.

For vias in the exposed pads:
- JLC cannot ink-plug vias in pads or within 0.35 mm of pads.
- Filled-and-capped (POFV) is available on 4-layer boards but is charged.
- JLC's assembly page states no mandatory rule, so choose between open vias (solder-wicking risk), selective filling identified by the unique 0.2 mm diameter, or paid POFV.

### Cited Findings
- **Board size:** single-board Standard PCBA 70 × 70 to 460 × 500 mm; Economic 10 × 10 to 470 × 500 mm. Panelised (both tiers) 10 × 10 to 250 × 250 mm, 250 × 250 mm recommended maximum. — [JLCPCB, "PCB Assembly Capabilities"](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
- **Rails and fiducials:** edge rails are required for Standard and not necessary for Economic. Fiducials are "Necessary" for Standard and "Not necessary" for Economic. — [JLCPCB PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
- **Pitch and package:** minimum IC pin spacing is 0.35 mm (Standard) and 0.4 mm (Economic). Minimum BGA pitch is 0.3 mm (Standard) and 0.5 mm (Economic). Minimum package is 0201 (Standard) and 0402 (Economic). — [JLCPCB PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
- **Page silences:** the PCBA capabilities page states no via-in-pad, thermal-pad-via or stencil/aperture rules. — [JLCPCB PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
- **Process edges:** recommended are "5 mm process edges, 2 mm tooling holes, and 1 mm fiducials placed 3.85 mm from the panel edge". With too-narrow process edges, components near the edge "might collide with the guide rails". — [JLCPCB help, "Specifications for Adding Process Edges and Positioning Holes" (updated 2026-09-09)](https://jlcpcb.com/help/article/specifications-for-adding-process-edges-and-positioning-holes)
- **Via-in-pad plugging:** vias in pads, and vias closer than 0.35 mm to a pad, "cannot be plugged with ink"; they can be epoxy- or copper-filled. Plugging can be specified per via diameter. — [JLCPCB via-covering article](https://jlcpcb.com/help/article/pcb-via-covering)
- **Solder wicking:** for regular vias in pads, "during reflow soldering the solder can be wicked into the hole, leaving too little on the surface to secure the component". POFV fixes this and is charged on 4-layer boards (hole 0.2–0.5 mm, ring ≥0.05 mm with 0.075 mm preferred, ≥0.45 mm from PTH/NPTH). — [JLCPCB POFV news (2022-11-02)](https://jlcpcb.com/news/free-via-in-pad-6-20-layer-pcbs-pofv)
- **Filled-via spacing:** filled vias need ≥0.35 mm clearance from other soldermask openings; epoxy or copper-paste fill supports 0.15–0.55 mm vias. — [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- The brief requires "a manufacturer/assembler-qualified filled/capped or approved tented/plugged/stencil arrangement" for the ST67/BQ thermal lands. It notes "tenting is not equivalent to filling", and says ordinary vias "should not be open via-in-pad under small SMT components". It also cites "the ST multi-via central-land recommendation, commonly five vias per land". — [layout brief §10/§13](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-16/Documentation/EMG_Main_PCB_Layout_Master_Prompt_2026-09-16.md)
- Project paste rule `PasteMaskExpansion` = 0 (paste openings equal pads, no windowpane rule). — [RULES.txt](file:///C:/Users/PMLS/Desktop/emg-saw/hardware/pcb_layout_2026-09-23_drl/evidence/NATIVE_FINAL_20260924T015854610Z/RULES.txt)

### Inferences
- **Tier choice.** The task context mentions 0.35 mm-pitch parts, which only Standard PCBA places. Standard PCBA needs a ≥70 × 70 mm single board or a panel with rails and fiducials, so plan an assembly panel with 5 mm rails, 1 mm fiducials 3.85 mm from the panel edge, and 2 mm tooling holes.
  - V-cut panel: raise copper-to-edge to ≥0.4 mm (0.5 mm per the brief). The exported 0.254 mm fails.
  - Routed tabs/mouse-bites: 0.2 mm is the fab minimum, but breakout damage argues for the brief's 0.5 mm.
  - Economic PCBA is possible only if every part is ≥0.4 mm pitch and ≥0402.
- **Exposed-pad vias.** Only the in-pad vias use a 0.2 mm hole, so JLC can identify them by diameter and fill only those. Three routes:
  - **(a) Paid POFV.** The ring (0.125 mm) is fine; keep ≥0.45 mm to any PTH/NPTH.
  - **(b) Open 0.2 mm vias.** Pair them with a windowpane paste aperture that avoids the via openings. This accepts some wicking and voiding, which JLC warns of.
  - **(c) Mask-tent from the bottom only.** JLC does not guarantee tents, and the brief says tenting is not filling.
  - Whichever route is chosen must be written into the order notes, because nothing in JLC's assembly page enforces it.
- **Paste.** With `PasteMaskExpansion` 0, the ST67 centre lands and the BQ24072T thermal pad would receive 100% paste openings. Add footprint-level segmented paste (windowpane) regions for large exposed pads per the device datasheets; JLC's pages give no stencil rule to rely on.
- **Near-pad vias.** Tented vias ≤0.35 mm from pads (e.g. the 0.175 mm GND via by U_MCU1-31) cannot be ink-plugged. Leave them tented or open, not "plugged".

### Gaps
- JLC's stencil thickness and its automatic handling of exposed-pad apertures were not found on the fetched pages.
- These search-result numbers were not verified by fetching the source page (the JLC edge-rails article): fiducial ≥3.35 mm from the board edge, rails ≥5 mm, component body ≥2.5 mm from the board edge. Treat them as unconfirmed.
- A snippet stating "JLCPCB SMT fully supports 0.4mm pitch QFNs, Via-in-Pad, and AXI" (JLC blog) was also not verified.
- Whether a single-board Standard PCBA order below 70 mm is auto-panelised by JLC or rejected was not verified.
- JLC's order-form behaviour when POFV is selected (all vias or only specified diameters) is only implied by the via-covering article's "specify which via diameters" wording.
- The actual pitch of the "0.35 mm-pitch" parts and any 0201 usage should be confirmed from the BOM; that decides between Standard and Economic PCBA.
