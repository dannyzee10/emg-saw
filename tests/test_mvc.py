"""
HG4 tests for the MVC calibration dialog: it must capture the held MAX (not the rest),
and %MVC must be consistent (current envelope / MVCref).

Run: python -m pytest tests/test_mvc.py -q
"""
import os
import sys
from pathlib import Path

import numpy as np

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FS = 2000.0


def _chunk(rng, sec, amp):
    n = int(sec * FS)
    return (1.65 + amp * rng.standard_normal(n)).reshape(-1, 1)   # absolute volts around mid


def test_mvc_dialog_captures_hold_not_rest():
    from PyQt5 import QtWidgets
    from gui.mvc_dialog import MvcDialog
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    rng = np.random.default_rng(0)

    dlg = MvcDialog(1, FS, ["FCR"])
    dlg.start_record()
    dlg.feed(_chunk(rng, 1.0, 0.004))    # rest
    dlg.feed(_chunk(rng, 3.0, 0.090))    # MAX hold
    dlg.feed(_chunk(rng, 2.0, 0.004))    # rest
    dlg.stop_record()

    ref = dlg.mvc_values[0]
    assert 0.02 < ref < 0.20, f"MVC should reflect the hold, not the rest: {ref}"


def test_mvc_peak_ge_best1s():
    from PyQt5 import QtWidgets
    from gui.mvc_dialog import MvcDialog
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    rng = np.random.default_rng(1)
    buf = np.concatenate([_chunk(rng, 1.0, 0.004), _chunk(rng, 3.0, 0.090),
                          _chunk(rng, 2.0, 0.004)], axis=0)

    dlg = MvcDialog(1, FS, ["FCR"])
    env = dlg._env(buf, 0)
    dlg.rule = "peak"
    peak, _, _ = dlg._compute_mvc(env)
    dlg.rule = "best1s"
    best1s, _, _ = dlg._compute_mvc(env)
    assert peak >= best1s > 0                     # peak envelope >= best sustained 1 s
