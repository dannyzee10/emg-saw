"""Repoint absolute references in candidate B's PrjPcb from the protected drl revision to B's own MainBoard.
Text INI edit of the project file only (no PcbDoc/SchDoc bytes are touched)."""
import os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(root, 'B_COMPACT_4L_2SIDE', 'MainBoard', 'EMG_MainBoard_Layout.PrjPcb')
old = 'C:\\Users\\PMLS\\Desktop\\emg-saw\\hardware\\pcb_layout_2026-09-23_drl\\MainBoard\\'
new = os.path.join(root, 'B_COMPACT_4L_2SIDE', 'MainBoard') + '\\'
b = open(p, 'rb').read()
enc = 'utf-8'
try:
    s = b.decode('utf-8')
except UnicodeDecodeError:
    s = b.decode('latin-1'); enc = 'latin-1'
n = s.count(old)
s2 = s.replace(old, new)
open(p, 'wb').write(s2.encode(enc))
print('replaced', n, 'reference(s) ->', new)
print('remaining drl refs:', s2.count('pcb_layout_2026-09-23_drl'))
