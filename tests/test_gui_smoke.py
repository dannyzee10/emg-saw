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
    win.close()
