#!/usr/bin/env python3
"""
EMG features + exoskeleton comparison from recorded CSVs (the Python real-time equivalent
of the offline Noraxon/MATLAB pipeline).

Label each recording via the scope's **Trial** field:
  - MVC (hold max contraction):   Trial contains "mvc"
  - No-Exo task trials:           Trial contains "noexo" / "no_exo" / "no-exo"
  - Exo task trials:              Trial contains "exo"  (but not "noexo")

    python scripts/emg_features.py                # scans emg_*.csv in the repo root
    python scripts/emg_features.py <dir>          # scans a folder
    python scripts/emg_features.py a.csv b.csv    # explicit files

Per task trial it computes: mean %MVC, peak %MVC, iEMG (%MVC·s), % time > 20% MVC,
median frequency, and the fatigue slope (median-freq trend). Then it reports
No-Exo vs Exo (mean ± SD) and the reduction % — the "exoskeleton helps" summary.

%MVC is the metric that lets you compare across subjects/muscles/electrode placements
(raw µV can't). MVCref = peak of the 100 ms moving-RMS over the MVC recording.
"""
import glob
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from dsp.dsp import EmgFilters, fatigue_trend

VREF, FULL = 3.3, 4095.0
MVC_THRESH_PCT = 20.0            # sustained effort above this %MVC = fatigue/pain zone (Rohmert)


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
    fs = 1.0 / np.median(np.diff(t)) if len(t) > 1 else float(meta.get("fs", "2000").split()[0])
    return meta, fs, codes[:, 0]           # 1-channel demo: first channel


def median_freq(x, fs, band=(20.0, 450.0)):
    n = len(x)
    if n < 16:
        return 0.0
    P = np.abs(np.fft.rfft((x - x.mean()) * np.hanning(n))) ** 2
    f = np.fft.rfftfreq(n, 1.0 / fs)
    m = (f >= band[0]) & (f <= min(band[1], 0.5 * fs))
    P, f = P[m], f[m]
    c = np.cumsum(P)
    return float(f[np.searchsorted(c, c[-1] / 2)]) if c[-1] > 0 else 0.0


def _bp_env(codes, fs):
    """Return (band-passed signal, RMS envelope in volts)."""
    filt = EmgFilters(fs)
    v = codes / FULL * VREF
    bp = filt.bandpass(v.reshape(-1, 1))[:, 0]
    env = filt.rms_envelope(bp.reshape(-1, 1))[:, 0]
    return bp, env


def mvc_ref(codes, fs, win_s=1.0):
    # 100% MVC = best continuous `win_s` RMS (robust to brief spikes; standard MVC practice)
    bp, _ = _bp_env(codes, fs)
    ac = bp - bp.mean()
    n = int(fs * win_s)
    if len(ac) < n:
        return float(np.sqrt(np.mean(ac ** 2)))
    csum = np.concatenate([[0.0], np.cumsum(ac ** 2)])
    win_ms = (csum[n:] - csum[:-n]) / n         # mean-square in every 1 s window
    return float(np.sqrt(win_ms.max()))


def trial_features(codes, fs, mvcref):
    bp, env = _bp_env(codes, fs)
    pct = env / mvcref * 100.0
    # fatigue: median frequency over 1 s windows -> linear slope
    n = int(fs * 1.0)
    mdf, ts = [], []
    for i in range(0, len(bp) - n, n // 2):
        mdf.append(median_freq(bp[i:i + n], fs)); ts.append(i / fs)
    slope, _ = fatigue_trend(mdf, ts) if len(mdf) >= 2 else (0.0, 0.0)
    return {
        "mean_pctMVC": float(pct.mean()),
        "peak_pctMVC": float(pct.max()),
        "iEMG_pctMVCs": float(np.trapezoid(pct, dx=1.0 / fs)) if hasattr(np, "trapezoid")
                        else float(np.trapz(pct, dx=1.0 / fs)),
        "time_above_pct": float(np.mean(pct > MVC_THRESH_PCT) * 100.0),
        "medF_hz": median_freq(bp, fs),
        "fatigue_slope_hz_s": slope,
        "dur_s": len(codes) / fs,
    }


def classify(trial):
    t = trial.lower()
    if "mvc" in t:
        return "mvc"
    if "noexo" in t or "no_exo" in t or "no-exo" in t:
        return "noexo"
    if "exo" in t:
        return "exo"
    return "other"


def gather(args):
    if not args:
        paths = sorted(glob.glob(os.path.join(ROOT, "emg_*.csv")), key=os.path.getmtime)
    elif len(args) == 1 and os.path.isdir(args[0]):
        paths = sorted(glob.glob(os.path.join(args[0], "emg_*.csv")), key=os.path.getmtime)
    else:
        paths = args
    return paths


def main():
    paths = gather(sys.argv[1:])
    if not paths:
        print("no emg_*.csv found. Record MVC + task trials first (label via the Trial field).")
        return

    buckets = {"mvc": [], "noexo": [], "exo": [], "other": []}
    for p in paths:
        meta, fs, codes = load(p)
        buckets[classify(meta.get("Trial", ""))].append((p, meta, fs, codes))

    if not buckets["mvc"]:
        print("No MVC recording found (Trial must contain 'mvc'). Files seen:")
        for p in paths:
            print("  -", os.path.basename(p), "Trial:", load(p)[0].get("Trial", "-"))
        return

    # MVCref = mean of the MVC recordings' peak RMS
    refs = [mvc_ref(codes, fs) for _, _, fs, codes in buckets["mvc"]]
    mvcref = float(np.mean(refs))
    print(f"MVCref = {mvcref * 1e3:.1f} mV  (peak sustained RMS, from {len(refs)} MVC file(s))\n")

    rows = {"noexo": [], "exo": []}
    for cond in ("noexo", "exo"):
        for p, meta, fs, codes in buckets[cond]:
            f = trial_features(codes, fs, mvcref)
            rows[cond].append(f)
            print(f"[{cond:5}] {os.path.basename(p):28} mean {f['mean_pctMVC']:5.1f}%MVC | "
                  f"peak {f['peak_pctMVC']:5.1f}% | iEMG {f['iEMG_pctMVCs']:6.0f} %MVCs | "
                  f">20%MVC {f['time_above_pct']:4.0f}% | medF {f['medF_hz']:3.0f} | "
                  f"fatigueslope {f['fatigue_slope_hz_s']:+.2f} Hz/s")

    if rows["noexo"] and rows["exo"]:
        print("\n=== No-Exo vs Exo (mean +/- SD, n trials each) ===")
        for key, unit in [("mean_pctMVC", "%MVC"), ("iEMG_pctMVCs", "%MVCs"),
                          ("time_above_pct", "% time>20%MVC"), ("fatigue_slope_hz_s", "Hz/s")]:
            no = np.array([r[key] for r in rows["noexo"]])
            ex = np.array([r[key] for r in rows["exo"]])
            red = (no.mean() - ex.mean()) / abs(no.mean()) * 100.0 if no.mean() else 0.0
            print(f"  {key:18} NoExo {no.mean():7.2f} +/- {no.std():5.2f} | "
                  f"Exo {ex.mean():7.2f} +/- {ex.std():5.2f} {unit:14} | reduction {red:+5.1f}%")
        print("\n(reduction% = (NoExo - Exo)/NoExo; positive = the exoskeleton lowered muscle demand)")


if __name__ == "__main__":
    main()
