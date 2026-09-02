"""
Headless GUI smoke test (HG4): build the branded MVC instrument at 5 channels,
run the Qt event loop against sim data, and tear it down — under
QT_QPA_PLATFORM=offscreen, with no display and no exception.

Run: python -m pytest tests/test_gui_smoke.py -q
"""
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_gui_builds_and_runs_5ch():
    from PyQt5 import QtWidgets
    from communication.sources import SimSource
    from gui.emg_plotter import EmgScope

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    src = SimSource(5, 2000.0, 12)
    win = EmgScope(src, 5, 2000.0, 3.3, 12, False, coupling="AC")
    win.show()

    # pump the event loop so the update timer fires against sim data
    for _ in range(40):
        app.processEvents()
        time.sleep(0.005)

    # 5 channel cards = 5 lanes were built
    assert len(win.channel_panel.cards) == 5

    # EMG baseline check button runs without error and reports a result
    win.btn_base.click()
    assert "Baseline" in win.lbl_hint.text() or "signal" in win.lbl_hint.text()

    # Set MVC opens the MVC calibration dialog (tested in test_mvc.py); Clear resets the reference
    win.mvc[0] = 1.0
    win.channel_panel.btn_mvc_clr.click()
    assert win.mvc[0] is None

    # % MVC view toggles without error (needs MVC set on all channels), raw + envelope paths
    win.mvc = [1.0] * win.nch
    win.cb_mvc.setChecked(True)          # % MVC on raw EMG
    for _ in range(6):
        app.processEvents()
        time.sleep(0.005)
    win.cb_env.setChecked(True)          # % MVC on RMS envelope
    for _ in range(6):
        app.processEvents()
        time.sleep(0.005)
    assert win.show_mvc and win._mvc_view_on()
    win.cmb_amp.setCurrentText("150%")   # amplitude (display range) selector
    for _ in range(4):
        app.processEvents()
        time.sleep(0.005)
    assert win.mvc_range == 150

    # Show Raw overrides the processed (%MVC / RMS env) view; the settings are kept
    win.cb_raw.setChecked(True)
    assert win.show_raw and not win._mvc_view_on()
    win.cb_raw.setChecked(False)
    assert win._mvc_view_on()

    # Record/Pause activity step hints update contextually
    win.btn_pause.setChecked(True)
    assert "paused" in win.lbl_hint.text().lower()
    win.btn_pause.setChecked(False)
    assert "record" in win.lbl_hint.text().lower()

    win.cb_mvc.setChecked(False)
    win.close()


def test_amp_norm_dialog_reports_config():
    from PyQt5 import QtWidgets
    from gui.amp_norm_dialog import AmpNormDialog
    QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    dlg = AmpNormDialog(algo="mean", window_ms=250.0, amp=150)
    assert dlg.algo() == "mean" and dlg.window_ms() == 250.0 and dlg.amp() == 150


def test_live_smoothing_algorithms_and_pipeline():
    """Img1/Img3/Img4: the live envelope honors the smoothing algorithm + window, and a
    real-time processing pipeline (mV ops) applies in the RMS-env path."""
    import numpy as np
    from PyQt5 import QtWidgets
    from communication.sources import SimSource
    from gui.emg_plotter import EmgScope
    QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    win = EmgScope(SimSource(2, 2000.0, 12), 2, 2000.0, 3.3, 12, False, coupling="AC")

    data = 1.65 + 0.05 * np.random.RandomState(0).randn(600, 2)   # absolute volts
    win.do_envelope = True
    win.smooth_algo, win.smooth_ms = "rms", 100.0
    env_rms = win._process(data)
    assert (env_rms >= 0).all()
    win.smooth_algo, win.smooth_ms = "mean", 50.0
    env_mean = win._process(data)
    assert (env_mean >= 0).all() and not np.allclose(env_rms, env_mean)   # algo actually changes it

    # Img2: a live processing pipeline (rectify) applies in the envelope path
    win.smooth_algo, win.live_pipeline = "rms", ["rectify"]
    rec = win._process(data)
    assert (rec >= 0).all()
    # normalization ops are stripped from a live pipeline (needs MVC -> use % MVC view)
    from dsp.pipeline import OPS
    assert not any(OPS[k][2] for k in win.live_pipeline)
    win.live_pipeline = []
    win.close()


def test_report_generates(tmp_path, monkeypatch):
    """HG4: the HTML report builds (with the M3 analytics columns) without exception."""
    from PyQt5 import QtWidgets
    from communication.sources import SimSource
    from gui.emg_plotter import EmgScope

    monkeypatch.setattr(os, "startfile", lambda *a, **k: None, raising=False)
    monkeypatch.chdir(tmp_path)

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    win = EmgScope(SimSource(2, 2000.0, 12), 2, 2000.0, 3.3, 12, False, coupling="AC")
    win.show()
    for _ in range(30):
        app.processEvents()
        time.sleep(0.005)

    win._report()
    htmls = list(tmp_path.glob("emg_report_*.html"))
    assert htmls, "no report written"
    txt = htmls[0].read_text(encoding="utf-8")
    assert "Fatigue" in txt and "iEMG" in txt
    win.close()
