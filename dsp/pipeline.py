"""Offline signal-processing pipeline (Noraxon MR 'Signal Processing' menu).

A pipeline is an ordered list of operation keys applied in sequence to one channel's
absolute-volt signal. Ops are pure functions of (sig, ctx) -> sig so they are trivially
testable without Qt. `ctx` carries {fs, filters (EmgFilters), mvc (this channel's ref, V),
smooth_ms}. Amplitude-normalization ops output % (of MVC / peak / mean); all others stay
in volts. Used by the Review window; the GUI builder lives in gui/processing_dialog.py.
"""
import numpy as np


def _ac(sig):
    return np.asarray(sig, dtype=float) - float(np.mean(sig))


def op_rectify(sig, ctx):
    return np.abs(_ac(sig))


def op_bandpass(sig, ctx):
    return ctx["filters"].bandpass(np.asarray(sig, dtype=float).reshape(-1, 1))[:, 0]


def op_notch50(sig, ctx):
    return ctx["filters"].apply_notch(np.asarray(sig, dtype=float).reshape(-1, 1), 50)[:, 0]


def op_notch60(sig, ctx):
    return ctx["filters"].apply_notch(np.asarray(sig, dtype=float).reshape(-1, 1), 60)[:, 0]


def op_rms(sig, ctx):
    """RMS smoothing (linear envelope) over smooth_ms."""
    return ctx["filters"].rms_envelope(_ac(sig).reshape(-1, 1),
                                       win_ms=ctx.get("smooth_ms", 100.0))[:, 0]


def op_mean(sig, ctx):
    """Mean-absolute smoothing: moving average of the rectified signal over smooth_ms."""
    n = max(1, int(ctx["fs"] * ctx.get("smooth_ms", 100.0) / 1000.0))
    if n <= 1:
        return np.abs(_ac(sig))
    k = np.ones(n) / n
    return np.convolve(np.abs(_ac(sig)), k, mode="same")


def op_norm_mvc(sig, ctx):
    """Normalize to the set MVC reference (V). Falls back to the signal's own peak."""
    ref = ctx.get("mvc")
    if not ref or ref <= 0:
        ref = float(np.max(sig)) + 1e-12
    return np.asarray(sig, dtype=float) / ref * 100.0


def op_norm_peak(sig, ctx):
    return np.asarray(sig, dtype=float) / (float(np.max(sig)) + 1e-12) * 100.0


def op_norm_mean(sig, ctx):
    return np.asarray(sig, dtype=float) / (float(np.mean(np.abs(sig))) + 1e-12) * 100.0


# key -> (label, fn, produces_percent)
OPS = {
    "rectify":  ("Rectify",                      op_rectify,   False),
    "bandpass": ("Band-pass 20-450 Hz",          op_bandpass,  False),
    "notch50":  ("Notch 50 Hz",                  op_notch50,   False),
    "notch60":  ("Notch 60 Hz",                  op_notch60,   False),
    "rms":      ("Smoothing: RMS",               op_rms,       False),
    "mean":     ("Smoothing: Mean-absolute",     op_mean,      False),
    "norm_mvc": ("Amplitude Normalization: % MVC",  op_norm_mvc,  True),
    "norm_peak":("Amplitude Normalization: % Peak", op_norm_peak, True),
    "norm_mean":("Amplitude Normalization: % Mean", op_norm_mean, True),
}

# quick presets (Review 'Operation' shortcuts) -> ordered pipeline
PRESETS = {
    "Raw":          [],
    "Rectified":    ["rectify"],
    "RMS envelope": ["bandpass", "rms"],
    "% MVC":        ["bandpass", "rms", "norm_mvc"],
}


def op_label(key):
    return OPS[key][0] if key in OPS else key


def apply_pipeline(sig, keys, ctx):
    """Apply the ordered op keys to a 1-D signal; unknown keys are skipped."""
    out = np.asarray(sig, dtype=float)
    for k in keys:
        if k in OPS:
            out = OPS[k][1](out, ctx)
    return out


def pipeline_unit(keys):
    """Display unit after the pipeline: '%' if it ends in a normalization, else 'mV'."""
    return "%" if any(OPS.get(k, ("", None, False))[2] for k in keys) else "mV"
