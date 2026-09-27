# Radio UART RX routed — native checkpoint BE

27 September 2026. User requested the easiest remaining connection. Selected `WIFI_UART_RX`, the shortest remaining endpoint gap; all four gaps failed the initial fixed-copper routing check, so a local reroute was needed.

## Applied change

- Added a 0.45/0.20 mm through via at(42.275,42.325), inside U_WIFI1 pad23's same-net copper; retained the existing project's filled/capped via-in-pad manufacturing requirement.
- Routed the UART on L3/Mid Layer2 at0.15 mm, connecting its existing copper near via(43.525,40.075).
- Adjusted local tracks on MCU_SPI_MISO, SYS_EN, WIFI_UART_TX, WIFI_BOOT and VSYS to make room. Net assignments and schematic pins are unchanged.
- Preserved the original VSYS via(43.125,41.625) and used0.40 mm for every added VSYS segment, including a direct extension into U_UV1.6. No long0.15 mm power replacement was applied.
- Exact applied batch:18tracks+1via added;15tracks removed. No component moves, via deletions, rule changes or schematic changes.

Applied sources: `ASTRA_UART_READY_ADDS.csv`, `ASTRA_UART_READY_DELS.csv`, `../work/OPS_BE_UART_READY.txt`. The earlier `ASTRA_BD_WIFI_LOCAL_*` candidate and `OPS_BE_UART.txt` were **not applied**: their long narrow VSYS replacement was rejected. The intermediate `ASTRA_UART_POWER_PRESERVED_*` files were superseded by the final READY files'0.40 mm extension.

## Verification

- Baseline BD backup/hashes: `ASTRA_BE_BEFORE_20260927/`.
- Full prewrite geometry check:19additions,15deletions, **PROBLEMS0**.
- Six-net graph check: `ASTRA_UART_READY_GRAPH_REVIEW.json`; UART2→1 copper components, all five neighboring nets1→1; retained interior contacts preserved.
- Native preflight, six polygon rebuilds, save and reopen: `ASTRA_APPLY_BE.txt`.
- Fresh native DRC: `DRC_C2_6L_BE.txt.html` / `.json`, completed20:59:18local;255total violations. Unrouted4→3. The ONLY removed detail is WIFI_UART_RX; no new detail was introduced.
- Three remaining opens: WIFI_SPI_CS, MCU_WIFI_UART_RX, MCU_WIFI_UART_TX.
- Unchanged other counts:6net antennae,157silk-mask,84silk-silk,5outline. Zero reported clearance/short/width/component-clearance violations. No new supply or GND open.
- Fresh native geometry: `GEOMETRY_C2_6L_BE.txt`. Exact delta PASS: `ASTRA_BE_DELTA.json`. Free tracks2216→2219, vias454→455; all231components,812pads and1629fixed export records unchanged. Writer's net-assigned track count2209 differs by ten unassigned tracks.
- Independent native review: `ASTRA_BE_INDEPENDENT_REVIEW.md/.json`.
- Eight SchDocs+PrjPcb hash-identical: `ASTRA_BE_SCHEMATIC_PROJECT_PRESERVATION.json`. Saved PCB hash: `ASTRA_BE_AFTER_HASH.json`.

Native DRC returned BooleanFalse with processing complete and document unmodified; diagnostic counts, not that Boolean, establish the result. Rules/nets/components/stack/outline are unchanged. The conservative raw-stream checker still flags body/pad/text/cache differences; body differences are confined to model IDs/checksums, while omitted pad/text metadata is not fully semantically compared. Do not describe the raw checker as an unconditional PASS.

## Continuation

Current project/PCB: `../C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PrjPcb` / `.PcbDoc`. Altium remains open with the saved BE board. Use BE geometry/DRC for subsequent work.

This is a routing checkpoint, not fabrication approval. Via-style batch coverage, remaining routes, antenna/silkscreen/outline cleanup and the previously recorded qualification gates remain open. No warning suppression was added. Preserve the already solved channel4 and Vc_1 routes. Add only the final READY CSV to any intentional future rip-up plan; do not use rejected candidates as routing history.
