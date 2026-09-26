"""Create candidate C2 (and a disposable API-proof copy) from candidate B's saved state.  B is read-only here.
Copies MainBoard (project, schematics, PcbDoc, libraries, OutJob) without History/Project Logs/Outputs/checkpoints,
repoints the PrjPcb's absolute references to the new folder, and records SHA-256 of every copied file."""
import hashlib, os, shutil, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(root, 'B_COMPACT_4L_2SIDE', 'MainBoard')
SKIP = ('History', 'Project Logs for', 'Project Outputs for', 'checkpoints', '__Previews')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest().upper()


def make(dst, label):
    if os.path.exists(dst):
        print('exists, not touched:', dst)
        return
    rows = []
    for dp, dn, fn in os.walk(src):
        dn[:] = [d for d in dn if not d.startswith(SKIP)]
        rel = os.path.relpath(dp, src)
        os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for f in fn:
            if f.endswith('.PrjPcbStructure'):
                continue
            s = os.path.join(dp, f); t = os.path.join(dst, rel, f)
            shutil.copy2(s, t)
            rows.append((os.path.normpath(os.path.join(rel, f)), sha(s), sha(t)))
    prj = os.path.join(dst, 'EMG_MainBoard_Layout.PrjPcb')
    b = open(prj, 'rb').read()
    try:
        s, enc = b.decode('utf-8'), 'utf-8'
    except UnicodeDecodeError:
        s, enc = b.decode('latin-1'), 'latin-1'
    n = s.count(src + '\\')
    s = s.replace(src + '\\', dst + '\\')
    open(prj, 'wb').write(s.encode(enc))
    bad = [r for r in rows if r[1] != r[2]]
    with open(os.path.join(root, 'evidence', '%s_SETUP_MANIFEST.csv' % label), 'w') as f:
        f.write('file,sha256_source_B,sha256_copy\n')
        for r in rows:
            f.write('%s,%s,%s\n' % r)
    print(label, 'files', len(rows), 'hash mismatches', len(bad), 'prjpcb refs repointed', n,
          'remaining B refs', s.count('B_COMPACT_4L_2SIDE'))


import sys as _s
for _t in (_s.argv[1:] or ['C2', 'disposable_c2api']):
    make(os.path.join(root, 'C2_COMPACT_4L_2SIDE', 'MainBoard') if _t == 'C2' else os.path.join(root, 'evidence', _t, 'MainBoard'), _t.upper())
print('B PcbDoc', sha(os.path.join(src, 'EMG_MainBoard_Layout.PcbDoc')))
