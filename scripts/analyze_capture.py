#!/usr/bin/env python3
"""
Analyze a recorded EMG CSV: per-channel RMS, pk-pk, median & mean frequency, mains ratio,
spectral centroid, and the lead-off verdict. Reads the metadata header for Trial context.

    python scripts/analyze_capture.py [path/to/emg_*.csv]   # default: newest emg_*.csv in cwd
"""
import glob
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from dsp.dsp import leadoff_report, mean_frequency

VREF, FULL = 3.3, 4095.0


def load(path):
    meta, rows, hdr = {}, [], None
    with open(path, encoding="utf-8") as f:
        for ln in f:
            s = ln.strip()
            if s.startswith("#"):
                if ":" in s:
                    k, v = s[1:].split(":", 1)
                    meta[k.strip()] = v.strip()
            elif s.startswith("t_s"):
                hdr = s.split(",")
            elif s and hdr:
                rows.append([float(x) for x in s.split(",")])
    data = np.array(rows)
    t, codes = data[:, 0], data[:, 1:]
    fs = 1.0 / np.median(np.diff(t)) if len(t) > 1 else float(meta.get("fs", 2000))
    return meta, fs, codes


def median_freq(ac, fs, band=(20.0, 450.0)):
    n = len(ac)
    P = np.abs(np.fft.rfft((ac - ac.mean()) * np.hanning(n))) ** 2
    f = np.fft.rfftfreq(n, 1.0 / fs)
    m = (f >= band[0]) & (f <= min(band[1], 0.5 * fs))
    P, f = P[m], f[m]
    c = np.cumsum(P)
    return float(f[np.searchsorted(c, c[-1] / 2)]) if c[-1] > 0 else 0.0


def main():
    path = (sys.argv[1] if len(sys.argv) > 1
            else max(glob.glob(os.path.join(ROOT, "emg_*.csv")), key=os.path.getmtime, default=None))
    if not path or not os.path.exists(path):
        print("no CSV found (give a path, or record one first)")
        return
    meta, fs, codes = load(path)
    dur = codes.shape[0] / fs
    print(f"== {os.path.basename(path)} ==  Trial: {meta.get('Trial', '-')!r}   "
          f"fs~{fs:.0f} Hz   N={codes.shape[0]}  ({dur:.1f}s)")
    for c in range(codes.shape[1]):
        volts = codes[:, c] / FULL * VREF
        ac = volts - volts.mean()
        rms = float(np.sqrt(np.mean(ac * ac))) * 1e3
        pk = float(np.ptp(volts)) * 1e3
        dcv = float(volts.mean())
        state, q, m = leadoff_report(volts, fs, VREF)
        print(f"  ch{c+1}: RMS {rms:7.1f} mV | pk-pk {pk:7.1f} mV | DC {dcv:4.2f} V | "
              f"medF {median_freq(ac, fs):4.0f} | meanF {mean_frequency(ac, fs):4.0f} Hz | "
              f"mains {m['mains'] * 100:3.0f}% | centroid {m['centroid']:4.0f} Hz | "
              f"--> {state.upper()} (q{q:.0f})")


if __name__ == "__main__":
    main()
