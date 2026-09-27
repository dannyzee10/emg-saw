# Bounded cleanup of the four new BG antenna branches

Offline candidate **passes** exported-copper contacts, clearance, edge and keepout checks. No CAD, router or native operation was run. Source is `GEOMETRY_C2_6L_BG.txt`; exact source hash and results are in `ASTRA_BG_ANTENNA_BOUNDED_CHECK.json`. All four originally flagged tracks were retained from BFS, rather than newly added by BG.

| Flagged branch | Bounded change and retained termination |
|---|---|
| Top `3V3_DIG`, (44.775,41.625) to (46.225,41.625), width 0.15 | Delete this leaf only. The remaining 0.15 diagonal and 0.40 feed already directly touch near (44.775,41.625); their connection and the source via remain. |
| L3 `WIFI_CHIP_EN`, (45.975,34.975) to (48.6045,34.975), width 0.20 | Delete this leaf and its immediate 0.20 predecessor (44.875,36.075) to (45.975,34.975). Stop at the retained 0.60/0.30 via (44.875,36.075), which retains two Top contacts. Deleting only the flagged track would expose the predecessor as another leaf. |
| L3 `WIFI_UART_TX`, (48.6045,41.925) to (48.9019,41.925), width 0.15 | Delete this leaf and its immediate 0.15 continuation to (49.225,41.925). The retained 0.20 track (48.9019,42.3481) to (49.225,42.025) directly contacts the retained 0.15 outgoing diagonal from (49.225,41.925) to (49.7985,42.4985). |
| L5 `3V3_DIG`, (51.025,33.675) to (51.025,37.075), width 0.15 | **Do not delete it outright:** that splits 3V3_DIG at an interior feed contact. Replace it with two 0.15 tracks: (51.025,33.675) to (51.025,35.025), then to (50.725,35.025). The last endpoint lies on the retained 0.40 feed's centerline. |

The L5 replacement preserves every point of both original contact areas. Contact with the 0.15 start diagonal is unchanged at 0.01776765 mm². Contact with the retained 0.40 feed (50.175,35.575) to (50.975,34.775) increases from **0.06314811 to 0.10557247 mm²**, with **zero lost original contact area**. The horizontal termination avoids reducing the junction to a tangential contact when trimming the old dead tail.

Deleting the six specified tracks and adding these two replacements preserves all retained copper connections on `3V3_DIG`, `WIFI_CHIP_EN` and `WIFI_UART_TX`. The 3V3_DIG graph also preserves connectivity at every existing track-width threshold: **0.15, 0.20, 0.30 and 0.40 mm**. No pads or vias are moved or removed. The small check completed in 0.375 seconds.

Candidate files are `ASTRA_BG_ANTENNA_BOUNDED_DELS.csv` (six rows) and `ASTRA_BG_ANTENNA_BOUNDED_ADDS.csv` (two rows). The contact inventory is `ASTRA_BG_ANTENNA_CONTACTS.json`; reproducing scripts are `../work/astra_bg_antenna_contacts.py` and `../work/astra_bg_antenna_cleanup_check.py`.

Recheck the candidate against the current saved state before applying; this evidence used BG, while root proceeded with the remote testpad/TX changes. Full poured geometry is not represented by the offline contact graph. Fresh native DRC must establish the resulting antenna count; this note does not claim the four reported violations are already removed from CAD.
