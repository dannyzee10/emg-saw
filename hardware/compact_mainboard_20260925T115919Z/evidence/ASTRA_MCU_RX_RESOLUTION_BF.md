# MCU UART RX routed — native checkpoint BF

27 September2026. User requested the next remaining route.

## Actual applied change

Connected `R_WIFI_UART_RX_LINK.2` on Bottom to `U_MCU1.93` on Top, net `MCU_WIFI_UART_RX`, using0.20 mm routing and two0.60/0.30 mm through vias. The route uses Bottom/L3/Top; the two internal GND-layer definitions are unchanged.

Local routes on3V3_DIG, I2C_SDA, MCU_BOOT0 and VSYS were adjusted to make room. I2C_SDA gained two0.45/0.20 mm vias; MCU_BOOT0 gained one0.60/0.30 mm via, with the existing filled/capped via-in-pad assembly requirement applicable where it overlaps its own pad.

Every added3V3_DIG and VSYS track is0.40 mm. Added a0.40 mm Bottom connection from existing VSYS source via(52.075,41.375) to CUP4_1.1 atx53.4119/y41.375, retaining the original regulator pin escape. Widening the full original pin escape was rejected because it failed clearance near the switch-node pin.

Final applied batch: **33tracks+5vias added;16tracks removed**. No component moves, pin swaps, via deletions, rules or schematic changes.

ONLY applied plan: `ASTRA_MCU_RX_REINFORCED_ADDS.csv` / `ASTRA_MCU_RX_REINFORCED_DELS.csv`, `../work/OPS_BF_UART_RX_REINFORCED.txt`. Raw RX1/READY candidates were superseded; POWER_READY failed clearance and was never applied.

## Measured evidence

- Prior BE backup and hashes: `ASTRA_BF_BEFORE_20260927/`.
- Combined final geometry precheck:38additions,16deletions, **PROBLEMS0**.
- `ASTRA_MCU_RX_REINFORCED_GRAPH_REVIEW.json`: target2→1 connected copper groups; all four neighboring nets remain connected, including retained interior contacts.
- `ASTRA_APPLY_BF.txt`: native preflight, six polygon rebuilds, save/reopen complete;147rules unchanged in count.
- `DRC_C2_6L_BF.txt.html` / `.json`: native processing finished21:22:37local. **254total violations;2unrouted**, down from255/3. Only the MCU_WIFI_UART_RX open was removed; no new diagnostic was introduced.
- Remaining opens: `MCU_WIFI_UART_TX`, `WIFI_SPI_CS`.
- Other reported categories unchanged:6antennae,157silk-mask,84silk-silk,5outline; zero copper-clearance/short/width/component-clearance violations.
- `GEOMETRY_C2_6L_BF.txt` / `ASTRA_BF_DELTA.json`: exact routing delta PASS. Free tracks2219→2236; vias455→460. All231packages,812pads and1629fixed export records unchanged. Writer net-assigned track count2226 excludes ten unassigned tracks.
- Eight SchDocs and PrjPcb hash-identical: `ASTRA_BF_SCHEMATIC_PROJECT_PRESERVATION.json`. Saved PCB identity: `ASTRA_BF_AFTER_HASH.json`.

Native DRC BooleanFalse is recorded separately from completed processing and actual diagnostic counts. No blanket suppression was added. The strict raw-stream checker retains body/pad/text differences; native geometry comparison and unchanged net/rule/stack/outline streams substantiate the limited routing verdict, not a universal metadata-equality claim.

## Current checkpoint

Project/PCB: `../C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PrjPcb` / `.PcbDoc`. Altium remains open with saved BF. Use BF exports for subsequent planning. Preserve prior channel4, Vc_1 and radio-side UART RX corrections.

This remains a routing checkpoint, not fabrication approval. Existing via-style batch coverage, final width/trace cleanup, silkscreen/outline/antenna diagnostics and qualification gates remain open. Only final REINFORCED CSVs may be included as intentional future rip-up history; do not apply rejected alternatives.
