"""Make a fresh-named runnable copy of a native script (Altium caches loaded script projects by name).
usage: python mkrun.py <script.pas> <prefix>  -> prints the .PrjScr basename to pass to run_wait.ps1"""
import os, shutil, sys, time
here = os.path.dirname(os.path.abspath(__file__))
src, prefix = sys.argv[1], sys.argv[2]
tag = time.strftime('%H%M%S')
base = '%s_%s' % (prefix, tag)
shutil.copy2(os.path.join(here, src), os.path.join(here, base + '.pas'))
open(os.path.join(here, base + '.PrjScr'), 'w').write('[Design]\nVersion=1.0\n[Document1]\nDocumentPath=%s.pas\n' % base)
print(base + '.PrjScr')
