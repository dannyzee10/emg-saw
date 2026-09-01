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


def test_mvc_save_dialog_defaults():
    from PyQt5 import QtWidgets
    from gui.mvc_dialog import MvcSaveDialog
    QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    dlg = MvcSaveDialog([0.05, 0.08], ["FCR", "ECR"], subject="S01")
    assert dlg.name().endswith("(MVC)")          # Noraxon-style auto '(MVC)' suffix
    assert "S01" in dlg.name()
    assert dlg.subject() == "S01"


def test_save_mvc_record_writes_stack(tmp_path, monkeypatch):
    from PyQt5 import QtWidgets
    from communication.sources import SimSource
    from gui.emg_plotter import EmgScope
    import json
    QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    monkeypatch.chdir(tmp_path)

    win = EmgScope(SimSource(2, FS, 12), 2, FS, 3.3, 12, False, coupling="AC")
    win.mvc = [0.05, 0.08]
    rec = win._save_mvc_record("S01 (MVC)", "S01")
    assert rec["channels"][0]["mvc_v"] == 0.05
    store = json.loads((tmp_path / "mvc_store.json").read_text(encoding="utf-8"))
    assert len(store) == 1 and store[0]["name"] == "S01 (MVC)"
    # a second save appends to the stack
    win._save_mvc_record("S01 b (MVC)", "S01")
    store = json.loads((tmp_path / "mvc_store.json").read_text(encoding="utf-8"))
    assert len(store) == 2
    win.close()


def test_save_recording_dialog_defaults():
    from PyQt5 import QtWidgets
    from gui.mvc_dialog import SaveRecordingDialog
    QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    dlg = SaveRecordingDialog(subject="S01", trial="grip", duration=4.2, samples=8400)
    assert "S01" in dlg.name() and "grip" in dlg.name()
    assert dlg.subject() == "S01" and dlg.trial() == "grip"
    assert not dlg.view and not dlg.discard          # defaults before any button


def test_finalize_and_summarize_recording(tmp_path, monkeypatch):
    from PyQt5 import QtWidgets
    from communication.sources import SimSource
    from gui.emg_plotter import EmgScope
    QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    monkeypatch.chdir(tmp_path)

    csv = tmp_path / "emg_20260101_120000.csv"
    lines = ["# Subject: S01", "# fs=2000 Hz, nch=1, vref=3.3 V", "t_s,ch1_code"]
    lines += [f"{i/FS:.6f},{2048 + (i % 7) * 40}" for i in range(400)]
    csv.write_text("\n".join(lines) + "\n", encoding="utf-8")

    win = EmgScope(SimSource(1, FS, 12), 1, FS, 3.3, 12, False, coupling="AC")
    new = win._finalize_recording_name(str(csv), "S01 grip test")
    assert new.endswith("_S01_grip_test.csv") and os.path.exists(new)
    assert not os.path.exists(str(csv))              # original was renamed, not duplicated
    summ = win._recording_summary(new)
    assert "mV" in summ                              # per-channel numeric summary produced
    win.close()
