"""
Display-side signal processing (done on the laptop, so you can tweak live —
same philosophy as Noraxon MR4 where raw + processed views are just view options).

Filters are designed once for the given fs. We filter the whole retained buffer
each redraw and show the tail; keeping the buffer longer than the visible window
hides filter edge-transients. For visualization that is exact enough and simple.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, iirnotch, sosfiltfilt, filtfilt


class EmgFilters:
    def __init__(self, fs: float):
        self.fs = fs
        self._design()

    def _design(self):
        fs = self.fs
        ny = fs / 2.0
        hp = 20.0 / ny
        lp = min(450.0, 0.9 * ny) / ny
        self.bp_sos = butter(4, [hp, lp], btype="band", output="sos")
        self.notch = {}
        for f0 in (50.0, 60.0):
            if f0 < ny:
                b, a = iirnotch(f0 / ny, Q=30.0)
                self.notch[int(f0)] = (b, a)

    def bandpass(self, x: np.ndarray) -> np.ndarray:
        if x.shape[0] < 20:
            return x
        return sosfiltfilt(self.bp_sos, x, axis=0)

    def apply_notch(self, x: np.ndarray, f0: int) -> np.ndarray:
        if f0 not in self.notch or x.shape[0] < 20:
            return x
        b, a = self.notch[f0]
        return filtfilt(b, a, x, axis=0)

    def rms_envelope(self, x: np.ndarray, win_ms: float = 100.0) -> np.ndarray:
        """Linear envelope: moving-RMS of the (already band-passed) signal."""
        n = max(1, int(self.fs * win_ms / 1000.0))
        if x.shape[0] < n:
            return np.abs(x)
        kernel = np.ones(n) / n
        out = np.empty_like(x, dtype=float)
        sq = x.astype(float) ** 2
        for c in range(x.shape[1]):
            out[:, c] = np.sqrt(np.convolve(sq[:, c], kernel, mode="same"))
        return out


def leadoff_status(x, fs, vref=3.3, mains_hz=50.0,
                   rail_frac=0.20, mains_dom=0.5, amp_floor=0.02):
    """Heuristic electrode-connection state from a RAW (un-notched, absolute-volt)
    single-channel window. No extra hardware — infers the state from signal shape:

        'open' : a large fraction of samples sit near 0 V or Vref (disconnected /
                 shorted -> the AD8237 output rails).
        'poor' : a sizeable signal dominated by mains (50/60 Hz) -> a floating,
                 high-impedance electrode acting as a mains antenna (gotcha #7).
        'good' : neither -> real EMG, or a quiet connected baseline.

    Must be fed the raw signal BEFORE the notch (mains info) and BEFORE band-pass
    (rail info). Thresholds are heuristic and tunable; this is a sanity indicator,
    not a true impedance (kOhm) measurement — that arrives with the ADS1299 LOFF (M4).
    """
    x = np.asarray(x, dtype=float)
    n = x.shape[0]
    if n < 32:
        return "good"
    # 1) rail / saturation fraction on the absolute-volt signal (0..vref)
    margin = 0.03 * vref
    rail = float(np.mean((x < margin) | (x > vref - margin)))
    if rail > rail_frac:
        return "open"
    # 2) mains dominance: mains-band power vs total AC power (needs un-notched signal)
    if float(np.ptp(x)) <= amp_floor:
        return "good"                       # quiet, connected baseline
    xc = x - x.mean()
    w = np.hanning(n)
    P = np.abs(np.fft.rfft(xc * w)) ** 2
    f = np.fft.rfftfreq(n, 1.0 / fs)

    def _band(lo, hi):
        m = (f >= lo) & (f < hi)
        return float(P[m].sum())

    mains = sum(_band(mains_hz * k - 2.0, mains_hz * k + 2.0)
                for k in (1, 2, 3) if mains_hz * k < fs / 2.0)
    total = _band(1.0, 0.49 * fs) + 1e-15
    if mains / total > mains_dom:
        return "poor"
    return "good"
