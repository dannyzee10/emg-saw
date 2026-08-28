"""
HG3 unit tests for the PC-side electrode lead-off heuristic (dsp.leadoff_status).

Synthetic signals modelling the AD8237 -> STM32 path (absolute volts, 0..Vref):
  railed low/high -> 'open', big 50 Hz sine -> 'poor', broadband EMG / quiet -> 'good'.

Run: python -m pytest tests/test_leadoff.py -q
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dsp.dsp import leadoff_status, leadoff_report, LeadoffTracker

FS = 2000.0
VREF = 3.3


def _t(n):
    return np.arange(n) / FS


def test_open_railed_low():
    # input pinned near 0 V (shorted to GND) -> rails low -> open
    x = np.full(1024, 0.004) + 1e-4 * np.random.randn(1024)
    assert leadoff_status(x, FS, VREF) == "open"


def test_open_railed_high():
    # input pinned near Vref (saturated) -> open
    x = np.full(1024, VREF - 0.004)
    assert leadoff_status(x, FS, VREF) == "open"


def test_poor_mains_dominated():
    # ~180 mVpp 50 Hz sine around mid-scale = floating electrode antenna -> poor
    x = VREF / 2 + 0.09 * np.sin(2 * np.pi * 50.0 * _t(2048))
    assert leadoff_status(x, FS, VREF, mains_hz=50.0) == "poor"


def test_good_emg_like():
    # band-limited (20-450 Hz) broadband around mid-scale = real EMG -> good
    rng = np.random.default_rng(0)
    noise = rng.standard_normal(2048)
    X = np.fft.rfft(noise)
    f = np.fft.rfftfreq(2048, 1.0 / FS)
    X[(f < 20) | (f > 450)] = 0
    emg = np.fft.irfft(X, n=2048)
    x = VREF / 2 + 0.03 * emg / (np.std(emg) + 1e-9)
    assert leadoff_status(x, FS, VREF) == "good"


def test_good_quiet_baseline():
    # small quiet noise around mid-scale = connected, resting -> good
    x = VREF / 2 + 0.002 * np.random.randn(1024)
    assert leadoff_status(x, FS, VREF) == "good"


def test_report_quality_ordering():
    # quality: good (EMG) > poor (mains) > open (railed)
    railed = np.full(1024, 0.004)
    mains = VREF / 2 + 0.09 * np.sin(2 * np.pi * 50.0 * _t(2048))
    rng = np.random.default_rng(1)
    X = np.fft.rfft(rng.standard_normal(2048))
    f = np.fft.rfftfreq(2048, 1.0 / FS)
    X[(f < 20) | (f > 450)] = 0
    good = VREF / 2 + 0.03 * np.fft.irfft(X, n=2048)
    q_open = leadoff_report(railed, FS, VREF)[1]
    q_poor = leadoff_report(mains, FS, VREF, mains_hz=50.0)[1]
    q_good = leadoff_report(good, FS, VREF)[1]
    assert q_good > q_poor > q_open


def test_tracker_hysteresis_ignores_single_blip():
    tr = LeadoffTracker(1, FS, VREF, mains_hz=50.0, hold=2)
    good = VREF / 2 + 0.002 * np.random.randn(1024)
    railed = np.full(1024, 0.004)
    for _ in range(4):
        tr.update(0, good)
    assert tr.state[0] == "good"
    tr.update(0, railed)              # one bad window must NOT flip the latched state
    assert tr.state[0] == "good"
    tr.update(0, railed)              # second consecutive bad window latches it
    assert tr.state[0] == "open"
