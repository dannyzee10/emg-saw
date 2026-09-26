"""Template-ise the proven read-only B scripts (geometry export, 3D-body export, batch DRC) for any copy.
Progress writes go to <out>.part; the polled result file is written once at the end (no file-sharing race)."""
import os, re
here = os.path.dirname(os.path.abspath(__file__))
BPCB = r"C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\B_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc"
for src, dst in (('export_geometry.pas', 'export_geometry_T.pas'), ('export_bodies.pas', 'export_bodies_T.pas'), ('run_drc.pas', 'run_drc_T.pas')):
    s = open(os.path.join(here, src), encoding='utf-8').read()
    assert BPCB in s, src
    s = s.replace(BPCB, '@ROOT@EMG_MainBoard_Layout.PcbDoc')
    s = re.sub(r"Const OutFile='[^']*';", "Const OutFile='@LOG@';", s)
    if src == 'run_drc.pas':
        s = re.sub(r"Const Report='[^']*';", "Const Report='@LOG@.html';", s)
    # interim saves -> .part ; the final save in the Finally block stays on OutFile
    parts = s.rsplit('L.SaveToFile(OutFile);', 1)
    s = parts[0].replace('L.SaveToFile(OutFile);', "L.SaveToFile(OutFile+'.part');") + 'L.SaveToFile(OutFile);' + parts[1]
    open(os.path.join(here, dst), 'w', encoding='utf-8').write(s)
    print(dst, 'interim->part', s.count("OutFile+'.part'"), 'final', s.count('L.SaveToFile(OutFile);'))
