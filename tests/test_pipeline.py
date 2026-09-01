"""Unit tests for the offline signal-processing pipeline (pure, no Qt)."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dsp.dsp import EmgFilters
from dsp.pipeline import apply_pipeline, pipeline_unit, OPS, PRESETS

FS = 2000.0


def _ctx(mvc=None):
    return {"fs": FS, "filters": EmgFilters(FS), "mvc": mvc, "smooth_ms": 100.0}


def test_rectify_is_nonnegative():
    sig = np.sin(2 * np.pi * 80 * np.arange(2000) / FS)
    out = apply_pipeline(sig, ["rectify"], _ctx())
    assert (out >= 0).all()


def test_rms_smoothing_positive_and_smoother():
    rng = np.random.default_rng(0)
    sig = 0.05 * rng.standard_normal(4000)
    out = apply_pipeline(sig, ["bandpass", "rms"], _ctx())
    assert (out >= 0).all()
    assert out.std() < sig.std()                 # envelope is smoother than the raw


def test_norm_mvc_maps_reference_to_100pct():
    sig = np.full(3000, 0.03)                    # steady 30 mV, already envelope-like
    out = apply_pipeline(sig, ["norm_mvc"], _ctx(mvc=0.03))
    assert abs(float(np.median(out)) - 100.0) < 1.0


def test_norm_peak_tops_at_100pct():
    rng = np.random.default_rng(1)
    sig = np.abs(0.02 * rng.standard_normal(2000)) + 0.01
    out = apply_pipeline(sig, ["norm_peak"], _ctx())
    assert abs(float(out.max()) - 100.0) < 1e-6


def test_pipeline_unit_switches_on_normalization():
    assert pipeline_unit([]) == "mV"
    assert pipeline_unit(["rectify", "rms"]) == "mV"
    assert pipeline_unit(["bandpass", "rms", "norm_mvc"]) == "%"


def test_unknown_keys_skipped():
    sig = np.ones(100)
    out = apply_pipeline(sig, ["nope", "rectify"], _ctx())
    assert out.shape == sig.shape


def test_presets_reference_real_ops():
    for _name, keys in PRESETS.items():
        for k in keys:
            assert k in OPS
