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
