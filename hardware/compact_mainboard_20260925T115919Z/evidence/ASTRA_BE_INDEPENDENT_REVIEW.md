# Independent UART BD-to-BE review

Native BE resolves WIFI_UART_RX. Unrouted connections changed 4 to 3 and total
DRC details changed 256 to 255. The only removed detail is WIFI_UART_RX between
U_WIFI1.23 and the via at (43.525,40.075); every other violation detail is
identical. No new short, clearance, width, component-clearance or power open was
reported. Remaining opens: WIFI_SPI_CS, MCU_WIFI_UART_RX, MCU_WIFI_UART_TX.

The native geometry delta exactly matches `ASTRA_UART_READY_ADDS.csv` and
`ASTRA_UART_READY_DELS.csv`: 18 tracks and one via added, 15 tracks removed.
Free tracks changed 2216 to 2219; vias changed 454 to 455. All exported pads,
components and fixed geometry are unchanged.

The independent prewrite graph check preserved every connection between retained
copper on MCU_SPI_MISO, SYS_EN, VSYS, WIFI_BOOT and WIFI_UART_TX. All remain one
connected component; WIFI_UART_RX changed two to one. The final CSV hashes match
the graph check. The original VSYS via at (43.125,41.625) remains, all added VSYS
tracks are 0.40 mm, and the direct 0.40 mm extension reaches U_UV1.6. The rejected
long 0.15 mm power detour is absent.

Saved Rules6, Nets6 and Components6 are byte-identical. Protected stack, layer,
outline, origin and other Board6 design parameters are unchanged. The eight
schematics and project file also have identical hashes.

Raw conservative comparison retains opaque Pads6, Texts/Texts6 and cached DRC
stream changes. Both body streams contain the established metadata pattern:
216 models before/after, with only MODELID and checksum fields changed in 73
nonembedded extrusion records; other body bytes are identical. These raw changes
are retained in the JSON, not silently waived.

Evidence: `ASTRA_UART_READY_GRAPH_REVIEW.json` and
`ASTRA_BE_INDEPENDENT_REVIEW.json`. Checkers are
`work/astra_check_uart_partial_graph.py` and `work/astra_review_uart_be.py`.
They perform no routing search, CAD edits or native application operations.

Saved BE PCB SHA-256:
`533d59452fb288d3b8175b2cd3c8a9c8d179107affbb1abfc1ad7ebedd75d486`
