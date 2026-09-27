# Named free-pad translation verifier, 27 September 2026

`work/astra_verify_routing_delta.py` now accepts the separately scoped option:

```text
--allow-free-pad-move TP_GND_DIG:0.2:0
```

The option checks exactly one `PAD|FREE|TP_GND_DIG` record in each native export. Only center X/Y and all four bounding-box coordinates may translate by the specified offsets, using the existing coordinate tolerance (default 0.00015 mm). All remaining native fields must match exactly, including FREE ownership, name, net, layer, hole, rotation, size and shape. Missing or ambiguous targets fail. Duplicate specifications fail.

Implementation: `work/astra_verify_routing_delta.py:202` checks the unique target and preserves its before/after native rows as evidence. At line 235, only the explicitly named FREE pad is separated from the unchanged-pad comparison; every other FREE pad and every component pad remains covered. Existing `--allow-move` component semantics remain in place. The JSON report adds `allowed_free_pad_translations` while retaining raw native record differences and input hashes. No synthetic geometry export replaces the native inputs.

For the provided testpad, the exact fixture changes center X `56.6710` to `56.8710`, bounding-box minimum X `56.1210` to `56.3210`, and maximum X `57.2210` to `57.4210`. All Y values and all non-coordinate fields remain unchanged.

Test command, run from `work/`:

```powershell
& 'C:/Users/PMLS/AppData/Local/Programs/Python/Python312/python.exe' -B -m unittest -v test_astra_verify_routing_delta
```

Observed result: **exit 0; 17 tests in 1.087 seconds; OK**. The eight new test methods cover the exact move, wrong net/size/layer/hole/rotation/shape, wrong center/bounding box, another FREE pad change, a same-named component pad change, duplicate target records, missing/renamed/component-owned targets, missing or duplicate allowances, and CLI/report integration. All nine existing component-translation tests also passed. The tests use small temporary export fixtures and do not load production board geometry.

This subtask changed only the verifier, its focused tests and this note. It did not launch CAD or a router, move any pad, or change any design/rule. Native readback and DRC of a subsequent authorized move remain separate evidence. Repository graph refresh remains with root.
