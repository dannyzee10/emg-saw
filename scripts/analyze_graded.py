#!/usr/bin/env python3
"""
%MVC-per-segment analysis for a `graded` / `rep` recording — the validation-campaign
companion to analyze_capture.py. Splits the recording into 5 s windows and prints the
mean %MVC of each (so a rest->25->50->75->max staircase is easy to read), plus overall
min/max and a monotonic-ish check.

    python scripts/analyze_graded.py <graded.csv> [mvc.csv]

If an MVC file is given, 100% = its peak sustained RMS (mvc_ref); otherwise the graded
file's own peak is used (self-normalized) and that is flagged. Reuses emg_features.
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import emg_features as ef                       # reuse load / mvc_ref / _bp_env


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: python scripts/analyze_graded.py <graded.csv> [mvc.csv]")
        return
    graded = args[0]
    mvc = args[1] if len(args) > 1 else None
    if not os.path.exists(graded):
        print("no such file:", graded)
        return

    meta, fs, codes = ef.load(graded)
    if mvc and os.path.exists(mvc):
        _, m_fs, m_codes = ef.load(mvc)
        ref = ef.mvc_ref(m_codes, m_fs)
        refsrc = f"MVC file {os.path.basename(mvc)}"
    else:
        ref = ef.mvc_ref(codes, fs)
        refsrc = "graded self-peak (no MVC file given)"

    _, env = ef._bp_env(codes, fs)
    pct = env / (ref + 1e-12) * 100.0
    dur = len(codes) / fs
    print(f"graded: {os.path.basename(graded)}  Trial={meta.get('Trial', '-')!r}  {dur:.1f}s  fs~{fs:.0f}")
    print(f"MVCref = {ref * 1e3:.1f} mV  ({refsrc})")

    win = max(1, int(5 * fs))
    seg = []
    print("per 5 s window  mean %MVC:")
    for i in range(0, len(pct), win):
        block = pct[i:i + win]
        if len(block) < win * 0.5:
            break
        m = float(block.mean())
        seg.append(m)
        print(f"  t={i/fs:5.1f}-{(i+len(block))/fs:5.1f}s : {m:6.1f} %MVC")
    mono = all(seg[k + 1] >= seg[k] - 5.0 for k in range(len(seg) - 1)) if len(seg) > 1 else True
    print(f"overall: min {pct.min():.1f}%  max {pct.max():.1f}%  mean {pct.mean():.1f}%  "
          f"| {'monotonic-ish' if mono else 'NON-monotonic'}")


if __name__ == "__main__":
    main()
