"""Run one NEGOTIATE box several times SEQUENTIALLY (one process at a time) with different routing-order seeds / zone
margins; stop at the first accepted result.  usage:
python neg_sweep.py STATE TAG "RNG:MARGIN,RNG:MARGIN,..." KEY=VALUE ...   (KEY=VALUEs as for run_repair.py)
Each try writes evidence/<TAG>_<n>_ADDS/DELS.csv and its own log; the winner is copied to <TAG>_ADDS/DELS.csv."""
import os, pathlib, shutil, subprocess, sys

state, tag, tries = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
extra = sys.argv[4:]
log_dir = os.environ.get('NEG_LOG_DIR', str(pathlib.Path(__file__).resolve().parent.parent / 'evidence' / 'routing_logs'))
pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)
for n, tr in enumerate(tries):
    rng, marg = tr.split(':')
    t = f'{tag}_{n}'
    with open(f'{log_dir}/{t.lower()}.log', 'w') as lg:
        subprocess.call([sys.executable, 'run_repair.py', state, t, f'NEG_RNG={rng}', f'NEG_MARGIN={marg}'] + extra,
                        stdout=lg, stderr=subprocess.STDOUT)
    txt = open(f'{log_dir}/{t.lower()}.log').read()
    res = [l for l in txt.splitlines() if l.startswith('NEGOTIATE ')]
    print(f'try {n} rng {rng} margin {marg}: {res[-1] if res else "no result"}', flush=True)
    if res and 'accepted' in res[-1]:
        for k in ('ADDS', 'DELS'):
            shutil.copy(f'../evidence/{t}_{k}.csv', f'../evidence/{tag}_{k}.csv')
        print(f'WINNER {t}', flush=True)
        break
else:
    print('no try accepted', flush=True)
