# Independent BH to BI saved-file comparison

Read-only comparison using immutable snapshots:

- BH: `ASTRA_BH_BEFORE_BI_20260927/EMG_MainBoard_Layout.PcbDoc`, SHA-256 `01e72cb0222f4f824c61f66a0a262fb08bdabdfc21d32b90e91cd4a4f28fd1e1`.
- BI: `ASTRA_BI_BEFORE_BJ_20260927/EMG_MainBoard_Layout.PcbDoc`, SHA-256 `368ac3f5802f522e992d59b28ce9e63624be7260affbe8cebf1a7dc4df8c33d3` (matches the BI coverage/audit snapshot).

**Exact rule and DRC-options verification passes. Whole-file design-content preservation remains unresolved.**

`ASTRA_BH_BI_RULE_OPTIONS_DELTA.json` proves all 147 Rules6 records are preserved except the unique VIA_STD_060_030 record's MINWIDTH `23.622mil` -> `17.7165mil` (0.60 -> 0.45 mm) and MINHOLEWIDTH `11.811mil` -> `7.874mil` (0.30 -> 0.20 mm). Raw target-record content outside those two field values is identical; all other rule records are byte-identical, including scopes, enabled states, priorities and identities.

The saved DRC options add exactly categories 9 and 11 to RULESETTOCHECK, remove none, and preserve all other option bytes. Board6 differences are limited to TIME and viewport keys VP.HX/HY/LX/LY. All other parsed Board6 parameters are identical. Across the OLE document, 150 complete streams are byte-identical, including unchanged tracks, nets, components, classes and rule/options headers.

The strict helper deliberately retains six raw-stream failures:

| Stream | Same before/after size | Changed bytes by position |
|---|---:|---:|
| Pads6/Data | 214,180 | 12,963 |
| Regions6/Data | 420,959 | 234,086 |
| ShapeBasedRegions6/Data | 670,344 | 230,351 |
| Texts/Data | 964 | 294 |
| Texts6/Data | 159,676 | 23,987 |
| Vias6/Data | 153,220 | 7,550 |

These are not established to be only DRC status bits. Pad/via changes include repeated 16-byte identifier patterns. Record-framing diagnostics agree with native Headers for Regions6, ShapeBasedRegions6 and Vias6. They show 124/124/470 records respectively; only 9/122/0 entire records remain identical as multisets. Thus reordered identical records alone do not explain all differences. No binary field semantics or harmlessness is inferred, and these differences are not waived.

Native BH-to-BI export equality separately proves the exported geometry fields. It cannot attest unexported pad, via, region or text metadata. The helper's exit 1 is expected for the six unresolved streams and must not be presented as unconditional design preservation.

New helper `work/astra_verify_via_rule_delta.py` only reads saved files and writes JSON evidence. Six focused regressions passed, covering authorized changes, scope/identity/other-rule corruption, ambiguous targets and duplicate fields, missing/extra/removed DRC categories, preserved versus changed Board6 design parameters, and strict rejection of unrelated geometry-stream changes.

```powershell
python -B -m unittest test_astra_verify_via_rule_delta.py -v
python -B astra_verify_via_rule_delta.py --before ../evidence/ASTRA_BH_BEFORE_BI_20260927/EMG_MainBoard_Layout.PcbDoc --after ../evidence/ASTRA_BI_BEFORE_BJ_20260927/EMG_MainBoard_Layout.PcbDoc --output ../evidence/ASTRA_BH_BI_RULE_OPTIONS_DELTA.json
```

No native CAD calls or writes were made by this review.
