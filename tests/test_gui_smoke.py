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

    # Set MVC opens the MVC calibration dialog (tested in test_mvc.py); Clear resets the reference
    win.mvc[0] = 1.0
    win.channel_panel.btn_mvc_clr.click()
    assert win.mvc[0] is None
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
