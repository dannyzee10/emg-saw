"""
HG3 unit tests for the M3 EMG analytics (dsp): iEMG, mean frequency, co-contraction,
onset/offset timing, fatigue trend. All validated against synthetic signals with a
known answer — no hardware needed.

Run: python -m pytest tests/test_dsp_analytics.py -q
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dsp.dsp import (iemg, mean_frequency, cocontraction_index,
                     onset_offset, fatigue_trend)

FS = 2000.0


def test_iemg_square_wave():
    # +/-1 square over 1 s -> integral of |x| = 1.0 V*s
    n = int(FS)
    x = np.sign(np.sin(2 * np.pi * 5 * np.arange(n) / FS))
    assert abs(iemg(x, FS) - 1.0) < 0.05


def test_mean_frequency_tone():
    n = 4000
    x = np.sin(2 * np.pi * 100.0 * np.arange(n) / FS)
    assert abs(mean_frequency(x, FS) - 100.0) < 5.0


def test_cci_identical_is_100():
    a = np.array([0, 1, 2, 3, 2, 1, 0], float)
    assert abs(cocontraction_index(a, a) - 100.0) < 1e-6


def test_cci_disjoint_is_0():
    a = np.array([0, 0, 0, 1, 1, 1], float)
    b = np.array([1, 1, 1, 0, 0, 0], float)
    assert cocontraction_index(a, b) == 0.0


def test_cci_partial_overlap():
    a = np.array([1, 1, 1, 1], float)
    b = np.array([1, 1, 0, 0], float)
    assert abs(cocontraction_index(a, b) - (2 * 2 / 6 * 100)) < 1e-6   # 66.67 %


def test_onset_offset_single_burst():
    env = np.zeros(1000)
    env[300:500] = 1.0                      # burst 0.300–0.500 s at fs=1000
    iv = onset_offset(env, 1000.0, thresh=0.5, min_on_ms=50, min_off_ms=50)
    assert len(iv) == 1
    on, off = iv[0]
    assert abs(on - 0.300) < 0.02 and abs(off - 0.500) < 0.02


def test_onset_offset_bridges_short_gap():
    env = np.zeros(1000)
    env[300:400] = 1.0
    env[410:500] = 1.0                      # 10 ms gap < 50 ms -> one interval
    iv = onset_offset(env, 1000.0, thresh=0.5, min_on_ms=50, min_off_ms=50)
    assert len(iv) == 1


def test_fatigue_trend_declining():
    slope, pct = fatigue_trend([100.0, 90.0, 80.0], times=[0.0, 1.0, 2.0])
    assert slope < 0 and abs(pct - (-20.0)) < 1e-6
