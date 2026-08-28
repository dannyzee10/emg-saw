"""EmgPlotWidget – encapsulates all real-time plotting and spectrum views."""

import numpy as np
import pyqtgraph as pg

CH_COLORS = ["#00e0ff", "#7CFC00", "#ff5050", "#ffb000", "#c080ff",
             "#ff80c0", "#80ffd0", "#ffd000"]


class EmgPlotWidget:
    """Holds the GraphicsLayoutWidget, per-channel plots, curves, overlays, cursors,
    and the optional live spectrum plot. Provides methods to update data."""

    def __init__(self, nch, fs):
        self.nch = nch
        self.fs = fs
        self.glw = pg.GraphicsLayoutWidget()
        self.glw.setBackground("#0b0f16")

        self.plots = []
        self.curves = []
        self.overlays = []
        self.cursors = []

        self._build_plots()
        self._build_spectrum()

    def _build_plots(self):
        for c in range(self.nch):
            p = self.glw.addPlot(row=c, col=0)
            p.showGrid(x=True, y=True, alpha=0.3)
            p.showAxis("right")
            p.showAxis("top")
            p.getAxis("right").setStyle(showValues=False)
            p.getAxis("top").setStyle(showValues=False)
            p.getViewBox().setBorder(pg.mkPen("#666666", width=1))
            p.setLabel("left", f"Ch{c+1}", units="V")
            p.setMouseEnabled(x=False, y=False)
            p.setMenuEnabled(False)
            p.setClipToView(True)
            p.setDownsampling(mode="peak", auto=True)
            p.getViewBox().disableAutoRange()
            if c > 0:
                p.setXLink(self.plots[0])
            p.setTitle(f"Ch{c+1}", color=CH_COLORS[c % len(CH_COLORS)], size="8pt")
            curve = p.plot(pen=pg.mkPen(CH_COLORS[c % len(CH_COLORS)], width=1))
            overlay = p.plot(pen=pg.mkPen("#ffffff", width=2))
            cursor = pg.InfiniteLine(angle=90, movable=False,
                                     pen=pg.mkPen("#888888", width=1))
            p.addItem(cursor)
            self.plots.append(p)
            self.curves.append(curve)
            self.overlays.append(overlay)
            self.cursors.append(cursor)
        self.plots[-1].setLabel("bottom", "time", units="s")

    def _build_spectrum(self):
        self.spec_plot = self.glw.addPlot(row=self.nch, col=0)
        self.spec_plot.showGrid(x=True, y=True, alpha=0.25)
        self.spec_plot.setLabel("left", "Power")
        self.spec_plot.setLabel("bottom", "Frequency", units="Hz")
        self.spec_plot.setXRange(0, min(500.0, self.fs / 2.0), padding=0)
        self.spec_plot.setMouseEnabled(x=False, y=False)
        self.spec_plot.setMenuEnabled(False)
        self.spec_plot.setMaximumHeight(150)
        self.spec_curves = []
        for c in range(self.nch):
            self.spec_curves.append(
                self.spec_plot.plot(pen=pg.mkPen(CH_COLORS[c % len(CH_COLORS)], width=1)))
        self.spec_plot.setVisible(False)

    def set_visible(self, visible):
        """Show/hide the spectrum plot."""
        self.spec_plot.setVisible(visible)

    def update_curves(self, t, data, connect="finite"):
        """Update all channel curves with new data. `data` shape (n_samples, nch)."""
        for c in range(self.nch):
            self.curves[c].setData(t, data[:, c], connect=connect)

    def update_overlay(self, c, t, y):
        """Update onset overlay for channel c."""
        self.overlays[c].setData(t, y, connect="finite")

    def update_cursor(self, value):
        for cur in self.cursors:
            cur.setValue(value)

    def set_cursor_visible(self, visible):
        for cur in self.cursors:
            cur.setVisible(visible)

    def update_spectrum(self, f, psd_list):
        """Update spectrum curves. `psd_list` is list of arrays per channel."""
        for c, psd in enumerate(psd_list):
            self.spec_curves[c].setData(f, psd)

    def clear_overlay(self, c):
        self.overlays[c].setData([], [])