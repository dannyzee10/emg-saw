"""MvcDialog — Noraxon-style MVC calibration with guided steps.

Open → live RMS-envelope preview + baseline check → ● Record the max hold → ■ Stop →
the peak MVC is highlighted (green window) with its value + bar → Use MVC. The main
window feeds live absolute-volt chunks via feed() (passive display, one reader).
"""
import time

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets

from dsp.dsp import EmgFilters

CH_COLORS = ["#00e0ff", "#7CFC00", "#ff5050", "#ffb000", "#c080ff",
             "#ff80c0", "#80ffd0", "#ffd000"]

GREEN, GREEN_H = "#2e7d32", "#388e3c"
RED, RED_H = "#c62828", "#d32f2f"


def _style(btn, kind):
    c = {"green": (GREEN, GREEN_H, "#fff", "bold"),
         "red": (RED, RED_H, "#fff", "bold"),
         "neutral": ("#1b2c48", "#243a5e", "#e6eefc", "normal")}[kind]
    bg, hv, fg, w = c
    btn.setStyleSheet(
        f"QPushButton{{min-height:34px;font-size:13px;font-weight:{w};padding:5px 18px;"
        f"border-radius:6px;background:{bg};color:{fg};border:none;}}"
        f"QPushButton:hover{{background:{hv};}}")


class MvcDialog(QtWidgets.QDialog):
    HINTS = {
        "ready": "Relax the muscle (baseline should be quiet), then press ● Record and hold your MAXIMUM ~5 s.",
        "recording": "● Recording — HOLD your maximum contraction!  Press ■ Stop when done.",
        "captured": "Peak MVC captured (green window). Click Use MVC to apply it, or Redo.",
    }

    def __init__(self, nch, fs, muscle_names=None, vref=3.3, parent=None):
        super().__init__(parent)
        self.nch = nch
        self.fs = fs
        self.vref = vref
        self.names = muscle_names or [f"Ch{c+1}" for c in range(nch)]
        self.filters = EmgFilters(fs)
        self._chunks = []
        self.state = "ready"              # ready -> recording -> captured
        self.recording = False            # kept for API compatibility
        self.mvc_values = [0.0] * nch
        self.rms_win_ms = 500.0           # Noraxon: 500-1000 ms
        self.rule = "peak"                # 'peak' (Noraxon) or 'best1s'
        self._max_s = 20.0
        self._build_ui()
        self._set_hint("ready")
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._redraw)
        self._timer.start(100)

    # ---------------------------------------------------------------- UI
    def _build_ui(self):
        self.setWindowTitle("MVC calibration")
        self.resize(780, 500)
        v = QtWidgets.QVBoxLayout(self)
        v.setSpacing(8)

        self.lbl_hint = QtWidgets.QLabel()
        self.lbl_hint.setWordWrap(True)
        self.lbl_hint.setStyleSheet("font-style:italic; font-size:13px; color:#bcd0ee;")
        v.addWidget(self.lbl_hint)

        self.lbl_base = QtWidgets.QLabel("baseline: —")
        self.lbl_base.setStyleSheet("color:#8aa0c0; font-size:12px;")
        v.addWidget(self.lbl_base)

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
            region = pg.LinearRegionItem(brush=(60, 220, 120, 55), movable=False)
            region.setVisible(False)
            p.addItem(region)
            self.regions.append(region)
            self.plots.append(p)
        self.plots[-1].setLabel("bottom", "time", units="s")

        bars = QtWidgets.QHBoxLayout()
        self.val_lbls, self.bars = [], []
        for c in range(self.nch):
            box = QtWidgets.QVBoxLayout()
            lbl = QtWidgets.QLabel(f"{self.names[c]}: —")
            lbl.setStyleSheet("font-size:12px; color:#e6eefc;")
            bar = QtWidgets.QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedHeight(12)
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
        _style(self.btn_rec, "green")
        lw = QtWidgets.QLabel("RMS win")
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
        _style(self.btn_use, "green")
        self.btn_redo = QtWidgets.QPushButton("Redo")
        self.btn_redo.clicked.connect(self.start_record)
        _style(self.btn_redo, "neutral")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        _style(self.btn_cancel, "neutral")
        ctl.addWidget(self.btn_rec)
        ctl.addWidget(lw)
        ctl.addWidget(self.cmb_win)
        ctl.addWidget(self.cmb_rule)
        ctl.addStretch(1)
        ctl.addWidget(self.btn_redo)
        ctl.addWidget(self.btn_use)
        ctl.addWidget(self.btn_cancel)
        v.addLayout(ctl)

    def _set_hint(self, state):
        self.lbl_hint.setText(self.HINTS.get(state, ""))

    # ---------------------------------------------------------------- data
    def feed(self, volts):
        if self.state == "captured":
            return
        a = np.asarray(volts, dtype=float)
        if a.ndim == 1:
            a = a.reshape(-1, 1)
        self._chunks.append(a)
        cap = int((self._max_s if self.state == "recording" else 1.5) * self.fs)
        tot = sum(ch.shape[0] for ch in self._chunks)
        while tot > cap and len(self._chunks) > 1:
            tot -= self._chunks.pop(0).shape[0]

    def _buffer(self):
        return np.concatenate(self._chunks, axis=0) if self._chunks else None

    def _env(self, buf, c):
        bp = self.filters.bandpass(buf[:, c:c + 1])[:, 0]
        return self.filters.rms_envelope((bp - bp.mean()).reshape(-1, 1),
                                         win_ms=self.rms_win_ms)[:, 0]

    def _redraw(self):
        if self.state == "captured":
            return
        buf = self._buffer()
        if buf is None or buf.shape[0] < 40:
            return
        t = np.arange(buf.shape[0]) / self.fs
        base = []
        for c in range(self.nch):
            env = self._env(buf, c)
            self.curves[c].setData(t, env * 1e3)
            base.append(float(np.median(env)) * 1e3)
        if self.state == "ready" and base:
            b = max(base)
            ok = b < 20.0
            self.lbl_base.setText(f"baseline: {b:.1f} mV  " + ("low ✓" if ok else "noisy ⚠ relax first"))
            self.lbl_base.setStyleSheet(f"color:{'#39d353' if ok else '#e3b341'}; font-size:12px;")

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
        self.stop_record() if self.state == "recording" else self.start_record()

    def start_record(self):
        self._chunks = []
        self.state = "recording"
        self.recording = True
        self.btn_rec.setText("■ Stop")
        _style(self.btn_rec, "red")
        self.btn_use.setEnabled(False)
        self._set_hint("recording")
        for r in self.regions:
            r.setVisible(False)

    def stop_record(self):
        self.state = "captured"
        self.recording = False
        self.btn_rec.setText("● Record MVC")
        _style(self.btn_rec, "green")
        buf = self._buffer()
        if buf is None or buf.shape[0] < int(0.2 * self.fs):
            self.state = "ready"
            self._set_hint("ready")
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
        self._set_hint("captured")


