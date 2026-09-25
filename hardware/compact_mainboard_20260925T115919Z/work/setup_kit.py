"""Copy the proven native-automation kit from the routing revision into this compact workspace and repoint
every absolute path to candidate B (work / evidence / B MainBoard).  Baseline A is never a target."""
import os, shutil
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
src = os.path.join(os.path.dirname(root), 'pcb_layout_2026-09-24_routing', 'work')
old_base = 'C:\\Users\\PMLS\\Desktop\\emg-saw\\.claude\\worktrees\\pcb-routing-0925\\hardware\\pcb_layout_2026-09-24_routing'
rep = [(old_base + '\\work', os.path.join(root, 'work')),
       (old_base + '\\evidence', os.path.join(root, 'evidence')),
       (old_base + '\\MainBoard', os.path.join(root, 'B_COMPACT_4L_2SIDE', 'MainBoard'))]
files = ['run_native.ps1', 'run_wait.ps1', 'win.ps1', 'export_geometry.pas', 'run_drc.pas', 'parse_drc.py',
         'apply_ops_v6.pas', 'discard_unsaved.pas', 'show_board.pas', 'probe_open_docs.pas', 'geom.py', 'render_area.py']
for f in files:
    b = open(os.path.join(src, f), 'rb').read()
    enc = 'utf-8'
    try:
        s = b.decode('utf-8')
    except UnicodeDecodeError:
        s = b.decode('latin-1'); enc = 'latin-1'
    for o, n in rep:
        s = s.replace(o, n)
    if old_base in s or 'pcb_layout_2026-09-23_drl' in s.replace("'evidence/inputs/CLASSES.txt'", ''):
        raise SystemExit(f'unreplaced reference left in {f}')
    open(os.path.join(here, f), 'wb').write(s.encode(enc))
    print('kit', f)
os.makedirs(os.path.join(root, 'evidence', 'inputs'), exist_ok=True)
shutil.copy(os.path.join(os.path.dirname(src), 'evidence', 'inputs', 'CLASSES.txt'), os.path.join(root, 'evidence', 'inputs', 'CLASSES.txt'))
for n in ('export_geometry', 'run_drc', 'show_board', 'probe_open_docs'):
    open(os.path.join(here, n + '.PrjScr'), 'w', newline='').write(f'[Design]\r\nVersion=1.0\r\n[Document1]\r\nDocumentPath={n}.pas\r\n')
print('done; root', root)
