# Combined bounded cleanup of all ten BH antenna warnings

**Offline candidate PASS: 19 track deletions and eight replacement tracks.** No pad or via is removed or moved. The VREF nets and the user's zero-length `NetJ_FPC1_8` segment are untouched. No router, native application or CAD write was performed by this reviewer.

Source: completed `GEOMETRY_C2_6L_BH.txt`, SHA256 `d3a094dc5ccabc24051e295fdc2878f064df6e4070c22d0490e69668f5c1689b`. The current BH native report has zero opens and the ten antenna warnings being reviewed. The earlier four-warning candidate CSVs remain unchanged.

Candidate files:

- `ASTRA_BH_ALL_ANTENNA_BOUNDED_DELS.csv`: 19 uniquely matched free tracks.
- `ASTRA_BH_ALL_ANTENNA_BOUNDED_ADDS.csv`: eight tracks.
- `ASTRA_BH_ALL_ANTENNA_BOUNDED_CHECK.json`: source hashes, exact contact checks and graph/power results.
- Reproducer: `../work/astra_bh_all_antennas_check.py`; bounded legacy contact inventory: `ASTRA_BH_LEGACY_ANTENNA_CONTACTS.json`.

## Ten warnings and bounded treatment

| Warning | Treatment |
|---|---|
| Top VBUS (14.825,38.725) to (16.300,37.250), 0.15 mm | Needed bridge: replace with (15.775,37.675) → (15.875,37.675) → (16.300,37.250), all 0.15 mm. Starts at the retained 0.40 mm feed endpoint. |
| L3 NetD_CC_ESD_1 (16.300,41.675) to (19.025,41.675), 0.15 mm | Remove the bounded five-track dead branch, stopping at retained via (15.075,42.175). The similarly positioned L5 route stays unchanged. |
| L3 NetD_CC_ESD_2 (20.025,38.125) to (20.025,39.325), 0.15 mm | Remove this leaf only; retain the via and its Top contacts. |
| Bottom 3V3_DIG (20.725,42.325) to (20.725,42.925), 0.40 mm | Remove this leaf and the adjacent 0.40 mm dead diagonal to via (21.075,43.225). Retain that via and its necessary L5/Bottom contacts. |
| L3 NetD_CC_ESD_2 (21.975,41.275) to (22.825,41.275), 0.15 mm | Needed bridge: replace with (22.125,41.225) → (22.175,41.275) → (22.825,41.275), all 0.15 mm. Starts at the retained incoming diagonal endpoint. |
| L5 VSYS (22.625,39.425) to (25.775,39.425), 0.15 mm | Remove the two-track dead tail and replace its following horizontal bridge with (27.525,40.175) → (27.575,40.125) → (32.825,40.125), all 0.15 mm. Preserve the interior branch from (23.025,44.675), joining its exact endpoint. |
| Top 3V3_DIG (44.775,41.625) to (46.225,41.625), 0.15 mm | Remove only the flagged leaf; the retained thin diagonal and 0.40 mm source feed still directly touch. |
| L3 WIFI_CHIP_EN (45.975,34.975) to (48.6045,34.975), 0.20 mm | Remove two-track leaf, stopping at retained via (44.875,36.075). |
| L3 WIFI_UART_TX (48.6045,41.925) to (48.9019,41.925), 0.15 mm | Remove two short leaves; retain the directly connected 0.20 mm reroute and 0.15 mm outgoing diagonal. |
| L5 3V3_DIG (51.025,33.675) to (51.025,37.075), 0.15 mm | Preserve the needed bridge using (51.025,33.675) → (51.025,35.025) → (50.725,35.025), all 0.15 mm. Full original contact areas remain; contact with the 0.40 mm feed increases. |

## Proof and limits

All seven affected nets remain one connected component, with no detached addition: `3V3_DIG`, `VBUS`, `VSYS`, `NetD_CC_ESD_1`, `NetD_CC_ESD_2`, `WIFI_CHIP_EN`, `WIFI_UART_TX`. Every retained connection is preserved using the established exported-copper graph and 0.00015 mm contact tolerance.

Power connectivity is preserved at every original width threshold: 3V3_DIG **0.15/0.20/0.30/0.40 mm**, VBUS **0.15/0.40 mm**, VSYS **0.15/0.30/0.40 mm**. New versus retained and new versus new copper checks have zero blockers; edge, keepout and L5 reserved-area checks pass. The check took 0.50 seconds.

The three legacy replacement bridges start at exact existing centerline endpoints. Their full 0.15 mm endpoint discs lie inside retained copper. VBUS and VSYS contact areas change as their offset dead-tail contacts are replaced with direct endpoint junctions; the proof does not claim every original overlap point is retained there. Every necessary pairwise contact survives, and no trace width is reduced. The L5 3V3_DIG replacement preserves all original overlap area, including the 0.40 mm feed contact: 0.06314811 → 0.10557247 mm².

This is a bounded candidate, not proof that native antenna violations have already disappeared. Native DRC after application must confirm the resulting count and zero opens. Full poured geometry and current/thermal capacity are outside this exported-copper graph. Root should use its current-state exact check before applying; via-rule alignment after BH does not itself alter this geometry.
