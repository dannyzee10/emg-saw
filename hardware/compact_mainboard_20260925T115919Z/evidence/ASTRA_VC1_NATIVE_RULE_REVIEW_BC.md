# Vc_1 native width and clearance review for BD

Read-only inspection of the frozen saved BC board, before the seven-segment BD candidate. No CAD process or router was run by this review, and no board or rule was changed.

- Source: `C:/Users/PMLS/Desktop/emg-saw/.claude/worktrees/pcb-routing-0925/hardware/compact_mainboard_20260925T115919Z/evidence/ASTRA_BD_BEFORE_20260927/EMG_MainBoard_Layout.PcbDoc`
- Board SHA256: `9c3eda3627a961779e80143e63f0e576cddd5b5951a383da2c6b2cfec7b2a5fd`
- `Rules6/Data` SHA256: `195482691ae58ab5a424c5115d3cb3e96eacbfc46e2771e44129af6b186fa295`
- Candidate: `evidence/ASTRA_VC1_READY_ADDS.csv`, seven `Vc_1` tracks, each 0.20 mm wide on `Mid Layer 4` (physical L5).

`Classes6/Data` contains `Vc_1` as `M9` in both `EMG_ANALOG` net-class records, unique IDs `IXUAYIVU` and `IGFYNGTX`. No other class record containing `Vc_1` was found.

The applicable width rules are:

| Rule | Enabled | Priority | Scope 1 | Scope 2 | Minimum | Preferred | Maximum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `WIDTH_EMG_ANALOG` | TRUE | 8 | `InNetClass('EMG_ANALOG')` | `All` | `5.9055mil` (~0.15 mm) | `7.874mil` (~0.20 mm) | `15.748mil` (~0.40 mm) |
| `Width` | TRUE | 10 | `All` | `All` | `5.9055mil` (~0.15 mm) | `7.874mil` (~0.20 mm) | `19.685mil` (~0.50 mm) |

`WIDTH_EMG_ANALOG` has unique ID `NATGITDQ`, `NETSCOPE=AnyNet`, and `LAYERKIND=SameLayer`. Its saved scalar fields are `MINLIMIT`, `PREFEREDWIDTH`, and `MAXLIMIT`; no `MIDLAYER4_*` override is present. Explicit 10 mil per-layer overrides begin at `MIDLAYER5` and continue through `MIDLAYER30`, which must not be confused with physical L5 (`Mid Layer 4`). The 0.20 mm candidate is within the dominant analog rule's limits. The duplicate analog class memberships give the same result.

The critical clearance pair is the candidate diagonal `(20.675,10.925)` to `(21.675,11.925)`, width 0.20 mm, against the `NetJ_FPC1_8` via at `(21.5,10.85)`, diameter 0.60 mm. Its supplied copper gap is 0.236396 mm.

The dominant local rule is `CLR_BK13_ESCAPE_J_FPC1`: `ENABLED=TRUE`, `PRIORITY=5`, `NETSCOPE=DifferentNets`, `LAYERKIND=SameLayer`, unique ID `UQODFDFY`. Both `GAP` and `GENERICCLEARANCE` are `5.1181mil` (~0.13 mm); `OBJECTCLEARANCES` is empty, so there is no separate serialized track-via clearance entry. Both scopes are exactly:

```text
InRegionAbsolute(578.7402,409.4488,858.2677,594.4882) And (InComponent('J_FPC1') Or InNet('3V0_ANA') Or InNet('GND') Or InNet('NetJ_FPC1_8') Or InNet('Va_1') Or InNet('Vb_1') Or InNet('Vc_1'))
```

The region is approximately x=14.7..21.8 mm, y=10.4..15.1 mm. The critical pair uses the two explicitly included nets in that connector region. Its 0.236396 mm gap exceeds the local 0.13 mm limit by approximately 0.106396 mm. The first four higher-priority clearance rules are the geographically separate J_FPC5, J_FPC4, J_FPC3, and J_FPC2 escape rules, so they do not supersede the J_FPC1 rule for this pair.

Outside a matching local exception, `Vc_1` is governed by the enabled `CLR_ANALOG_025`, priority 96, unique ID `ILRNXKSV`. Scope 1 is exactly `InNetClass('EMG_ANALOG') Or InNetClass('EMG_ADC') Or InNetClass('EMG_REFERENCE')`; scope 2 is `All`. `NETSCOPE=DifferentNets`, `LAYERKIND=SameLayer`, and both `GAP` and `GENERICCLEARANCE` are `9.8425mil` (~0.25 mm), with empty `OBJECTCLEARANCES`.

The enabled priority-95 `CLR_POWER_025` also requires ~0.25 mm for `InNetClass('EMG_POWER')` versus `All`. The enabled general fallbacks, `CLR_GENERAL_020` (priority 97, `All` versus `All`, `7.874mil`) and `Clearance` (priority 98, `All` versus `All`, `10mil`), have lower priority than the analog rule. `CLR_PADS_J_FPC1_010` (priority 90, `3.937mil`) applies to pads in J_FPC1 on both sides and does not apply to the critical track-via pair. Thus the critical pair uses the local ~0.13 mm exception; the remaining candidate clearance checks retain ~0.25 mm unless a matching higher-priority exception applies.

After this frozen-BC inspection, the parent reported completed native BD verification: no new width or clearance violations, only the `Vc_1` unrouted violation removed (5 to 4 remaining), and unchanged `Rules6` bytes. That native result corroborates the saved-rule interpretation; corresponding artifacts are `DRC_C2_6L_BD.json`, `ASTRA_BD_STRUCTURE.json`, and `ASTRA_BD_DELTA.json` in `evidence/`.

This review establishes saved rule values, class membership, and the specified pair's threshold. It does not independently rerun native query matching or DRC, and does not substitute for the parent's complete geometry, connectivity, and native DRC verification.
