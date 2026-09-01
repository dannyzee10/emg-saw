"""
Real-time EMG OSCILLOSCOPE + recorder for an STM32-based sensor.

Bench-scope / Noraxon-MR4 style controls:
    Sweep/Scroll | Coupling DC/AC/GND | Volts/div | Time/div | Vert position | Autoset
    Probe scale (for dividers) | Notch 50/60 | RMS envelope | Pause | Record CSV

    python emg_plotter.py --sim --channels 1                              # UI demo, no hw
    python emg_plotter.py --port COM8 --baud 115200 --ascii --channels 1 --fs 500 --kick

Display modes:
  SWEEP  -> hospital-monitor / MR4 style: fixed screen, a write-head sweeps left->right
            painting new data behind it (blank gap ahead), old data wraps at the edge.
  SCROLL -> strip-chart: whole trace slides right->left continuously.

Coupling:
  DC  -> true absolute voltage (GND input = flat 0 V, 3.3 V input = flat 3.3 V line)
  AC  -> DC blocked, trace centered on 0 (use for EMG riding on a VREF bias)
  GND -> input ignored, shows the 0 baseline
Recording always writes raw ADC codes + timestamps (nothing lost to display DSP).

NOTE: the STM32 ADC only measures 0..VREF (3.3 V). To view a 5 V rail, feed it
through a /2 resistor divider into PA0 and set Probe = 2.0 (PA0 is NOT 5 V tolerant).
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time
from collections import deque

from pathlib import Path

if getattr(sys, 'frozen', False):
    ROOT = Path(sys._MEIPASS)
else:
    ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

from dsp.dsp import (EmgFilters, LeadoffTracker, mean_frequency, cocontraction_index,
                     iemg, onset_offset, fatigue_trend)
from communication.sources import SerialSource, AsciiSource, SimSource
from gui.model import AcquisitionModel
from gui.controller import MainController
from gui.plot_widget import EmgPlotWidget
from gui.channel_panel import ChannelPanel
from gui.recording_controller import RecordingController
# ST-LINK programmer CLI — used to auto-revive the board if it halts (--kick).
PROG_CLI = (r"C:\ST\STM32CubeIDE_1.16.1\STM32CubeIDE\plugins"
            r"\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.1.400.202404281720"
            r"\tools\bin\STM32_Programmer_CLI.exe")

CH_COLORS = ["#00e0ff", "#7CFC00", "#ff5050", "#ffb000", "#c080ff",
             "#ff80c0", "#80ffd0", "#ffd000"]

UNIVERSITY = "Beihang University"
APP_NAME = "EMG Acquisition System"
APP_VERSION = "v1.0"

APP_STYLE = """
QMainWindow, QWidget { background:#0b0f16; color:#d6deeb; font-family:'Segoe UI',Arial; font-size:12px; }
QFrame#header { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0c1c3d, stop:1 #133060);
                border-bottom:2px solid #2f6fed; }
QFrame#footer { background:#0d1420; border-top:1px solid #1c2740; }
QLabel#uniName { font-size:17px; font-weight:700; color:#ffffff; }
QLabel#appName { font-size:11px; color:#9bb0d0; }
QLabel#clock   { font-size:14px; font-weight:600; color:#6fb2ff; }
QLabel#footerL, QLabel#footerR { color:#7f92ad; font-size:11px; }
QLabel#logoBadge { background:#2f6fed; color:#ffffff; font-weight:800; font-size:20px;
                   padding:6px 12px; border-radius:8px; }
