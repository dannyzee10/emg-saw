# MCU_WIFI_UART_RX candidate review

Native source: `GEOMETRY_C2_6L_BE.txt`. Candidate: `ASTRA_BE_UART_RX1_ADDS.csv` / `ASTRA_BE_UART_RX1_DELS.csv`, initially copied unchanged to `ASTRA_MCU_RX_READY_*`. This note concerns that initial 37-add / 16-delete candidate only; final READY edits require renewed verification.

- Exact lightweight graph review passed: 32 tracks and five vias added; 16 tracks deleted. MCU_WIFI_UART_RX joins two components into one. 3V3_DIG, I2C_SDA, MCU_BOOT0 and VSYS each remain one component. Every retained same-net copper connection is preserved, and no new primitive is detached. Machine evidence: `ASTRA_BE_UART_RX1_GRAPH_REVIEW.json`.
- New target tracks are 0.20 mm; its two vias are 0.60/0.30 mm. EMG_CONTROL native width rule permits 0.15–0.50 mm, with 0.20 mm preferred. Native routing layers permit the used Top, Mid Layer 2 and Bottom layers. Native clearance checks remain required.
- All new VSYS and 3V3_DIG tracks are 0.40 mm. Nevertheless, a concrete power-width dependency changes: the new Bottom VSYS start `(53.775,41.725)` lands inside CUP4_1.1, but the retained connection from source via `(52.075,41.375)` to that capacitor is a **0.30 mm** Bottom track. The track runs UP2.4 `(51.5619,41.1685)` to CUP4_1.1 `(53.4119,41.3835)` (native BE geometry line 4158). Deleting the original 0.40 mm Mid Layer 2 branch makes the replacement depend on this narrower existing segment. Connectivity PASS does not establish an entirely 0.40 mm source-to-load path.
- Added I2C_SDA vias meet retained/new tracks; MCU_BOOT0 via `(55.575,45.025)` overlaps R_MCU_BOOT0_PD.2. Both new target vias coincide with their layer-transition track endpoints. No orphan via was identified.

No CAD or native application operation was performed. The power-width finding was sent to the root agent before application. Board geometry, net/rule/stack preservation and exact DRC changes must be checked against native BF after saving.

## Final reinforced candidate

The root agent selected `ASTRA_MCU_RX_REINFORCED_ADDS.csv` / `ASTRA_MCU_RX_REINFORCED_DELS.csv`: 33 tracks and five vias added, 16 tracks deleted. It retains the original 0.30 mm UP2 pad escape and adds a direct 0.40 mm Bottom segment from source via center `(52.075,41.375)` to `(53.4119,41.375)`, inside CUP4_1.1. This bypasses the narrower feed dependency above. The earlier full-feed widening trial `POWER_READY` failed clearance near UP2.3 and was not selected.

Independent graph review of the final REINFORCED files passed in 1.74 seconds: MCU_WIFI_UART_RX joins 2→1 components; all four other affected nets remain 1→1, every retained copper connection is preserved, and no addition is detached. See `ASTRA_MCU_RX_REINFORCED_GRAPH_REVIEW.json` for input hashes and exact results. Native BF review is separately captured in `ASTRA_BF_INDEPENDENT_REVIEW.json` when exports are complete.
