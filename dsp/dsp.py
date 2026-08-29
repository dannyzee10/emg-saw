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


def leadoff_report(x, fs, vref=3.3, mains_hz=50.0,
                   rail_frac=0.20, mains_dom=0.5, amp_floor=0.02, emg_hi=250.0):
    """Analyse one RAW (un-notched, absolute-volt) single-channel window; return
    ``(state, quality, metrics)``:

        state   : 'open' (railed near 0/Vref -> disconnected/shorted), 'poor'
                  (mains-dominated -> floating high-impedance electrode / antenna),
                  or 'good' (real EMG or a quiet connected baseline).
        quality : 0-100 signal-quality index (100 = clean, 0 = railed).
        metrics : {'rail': frac railed, 'mains': mains/total power, 'dc': |offset|/half-scale}.

    Must be fed the signal BEFORE the notch (mains info) and BEFORE band-pass (rail info).
    Heuristic, not a kOhm impedance measurement (that arrives with the ADS1299 LOFF, M4).
    With a working DRL, a connected electrode has its mains actively cancelled, so
    residual mains is a strong 'bad electrode' cue.
    """
    x = np.asarray(x, dtype=float)
    n = x.shape[0]
    if n < 32:
        return "good", 100.0, {"rail": 0.0, "mains": 0.0, "dc": 0.0, "centroid": 0.0}
    margin = 0.03 * vref
    rail = float(np.mean((x < margin) | (x > vref - margin)))
    dc = float(abs(x.mean() - vref / 2.0) / (vref / 2.0 + 1e-12))   # 0=centered, 1=at rail
    ptp = float(np.ptp(x))
    mains_ratio = 0.0
    centroid = 0.0
    if ptp > amp_floor:
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
        mains_ratio = mains / total
        # spectral centroid over the EMG band: real sEMG sits ~50-150 Hz; a floating pin's
        # broadband/high-freq noise pushes it far up -> a "not physiological EMG" cue.
        bm = (f >= 20.0) & (f <= min(0.49 * fs, 500.0))
        pw = float(P[bm].sum())
        centroid = float((f[bm] * P[bm]).sum() / pw) if pw > 0 else 0.0

    if rail > rail_frac:
        state = "open"
    elif ptp > amp_floor and (mains_ratio > mains_dom or centroid > emg_hi):
        state = "poor"
    else:
        state = "good"

    quality = 100.0 * (1.0 - min(1.0, rail)) / (1.0 + 3.0 * mains_ratio)
    if centroid > emg_hi:
        quality *= max(0.15, (emg_hi / centroid) ** 2)   # non-physiological spectrum
    quality = float(max(0.0, min(100.0, quality)))
    return state, quality, {"rail": rail, "mains": mains_ratio, "dc": dc, "centroid": centroid}


def leadoff_status(x, fs, vref=3.3, mains_hz=50.0, **kw):
    """Back-compatible wrapper: just the state string from :func:`leadoff_report`."""
    return leadoff_report(x, fs, vref, mains_hz, **kw)[0]


class LeadoffTracker:
    """Per-channel electrode lead-off with temporal hysteresis (no flicker) and a
    smoothed 0-100 quality score. Feed one raw window per channel per update tick;
    a new state must persist ``hold`` ticks before it latches (debounce)."""

    def __init__(self, nch, fs, vref=3.3, mains_hz=50.0, hold=2):
        self.nch = nch
        self.fs = fs
        self.vref = vref
        self.mains_hz = mains_hz
        self.hold = hold
        self.state = ["good"] * nch
        self.quality = [100.0] * nch
        self._pending = [None] * nch
        self._count = [0] * nch

    def update(self, ch, x):
        raw, q, _ = leadoff_report(x, self.fs, self.vref, self.mains_hz)
        self.quality[ch] = 0.6 * self.quality[ch] + 0.4 * q            # EMA smoothing
        if raw == self.state[ch]:
            self._pending[ch], self._count[ch] = None, 0
        elif raw == self._pending[ch]:
            self._count[ch] += 1
            if self._count[ch] >= self.hold:
                self.state[ch], self._pending[ch], self._count[ch] = raw, None, 0
        else:
            self._pending[ch], self._count[ch] = raw, 1
        return self.state[ch], self.quality[ch]


# ------------------------------------------------------------------ analytics (M3)
def iemg(x, fs):
    """Integrated EMG: area under the rectified (DC-removed) signal, in V·s.
    A measure of total muscle activity over the window."""
    x = np.asarray(x, dtype=float)
    if x.shape[0] < 2:
        return 0.0
    trapz = getattr(np, "trapezoid", np.trapz)      # numpy 2.x renamed trapz -> trapezoid
    return float(trapz(np.abs(x - x.mean()), dx=1.0 / fs))


def mean_frequency(x, fs, band=(20.0, 450.0)):
    """Mean (centroid) frequency of the power spectrum over `band` (Hz). Complements
    median frequency; both fall during a sustained contraction as the muscle fatigues."""
    x = np.asarray(x, dtype=float)
    n = x.shape[0]
    if n < 8:
        return 0.0
    P = np.abs(np.fft.rfft((x - x.mean()) * np.hanning(n))) ** 2
    f = np.fft.rfftfreq(n, 1.0 / fs)
    m = (f >= band[0]) & (f <= min(band[1], 0.5 * fs))
    tot = float(P[m].sum())
    return float((f[m] * P[m]).sum() / tot) if tot > 0 else 0.0


def cocontraction_index(a, b):
    """Symmetric co-activation index between two RMS envelopes (same length), 0..100 %:
    ``2·Σ min(a,b) / Σ (a+b) · 100``. 100 % = identical activation, 0 % = no overlap."""
    a = np.abs(np.asarray(a, dtype=float))
    b = np.abs(np.asarray(b, dtype=float))
    denom = float((a + b).sum())
    if denom <= 0:
        return 0.0
    return float(2.0 * np.minimum(a, b).sum() / denom * 100.0)


def onset_offset(env, fs, thresh, min_on_ms=50.0, min_off_ms=50.0):
    """Activation intervals from an RMS envelope crossing `thresh`. Returns a list of
    ``(onset_s, offset_s)``; runs shorter than `min_on_ms` are ignored and gaps shorter
    than `min_off_ms` are bridged (debounce)."""
    env = np.asarray(env, dtype=float)
    n = env.shape[0]
    if n == 0:
        return []
    min_on = max(1, int(fs * min_on_ms / 1000.0))
    min_off = max(1, int(fs * min_off_ms / 1000.0))
    above = env >= thresh
    intervals, i = [], 0
    while i < n:
        if above[i]:
            start, j, gap, last = i, i, 0, i
            while j < n:
                if above[j]:
                    last, gap = j, 0
                else:
                    gap += 1
                    if gap >= min_off:
                        break
                j += 1
            if (last - start + 1) >= min_on:
                intervals.append((start / fs, (last + 1) / fs))
            i = j + 1
        else:
            i += 1
    return intervals


def fatigue_trend(mdf_series, times=None):
    """Linear trend of a median/mean-frequency series over a trial. Returns
    ``(slope_hz_per_s, pct_change)``; a negative slope = fatigue (spectral compression)."""
    y = np.asarray(mdf_series, dtype=float)
    n = y.shape[0]
    if n < 2:
        return 0.0, 0.0
    t = np.asarray(times, dtype=float) if times is not None else np.arange(n, dtype=float)
    slope = float(np.polyfit(t, y, 1)[0])
    pct = float((y[-1] - y[0]) / (y[0] + 1e-12) * 100.0)
    return slope, pct
