# Exact CL_4 translation verification

`work/astra_verify_routing_delta.py` now accepts explicit, repeatable
`--allow-move REF:DX_MM:DY_MM`. For BC, the allowance is `CL_4:-3.1:0`.

The verifier compares the original before and after native rows directly. It
requires exactly one component record and the same nonempty pad multiset for the
named component. Only component/pad centers and bounding-box coordinates may
translate by the specified displacement, within the existing 0.00015 mm numeric
tolerance. Net names, component and pad identities, layers, rotation, copper
dimensions, holes, shapes, and every other exported field remain exact. All other
component/pad records and fixed geometry retain their previous exact comparison.
The copper addition/deletion checks are unchanged.

`allowed_component_translations` contains each checked translation and the actual
native before/after rows. `unchanged` explicitly covers the remaining records;
`raw_native_record_changes` preserves the complete original differences, including
the authorized move. Existing input paths and SHA-256 hashes are retained. No
projected export is written or labeled as native.

Validation: `python -B -m unittest -v test_astra_verify_routing_delta` passed all
9 tests in 0.666 s. Fixtures cover the exact allowed move, rejection without an
allowance, changed pad net, other component/pad movement, wrong displacement,
rotation/size/layer changes, missing/duplicate pads, unknown/duplicate allowances,
unplanned copper changes, and preservation of CLI input bytes, paths, and hashes.

From `work/` after the native BC geometry export finishes:

```powershell
& 'C:/Users/PMLS/AppData/Local/Programs/Python/Python312/python.exe' -B astra_verify_routing_delta.py --before ../evidence/GEOMETRY_C2_6L_BB.txt --after ../evidence/GEOMETRY_C2_6L_BC.txt --adds ../evidence/ASTRA_CH4_READY_ADDS.csv --dels ../evidence/ASTRA_CH4_READY_DELS.csv --allow-move CL_4:-3.1:0 --output ../evidence/ASTRA_BC_DELTA.json
```

This is verifier preparation only. No CAD files or native processes were opened
or changed, and no actual BC verification result is claimed here. Native geometry
still omits net objects, rule definitions, stackup, via spans, and full component
body geometry; their separate checks and native DRC remain necessary.