QLabel#logoCard { background:#ffffff; border-radius:8px; padding:6px 12px; }
QComboBox, QDoubleSpinBox { background:#131b2b; border:1px solid #26324c; border-radius:4px;
                            padding:2px 6px; min-height:20px; color:#d6deeb; }
QComboBox:hover, QDoubleSpinBox:hover { border:1px solid #2f6fed; }
QComboBox QAbstractItemView { background:#131b2b; color:#d6deeb; selection-background-color:#2f6fed; }
QPushButton { background:#131b2b; border:1px solid #26324c; border-radius:4px; padding:3px 10px; }
QPushButton:hover { background:#1b2740; }
QPushButton:checked { background:#2f6fed; color:#ffffff; border:1px solid #2f6fed; }
QCheckBox { color:#c2d0e6; }
QLabel { color:#c2d0e6; }
QFrame#session { background:#0e1626; border-bottom:1px solid #1c2740; }
QFrame#chpanel { background:#0d1420; border-right:1px solid #1c2740; }
QLabel#panelHdr { color:#6f86a8; font-size:10px; font-weight:700; letter-spacing:2px; }
QFrame#chcard { background:#121b2b; border-radius:6px; }
QLineEdit { background:#0b1220; border:1px solid #26324c; border-radius:4px; padding:3px 6px; color:#e8eef8; }
QLineEdit:focus { border:1px solid #2f6fed; }
QLineEdit#muscle { font-weight:700; font-size:13px; }
QLabel#rmsBig { font-size:18px; font-weight:800; }
QLabel#subStat { color:#8fa3bf; font-size:11px; }
QProgressBar { background:#0b1220; border:1px solid #26324c; border-radius:4px; }
"""

NVDIV = 8                                   # vertical divisions (like a bench scope)
NHDIV = 10                                  # horizontal divisions
VDIV_CHOICES = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]        # volts/div
TDIV_CHOICES = [(0.010, "10 ms"), (0.020, "20 ms"), (0.050, "50 ms"),
                (0.100, "100 ms"), (0.200, "200 ms"), (0.500, "500 ms"),
                (1.000, "1 s"), (2.000, "2 s")]                          # sec/div


class EmgScope(QtWidgets.QMainWindow):
    def __init__(self, source, nch, fs, vref, bits, ascii_mode, coupling="DC"):
        super().__init__()
        self.source = source
        self.nch = nch
        self.fs = fs
        self.vref = vref
        self.full = float((1 << bits) - 1)
        self.filters = EmgFilters(fs)
        self._leadoff = LeadoffTracker(nch, fs, vref)   # per-channel electrode lead-off
        self._mdf_hist = [deque(maxlen=600) for _ in range(nch)]   # (t, median-freq) -> fatigue
        self._mvc_dialog = None            # open MVC calibration dialog (fed live by _update)
        self.show_mvc = False              # % MVC display mode (RMS envelope normalized, 0-120%)
        self.mvc_range = 120               # % MVC display range ("Amplitude", Noraxon default 120)

        # scope state
        self.coupling = coupling            # DC / AC / GND
        self.vdiv = 0.5                     # volts / division
        self.tdiv = 0.100                   # seconds / division
        self.vpos = vref / 2.0 if coupling == "DC" else 0.0   # screen-center voltage
        self.probe = 1.0                   # multiply measured volts (e.g. 2.0 for /2 divider)
        self.do_notch = 0
        self.do_envelope = False
        self.show_raw = False              # momentary raw override (Show Raw) over env/%MVC
        self.paused = False
        self.autoscale = False             # per-channel auto vertical scaling (MR4 style)
        self._proc_cache = None            # last processed visible window (for readouts)

        # research-instrument state
        self.muscle_names = [f"Ch{c+1}" for c in range(nch)]   # editable per channel
        self.markers = []                  # list of (elapsed_s, label) event markers
        self._act_max = [1e-3] * nch       # per-channel running max RMS -> activation meter
        self.mvc = [None] * nch            # per-channel MVC reference RMS (None = unset)
        self.show_onset = False            # activation highlight overlay
        self.show_spectrum = False         # live FFT sub-view
        self.overlays = []                 # onset highlight curves (per channel)
        self.spec_plot = None
        self.spec_curves = []

        # display mode
        self.mode = "sweep"                # "sweep" (monitor) or "scroll" (strip-chart)
        self.screen_n = max(2, int(self.tdiv * NHDIV * fs))
        self.sweep_y = None                # persistent on-screen buffer for sweep mode
        self.sweep_pos = 0

        # retain a bit more than the widest time base; ring holds ABSOLUTE volts
        self.buf_s = max(TDIV_CHOICES[-1][0] * NHDIV + 1.0, 6.0)
        self.buf_n = int(self.buf_s * fs)
        self.ring = np.zeros((self.buf_n, nch), dtype=float)
        self.filled = 0

        self.recording = RecordingController(fs, nch, vref)

        self._last_stat_t = time.perf_counter()
        self._last_stat_n = 0
        self.total_samples = 0

        # auto-revive (set by main when --kick)
        self.kick_cli = None
        self._last_kick = 0.0
        self._kick_proc = None

        self._start_time = time.time()
        port = getattr(source, "port", None)
        baud = getattr(source, "baud", None)
        self._conn_info = (f"Port {port} @ {baud} baud" if port
                           else "Source: Simulation")

        # Create plot widget and channel panel
        self.plot_widget = EmgPlotWidget(nch, fs)
        self.channel_panel = ChannelPanel(nch, muscle_names=self.muscle_names)

        # Set aliases
        self.plots = self.plot_widget.plots
        self.curves = self.plot_widget.curves
        self.cursors = self.plot_widget.cursors
        self.overlays = self.plot_widget.overlays
        self.spec_plot = self.plot_widget.spec_plot
        self.spec_curves = self.plot_widget.spec_curves
        self.ch_cards = self.channel_panel.cards
        # ChannelPanel's MVC buttons were left unconnected by the MVC refactor — wire them
        self.channel_panel.btn_mvc.clicked.connect(self._set_mvc)
        self.channel_panel.btn_mvc_clr.clicked.connect(self._clear_mvc)

        self._build_ui()
        self._apply_scaling()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(16)

        self.clock_timer = QtCore.QTimer()
        self.clock_timer.timeout.connect(self._tick_clock)
        self.clock_timer.start(1000)
        self._tick_clock()

        # Create model and controller wrappers
        self.model = AcquisitionModel(source, nch, fs)
        self.controller = MainController(self.model)
        self.controller.start()

    # ---------- UI ----------
    def _build_ui(self):
        self.setWindowTitle(f"{UNIVERSITY} — {APP_NAME}")
        self.setStyleSheet(APP_STYLE)
        self.resize(1300, 200 * self.nch + 190)
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        v = QtWidgets.QVBoxLayout(central)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        v.addWidget(self._build_header())
        v.addWidget(self._build_session_bar())

        barframe = QtWidgets.QFrame()
        bar = QtWidgets.QHBoxLayout(barframe)
        bar.setContentsMargins(12, 8, 12, 8)
        bar.setSpacing(8)

        bar.addWidget(QtWidgets.QLabel("Mode"))
        self.cmb_mode = QtWidgets.QComboBox()
        self.cmb_mode.addItems(["Sweep", "Scroll"])
        self.cmb_mode.currentTextChanged.connect(self._on_mode)
        bar.addWidget(self.cmb_mode)

        bar.addWidget(QtWidgets.QLabel("Coupling"))
        self.cmb_couple = QtWidgets.QComboBox()
        self.cmb_couple.addItems(["DC", "AC", "GND"])
        self.cmb_couple.setCurrentText(self.coupling)
        self.cmb_couple.currentTextChanged.connect(self._on_coupling)
        bar.addWidget(self.cmb_couple)

        bar.addWidget(QtWidgets.QLabel("V/div"))
        self.cmb_vdiv = QtWidgets.QComboBox()
        self.cmb_vdiv.addItems([self._fmt_v(x) for x in VDIV_CHOICES])
        self.cmb_vdiv.setCurrentText(self._fmt_v(self.vdiv))
        self.cmb_vdiv.currentIndexChanged.connect(self._on_vdiv)
        bar.addWidget(self.cmb_vdiv)

        bar.addWidget(QtWidgets.QLabel("Time/div"))
        self.cmb_tdiv = QtWidgets.QComboBox()
        self.cmb_tdiv.addItems([lbl for _, lbl in TDIV_CHOICES])
        self.cmb_tdiv.setCurrentText("100 ms")
        self.cmb_tdiv.currentIndexChanged.connect(self._on_tdiv)
        bar.addWidget(self.cmb_tdiv)

        bar.addWidget(QtWidgets.QLabel("Vpos(V)"))
        self.spn_vpos = QtWidgets.QDoubleSpinBox()
        self.spn_vpos.setRange(-2 * self.vref, 3 * self.vref)
        self.spn_vpos.setSingleStep(0.1)
        self.spn_vpos.setValue(self.vpos)
        self.spn_vpos.valueChanged.connect(self._on_vpos)
        bar.addWidget(self.spn_vpos)

        self.btn_auto = QtWidgets.QPushButton("Autoset")
        self.btn_auto.clicked.connect(self._autoset)
        bar.addWidget(self.btn_auto)

        bar.addWidget(QtWidgets.QLabel("Probe x"))
        self.spn_probe = QtWidgets.QDoubleSpinBox()
        self.spn_probe.setRange(0.1, 100.0)
        self.spn_probe.setSingleStep(0.5)
        self.spn_probe.setValue(1.0)
        self.spn_probe.valueChanged.connect(lambda x: setattr(self, "probe", float(x)))
        bar.addWidget(self.spn_probe)

        bar.addWidget(QtWidgets.QLabel("Notch"))
        self.cmb_notch = QtWidgets.QComboBox()
        self.cmb_notch.addItems(["off", "50 Hz", "60 Hz"])
        self.cmb_notch.currentTextChanged.connect(self._on_notch)
        bar.addWidget(self.cmb_notch)

        self.cb_env = QtWidgets.QCheckBox("RMS env")
        self.cb_env.stateChanged.connect(self._on_envelope)
        bar.addWidget(self.cb_env)

        self.cb_raw = QtWidgets.QCheckBox("Show Raw")
        self.cb_raw.setToolTip("Momentarily show the raw EMG (overrides RMS env / % MVC) — your settings are kept")
        self.cb_raw.stateChanged.connect(self._on_show_raw)
        bar.addWidget(self.cb_raw)

        self.cb_auto = QtWidgets.QCheckBox("Auto V/ch")
        self.cb_auto.setToolTip("Auto-scale each channel's lane to its own signal (MR4 style)")
        self.cb_auto.stateChanged.connect(self._on_auto)
        bar.addWidget(self.cb_auto)

        self.cb_onset = QtWidgets.QCheckBox("Onset")
        self.cb_onset.setToolTip("Highlight active (contraction) periods on the trace")
        self.cb_onset.stateChanged.connect(lambda s: setattr(self, "show_onset", bool(s)))
        bar.addWidget(self.cb_onset)

        self.cb_mvc = QtWidgets.QCheckBox("% MVC")
        self.cb_mvc.setToolTip("Show each lane as % MVC — RMS envelope normalized to the MVC, 0-120% (set MVC first)")
        self.cb_mvc.stateChanged.connect(self._on_mvc_view)
        bar.addWidget(self.cb_mvc)

        self.cmb_amp = QtWidgets.QComboBox()
        self.cmb_amp.addItems(["100%", "120%", "150%", "200%"])
        self.cmb_amp.setCurrentText("120%")
        self.cmb_amp.setToolTip("% MVC display range (Amplitude) — Noraxon default 120% shows effort above the MVC")
        self.cmb_amp.currentTextChanged.connect(self._on_amp_range)
        bar.addWidget(self.cmb_amp)

        self.btn_base = QtWidgets.QPushButton("EMG Baseline")
        self.btn_base.setToolTip("Check the resting EMG baseline before recording — relax the muscle, then click")
        self.btn_base.clicked.connect(self._baseline_check)
        bar.addWidget(self.btn_base)

        self.cb_spec = QtWidgets.QCheckBox("Spectrum")
        self.cb_spec.setToolTip("Show a live FFT frequency spectrum below the traces")
        self.cb_spec.stateChanged.connect(self._on_spectrum)
        bar.addWidget(self.cb_spec)

        self.btn_pause = QtWidgets.QPushButton("Pause")
        self.btn_pause.setCheckable(True)
        self.btn_pause.toggled.connect(self._on_pause)
        bar.addWidget(self.btn_pause)

        self.btn_rec = QtWidgets.QPushButton("● Record")
        self.btn_rec.setCheckable(True)
        self.btn_rec.toggled.connect(self._on_record)
        self.btn_rec.setStyleSheet(
            "QPushButton{min-height:30px;font-size:13px;font-weight:bold;padding:4px 16px;"
            "border-radius:6px;background:#2e7d32;color:#fff;border:none;}"
            "QPushButton:hover{background:#388e3c;} QPushButton:checked{background:#c62828;}")
        bar.addWidget(self.btn_rec)

        bar.addStretch(1)
        self.lbl_stat = QtWidgets.QLabel("")
        bar.addWidget(self.lbl_stat)
        v.addWidget(barframe)

        # transient result banner (EMG baseline check etc.) — big, colored, auto-hides
        self.lbl_banner = QtWidgets.QLabel("")
        self.lbl_banner.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_banner.setVisible(False)
        v.addWidget(self.lbl_banner)
        self._banner_timer = QtCore.QTimer(self)
        self._banner_timer.setSingleShot(True)
        self._banner_timer.timeout.connect(lambda: self.lbl_banner.setVisible(False))

        mainrow = QtWidgets.QHBoxLayout()
        mainrow.setContentsMargins(0, 0, 0, 0)
        mainrow.setSpacing(0)

        mainrow.addWidget(self.channel_panel)
        mainrow.addWidget(self.plot_widget.glw, 1)
        v.addLayout(mainrow, 1)

        v.addWidget(self._build_footer())

    # ---------- session bar + channel panel (research instrument) ----------
    def _build_session_bar(self):
        sf = QtWidgets.QFrame()
        sf.setObjectName("session")
        s = QtWidgets.QHBoxLayout(sf)
        s.setContentsMargins(14, 5, 14, 5)
        s.setSpacing(8)
        self.ed_subject = QtWidgets.QLineEdit()
        self.ed_subject.setPlaceholderText("Subject / ID")
        self.ed_subject.setMaximumWidth(160)
        self.ed_trial = QtWidgets.QLineEdit()
        self.ed_trial.setPlaceholderText("Trial / task")
        self.ed_trial.setMaximumWidth(160)
        self.ed_notes = QtWidgets.QLineEdit()
        self.ed_notes.setPlaceholderText("Notes")
        for lab, w in (("Subject", self.ed_subject), ("Trial", self.ed_trial), ("Notes", self.ed_notes)):
            s.addWidget(QtWidgets.QLabel(lab))
            s.addWidget(w, 1 if lab == "Notes" else 0)
        self.btn_marker = QtWidgets.QPushButton("⚑ Marker")
        self.btn_marker.setToolTip("Drop a timestamped event marker (also key: M)")
        self.btn_marker.clicked.connect(self._add_marker)
        self.btn_snap = QtWidgets.QPushButton("⧉ Snapshot")
        self.btn_snap.clicked.connect(self._snapshot)
        self.btn_report = QtWidgets.QPushButton("📄 Report")
        self.btn_report.clicked.connect(self._report)
        s.addWidget(self.btn_marker)
        s.addWidget(self.btn_snap)
        s.addWidget(self.btn_report)
        return sf

    def _build_channel_panel(self):
        pf = QtWidgets.QFrame()
        pf.setObjectName("chpanel")
        pf.setFixedWidth(228)
        col = QtWidgets.QVBoxLayout(pf)
        col.setContentsMargins(8, 8, 8, 8)
        col.setSpacing(8)
        hdr = QtWidgets.QLabel("CHANNELS")
        hdr.setObjectName("panelHdr")
        col.addWidget(hdr)
        mvc_row = QtWidgets.QHBoxLayout()
        self.btn_mvc = QtWidgets.QPushButton("Set MVC")
        self.btn_mvc.setToolTip("Hold a max contraction, then click to set 100% MVC reference")
        self.btn_mvc.clicked.connect(self._set_mvc)
        self.btn_mvc_clr = QtWidgets.QPushButton("Clear")
        self.btn_mvc_clr.clicked.connect(self._clear_mvc)
        mvc_row.addWidget(self.btn_mvc)
        mvc_row.addWidget(self.btn_mvc_clr)
        col.addLayout(mvc_row)
        self.ch_cards = []
        for c in range(self.nch):
            color = CH_COLORS[c % len(CH_COLORS)]
            card = QtWidgets.QFrame()
            card.setObjectName("chcard")
            card.setStyleSheet(f"#chcard {{ border-left:4px solid {color}; }}")
            cl = QtWidgets.QVBoxLayout(card)
            cl.setContentsMargins(8, 6, 8, 6)
            cl.setSpacing(3)
            name = QtWidgets.QLineEdit(self.muscle_names[c])
            name.setObjectName("muscle")
            name.textChanged.connect(lambda t, i=c: self._set_muscle(i, t))
            cl.addWidget(name)
            rms = QtWidgets.QLabel("RMS  —")
            rms.setObjectName("rmsBig")
            rms.setStyleSheet(f"color:{color};")
            cl.addWidget(rms)
            sub = QtWidgets.QLabel("pk-pk —    medF —")
            sub.setObjectName("subStat")
            cl.addWidget(sub)
            bar = QtWidgets.QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedHeight(8)
            bar.setStyleSheet(f"QProgressBar::chunk {{ background:{color}; }}")
            cl.addWidget(bar)
            col.addWidget(card)
            self.ch_cards.append({"name": name, "rms": rms, "sub": sub, "bar": bar})
        col.addStretch(1)
        return pf

    def _set_muscle(self, i, text):
        if 0 <= i < len(self.muscle_names):
            self.muscle_names[i] = text or f"Ch{i+1}"

    # ---------- branding chrome ----------
    def _build_header(self):
        hf = QtWidgets.QFrame()
        hf.setObjectName("header")
        h = QtWidgets.QHBoxLayout(hf)
        h.setContentsMargins(14, 8, 14, 8)
        h.setSpacing(12)

        logo_path = str(ROOT / "assets" / "logo.png")
        pm = QtGui.QPixmap(logo_path) if os.path.exists(logo_path) else QtGui.QPixmap()
        has_logo = not pm.isNull()
        logo = QtWidgets.QLabel()
        if has_logo:
            logo.setPixmap(pm.scaledToHeight(44, QtCore.Qt.SmoothTransformation))
            logo.setObjectName("logoCard")          # white card so the navy logo pops
            self.setWindowIcon(QtGui.QIcon(logo_path))
        else:
            logo.setText("BUAA")
            logo.setObjectName("logoBadge")
        h.addWidget(logo)

        tbox = QtWidgets.QVBoxLayout()
        tbox.setSpacing(0)
        # if the logo already carries the university name, lead with the app name
        title = APP_NAME if has_logo else UNIVERSITY
        subtitle = (f"Real-time surface EMG   ·   {APP_VERSION}" if has_logo
                    else f"{APP_NAME}   ·   {APP_VERSION}")
        t1 = QtWidgets.QLabel(title)
        t1.setObjectName("uniName")
        t2 = QtWidgets.QLabel(subtitle)
        t2.setObjectName("appName")
        tbox.addWidget(t1)
        tbox.addWidget(t2)
        h.addLayout(tbox)

        h.addStretch(1)
        self.lbl_clock = QtWidgets.QLabel("")
        self.lbl_clock.setObjectName("clock")
        h.addWidget(self.lbl_clock)
        return hf

    def _build_footer(self):
        ff = QtWidgets.QFrame()
        ff.setObjectName("footer")
        ff.setFixedHeight(26)
        f = QtWidgets.QHBoxLayout(ff)
        f.setContentsMargins(14, 2, 14, 2)
        self.lbl_conn = QtWidgets.QLabel(self._conn_info)
        self.lbl_conn.setObjectName("footerL")
        f.addWidget(self.lbl_conn)
        self.lbl_hint = QtWidgets.QLabel("Ready — check EMG Baseline, then press ● Record to capture the activity.")
        self.lbl_hint.setStyleSheet("font-style:italic; color:#7fa8dd;")
        f.addWidget(self.lbl_hint)
        f.addStretch(1)
        self.lbl_footer = QtWidgets.QLabel("Ready")
        self.lbl_footer.setObjectName("footerR")
        f.addWidget(self.lbl_footer)
        return ff

    def _tick_clock(self):
        self.lbl_clock.setText(time.strftime("%Y-%m-%d   %H:%M:%S"))
        el = int(time.time() - self._start_time)
        rec = " ● RECORDING" if self.recording.active else ""
        self.lbl_footer.setText(
            f"Elapsed  {el//3600:02d}:{el%3600//60:02d}:{el%60:02d}{rec}")

    # ---------- control handlers ----------
    @staticmethod
    def _fmt_v(x):
        return f"{x*1000:.0f} mV" if x < 1 else f"{x:.1f} V"

    def _on_mode(self, txt):
        self.mode = "sweep" if txt == "Sweep" else "scroll"
        self.sweep_y = None                       # rebuild sweep buffer
        for cur in self.cursors:
            cur.setVisible(self.mode == "sweep")

    def _on_coupling(self, txt):
        self.coupling = txt
        self.vpos = self.vref / 2.0 if txt == "DC" else 0.0
        self.spn_vpos.blockSignals(True)
        self.spn_vpos.setValue(self.vpos)
        self.spn_vpos.blockSignals(False)
        self.sweep_y = None                       # baseline changed -> repaint
        self._apply_scaling()

    def _on_vdiv(self, idx):
        self.vdiv = VDIV_CHOICES[idx]
        self._apply_scaling()

    def _on_tdiv(self, idx):
        self.tdiv = TDIV_CHOICES[idx][0]
        self._apply_scaling()

    def _on_vpos(self, val):
        self.vpos = float(val)
        self._apply_scaling()

    def _on_notch(self, txt):
        self.do_notch = 0 if txt == "off" else int(txt.split()[0])

    def _on_pause(self, checked):
        self.paused = checked
        self.btn_pause.setText("Resume" if checked else "Pause")
        self._update_rec_hint()

    def _on_show_raw(self, s):
        self.show_raw = bool(s)
        self.sweep_y = None                 # units may change (env/% -> raw) -> rebuild sweep
        self._apply_scaling()

    def _update_rec_hint(self):
        """Guide the Record -> Pause -> Stop activity with a contextual step hint."""
        if self.recording.active:
            if self.paused:
                self.lbl_hint.setText("View paused (still recording) — Resume to watch, or ■ Stop to finish & save.")
            else:
                self.lbl_hint.setText("● Recording — Pause freezes the view (capture continues); ■ Stop finishes & saves.")
        elif self.paused:
            self.lbl_hint.setText("View paused — Resume to watch. Press ● Record to capture the activity.")
        else:
            self.lbl_hint.setText("Ready — check EMG Baseline, then press ● Record to capture the activity.")

    def _on_auto(self, s):
        self.autoscale = bool(s)
        self._apply_scaling()

    @staticmethod
    def _fmt_amp(v):
        av = abs(v)
        if av < 1e-3:
            return f"{v*1e6:.0f} uV"
        if av < 1.0:
            return f"{v*1e3:.1f} mV"
        return f"{v:.2f} V"

    @staticmethod
    def _make_ticks(lo, hi, step):
        n0 = int(math.ceil((lo - 1e-9) / step))
        n1 = int(math.floor((hi + 1e-9) / step))
        return [(i * step, f"{i*step:g}") for i in range(n0, n1 + 1)]

    @staticmethod
    def _nice_step(raw):
        if raw <= 0:
            return 0.1
        p = 10 ** math.floor(math.log10(raw))
        for m in (1, 2, 2.5, 5, 10):
            if m * p >= raw - 1e-12:
                return m * p
        return 10 * p

    # ---------- research metrics + export ----------
    def _median_freq(self, x):
        """EMG median frequency (Hz) over the 20-450 Hz band — a fatigue indicator."""
        n = len(x)
        if n < 32:
            return 0.0
        f = np.fft.rfftfreq(n, 1.0 / self.fs)
        P = np.abs(np.fft.rfft(x * np.hanning(n))) ** 2
        band = (f >= 20.0) & (f <= 450.0)
        if not band.any():
            return 0.0
        fb, Pb = f[band], P[band]
        cum = np.cumsum(Pb)
        if cum[-1] <= 0:
            return 0.0
        idx = int(np.searchsorted(cum, cum[-1] / 2.0))
        return float(fb[min(idx, len(fb) - 1)])

    def _set_mvc(self):
        from gui.mvc_dialog import MvcDialog, MvcSaveDialog
        dlg = MvcDialog(self.nch, self.fs, self.muscle_names, vref=self.vref, parent=self)
        self._mvc_dialog = dlg
        try:
            accepted = dlg.exec_()
        finally:
            self._mvc_dialog = None
        if accepted != QtWidgets.QDialog.Accepted:
            return
        for c in range(self.nch):
            if dlg.mvc_values[c] > 0:
                self.mvc[c] = dlg.mvc_values[c]
        # #5 Save Data dialog (auto '(MVC)' name + subject) -> persist to the MVC stack
        save = MvcSaveDialog(self.mvc, self.muscle_names, subject=self.ed_subject.text(), parent=self)
        if save.exec_() == QtWidgets.QDialog.Accepted:
            rec = self._save_mvc_record(save.name(), save.subject())
            if save.subject():
                self.ed_subject.setText(save.subject())
            note = f"saved as “{rec['name']}”"
        else:
            note = "not saved"
        # #6 auto-activate the normalized (%MVC) view + 'MVC stack updated'
        self._activate_mvc(note)

    def _save_mvc_record(self, name, subject):
        """Persist the current per-channel MVC to mvc_store.json (the reusable 'MVC stack')."""
        import json
        rec = {"name": name, "subject": subject,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), "fs": self.fs,
               "channels": [{"name": self.muscle_names[c],
                             "mvc_v": v, "mvc_mv": (v * 1e3 if v else None)}
                            for c, v in enumerate(self.mvc)]}
        path = os.path.abspath("mvc_store.json")
        store = []
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    store = json.load(f)
            except Exception:
                store = []
        store.append(rec)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)
        return rec

    def _activate_mvc(self, note):
        """#6: after MVC, switch the scope to %MVC (y-axis becomes %) and confirm."""
        self.lbl_footer.setText(
            "MVC captured: " + ", ".join(self._fmt_amp(v) for v in self.mvc if v) +
            " — channels now show % MVC")
        self.lbl_hint.setText(f"MVC set ✓ — normalized to % MVC (0–{self.mvc_range}%). Untick % MVC for raw.")
        if not self.cb_mvc.isChecked():
            self.cb_mvc.setChecked(True)          # auto-activate normalized view (fires _on_mvc_view)
        else:
            self.sweep_y = None
            self._apply_scaling()
        self._flash_banner("ok", f"MVC stack updated — amplitude normalized to %MVC ({note})")

    def _clear_mvc(self):
        self.mvc = [None] * self.nch
        self.lbl_footer.setText("MVC cleared")

    def _on_spectrum(self, s):
        self.show_spectrum = bool(s)
        if self.spec_plot is not None:
            self.spec_plot.setVisible(self.show_spectrum)

    def _mvc_view_on(self):
        return self.show_mvc and all(v for v in self.mvc) and not self.show_raw

    def _on_mvc_view(self, s):
        self.show_mvc = bool(s)
        if self.show_mvc and not self._mvc_view_on():
            self.lbl_footer.setText("Set MVC first (Set MVC button), then enable % MVC view")
        self.sweep_y = None                # units changed -> rebuild the sweep buffer
        self._apply_scaling()

    def _on_envelope(self, s):
        self.do_envelope = bool(s)
        if self.show_mvc:                  # %MVC axis differs for raw vs envelope
            self.sweep_y = None
            self._apply_scaling()

    def _on_amp_range(self, t):
        try:
            self.mvc_range = int(t.rstrip("%"))
        except ValueError:
            self.mvc_range = 120
        if self.show_mvc:
            self.sweep_y = None
            self._apply_scaling()

    def _baseline_check(self):
        """Noraxon-style EMG Baseline Check: report per-channel resting RMS AND the electrode
        lead-off state (the SAME latched state that drives the channel dot), so a disconnected
        or poor lead fails the baseline even though its RMS is low."""
        show_n = min(int(2.0 * self.fs), self.filled)
        if show_n < 40:
            self.lbl_hint.setText("EMG Baseline: no signal yet — stream, relax the muscle, then click")
            self._baseline_popup("warn", "No signal yet",
                                 "Start streaming, relax the muscle, then click EMG Baseline.")
            return
        raw = self.ring[-show_n:]
        parts, lines = [], []
        level = "ok"                                    # ok -> warn -> bad (worst channel wins)
        for c in range(self.nch):
            bp = self.filters.bandpass(raw[:, c:c + 1])[:, 0]
            env = self.filters.rms_envelope((bp - bp.mean()).reshape(-1, 1))[:, 0]
            lvl = float(np.median(env)) * 1e3          # mV
            st = self._leadoff.state[c]                # 'good'/'poor'/'open' == the dot colour
            if st == "open":
                sev, note = "bad", "DISCONNECTED — reconnect the electrode / lead"
            elif st == "poor":
                sev, note = "warn", f"poor contact / noisy ({lvl:.1f} mV) — check electrode + DRL"
            elif lvl >= 20.0:
                sev, note = "warn", f"not relaxed ({lvl:.1f} mV) — rest the muscle"
            else:
                sev, note = "ok", f"{lvl:.1f} mV — relaxed ✓"
            level = self._worse(level, sev)
            mark = {"ok": "✓", "warn": "⚠", "bad": "✗"}[sev]
            parts.append(f"{self.muscle_names[c]} {mark}")
            lines.append(f"{self.muscle_names[c]}:  {note}")
        tag = {"ok": "OK — relaxed ✓", "warn": "CHECK ⚠", "bad": "LEAD OFF ✗"}[level]
        color = {"ok": "#39d353", "warn": "#e3b341", "bad": "#ff6b6b"}[level]
        self.lbl_hint.setStyleSheet(f"font-style:italic; font-weight:bold; color:{color};")
        self.lbl_hint.setText("EMG Baseline: " + " | ".join(parts) + "  —  " + tag)
        head = {"ok": "Baseline OK — muscle relaxed ✓", "warn": "Baseline CHECK ⚠",
                "bad": "Electrode LEAD OFF ✗"}[level]
        info = "\n".join(lines) + ("\n\nReady to record MVC." if level == "ok"
                else "\n\nFix the flagged channel(s), then re-check.")
        self._baseline_popup(level, head, info)

    @staticmethod
    def _worse(a, b):
        order = {"ok": 0, "warn": 1, "bad": 2}
        return a if order[a] >= order[b] else b

    def _baseline_popup(self, level, head, info):
        one = info.replace("\n\n", "  —  ").replace("\n", "   ")
        self._flash_banner(level, f"EMG Baseline — {head}      ({one})")

    def _flash_banner(self, level, text):
        """Big in-window banner below the toolbar (child widget -> safe teardown, no modal
        to dismiss). level = ok/warn/bad; auto-hides after a few seconds."""
        bg, fg = {"ok": ("#173d1f", "#39d353"),
                  "warn": ("#3d2f10", "#e3b341"),
                  "bad": ("#3d1414", "#ff6b6b")}[level]
        self.lbl_banner.setStyleSheet(
            f"background:{bg}; color:{fg}; font-size:15px; font-weight:bold;"
            f"padding:8px; border:1px solid {fg}; border-radius:4px;")
        self.lbl_banner.setText(text)
        self.lbl_banner.setVisible(True)
        self._banner_timer.start(6000)

    def _onset_overlay(self, c, t, y):
        """Highlight active (contraction) samples in white on top of the trace."""
        ov = self.overlays[c]
        if not self.show_onset or len(y) < 16:
            ov.setData([], [])
            return
        yc = np.nan_to_num(y, nan=0.0)
        env = self.filters.rms_envelope(yc.reshape(-1, 1))[:, 0]
        emax = float(env.max()) if env.size else 0.0
        if self.mvc[c]:
            thr = 0.15 * self.mvc[c]                     # active above 15% MVC
        else:
            base = float(np.percentile(env, 20))
            thr = max(base * 3.0, 0.10 * emax)
        mask = (env > thr) & ~np.isnan(y)
        ov.setData(t, np.where(mask, y, np.nan), connect="finite")

    def _add_marker(self):
        el = time.time() - self._start_time
        label = f"M{len(self.markers) + 1}"
        self.markers.append((el, label))
        if self.recording.active:
            self.recording.write_marker(label, el)
        self.lbl_footer.setText(f"⚑ Marker {label} @ {el:.1f}s   (total {len(self.markers)})")

    def _snapshot(self):
        fname = time.strftime("emg_snapshot_%Y%m%d_%H%M%S.png")
        self.centralWidget().grab().save(fname)
        self.lbl_footer.setText(f"Snapshot saved: {fname}")
        return fname

    def _report(self):
        ts = time.strftime("%Y%m%d_%H%M%S")
        png = f"emg_report_{ts}.png"
        self.centralWidget().grab().save(png)
        proc = self._proc_cache
        rows = ""
        for c in range(self.nch):
            if proc is not None and proc.shape[0] > 2:
                x = proc[:, c]; ac = x - x.mean()
                rms_v = float(np.sqrt(np.mean(ac * ac)))
                rms = self._fmt_amp(rms_v)
                pk = self._fmt_amp(float(np.ptp(x)))
                mf = f"{self._median_freq(ac):.0f}"
                mnf = f"{mean_frequency(ac, self.fs):.0f}"
                ie = f"{iemg(ac, self.fs) * 1e3:.1f}"
                mvc = f"{100.0 * rms_v / self.mvc[c]:.0f}%" if self.mvc[c] else "&mdash;"
                env = self.filters.rms_envelope(proc[:, c:c + 1])[:, 0]
                thr = 0.2 * float(env.max()) if env.size else 0.0
                iv = onset_offset(env, self.fs, thr) if thr > 0 else []
                onset = f"{len(iv)} ({iv[0][0]:.2f}s)" if iv else "0"
                if len(self._mdf_hist[c]) >= 4:
                    ts_, mdfs_ = zip(*self._mdf_hist[c])
                    _, fpct = fatigue_trend(mdfs_, ts_)
                    fat = f"{fpct:+.0f}%"
                else:
                    fat = "&mdash;"
            else:
                rms = pk = mf = mnf = ie = mvc = onset = fat = "&mdash;"
            color = CH_COLORS[c % len(CH_COLORS)]
            rows += (f"<tr><td style='color:{color};font-weight:700'>{self.muscle_names[c]}</td>"
                     f"<td>{rms}</td><td>{pk}</td><td>{mf}</td><td>{mnf}</td>"
                     f"<td>{ie}</td><td>{mvc}</td><td>{onset}</td><td>{fat}</td></tr>")
        marks = "".join(f"<li>{l} @ {t:.2f}s</li>" for t, l in self.markers) or "<li>none</li>"
        el = int(time.time() - self._start_time)
        html = f"""<!doctype html><html><head><meta charset='utf-8'><title>EMG Report {ts}</title>
<style>body{{font-family:'Segoe UI',Arial;margin:32px;color:#111}}
h1{{color:#123a7a}} table{{border-collapse:collapse;margin:10px 0}}
td,th{{border:1px solid #ccc;padding:6px 16px;text-align:left}} th{{background:#eef3fb}}
.meta td{{border:none;padding:2px 14px 2px 0}} img{{max-width:100%;border:1px solid #ccc;margin-top:10px}}</style>
</head><body>
<h1>{UNIVERSITY} &mdash; EMG Report</h1>
<table class='meta'>
<tr><td><b>Subject</b></td><td>{self.ed_subject.text() or '&mdash;'}</td></tr>
<tr><td><b>Trial</b></td><td>{self.ed_trial.text() or '&mdash;'}</td></tr>
<tr><td><b>Notes</b></td><td>{self.ed_notes.text() or '&mdash;'}</td></tr>
<tr><td><b>Date</b></td><td>{time.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
<tr><td><b>Duration</b></td><td>{el//60:02d}:{el%60:02d}</td></tr>
<tr><td><b>Acquisition</b></td><td>{self.fs:.0f} S/s &middot; {self.nch} channel(s) &middot; {self._conn_info}</td></tr>
</table>
<h3>Per-channel summary</h3>
<table><tr><th>Muscle</th><th>RMS</th><th>pk-pk</th><th>Med Hz</th><th>Mean Hz</th><th>iEMG mV&middot;s</th><th>% MVC</th><th>Onsets</th><th>Fatigue</th></tr>{rows}</table>
<h3>Event markers</h3><ul>{marks}</ul>
<h3>Snapshot</h3><img src='{png}'>
</body></html>"""
        fn = f"emg_report_{ts}.html"
        with open(fn, "w", encoding="utf-8") as f:
            f.write(html)
        self.lbl_footer.setText(f"Report saved: {fn}")
        try:
            os.startfile(os.path.abspath(fn))
        except Exception:
            pass

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_M:
            self._add_marker()
        else:
            super().keyPressEvent(ev)

    def _apply_scaling(self):
        half = self.vdiv * NVDIV / 2.0
        window = self.tdiv * NHDIV
        new_screen_n = max(2, int(window * self.fs))
        if new_screen_n != self.screen_n:
            self.screen_n = new_screen_n
            self.sweep_y = None                   # time base changed -> rebuild sweep
        # explicit time ticks INCLUDING the right-edge value so labels span the full width
        nx = max(1, int(round(window / self.tdiv)))
        xticks = [(i * self.tdiv, f"{i*self.tdiv:g}") for i in range(nx + 1)]
        # snap the Y range so the top & bottom edges land exactly on grid lines (incl. below 0)
        ylo = math.floor((self.vpos - half) / self.vdiv + 1e-9) * self.vdiv
        yhi = ylo + self.vdiv * NVDIV
        mvc_view = self._mvc_view_on()
        for i, p in enumerate(self.plots):
            p.setXRange(0, window, padding=0)
            p.getAxis("bottom").setTicks([xticks])
            if mvc_view:
                p.setLabel("left", "%MVC")
                if self.do_envelope:                  # RMS envelope: 0-<range>% activation view
                    p.getViewBox().disableAutoRange()
                    hi_ = self.mvc_range
                    p.setYRange(0, hi_, padding=0)
                    step = 20 if hi_ <= 120 else (25 if hi_ <= 150 else 50)
                    p.getAxis("left").setTicks([[(v, str(v)) for v in range(0, hi_ + 1, step)]])
                else:                                 # raw EMG normalized: fit the +/- swing
                    p.getAxis("left").setTicks(None)
                    p.getViewBox().enableAutoRange(axis="y")
            else:
                p.getViewBox().disableAutoRange()
                p.setLabel("left", f"Ch{i+1}", units="V")
                if not self.autoscale:                # autoscale Y is set in _update_status
                    p.setYRange(ylo, yhi, padding=0)
                    p.getAxis("left").setTicks([self._make_ticks(ylo, yhi, self.vdiv)])

    def _autoset(self):
        if self.filled < 10:
            return
        show_n = min(self.screen_n, self.filled)
        proc = self._process(self.ring[-show_n:])
        lo, hi = float(np.min(proc)), float(np.max(proc))
        target = max(hi - lo, 1e-4) / 6.0
        cands = [x for x in VDIV_CHOICES if x >= target]
        self.vdiv = cands[0] if cands else VDIV_CHOICES[-1]
        self.vpos = (hi + lo) / 2.0
        self.cmb_vdiv.blockSignals(True)
        self.cmb_vdiv.setCurrentText(self._fmt_v(self.vdiv))
        self.cmb_vdiv.blockSignals(False)
        self.spn_vpos.blockSignals(True)
        self.spn_vpos.setValue(self.vpos)
        self.spn_vpos.blockSignals(False)
        self._apply_scaling()

    # ---------- data path ----------
    def _process(self, data):
        """Absolute volts in -> displayed volts out (coupling + optional filters)."""
        if self._mvc_view_on():
            out = np.empty_like(data, dtype=float)
            for c in range(self.nch):
                bp = self.filters.bandpass(data[:, c:c + 1])[:, 0]
                bp = bp - bp.mean()
                sig = self.filters.rms_envelope(bp.reshape(-1, 1))[:, 0] if self.do_envelope else bp
                out[:, c] = sig / self.mvc[c] * 100.0   # % MVC (envelope if RMS env on, else raw EMG)
            return out
        if self.coupling == "GND":
            return np.zeros_like(data)
        out = data
        if self.coupling == "AC":
            out = out - out.mean(axis=0)            # block DC, center on 0
        if self.do_notch:
            out = self.filters.apply_notch(out, self.do_notch)
        if self.do_envelope and not self.show_raw:      # Show Raw overrides the envelope
            base = out if self.coupling == "AC" else out - out.mean(axis=0)
            out = self.filters.rms_envelope(base)
        return out

    def _update(self):
        new = self.model.read_new()
        if new.shape[0] == 0:
            self._update_status()
            return

        if self.recording.active:
            base_t = self.total_samples / self.fs
            self.recording.write_samples(new, base_t)
        self.total_samples += new.shape[0]

        # ABSOLUTE volts (0..vref), scaled by probe
        volts = new.astype(float) / self.full * self.vref * self.probe
        if self._mvc_dialog is not None:
            self._mvc_dialog.feed(volts)
        n = new.shape[0]
        if n >= self.buf_n:
            self.ring[:] = volts[-self.buf_n:]
            self.filled = self.buf_n
        else:
            self.ring[:-n] = self.ring[n:]
            self.ring[-n:] = volts
            self.filled = min(self.buf_n, self.filled + n)

        if not self.paused:
            if self.mode == "sweep":
                self._sweep_update(n)
            else:
                self._scroll_redraw()
        self._update_status()

    def _scroll_redraw(self):
        show_n = min(self.screen_n, self.filled)
        if show_n < 2:
            return
        raw = self.ring[-show_n:]                              # newest data lives at the tail
        proc = self._process(raw)
        self._proc_cache = proc
        t = np.arange(show_n) / self.fs
        for c in range(self.nch):
            self.curves[c].setData(t, proc[:, c])
            self._onset_overlay(c, t, proc[:, c])

    def _sweep_update(self, n_new):
        screen_n = self.screen_n
        if self.sweep_y is None or self.sweep_y.shape[0] != screen_n:
            self.sweep_y = np.full((screen_n, self.nch), np.nan)
            self.sweep_pos = 0
        need = min(self.filled, screen_n)
        proc = self._process(self.ring[-need:])           # newest data lives at the tail
        self._proc_cache = proc
        n_new = min(n_new, screen_n)
        newvals = proc[-n_new:]                     # the newest processed samples
        pos = self.sweep_pos
        for i in range(n_new):                      # paint new data behind the write head
            self.sweep_y[pos] = newvals[i]
            pos = (pos + 1) % screen_n
        gap = max(2, int(0.015 * screen_n))         # blank "erase bar" just ahead
        for g in range(gap):
            self.sweep_y[(pos + g) % screen_n] = np.nan
        self.sweep_pos = pos

        t = np.arange(screen_n) / self.fs
        for c in range(self.nch):
            self.curves[c].setData(t, self.sweep_y[:, c], connect="finite")
            self._onset_overlay(c, t, self.sweep_y[:, c])
        cx = self.sweep_pos / self.fs
        for cur in self.cursors:
            cur.setValue(cx)

    def _update_status(self):
        now = time.perf_counter()
        if now - self._last_stat_t >= 0.5:
            dn = self.total_samples - self._last_stat_n
            rate = dn / (now - self._last_stat_t)
            self._last_stat_t = now
            self._last_stat_n = self.total_samples
            drp = getattr(self.source, "dropped", 0)
            rec = f" | REC {self.recording.count}" if self.recording.active else ""
            self.lbl_stat.setText(
                f"{rate:5.0f} S/s | {self.mode} | {self.coupling}"
                f" | {self._fmt_v(self.vdiv)}/div | {self.tdiv*1000:.0f} ms/div"
                f" | drop {drp}{rec}")

            # per-channel live readouts (RMS + pk-pk) and optional auto V/lane (MR4 style)
            proc = self._proc_cache
            if proc is not None and proc.shape[0] > 2:
                need = min(self.filled, self.screen_n)
                rawwin = self.ring[-need:] if need >= 64 else None   # raw un-notched volts
                mains_hz = self.do_notch if self.do_notch in (50, 60) else 50
                self._leadoff.mains_hz = mains_hz
                for c in range(self.nch):
                    x = proc[:, c]
                    ac = x - x.mean()
                    rms = float(np.sqrt(np.mean(ac * ac)))
                    pk = float(np.ptp(x))
                    mf = self._median_freq(ac)
                    mnf = mean_frequency(ac, self.fs)
                    self._mdf_hist[c].append((self.total_samples / self.fs, mf))
                    env_c = self.filters.rms_envelope(ac.reshape(-1, 1))[:, 0]
                    cur = float(env_c[-max(1, int(0.25 * self.fs)):].mean())  # current RMS-env level
                    self.plots[c].setTitle(
                        f"{self.muscle_names[c]}   RMS {self._fmt_amp(rms)}"
                        f"   pk-pk {self._fmt_amp(pk)}   medF {mf:.0f}  mnF {mnf:.0f} Hz",
                        color=CH_COLORS[c % len(CH_COLORS)], size="8pt")
                    if c < len(self.ch_cards):
                        card = self.ch_cards[c]
                        if self.mvc[c]:
                            pct = 100.0 * cur / self.mvc[c]
                            card["rms"].setText(f"{pct:.0f}% MVC")
                            card["sub"].setText(
                                f"RMS {self._fmt_amp(rms)}    medF {mf:.0f} Hz")
                            card["bar"].setValue(int(min(100, pct)))
                        else:
                            card["rms"].setText(f"RMS  {self._fmt_amp(rms)}")
                            card["sub"].setText(
                                f"pk-pk {self._fmt_amp(pk)}    medF {mf:.0f} Hz")
                            self._act_max[c] = max(self._act_max[c] * 0.999, rms, 1e-4)
                            card["bar"].setValue(int(min(100, 100 * rms / self._act_max[c])))
                        if rawwin is not None:
                            st, q = self._leadoff.update(c, rawwin[:, c])
                            self.channel_panel.set_status(c, st, q)
                    if self.autoscale and not self.show_mvc:
                        lo, hi = float(x.min()), float(x.max())
                        span = max(hi - lo, 1e-4)
                        step = self._nice_step(span / (NVDIV - 2))
                        ylo2 = math.floor((lo - 0.15 * span) / step) * step
                        yhi2 = math.ceil((hi + 0.15 * span) / step) * step
                        self.plots[c].setYRange(ylo2, yhi2, padding=0)
                        self.plots[c].getAxis("left").setTicks(
                            [self._make_ticks(ylo2, yhi2, step)])

                if self.nch >= 2:
                    env0 = self.filters.rms_envelope(proc[:, 0:1])[:, 0]
                    env1 = self.filters.rms_envelope(proc[:, 1:2])[:, 0]
                    cci = cocontraction_index(env0, env1)
                    self.lbl_stat.setText(self.lbl_stat.text() + f" | CCI(1,2) {cci:.0f}%")

                if len(self._mdf_hist[0]) >= 4:
                    ts_, mdfs_ = zip(*self._mdf_hist[0])
                    _, fpct = fatigue_trend(mdfs_, ts_)
                    self.lbl_stat.setText(self.lbl_stat.text() + f" | fat(1) {fpct:+.0f}%")

                if self.show_spectrum and proc.shape[0] >= 64:
                    n = proc.shape[0]
                    f = np.fft.rfftfreq(n, 1.0 / self.fs)
                    w = np.hanning(n)
                    for c in range(self.nch):
                        ac = proc[:, c] - proc[:, c].mean()
                        self.spec_curves[c].setData(f, np.abs(np.fft.rfft(ac * w)))

            busy = self._kick_proc is not None and self._kick_proc.poll() is None
            if self.kick_cli and rate == 0 and not busy and (now - self._last_kick) > 4.0:
                self._last_kick = now
                try:
                    import subprocess
                    self._kick_proc = subprocess.Popen(
                        [self.kick_cli, "-c", "port=SWD", "mode=UR", "-rst", "-run"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass

    def _on_record(self, checked):
        if checked:
            self.recording.start(
                subject=self.ed_subject.text(),
                trial=self.ed_trial.text(),
                notes=self.ed_notes.text(),
                muscles=self.muscle_names,
            )
            self.btn_rec.setText("■ Stop")
        else:
            self.recording.stop()
            self.btn_rec.setText("● Record")
            self._flash_banner("ok", "Recording saved ✓ — open 📄 Report, or press ● Record for another.")
        self._update_rec_hint()

    def closeEvent(self, ev):
        self.controller.stop()
        if self.recording.active:
            self.recording.stop()
        super().closeEvent(ev)


def main():
    # Create QApplication FIRST, before any Qt objects or widgets
    app = QtWidgets.QApplication(sys.argv)
    pg.setConfigOptions(antialias=False, background="k", foreground="w")

    ap = argparse.ArgumentParser(description="Real-time EMG oscilloscope for STM32 sensor")
    ap.add_argument("--port", help="serial port, e.g. COM8")
    ap.add_argument("--baud", type=int, default=115200,
                    help="must match firmware USART baud (ASCII bring-up = 115200)")
    ap.add_argument("--channels", type=int, default=1)
    ap.add_argument("--fs", type=float, default=2000.0, help="sample rate per channel")
    ap.add_argument("--vref", type=float, default=3.3, help="ADC reference volts")
    ap.add_argument("--bits", type=int, default=12, help="ADC resolution bits")
    ap.add_argument("--coupling", choices=["DC", "AC", "GND"], default="DC",
                    help="initial coupling (DC=absolute volts, AC=centered on 0)")
    ap.add_argument("--ascii", action="store_true", help="parse csv lines instead of binary")
    ap.add_argument("--sim", action="store_true", help="synthetic EMG, no hardware")
    ap.add_argument("--kick", action="store_true",
                    help="revive the board via ST-LINK before opening the port + if it halts")
    ap.add_argument("--no-bandpass", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--window", type=float, default=None, help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.sim:
        source = SimSource(args.channels, args.fs, args.bits)
    elif args.port:
        if args.ascii:
            source = AsciiSource(args.port, args.baud, args.channels)
        else:
            source = SerialSource(args.port, args.baud, args.channels)
    else:
        ap.error("give --port COMx (or --sim to try without hardware)")

    # Kick the firmware BEFORE the source opens the port (board must be running).
    if args.kick and not args.sim:
        import subprocess
        try:
            subprocess.run([PROG_CLI, "-c", "port=SWD", "mode=UR", "-rst", "-run"],
                           capture_output=True, text=True, timeout=20)
        except Exception as e:
            print("[main] pre-kick failed:", e, file=sys.stderr, flush=True)
        time.sleep(0.5)

    win = EmgScope(source, args.channels, args.fs, args.vref, args.bits,
                   args.ascii, coupling=args.coupling)
    if args.kick:
        win.kick_cli = PROG_CLI
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
