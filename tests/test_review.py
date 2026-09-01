"""HG4 tests for the offline View/Review window: it loads a saved recording, switches
processing Operations, scrubs a playback cursor, and writes an HTML report.

Run: QT_QPA_PLATFORM=offscreen python -m pytest tests/test_review.py -q
"""
import os
import sys
from pathlib import Path

import numpy as np

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FS = 2000.0


def _write_csv(path, n=1200, nch=2):
    lines = ["# Subject: S01", "# Trial: grip", f"# fs={FS:.0f} Hz, nch={nch}, vref=3.3 V",
             "# MARKER onset t=0.250",
             "t_s," + ",".join(f"ch{c+1}_code" for c in range(nch))]
    rng = np.random.default_rng(0)
    for i in range(n):
        codes = [int(2048 + 300 * np.sin(2 * np.pi * 80 * i / FS) + 40 * rng.standard_normal())
                 for _ in range(nch)]
        lines.append(f"{i/FS:.6f}," + ",".join(str(x) for x in codes))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_review_loads_views_playback_and_report(tmp_path, monkeypatch):
    from PyQt5 import QtWidgets
    from gui.review_window import ReviewWindow
    QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    monkeypatch.chdir(tmp_path)

    csv = tmp_path / "emg_20260101_120000.csv"
    _write_csv(csv, n=1200, nch=2)

    win = ReviewWindow(str(csv), FS, 2, 3.3, 4095.0, ["FCR", "ECR"], mvc=[0.05, None])
    assert win.nch == 2
    assert win.markers and abs(win.markers[0][0] - 0.25) < 1e-6      # marker parsed
    assert win._disp.shape[0] == 1200

    # every Operation recomputes the display without error, with the right units
    for op in win.VIEWS:
        win.cmb_view.setCurrentText(op)
        assert win._disp.shape == (1200, 2)
    assert win._unit == "%"                                          # last op was % MVC
    win.cmb_view.setCurrentText("Raw")
    assert win._unit == "mV"

    # scrub + one playback tick advance the cursor
    win.slider.setValue(600)
    assert win.cursor_i == 600
    win.btn_play.setChecked(True)
    win._tick()
    assert win.cursor_i > 600
    win.btn_play.setChecked(False)

    fn = win._report()
    assert os.path.exists(fn)
    txt = Path(fn).read_text(encoding="utf-8")
    assert "EMG Review" in txt and "FCR" in txt and "grip" in txt
    win.close()


def test_processing_dialog_build_and_channel_scope(tmp_path, monkeypatch):
    from PyQt5 import QtCore, QtWidgets
    from gui.review_window import ReviewWindow
    from gui.processing_dialog import ProcessingDialog
    QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    monkeypatch.chdir(tmp_path)
    csv = tmp_path / "emg_20260101_120000.csv"
    _write_csv(csv, n=1200, nch=2)
    win = ReviewWindow(str(csv), FS, 2, 3.3, 4095.0, ["FCR", "ECR"], mvc=[0.05, 0.05])

    # builder: seeded, Insert from Available, Remove All
    dlg = ProcessingDialog(["rectify"], 2, ["FCR", "ECR"], channels="all")
    assert dlg.selected_keys() == ["rectify"]
    for i in range(dlg.avail.count()):
        if dlg.avail.item(i).data(QtCore.Qt.UserRole) == "rms":
            dlg.avail.setCurrentRow(i)
            break
    dlg._insert()
    assert dlg.selected_keys() == ["rectify", "rms"]
    # Remove All asks to confirm — 'No' keeps the pipeline
    monkeypatch.setattr(QtWidgets.QMessageBox, "question",
                        lambda *a, **k: QtWidgets.QMessageBox.No)
    dlg._remove_all()
    assert dlg.selected_keys() == ["rectify", "rms"]
    # 'Yes' clears it
    monkeypatch.setattr(QtWidgets.QMessageBox, "question",
                        lambda *a, **k: QtWidgets.QMessageBox.Yes)
    dlg._remove_all()
    assert dlg.selected_keys() == []
    assert dlg.channels() == "all"

    # apply a normalizing pipeline to ALL channels -> both lanes in %
    win.pipeline = ["bandpass", "rms", "norm_mvc"]
    win.proc_channels = "all"
    win._recompute()
    assert win._units == ["%", "%"]

    # scope the pipeline to channel 0 only -> ch0 %, ch1 stays raw mV
    win.proc_channels = 0
    win._recompute()
    assert win._units[0] == "%" and win._units[1] == "mV"
    win.close()


def test_review_normalize_modes_window_and_result(tmp_path, monkeypatch):
    from PyQt5 import QtWidgets
    from gui.review_window import ReviewWindow
    from gui.normalize_dialog import NormalizeDialog
    QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    monkeypatch.chdir(tmp_path)
    csv = tmp_path / "emg_20260101_120000.csv"
    _write_csv(csv, n=2000, nch=2)
    win = ReviewWindow(str(csv), FS, 2, 3.3, 4095.0, ["FCR", "ECR"], mvc=[0.05, None])

    # Peak over the whole recording -> % axis, refs set, result markers shown, peak ~100%
    win._apply_normalize("peak", None, False, "", 150)
    assert win._units == ["%", "%"]
    assert win._norm_refs and all(r > 0 for r in win._norm_refs)
    assert win.amp_range == 150
    assert win.peak_regions[0].isVisible() and win.ref_lines[0].isVisible()
    assert abs(float(win._disp[:, 0].max()) - 100.0) < 2.0

    # Manual: reference = manual mV -> volts
    win._apply_normalize("manual", 40.0, False, "", 120)
    assert abs(win._norm_refs[0] - 0.040) < 1e-9

    # MVC: ch0 uses the set MVC (0.05 V); ch1 (no MVC) falls back to its peak
    win._apply_normalize("mvc", None, False, "", 120)
    assert abs(win._norm_refs[0] - 0.05) < 1e-9 and win._norm_refs[1] > 0

    # Other record: reference = peak of another file's envelope
    other = tmp_path / "emg_20260101_130000.csv"
    _write_csv(other, n=1500, nch=2)
    win._apply_normalize("other", None, False, str(other), 120)
    assert win._norm_refs and win._norm_refs[0] > 0

    # Pick window restricts the reference; a preset then hides the result markers
    win.btn_pick.setChecked(True)
    w = win._picked_window()
    assert w is not None and w[1] > w[0]
    win._apply_normalize("peak", None, True, "", 120)
    assert win._norm_window == w
    win.cmb_view.setCurrentText("Raw")
    assert not win.peak_regions[0].isVisible() and not win.ref_lines[0].isVisible()

    # dialog reports its picks (MODES order: Peak, Mean, MVC, Manual, Other)
    dlg = NormalizeDialog(has_window=True, has_mvc=True)
    dlg.cmb_mode.setCurrentIndex(2)
    assert dlg.mode() == "mvc"
    assert dlg.amp_range() == 120 and dlg.use_window() is True
    win.close()
