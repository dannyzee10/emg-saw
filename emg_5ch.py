import sys
from PyQt5 import QtWidgets
import pyqtgraph as pg

app = QtWidgets.QApplication(sys.argv)
pg.setConfigOptions(antialias=False, background="k", foreground="w")

from communication.sources import SimSource
from gui.emg_plotter import EmgScope
import argparse

args = argparse.Namespace(
    sim=True,
    channels=5,
    port=None,
    baud=115200,
    ascii=False,
    fs=2000.0,
    vref=3.3,
    bits=12,
    coupling="DC",
    kick=False
)

source = SimSource(args.channels, args.fs, args.bits)
win = EmgScope(source, args.channels, args.fs, args.vref, args.bits,
               args.ascii, coupling=args.coupling)
win.show()
sys.exit(app.exec_())
