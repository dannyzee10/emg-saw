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