class MvcSaveDialog(QtWidgets.QDialog):
    """Noraxon-style 'Save Data' step shown right after an MVC capture: name the record
    (auto '(MVC)' suffix), confirm the subject, then Save & Activate (persist the MVC to the
    stack + normalize the scope to %MVC) or Skip. Adapted to our single-window scope."""

    def __init__(self, mvc_values, muscle_names, subject="", parent=None):
        super().__init__(parent)
        self.mvc_values = list(mvc_values)
        self.muscle_names = list(muscle_names)
        self.setWindowTitle("Save MVC")
        self.resize(460, 300)
        v = QtWidgets.QVBoxLayout(self)
        v.setSpacing(8)

        head = QtWidgets.QLabel("MVC captured — save it to the MVC stack and normalize the scope to %MVC.")
        head.setWordWrap(True)
        head.setStyleSheet("font-weight:bold; color:#e6eefc;")
        v.addWidget(head)

        form = QtWidgets.QFormLayout()
        stamp = time.strftime("%Y-%m-%d %H:%M")
        base = subject.strip() or "Session"
        self.ed_name = QtWidgets.QLineEdit(f"{base} {stamp} (MVC)")
        self.ed_subject = QtWidgets.QLineEdit(subject.strip())
        form.addRow("Name", self.ed_name)
        form.addRow("Subject", self.ed_subject)
        v.addLayout(form)

        rows = "\n".join(f"   {self.muscle_names[c]}:  {val*1e3:.1f} mV  (100% MVC)"
                         for c, val in enumerate(self.mvc_values) if val)
        info = QtWidgets.QLabel("Reference levels:\n" + (rows or "   (none)"))
        info.setStyleSheet("color:#bcd0ee; font-size:12px;")
        v.addWidget(info)
        v.addStretch(1)

        ctl = QtWidgets.QHBoxLayout()
        ctl.addStretch(1)
        self.btn_skip = QtWidgets.QPushButton("Skip")
        self.btn_skip.clicked.connect(self.reject)
        _style(self.btn_skip, "neutral")
        self.btn_save = QtWidgets.QPushButton("Save & Activate")
        self.btn_save.clicked.connect(self.accept)
        _style(self.btn_save, "green")
        ctl.addWidget(self.btn_skip)
        ctl.addWidget(self.btn_save)
        v.addLayout(ctl)

    def name(self):
        return self.ed_name.text().strip() or "MVC"

    def subject(self):
        return self.ed_subject.text().strip()
