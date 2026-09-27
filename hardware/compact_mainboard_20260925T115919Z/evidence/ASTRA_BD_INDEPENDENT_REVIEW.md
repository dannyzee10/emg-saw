# Independent Vc_1 BC-to-BD review

The authorized seven-track Vc_1 path is saved and its remaining native open is
resolved. Native free tracks changed 2209 to 2216; vias remain 454. All additions
exactly match the approved 0.20 mm path on Mid Layer 4 (L5). No deletions,
component moves or new vias were requested or found. Every exported pad,
component and fixed primitive is unchanged.

Native DRC total changed 257 to 256 and unrouted connections changed 5 to 4.
The sole removed violation detail is Vc_1 between the existing vias
(15.900,11.200) and (24.175,19.325). Every other violation detail is identical;
there are no added details or new power/copper opens. No nonzero clearance,
short, width or component-clearance summary rows were found.

The four unchanged opens are WIFI_SPI_CS, MCU_WIFI_UART_RX,
MCU_WIFI_UART_TX and WIFI_UART_RX.

Saved Rules6, Nets6 and Components6 streams are byte-identical to the frozen BC
backup. Protected Board6 stack/layer, outline, origin and other design parameters
are unchanged. SHA-256 checks also confirm the eight schematics and project file
are unchanged. The native width/clearance rule applicability is documented in
`ASTRA_VC1_NATIVE_RULE_REVIEW_BC.md`.

Conservative raw-stream comparison still reports Pads6/Data, Texts/Data,
Texts6/Data and the silk-to-mask cached-violation stream. These differences are
retained in the JSON and are not newly proven to be serialization-only. Exported
pad geometry and all remaining native DRC detail strings are identical; text
semantics are not part of the geometry export.

Evidence: `ASTRA_BD_INDEPENDENT_REVIEW.json`; reproducible read-only checker:
`work/astra_review_vc1_bd.py`. Original native input paths and hashes are retained.

Saved BC backup SHA-256:
`9c3eda3627a961779e80143e63f0e576cddd5b5951a383da2c6b2cfec7b2a5fd`

Saved BD PCB SHA-256:
`6062f8f16ae5b71fc85db1b179c43de1777fc44037730ca97ae6d42b6d87688a`

This reviewer performed no CAD edits, routing searches or native application
operations. Remaining routing and reported silk/antenna/edge work is outside
this completed Vc_1 delta check.
