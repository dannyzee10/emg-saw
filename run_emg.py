import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    ROOT = Path(sys._MEIPASS)
else:
    ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from PyQt5 import QtWidgets
import pyqtgraph as pg

app = QtWidgets.QApplication(sys.argv)
pg.setConfigOptions(antialias=False, background="k", foreground="w")

import argparse
from communication.sources import SimSource, SerialSource, AsciiSource
from gui.model import AcquisitionModel
from gui.controller import MainController
from gui.plot_widget import EmgPlotWidget
from gui.channel_panel import ChannelPanel
from gui.emg_plotter import EmgScope

ap = argparse.ArgumentParser()
ap.add_argument("--sim", action="store_true")
ap.add_argument("--channels", type=int, default=1)
ap.add_argument("--port")
ap.add_argument("--baud", type=int, default=115200)
ap.add_argument("--ascii", action="store_true")
ap.add_argument("--fs", type=float, default=2000.0)
ap.add_argument("--vref", type=float, default=3.3)
ap.add_argument("--bits", type=int, default=12)
ap.add_argument("--coupling", default="DC")
ap.add_argument("--kick", action="store_true")
args = ap.parse_args()
if not args.sim and not args.port:
    args.sim = True
    if args.channels is None:
        args.channels = 1

if args.sim:
    source = SimSource(args.channels, args.fs, args.bits)
elif args.port:
    if args.ascii:
        source = AsciiSource(args.port, args.baud, args.channels)
    else:
        source = SerialSource(args.port, args.baud, args.channels)
else:
    ap.error("give --port COMx or --sim")

win = EmgScope(source, args.channels, args.fs, args.vref, args.bits,
               args.ascii, coupling=args.coupling)
win.show()
sys.exit(app.exec_())
