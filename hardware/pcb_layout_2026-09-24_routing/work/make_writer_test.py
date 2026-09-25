"""Make a disposable-copy variant of a writer script under a UNIQUE name (Altium keeps loaded scripts in
memory, so re-running the same name can execute stale text), to prove compile/run before touching the
routing board.  usage: python make_writer_test.py apply_ops_bN.pas OPS_TEST_xx.txt
Prints the generated script base name (wt_HHMMSS)."""
import shutil, sys, time
src, opsname = sys.argv[1], sys.argv[2]
tag = 'wt_' + time.strftime('%H%M%S')
D = r'C:\Users\PMLS\Desktop\emg-saw\handoff_opus55\capability_test' + '\\'
R = r'C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing' + '\\'
s = open(src, encoding='utf-8').read()
reps = [
    (f"Const PcbPath='{R}MainBoard\\EMG_MainBoard_Layout.PcbDoc';", f"Const PcbPath='{D}disposable\\DISPOSABLE_COPY.PcbDoc';"),
    (f"Const OpsFile='{R}work\\OPS.txt';", f"Const OpsFile='{D}OPS_TEST.txt';"),
    (f"Const OutFile='{R}evidence\\APPLY_OPS_LOG.txt';", f"Const OutFile='{D}APPLY_OPS_TEST_LOG.txt';"),
    ("If D.Modified Then Raise('PCB has unsaved changes - refusing to write');", "// disposable test: unsaved state tolerated"),
]
for a, b in reps:
    assert a in s, a
    s = s.replace(a, b)
open(D + tag + '.pas', 'w', encoding='utf-8').write(s)
open(D + tag + '.PrjScr', 'w').write("[Design]\r\nVersion=1.0\r\n[Document1]\r\nDocumentPath=" + tag + ".pas\r\n")
shutil.copy(D + opsname, D + 'OPS_TEST.txt')
print(tag)
