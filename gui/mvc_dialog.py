"""MvcDialog — Noraxon-style MVC calibration.

Record a maximum contraction, watch the live RMS envelope, then set 100% MVC =
peak (or best-1 s) of the envelope in the auto-selected (highlighted) window.
The main window feeds live absolute-volt chunks via feed(); this is a passive
display so only one reader stays on the source.
"""
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets

from dsp.dsp import EmgFilters

CH_COLORS = ["#00e0ff", "#7CFC00", "#ff5050", "#ffb000", "#c080ff",
             "#ff80c0", "#80ffd0", "#ffd000"]


class MvcDialog(QtWidgets.QDialog):
    def __init__(self, nch, fs, muscle_names=None, vref=3.3, parent=None):
        super().__init__(parent)
        self.nch = nch
        self.fs = fs
        self.vref = vref
        self.names = muscle_names or [f"Ch{c+1}" for c in range(nch)]
        self.filters = EmgFilters(fs)
        self._chunks = []
        self.recording = False
        self.mvc_values = [0.0] * nch     # per-channel MVCref (volts) on accept
        self.rms_win_ms = 500.0           # Noraxon: 500-1000 ms normalization window
        self.rule = "peak"                # 'peak' (Noraxon) or 'best1s' (research)
        self._max_s = 20.0
        self._build_ui()
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._redraw)
        self._timer.start(100)            # 10 Hz live envelope redraw

    # ---------------------------------------------------------------- UI
    def _build_ui(self):
        self.setWindowTitle("MVC calibration")
        self.resize(760, 480)
        v = QtWidgets.QVBoxLayout(self)

        hint = QtWidgets.QLabel(
            "Press ● Record, hold your MAXIMUM contraction ~5 s, then ■ Stop.  "
            "100% MVC = peak of the RMS envelope in the highlighted window.")
        hint.setWordWrap(True)
        v.addWidget(hint)

        self.glw = pg.GraphicsLayoutWidget()
        self.glw.setBackground("#0b0f16")
        v.addWidget(self.glw, 1)
        self.plots, self.curves, self.regions = [], [], []
        for c in range(self.nch):
            p = self.glw.addPlot(row=c, col=0)
            p.showGrid(x=True, y=True, alpha=0.3)
            p.setLabel("left", self.names[c], units="mV")
            p.setMouseEnabled(x=False, y=False)
            p.setMenuEnabled(False)
            col = CH_COLORS[c % len(CH_COLORS)]
            self.curves.append(p.plot(pen=pg.mkPen(col, width=1.6)))
            region = pg.LinearRegionItem(brush=(60, 220, 120, 45), movable=False)
            region.setVisible(False)
            p.addItem(region)
            self.regions.append(region)
            self.plots.append(p)
        self.plots[-1].setLabel("bottom", "time", units="s")

        # per-channel MVC value + bar (the "MVC in the bar")
        bars = QtWidgets.QHBoxLayout()
        self.val_lbls, self.bars = [], []
        for c in range(self.nch):
            box = QtWidgets.QVBoxLayout()
            lbl = QtWidgets.QLabel(f"{self.names[c]}: —")
            bar = QtWidgets.QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedHeight(10)
            bar.setStyleSheet(f"QProgressBar::chunk {{ background:{CH_COLORS[c % len(CH_COLORS)]}; }}")
            box.addWidget(lbl)
            box.addWidget(bar)
            self.val_lbls.append(lbl)
            self.bars.append(bar)
            bars.addLayout(box)
        v.addLayout(bars)

        ctl = QtWidgets.QHBoxLayout()
        self.btn_rec = QtWidgets.QPushButton("● Record MVC")
        self.btn_rec.clicked.connect(self._toggle_record)
        self.cmb_win = QtWidgets.QComboBox()
        self.cmb_win.addItems(["250 ms", "500 ms", "1000 ms"])
        self.cmb_win.setCurrentText("500 ms")
        self.cmb_win.currentTextChanged.connect(lambda t: setattr(self, "rms_win_ms", float(t.split()[0])))
        self.cmb_rule = QtWidgets.QComboBox()
        self.cmb_rule.addItems(["Peak (Noraxon)", "Best 1 s (research)"])
        self.cmb_rule.currentTextChanged.connect(
            lambda t: setattr(self, "rule", "peak" if t.startswith("Peak") else "best1s"))
        self.btn_use = QtWidgets.QPushButton("Use MVC")
        self.btn_use.clicked.connect(self.accept)
        self.btn_use.setEnabled(False)
        self.btn_redo = QtWidgets.QPushButton("Redo")
        self.btn_redo.clicked.connect(self.start_record)
        self.btn_cancel = QtWidgets.QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        ctl.addWidget(self.btn_rec)
        ctl.addWidget(QtWidgets.QLabel("RMS win"))
        ctl.addWidget(self.cmb_win)
        ctl.addWidget(self.cmb_rule)
        ctl.addStretch(1)
        ctl.addWidget(self.btn_redo)
        ctl.addWidget(self.btn_use)
        ctl.addWidget(self.btn_cancel)
        v.addLayout(ctl)

    # ---------------------------------------------------------------- data
    def feed(self, volts):
        if not self.recording:
            return
        a = np.asarray(volts, dtype=float)
        if a.ndim == 1:
            a = a.reshape(-1, 1)
        self._chunks.append(a)
        tot = sum(ch.shape[0] for ch in self._chunks)
        cap = int(self._max_s * self.fs)
        while tot > cap and len(self._chunks) > 1:
            tot -= self._chunks.pop(0).shape[0]

    def _buffer(self):
        return np.concatenate(self._chunks, axis=0) if self._chunks else None

    def _env(self, buf, c):
        bp = self.filters.bandpass(buf[:, c:c + 1])[:, 0]
        return self.filters.rms_envelope((bp - bp.mean()).reshape(-1, 1),
                                         win_ms=self.rms_win_ms)[:, 0]

    def _redraw(self):
        if not self.recording:
            return
        buf = self._buffer()
        if buf is None or buf.shape[0] < 40:
            return
        t = np.arange(buf.shape[0]) / self.fs
        for c in range(self.nch):
            self.curves[c].setData(t, self._env(buf, c) * 1e3)

    def _compute_mvc(self, env):
        n = len(env)
        if self.rule == "peak":
            i = int(np.argmax(env))
            w = int(0.1 * self.fs)
            return float(env[i]), max(0, i - w), min(n, i + w)
        k = min(n, int(1.0 * self.fs))
        if n <= k:
            return float(env.mean()), 0, n
        m = np.convolve(env, np.ones(k) / k, mode="valid")
        j = int(np.argmax(m))
        return float(m[j]), j, j + k

    # ---------------------------------------------------------------- control
    def _toggle_record(self):
        self.stop_record() if self.recording else self.start_record()

    def start_record(self):
        self._chunks = []
        self.recording = True
        self.btn_rec.setText("■ Stop")
        self.btn_use.setEnabled(False)
        for r in self.regions:
            r.setVisible(False)

    def stop_record(self):
        self.recording = False
        self.btn_rec.setText("● Record MVC")
        buf = self._buffer()
        if buf is None or buf.shape[0] < int(0.2 * self.fs):
            return
        t = np.arange(buf.shape[0]) / self.fs
        for c in range(self.nch):
            env = self._env(buf, c)
            self.curves[c].setData(t, env * 1e3)
            ref, i0, i1 = self._compute_mvc(env)
            self.mvc_values[c] = ref
            self.regions[c].setRegion([i0 / self.fs, i1 / self.fs])
            self.regions[c].setVisible(True)
            self.val_lbls[c].setText(f"{self.names[c]}: {ref*1e3:.1f} mV  (100% MVC)")
            self.bars[c].setValue(100)
        self.btn_use.setEnabled(any(v > 0 for v in self.mvc_values))
