"""Write final routing evidence only; never edits CAD or launches Altium."""
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / 'evidence'
BOARD = ROOT / 'C2_COMPACT_4L_2SIDE' / 'MainBoard'
def read(name):
    return json.loads((EV / name).read_text(encoding='utf-8'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

pcb = BOARD / 'EMG_MainBoard_Layout.PcbDoc'
rules = read('ASTRA_BJ_ALL_FREE_TRACE_RULES.json')
delta = read('ASTRA_BJ_DELTA.json')
drc = read('DRC_C2_6L_BJ.json')
coverage = read('ASTRA_BJ_DRC_COVERAGE.json')
independent = read('ASTRA_BJ_INDEPENDENT_REVIEW.json')
assert rules['passed'] and delta['passed'] and independent['passed']
assert sha(pcb) == rules['inputs']['pcb_sha256'] == coverage['pcb_sha256']
assert not coverage['required_batch_missing']
assert int(drc['total']) == 246 and len(drc['details']) == 246
counts = Counter(v.split(':')[0] for v in drc['details'])
assert counts == {'Silk To Solder Mask Clearance Constraint': 157,
                  'Silk To Silk Clearance Constraint': 84,
                  'Board Outline Clearance(Outline Edge)': 5}
assert rules['primitive_counts'] == {'VIA': 470, 'TRACK': 2281}
source = []
for path in sorted(BOARD.iterdir()):
    if path.suffix.lower() not in ('.schdoc', '.prjpcb'):
        continue
    original = EV / 'ASTRA_BFS_BEFORE_BG_20260927' / path.name
    assert original.is_file() and sha(original) == sha(path), path
    source.append({'file': str(path), 'sha256': sha(path), 'unchanged_since_BFS': True})
assert len(source) == 9
assert 'CurrentVariant=PROTO_1_REMOTE_NTC' in (BOARD/'EMG_MainBoard_Layout.PrjPcb').read_text()
manifest = {'created_local': datetime.now().isoformat(), 'pcb': str(pcb),
            'pcb_sha256': sha(pcb), 'variant': 'PROTO_1_REMOTE_NTC',
            'source_files': source, 'evidence': []}
names = ['GEOMETRY_C2_6L_BJ.txt', 'DRC_C2_6L_BJ.txt.html',
         'DRC_C2_6L_BJ.json', 'ASTRA_BJ_ALL_FREE_TRACE_RULES.json',
         'ASTRA_BJ_DELTA.json', 'ASTRA_BJ_DRC_COVERAGE.json',
         'ASTRA_BJ_INDEPENDENT_REVIEW.json', 'ASTRA_BJ_TRACE_SHAPE_INVENTORY.json',
         'ASTRA_BI_ANTENNA_GRAPH.json', 'ASTRA_BH_BI_RULE_OPTIONS_DELTA.json']
for name in names:
    path = EV/name
    manifest['evidence'].append({'file': name, 'sha256': sha(path)})
(EV/'ASTRA_BJ_FINAL_HASHES.json').write_text(json.dumps(manifest, indent=2)+'\n')
report = f'''# Routing completion and all-trace check — BJ, 27 September 2026

**Routing complete; not fabrication release.** The saved native Altium PCB has zero unrouted connections and zero net-antenna violations. Your manual Channel 1 trace edit is retained.

## Open this project

`{BOARD / 'EMG_MainBoard_Layout.PrjPcb'}`

PCB: `{pcb}`

Variant: `PROTO_1_REMOTE_NTC`. The historical folder name contains `4L`; the actual saved board has six copper layers. This is the existing active routing worktree, not the September 16 schematic baseline or a scratch PCB.

Final PCB SHA256: `{sha(pcb)}`.

## Changes actually made

| Checkpoint | Change | Native evidence |
|---|---|---|
| BFS | Saved/reopened your manual NetJ_FPC1_8 edit; complete readback matched its unsaved export | ASTRA_SAVE_USER_BFS.txt; ASTRA_USER_EDIT_BEFORE_BG_REVIEW.json |
| BG | Routed WIFI_SPI_CS; 82 tracks/12 vias added, 40 tracks/8 vias removed; preserved power-feed connectivity at original width thresholds | ASTRA_APPLY_BG_REBASED.txt; ASTRA_BG_INDEPENDENT_REVIEW.json |
| BGM | Moved free GND test pad TP_GND_DIG by +0.20 mm X only, to (56.871,44.829); no circuit/pad-size change | ASTRA_MOVE_TP_BGM.txt; ASTRA_BGM_DELTA.json |
| BH | Routed MCU_WIFI_UART_TX with explicit via-center joins; 23 tracks/6 vias added, nothing deleted | ASTRA_APPLY_BH_CENTERED.txt; ASTRA_BH_INDEPENDENT_REVIEW.json |
| BI | Via rule minimum diameter/hole 0.60/0.30 → 0.45/0.20 mm; preferred/max remain 0.60/0.30. Enabled native Routing Layers and Routing Via Style batch checks | ASTRA_ALIGN_VIA_BI.txt; ASTRA_READ_VIA_BI.txt; ASTRA_BI_DRC_COVERAGE.json |
| BJ | Removed bounded dangling ends on seven nets, preserving necessary junctions; 19 tracks replaced by eight, no vias/pads/components removed | ASTRA_APPLY_BJ.txt; ASTRA_BJ_DELTA.json; ASTRA_BI_ANTENNA_GRAPH.json |

Both last interfaces now connect their actual assigned pins: R_SPI_CS.1 / U_WIFI1.24 / R_WIFI_CS_PD.1, and R_WIFI_UART_TX_LINK.2 / U_MCU1.92. The previously approved MCU UART pin assignment was preserved.

Backups were saved before every CAD mutation group: ASTRA_BG_BEFORE_20260927 (original BF), ASTRA_BFS_BEFORE_BG_20260927, ASTRA_BG_BEFORE_BGM_20260927, ASTRA_BGM_BEFORE_BH_20260927, ASTRA_BH_BEFORE_BI_20260927 and ASTRA_BI_BEFORE_BJ_20260927. No git reset, cleanup, commit or push was performed.

## Actual final checks

Native Altium save/reopen, polygon rebuild, completed batch DRC and geometry export all completed. The DRC processing Boolean returned False; the completed HTML report and individual rule rows establish the actual results below.

| Check | Final result |
|---|---:|
| Unrouted connections | 0 |
| Short circuit / copper clearance / width violations | 0 / 0 / 0 |
| Routing-layer / via-style violations | 0 / 0 |
| Net antennae / component clearance violations | 0 / 0 |
| Free copper tracks checked for width and allowed layer | 2,281 / 2,281 pass |
| Vias checked against saved diameter/hole rule | 470 / 470 pass |
| Independent width/layer/via checks | 5,032 pass; no unresolved scopes |
| Native via through-layer readback | 470 through vias; zero outside aligned envelope |
| Silkscreen-to-mask findings | 157 |
| Silkscreen-to-silkscreen findings | 84 |
| Outline findings, all overlay text/graphics | 5 |
| Total remaining native DRC findings | 246 |

Ten additional free TRACK records belong to Mechanical Layer 4 and are explicitly excluded from copper checks. No netless copper tracks or unresolved free copper arcs were omitted. Native DRC covers footprint copper and repoured polygons; the independent free-track checker is not a replacement for those native checks.

All 231 component placements and 812 pad records remain unchanged by the routing stages, except the explicitly allowed 0.20 mm free test-pad move. All eight SchDocs and the PrjPcb match the protected BFS hashes. The seven user-edited trace records, including its zero-length segment, remain intact. The AFE, MCU/RF schematics, remote NTC variant, connector mappings and circuit architecture were not edited. Existing connected power paths were checked at their original width thresholds before rerouting or trimming; this is a preservation test, not an absolute current-capacity guarantee.

## Remaining work and limits

- The 246 remaining DRC items are overlay finishing work. Exact outline objects and coordinates are listed in ASTRA_ALL_FREE_TRACE_AUDIT.md. They are not copper outline violations. No rule was weakened to hide them.
- Shape inventory finds one zero-length user-edited trace at export precision and three surplus exact duplicate GND records. They produce no current electrical DRC violation and were left unchanged; they are recorded in ASTRA_BJ_TRACE_SHAPE_INVENTORY.json.
- Via-in-pad provisions still require an assembler-qualified filled/capped or otherwise approved process. Tenting is not equivalent to filling. There is no active native ViasUnderSMD rule; the generic differential-pair routing check remains outside batch and no new differential pair was added.
- Exact rules/options comparison proves only the two via minimum fields and batch kinds 9/11 changed in BI. Strict raw binary comparison also records opaque pad/via/region/text serialization differences; it is not reported as bit-identical. Native geometry, mapping, through-via, rule and connectivity readbacks support the stated electrical results; full opaque-field equivalence was not established.
- Width-rule compliance and preserved power paths do not establish absolute current capacity, impedance, RF return-path quality, electrode performance, battery safety or fabrication qualification. Final DFM, stack/impedance, antenna/enclosure, assembly, and hardware tests remain separate release gates. No fabrication or body-use approval is implied.

Published JLCPCB six-layer capabilities include 1.2 mm boards and via geometry smaller than the selected 0.45/0.20 and 0.50/0.30 mm pairs. These selected pairs satisfy the published hole/annular geometry limits; the exact stack/order and via-in-pad process still need fabrication review. Sources: [six-layer capabilities](https://jlcpcb.com/resources/6-layer-pcbs), [manufacturing capabilities](https://jlcpcb.com/capabilities/pcb-capabilities).

## Evidence and next operation

Use DRC_C2_6L_BJ.txt.html, GEOMETRY_C2_6L_BJ.txt, ASTRA_BJ_INDEPENDENT_REVIEW.json, ASTRA_BJ_ALL_FREE_TRACE_RULES.json, ASTRA_BJ_DRC_COVERAGE.json and ASTRA_BJ_FINAL_HASHES.json. Earlier BF/BG/BH reports describe earlier states and their open-count/coverage conclusions are superseded here.

Next task: a separately backed-up silkscreen/overlay finishing pass addressing the 246 remaining entries while preserving BJ copper and re-running native DRC. No further routing is needed to close the current netlist.
'''
(EV/'ASTRA_ROUTING_COMPLETE_BJ_20260927.md').write_text(report, encoding='utf-8')
resume = EV/'ROUTING_RESUME.md'
prior = resume.read_text(encoding='utf-8')
heading = '# CURRENT: BJ — routing complete and all-trace checks, 27 September 2026\n\n'
assert not prior.startswith(heading), 'Do not duplicate final resume entry'
resume.write_text(heading + f'''- Native DRC: zero opens/antennae/shorts/clearance/width/layer/via errors. Remaining246 =157silk-mask+84silk-silk+5overlay-outline.
- Current savedPCB hash `{sha(pcb)}`. Altium left open on this saved PCB; inspect live state before any new writer.
- All2281freecoppertracks and470vias pass5032independent width/layer/via checks. Via rule min.45/.20; preferred/max.60/.30. Native batch kinds9/11 are now enabled; previous coverage gap closed.
- User edit retained. TP_GND_DIG +.20mmX; no schematic/project changes. Remaining raw-serialization and manufacturing limitations are documented, not waived.
- Authoritative summary: ASTRA_ROUTING_COMPLETE_BJ_20260927.md; finalnativebase GEOMETRY_C2_6L_BJ.txt / DRC_C2_6L_BJ.json. All approved adds/deletes named in report. Do not apply old candidates again.
- Next bounded work: overlay finishing. No current unrouted task remains. No fabrication release.

---

''' + prior, encoding='utf-8')
print(json.dumps({'report': str(EV/'ASTRA_ROUTING_COMPLETE_BJ_20260927.md'),
                  'pcb_sha256': sha(pcb), 'remaining_unrouted': 0,
                  'remaining_drc': 246, 'preserved_schematic_project_files': len(source)}, indent=2))
