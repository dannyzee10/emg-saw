"""Academic-correctness checks for the EMG metrics: each formula is verified against a
signal with a known analytical answer (De Luca 1997; Merletti & Parker 2004; Winter 2009).
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dsp.dsp import (median_frequency, mean_frequency, iemg,
                     cocontraction_index, onset_offset, fatigue_trend)

FS = 2000.0


def test_mdf_and_mnf_of_a_pure_tone():
    # a 150 Hz tone: all power at 150 Hz -> MDF = MNF = 150 Hz
    t = np.arange(4000) / FS
    x = np.sin(2 * np.pi * 150.0 * t)
    assert abs(median_frequency(x, FS) - 150.0) < 3.0
    assert abs(mean_frequency(x, FS) - 150.0) < 3.0


def test_mdf_of_flat_band_is_the_midpoint():
    # flat spectrum over 100-200 Hz -> equal energy either side of 150 Hz
    n = 4096
    rng = np.random.default_rng(0)
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1.0 / FS)
    X[(f < 100) | (f > 200)] = 0
    x = np.fft.irfft(X, n=n)
    assert abs(median_frequency(x, FS) - 150.0) < 15.0
    assert abs(mean_frequency(x, FS) - 150.0) < 15.0


def test_iemg_equals_rectified_area():
    # square wave amplitude A, zero mean -> |x| = A -> iEMG = integral(A) = A*T
    A, T = 0.01, 1.0
    n = int(T * FS)
    x = A * np.sign(np.sin(2 * np.pi * 50.0 * np.arange(n) / FS))
    assert abs(iemg(x, FS) - A * T) < 0.05 * A * T


def test_cocontraction_bounds():
    assert abs(cocontraction_index(np.ones(100), np.ones(100)) - 100.0) < 1e-6   # identical
    a = np.array([1.0, 0.0] * 50)
    b = np.array([0.0, 1.0] * 50)
    assert cocontraction_index(a, b) < 1e-6                                       # disjoint


def test_fatigue_slope_is_negative_for_declining_mdf():
    t = np.arange(10.0)
    slope, pct = fatigue_trend(100.0 - 2.0 * t, t)
    assert slope < 0 and pct < 0


def test_onset_detects_a_single_burst():
    env = np.zeros(2000)
    env[800:1200] = 1.0                                   # 0.4-0.6 s burst
    iv = onset_offset(env, FS, thresh=0.5)
    assert len(iv) == 1 and abs(iv[0][0] - 0.4) < 0.02 and abs(iv[0][1] - 0.6) < 0.02
