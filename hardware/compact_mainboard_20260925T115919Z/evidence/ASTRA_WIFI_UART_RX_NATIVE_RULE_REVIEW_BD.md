# WIFI_UART_RX native rule review from frozen BD

Read-only review of saved native `Rules6/Data`, `Classes6/Data`, and the BD geometry export. No CAD process or router was run, and no CAD file, rule, or planner policy was changed.

- Board: `C:/Users/PMLS/Desktop/emg-saw/.claude/worktrees/pcb-routing-0925/hardware/compact_mainboard_20260925T115919Z/evidence/ASTRA_BE_BEFORE_20260927/EMG_MainBoard_Layout.PcbDoc`
- Board SHA256: `6062f8f16ae5b71fc85db1b179c43de1777fc44037730ca97ae6d42b6d87688a`
- `Rules6/Data` SHA256: `195482691ae58ab5a424c5115d3cb3e96eacbfc46e2771e44129af6b186fa295`
- Geometry reference: `evidence/GEOMETRY_C2_6L_BD.txt`.

`WIFI_UART_RX` is member `M1` of both `EMG_CONTROL` records (unique IDs `XQWFAALL` and `FIQXQOKM`), with no other class membership found. `WIFI_BOOT` is member `M4` of the same records.

The dominant width rule is `WIDTH_EMG_CONTROL`, enabled, priority 9, scope 1 `InNetClass('EMG_CONTROL')`, scope 2 `All`, `NETSCOPE=AnyNet`, `LAYERKIND=SameLayer`. Saved fields are `MINLIMIT=5.9055mil` (~0.15 mm), `PREFEREDWIDTH=7.874mil` (~0.20 mm), and `MAXLIMIT=19.685mil` (~0.50 mm). No Top, Mid Layer 2, Mid Layer 4, or Bottom width override is present. The enabled fallback `Width`, priority 10, has `All`/`All` scopes and the same limits.

| Physical layer | Native layer | Minimum / preferred / maximum | Proposed widths allowed |
| --- | --- | --- | --- |
| L1 | Top Layer | 0.15 / 0.20 / 0.50 mm | 0.15 and 0.20 mm |
| L3 | Mid Layer 2 | 0.15 / 0.20 / 0.50 mm | 0.15 and 0.20 mm |
| L5 | Mid Layer 4 | 0.15 / 0.20 / 0.50 mm | 0.15 and 0.20 mm |
| L6 | Bottom Layer | 0.15 / 0.20 / 0.50 mm | 0.15 and 0.20 mm |

The sole `RoutingLayers` rule is enabled, priority 1, scope 1 `All`, scope 2 `All`, `NETSCOPE=AnyNet`. Its `TOP LAYER_V5`, `MID LAYER 2_V5`, `MID LAYER 4_V5`, and `BOTTOM LAYER_V5` flags are all `TRUE`. The requested layers are therefore permitted by the saved native routing-layer rule. This is separate from any planner reservation or plane-integrity requirement; physical L4 (`Mid Layer 3`, GND) remains outside this routing proposal.

Relevant enabled clearance rules are:

| Rule | Priority | Scope 1 | Scope 2 | Saved gap / nominal mm |
| --- | --- | --- | --- | --- |
| `CLR_POWER_025` | 95 | `InNetClass('EMG_POWER')` | `All` | `9.8425mil` / 0.25 mm |
| `CLR_ANALOG_025` | 96 | `InNetClass('EMG_ANALOG') Or InNetClass('EMG_ADC') Or InNetClass('EMG_REFERENCE')` | `All` | `9.8425mil` / 0.25 mm |
| `CLR_GENERAL_020` | 97 | `All` | `All` | `7.874mil` / 0.20 mm |
| `Clearance` | 98 | `All` | `All` | `10mil` / 0.254 mm |

All have `NETSCOPE=DifferentNets` and `LAYERKIND=SameLayer`. For the first three rules, `GENERICCLEARANCE` equals `GAP` and `OBJECTCLEARANCES` is empty. The priority-98 fallback cannot override the higher-priority general rule for ordinary copper pairs. No local U_WIFI1/U_UV1 routing track-pad exception was found.

The checked neighboring nets resolve as follows; values apply when their copper shares a layer with the proposed RX copper:

| Opposing object or net | Native net class | Applicable rule | Clearance |
| --- | --- | --- | --- |
| U_WIFI1.22, `WIFI_UART_TX` | EMG_CONTROL | CLR_GENERAL_020 | 0.20 mm |
| U_WIFI1.24, `WIFI_SPI_CS` | EMG_SPI | CLR_GENERAL_020 | 0.20 mm |
| U_WIFI1.21, `WIFI_SPI_RDY` | EMG_CONTROL | CLR_GENERAL_020 | 0.20 mm |
| `WIFI_BOOT` copper | EMG_CONTROL | CLR_GENERAL_020 | 0.20 mm |
| U_WIFI1 ground pads or U_UV1.2, `GND` | EMG_GND | CLR_GENERAL_020 | 0.20 mm |
| U_UV1.1, `SYS_EN` | EMG_CONTROL | CLR_GENERAL_020 | 0.20 mm |
| U_UV1.3/.5/.6 or other `VSYS` copper | EMG_POWER | CLR_POWER_025 | 0.25 mm |
| U_WIFI1.9/.16/.25 or other `3V3_DIG` copper | EMG_POWER | CLR_POWER_025 | 0.25 mm |

The geometry export identifies the target as U_WIFI1.23, `WIFI_UART_RX`, Top Layer, center `(42.1260,42.4750)` mm. Immediate pad neighbors U_WIFI1.22 and .24 are also on Top; U_UV1 pads are on Bottom.

`CLR_ST67_ANTENNA_BOUNDARY_NO_EXTRA_GAP`, enabled priority 12, has `GAP=0mil`, but its scope is U_WIFI1 pads 25 through 32 versus a keepout-layer region. It does not grant reduced clearance to RX routing copper, vias, or adjacent module pads. The VSYS-specific lower-numbered exceptions found in the rules target named UP1/UP2 pads or a NetL1_1 track; they do not match an RX-to-VSYS pair.

These findings establish native rule permission and thresholds. They do not establish a legal physical route or via site, connectivity, or a DRC pass for a proposed candidate. Full copper/hole checks and native DRC remain necessary after a candidate is prepared and applied.
