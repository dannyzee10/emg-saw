"""Instantiate a *_T.pas template for a target copy and emit a fresh-named runnable .PrjScr.
usage: python mkvariant.py <template_T.pas> <prefix> <target: C2|DISP|B> <logname>"""
import os, sys, time
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
tpl, prefix, target, logname = sys.argv[1:5]
ROOTS = {'C2': os.path.join(root, 'C2_COMPACT_4L_2SIDE', 'MainBoard') + '\\',
         'DISP': os.path.join(root, 'evidence', 'disposable_c2api', 'MainBoard') + '\\',
         'DISP2': os.path.join(root, 'evidence', 'disposable_c2api2', 'MainBoard') + '\\',
         'B': os.path.join(root, 'B_COMPACT_4L_2SIDE', 'MainBoard') + '\\'}
pcb = 'EMG_MainBoard_Layout.PcbDoc'
others = ';'.join(v + pcb for k, v in ROOTS.items() if k != target)
s = open(os.path.join(here, tpl), encoding='utf-8').read()
s = s.replace('@ROOT@', ROOTS[target]).replace('@LOG@', os.path.join(root, 'evidence', logname)).replace('@OTHERS@', others).replace('@MODE@', os.environ.get('SWAP_MODE', 'MIXED')).replace('@OPS@', os.environ.get('OPS_FILE', 'C2_OPS.txt'))
base = '%s_%s' % (prefix, time.strftime('%H%M%S'))
open(os.path.join(here, base + '.pas'), 'w', encoding='utf-8').write(s)
open(os.path.join(here, base + '.PrjScr'), 'w').write('[Design]\nVersion=1.0\n[Document1]\nDocumentPath=%s.pas\n' % base)
print(base + '.PrjScr')
