"""ReviewWindow — offline View/Review of a saved EMG recording (Noraxon MR 'View' mode
adapted to our single window): the whole recording is drawn statically, a playback cursor
scrubs through it, view/processing Operations recolor the trace, and Report writes an HTML.

The offline amplitude-normalization pipeline (normalize to peak / mean / MVC over a picked
window) plugs into the Operations bar in the following tasks; this is the review shell.
"""
import os
import time

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

from dsp.dsp import EmgFilters, leadoff_report, mean_frequency, iemg

CH_COLORS = ["#00e0ff", "#7CFC00", "#ff5050", "#ffb000", "#c080ff",
             "#ff80c0", "#80ffd0", "#ffd000"]
UNIVERSITY = "Beihang University"


def median_freq(ac, fs, band=(20.0, 450.0)):
    n = len(ac)
    if n < 8:
        return 0.0
    P = np.abs(np.fft.rfft((ac - ac.mean()) * np.hanning(n))) ** 2
    f = np.fft.rfftfreq(n, 1.0 / fs)
    m = (f >= band[0]) & (f <= min(band[1], 0.5 * fs))
    P, f = P[m], f[m]
    c = np.cumsum(P)
    return float(f[np.searchsorted(c, c[-1] / 2)]) if c.size and c[-1] > 0 else 0.0


class ReviewWindow(QtWidgets.QDialog):
    VIEWS = ["Raw", "Rectified", "RMS envelope", "% MVC"]
    SPEEDS = ["0.5x", "1x", "2x", "4x"]

    def __init__(self, path, fs, nch, vref, full, muscle_names, mvc=None, parent=None):
        super().__init__(parent)
        self.path = path
        self.fs = float(fs)
        self.vref = vref
        self.full = full
        self.meta = {}
        self.markers = []
        self._load(path)                       # -> self.codes (N,nch), self.t, meta, markers, fs
        self.nch = self.codes.shape[1]
        self.mvc = (list(mvc) if mvc else [None] * self.nch)[:self.nch]
        if not any(v for v in self.mvc):        # no live MVC -> fall back to the saved MVC stack
            self._load_mvc_from_stack()
        names = list(muscle_names) if muscle_names else []
        self.muscle_names = [names[c] if c < len(names) else f"Ch{c+1}" for c in range(self.nch)]
        self.filters = EmgFilters(self.fs)
        self.do_notch = 0
        self.pipeline = []              # ordered op keys (Signal Processing pipeline)
        self.proc_channels = "all"      # 'all' or a channel index
        self._norm_refs = None          # per-channel normalization reference (V)
        self._norm_mode = None
        self._peak_idx = None           # per-channel envelope-peak sample (green window)
        self._norm_window = None        # (i0,i1) window used for the reference, or None
        self.amp_range = 120            # % axis top after normalization
        self.cursor_i = 0
        self.playing = False
        self._disp = None
        self._units = []
        self._unit = "mV"
        self._build_ui()
        self._recompute()
        self._redraw()

    # --------------------------------------------------------------- load
    def _load(self, path):
        rows = []
        with open(path, encoding="utf-8") as f:
            for ln in f:
                s = ln.strip()
                if s.startswith("# MARKER"):
                    try:
                        body = s[len("# MARKER"):].strip()
                        label, tv = body.rsplit("t=", 1)
                        self.markers.append((float(tv), label.strip()))
                    except ValueError:
                        pass
                elif s.startswith("#") and ":" in s:
                    k, v = s[1:].split(":", 1)
                    self.meta[k.strip()] = v.strip()
                elif s.startswith("t_s") or not s or s.startswith("#"):
                    continue
                else:
                    rows.append([float(x) for x in s.split(",")])
        data = np.array(rows) if rows else np.zeros((2, 2))
        self.t = data[:, 0]
        self.codes = data[:, 1:] if data.shape[1] > 1 else np.zeros((data.shape[0], 1))
        if self.t.shape[0] > 1:
            dt = float(np.median(np.diff(self.t)))
            if dt > 0:
                self.fs = 1.0 / dt

    # --------------------------------------------------------------- UI
    def _build_ui(self):
        self.setWindowTitle(f"Review — {os.path.basename(self.path)}")
        self.resize(1000, 640)
        v = QtWidgets.QVBoxLayout(self)
        v.setSpacing(6)

        dur = self.codes.shape[0] / self.fs
        info = QtWidgets.QLabel(
            f"{self.meta.get('Subject', '') or '—'}  ·  {self.meta.get('Trial', '') or '—'}  "
            f"·  {dur:.1f} s  ·  {self.fs:.0f} S/s  ·  {self.nch} ch")
        info.setStyleSheet("color:#bcd0ee; font-weight:bold;")
        v.addWidget(info)

        ops = QtWidgets.QHBoxLayout()
        ops.addWidget(QtWidgets.QLabel("Operation"))
        self.cmb_view = QtWidgets.QComboBox()
        self.cmb_view.addItems(self.VIEWS + ["Custom"])
        self.cmb_view.currentTextChanged.connect(self._on_view)
        ops.addWidget(self.cmb_view)
        self.btn_proc = QtWidgets.QPushButton("⚙ Signal Processing")
        self.btn_proc.setToolTip("Build a custom offline processing pipeline (Available -> Selected)")
        self.btn_proc.clicked.connect(self._open_processing)
        ops.addWidget(self.btn_proc)
        self.btn_pick = QtWidgets.QPushButton("▭ Pick Window")
        self.btn_pick.setCheckable(True)
        self.btn_pick.setToolTip("Drag a window to restrict Peak/Mean normalization to it")
        self.btn_pick.toggled.connect(self._toggle_pick)
        ops.addWidget(self.btn_pick)
        self.btn_norm = QtWidgets.QPushButton("⤢ Normalize…")
        self.btn_norm.setToolTip("Amplitude-normalize to Peak/Mean/MVC/Manual/Other (= 100 %)")
        self.btn_norm.clicked.connect(self._open_normalize)
        ops.addWidget(self.btn_norm)
        ops.addWidget(QtWidgets.QLabel("Notch"))
        self.cmb_notch = QtWidgets.QComboBox()
        self.cmb_notch.addItems(["off", "50 Hz", "60 Hz"])
        self.cmb_notch.currentTextChanged.connect(self._on_notch)
        ops.addWidget(self.cmb_notch)
        ops.addStretch(1)
        self.btn_play = QtWidgets.QPushButton("▶ Play")
        self.btn_play.setCheckable(True)
        self.btn_play.toggled.connect(self._on_play)
        ops.addWidget(self.btn_play)
        ops.addWidget(QtWidgets.QLabel("Speed"))
        self.cmb_speed = QtWidgets.QComboBox()
        self.cmb_speed.addItems(self.SPEEDS)
        self.cmb_speed.setCurrentText("1x")
        ops.addWidget(self.cmb_speed)
        self.btn_report = QtWidgets.QPushButton("📄 Report")
        self.btn_report.clicked.connect(self._report)
        ops.addWidget(self.btn_report)
        v.addLayout(ops)

        self.glw = pg.GraphicsLayoutWidget()
        self.glw.setBackground("#0b0f16")
        v.addWidget(self.glw, 1)
        self.plots, self.curves, self.cursors = [], [], []
        self.pick_regions, self.peak_regions, self.ref_lines = [], [], []
        for c in range(self.nch):
            p = self.glw.addPlot(row=c, col=0)
            p.showGrid(x=True, y=True, alpha=0.3)
            p.setMouseEnabled(x=True, y=False)
            p.setMenuEnabled(False)
            col = CH_COLORS[c % len(CH_COLORS)]
            p.setLabel("left", self.muscle_names[c], units=self._unit)
            # green 'peak window' (reference), behind the trace; added first = drawn under
            gr = pg.LinearRegionItem(brush=(60, 220, 120, 55), movable=False)
            gr.setVisible(False)
            p.addItem(gr)
            self.peak_regions.append(gr)
            self.curves.append(p.plot(pen=pg.mkPen(col, width=1.2)))
            # yellow movable selection window (Pick)
            pr = pg.LinearRegionItem(brush=(255, 210, 0, 45), movable=True)
            pr.setVisible(False)
            pr.sigRegionChanged.connect(lambda _r, ci=c: self._sync_pick(ci))
            p.addItem(pr)
            self.pick_regions.append(pr)
            rl = pg.InfiniteLine(angle=0, movable=False, pos=100.0,
                                 pen=pg.mkPen("#39d353", width=1, style=QtCore.Qt.DashLine))
            rl.setVisible(False)
            p.addItem(rl)
            self.ref_lines.append(rl)
            cur = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen("#ffd000", width=1.5))
            cur.sigPositionChanged.connect(self._on_cursor_drag)
            p.addItem(cur)
            for mt, _lbl in self.markers:
                p.addItem(pg.InfiniteLine(pos=mt, angle=90, pen=pg.mkPen("#888888", width=1,
                                          style=QtCore.Qt.DashLine)))
            if c > 0:
                p.setXLink(self.plots[0])
            self.plots.append(p)
            self.cursors.append(cur)
        self.plots[-1].setLabel("bottom", "time", units="s")

        row = QtWidgets.QHBoxLayout()
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, max(1, self.codes.shape[0] - 1))
        self.slider.valueChanged.connect(self._on_slider)
        row.addWidget(self.slider, 1)
        self.lbl_read = QtWidgets.QLabel("")
        self.lbl_read.setStyleSheet("color:#e6eefc; font-family:Consolas,monospace;")
        row.addWidget(self.lbl_read)
        v.addLayout(row)

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._tick)

    # --------------------------------------------------------------- processing
    def _recompute(self):
        """Run the Signal-Processing pipeline per channel; build display array + per-channel units.
        Channels outside the pipeline's scope stay raw (mV); each plot carries its own unit."""
        from dsp.pipeline import apply_pipeline, pipeline_unit
        n = self.codes.shape[0]
        out = np.zeros((n, self.nch), dtype=float)
        units = []
        for c in range(self.nch):
            v = self.codes[:, c] / self.full * self.vref
            ac = v - v.mean()
            if self.do_notch:
                ac = self.filters.apply_notch(ac.reshape(-1, 1), self.do_notch)[:, 0]
            apply_here = self.pipeline and (self.proc_channels == "all" or self.proc_channels == c)
            if apply_here:
                ctx = {"fs": self.fs, "filters": self.filters, "mvc": self.mvc[c],
                       "smooth_ms": getattr(self, "smooth_ms", 100.0),
                       "norm_ref": (self._norm_refs[c] if self._norm_refs else None)}
                sig = apply_pipeline(ac, self.pipeline, ctx)
                unit = pipeline_unit(self.pipeline)
                out[:, c] = sig if unit == "%" else sig * 1e3
                units.append(unit)
            else:
                out[:, c] = ac * 1e3
                units.append("mV")
        self._disp = out
        self._units = units
        self._unit = units[0] if units else "mV"

    def _redraw(self):
        t = self.t if self.t.shape[0] == self._disp.shape[0] else np.arange(self._disp.shape[0]) / self.fs
        self._tvec = t
        normalizing = "normalize" in self.pipeline
        for c in range(self.nch):
            self.curves[c].setData(t, self._disp[:, c])
            self.plots[c].setLabel("left", self.muscle_names[c], units=self._units[c])
            if self._units[c] == "%":
                self.plots[c].setYRange(0, self.amp_range, padding=0)
            else:
                self.plots[c].enableAutoRange(axis="y")
            if not normalizing:
                self.peak_regions[c].setVisible(False)
                self.ref_lines[c].setVisible(False)
        self._update_cursor()

    # --------------------------------------------------------------- cursor / playback
    def _update_cursor(self):
        i = int(np.clip(self.cursor_i, 0, self._disp.shape[0] - 1))
        tc = float(self._tvec[i])
        for cur in self.cursors:
            cur.blockSignals(True)
            cur.setValue(tc)
            cur.blockSignals(False)
        self.slider.blockSignals(True)
        self.slider.setValue(i)
        self.slider.blockSignals(False)
        vals = "  ".join(f"{self.muscle_names[c]} {self._disp[i, c]:.1f}{self._units[c]}"
                         for c in range(self.nch))
        total = self._disp.shape[0] / self.fs
        self.lbl_read.setText(f"t={tc:6.2f}/{total:5.1f}s   {vals}")

    def _on_slider(self, val):
        self.cursor_i = int(val)
        self._update_cursor()

    def _on_cursor_drag(self, line):
        self.cursor_i = int(np.clip(line.value() * self.fs, 0, self._disp.shape[0] - 1))
        self._update_cursor()

    def _on_play(self, checked):
        self.playing = checked
        self.btn_play.setText("⏸ Pause" if checked else "▶ Play")
        if checked:
            if self.cursor_i >= self._disp.shape[0] - 1:
                self.cursor_i = 0
            self._timer.start(33)
        else:
            self._timer.stop()

    def _tick(self):
        speed = float(self.cmb_speed.currentText().rstrip("x"))
        self.cursor_i += int(speed * self.fs * 0.033)
        if self.cursor_i >= self._disp.shape[0] - 1:
            self.cursor_i = self._disp.shape[0] - 1
            self.btn_play.setChecked(False)
        self._update_cursor()

    def _on_view(self, t):
        from dsp.pipeline import PRESETS
        if t in PRESETS:                        # a quick preset defines a whole pipeline
            self.pipeline = list(PRESETS[t])
            self.proc_channels = "all"
            self._recompute()
            self._redraw()
        # 'Custom' is set by the Signal Processing dialog; ignore its combo echo

    def _open_processing(self):
        """Open the Signal Processing pipeline builder; apply the result to the review."""
        from gui.processing_dialog import ProcessingDialog
        dlg = ProcessingDialog(self.pipeline, self.nch, self.muscle_names,
                               self.proc_channels, parent=self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.pipeline = dlg.selected_keys()
            self.proc_channels = dlg.channels()
            self._norm_refs = None                  # a manual pipeline clears any normalize ref
            self.cmb_view.blockSignals(True)
            self.cmb_view.setCurrentText("Custom")
            self.cmb_view.blockSignals(False)
            self._recompute()
            self._redraw()

    # ---------------------------------------------------------------- normalization (Img13-15)
    def _toggle_pick(self, on):
        if on:
            n = self._disp.shape[0]
            lo = float(self._tvec[int(n * 0.35)])
            hi = float(self._tvec[int(n * 0.60)])
            for r in self.pick_regions:
                r.blockSignals(True)
                r.setRegion([lo, hi])
                r.setVisible(True)
                r.blockSignals(False)
        else:
            for r in self.pick_regions:
                r.setVisible(False)

    def _sync_pick(self, ci):
        lo, hi = self.pick_regions[ci].getRegion()
        for c, r in enumerate(self.pick_regions):
            if c != ci:
                r.blockSignals(True)
                r.setRegion([lo, hi])
                r.blockSignals(False)

    def _picked_window(self):
        if not getattr(self, "btn_pick", None) or not self.btn_pick.isChecked():
            return None
        lo, hi = self.pick_regions[0].getRegion()
        n = self._disp.shape[0]
        i0 = int(np.clip(np.searchsorted(self._tvec, lo), 0, n))
        i1 = int(np.clip(np.searchsorted(self._tvec, hi), 0, n))
        return (min(i0, i1), max(i0, i1)) if i1 > i0 else None

    def _channel_env(self, c):
        v = self.codes[:, c] / self.full * self.vref
        ac = v - v.mean()
        if self.do_notch:
            ac = self.filters.apply_notch(ac.reshape(-1, 1), self.do_notch)[:, 0]
        bp = self.filters.bandpass(ac.reshape(-1, 1))[:, 0]
        return self.filters.rms_envelope((bp - bp.mean()).reshape(-1, 1))[:, 0]

    def _load_mvc_from_stack(self):
        """Populate self.mvc from the latest mvc_store.json entry (the persisted 'MVC stack'),
        so offline MVC-normalization works even when the scope was restarted (no live MVC)."""
        import json
        path = os.path.abspath("mvc_store.json")
        if not os.path.exists(path):
            return
        try:
            with open(path, encoding="utf-8") as f:
                store = json.load(f)
        except Exception:
            return
        if not store:
            return
        chans = store[-1].get("channels", [])
        for c in range(min(self.nch, len(chans))):
            v = chans[c].get("mvc_v")
            if v:
                self.mvc[c] = float(v)

    def _load_other_env(self, path):
        rows = []
        try:
            with open(path, encoding="utf-8") as f:
                for ln in f:
                    s = ln.strip()
                    if not s or s.startswith("#") or s.startswith("t_s"):
                        continue
                    rows.append([float(x) for x in s.split(",")])
        except OSError:
            return None
        if not rows:
            return None
        codes = np.array(rows)[:, 1:]
        envs = []
        for c in range(codes.shape[1]):
            v = codes[:, c] / self.full * self.vref
            ac = v - v.mean()
            bp = self.filters.bandpass(ac.reshape(-1, 1))[:, 0]
            envs.append(self.filters.rms_envelope((bp - bp.mean()).reshape(-1, 1))[:, 0])
        return envs

    def _open_normalize(self):
        from gui.normalize_dialog import NormalizeDialog
        dlg = NormalizeDialog(self._picked_window() is not None, any(self.mvc), parent=self)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return
        self._apply_normalize(dlg.mode(), dlg.manual_mv(), dlg.use_window(),
                              dlg.other_path(), dlg.amp_range())

    def _apply_normalize(self, mode, manual_mv, use_window, other_path, amp_range):
        """Compute a per-channel reference (=100 %) from the chosen source/window, then run
        [band-pass -> RMS -> normalize] and show the % result (green peak window + ref line)."""
        from dsp.pipeline import compute_reference, peak_index
        self.amp_range = int(amp_range)
        window = self._picked_window() if use_window else None
        self._norm_window = window
        other = self._load_other_env(other_path) if (mode == "other" and other_path) else None
        manual_v = (manual_mv / 1e3) if (manual_mv and manual_mv > 0) else None
        refs, peaks = [], []
        for c in range(self.nch):
            env = self._channel_env(c)
            if mode == "other" and other is not None and c < len(other):
                ref = float(np.max(other[c])) + 1e-12
            else:
                ref = compute_reference(env, mode, mvc=self.mvc[c], manual=manual_v, window=window)
            refs.append(ref)
            peaks.append(peak_index(env, window))
        self._norm_refs = refs
        self._norm_mode = mode
        self._peak_idx = peaks
        self.pipeline = ["bandpass", "rms", "normalize"]
        self.proc_channels = "all"
        self.cmb_view.blockSignals(True)
        self.cmb_view.setCurrentText("Custom")
        self.cmb_view.blockSignals(False)
        self._recompute()
        self._redraw()
        self._show_norm_result(window)

    def _show_norm_result(self, window):
        """Img15: % axis at the chosen range, a 100 % reference line, and the green 'peak
        window' — the picked window, else a band around each channel's envelope peak."""
        for c in range(self.nch):
            self.plots[c].setYRange(0, self.amp_range, padding=0)
            if window:
                i0, i1 = window
            else:
                pk = self._peak_idx[c]
                half = max(1, int(0.1 * self.fs))
                i0, i1 = max(0, pk - half), min(len(self._tvec) - 1, pk + half)
            t0 = float(self._tvec[int(np.clip(i0, 0, len(self._tvec) - 1))])
            t1 = float(self._tvec[int(np.clip(i1, 0, len(self._tvec) - 1))])
            self.peak_regions[c].setRegion([t0, t1])
            self.peak_regions[c].setVisible(True)
            self.ref_lines[c].setValue(100.0)
            self.ref_lines[c].setVisible(True)
        mode_lbl = {"peak": "Peak", "mean": "Mean", "mvc": "MVC",
                    "manual": "Manual", "other": "Other record"}.get(self._norm_mode, self._norm_mode)
        win = " over picked window" if window else ""
        self.lbl_read.setText(f"Normalized to {mode_lbl}{win} — 100% ref line, 0-{self.amp_range}% axis")

    def _on_notch(self, t):
        self.do_notch = 0 if t.startswith("off") else int(t.split()[0])
        self._recompute()
        self._redraw()

    # --------------------------------------------------------------- report
    def _report(self):
        ts = time.strftime("%Y%m%d_%H%M%S")
        png = os.path.abspath(f"review_{ts}.png")
        try:
            self.grab().save(png)
        except Exception:
            png = ""
        rows = ""
        for c in range(self.nch):
            v = self.codes[:, c] / self.full * self.vref
            ac = v - v.mean()
            rms = float(np.sqrt(np.mean(ac * ac))) * 1e3
            pk = float(np.ptp(v)) * 1e3
            mf = median_freq(ac, self.fs)
            mnf = mean_frequency(ac, self.fs)
            ie = iemg(ac, self.fs) * 1e3
            st, _, _ = leadoff_report(v, self.fs, self.vref)
            pct = (f"{100.0 * float(np.median(np.abs(ac))) / self.mvc[c]:.0f}%"
                   if self.mvc[c] else "&mdash;")
            col = CH_COLORS[c % len(CH_COLORS)]
            rows += (f"<tr><td style='color:{col};font-weight:700'>{self.muscle_names[c]}</td>"
                     f"<td>{rms:.1f}</td><td>{pk:.0f}</td><td>{mf:.0f}</td><td>{mnf:.0f}</td>"
                     f"<td>{ie:.1f}</td><td>{pct}</td><td>{st}</td></tr>")
        marks = "".join(f"<li>{l} @ {t:.2f}s</li>" for t, l in self.markers) or "<li>none</li>"
        dur = self.codes.shape[0] / self.fs
        img = f"<h3>Snapshot</h3><img src='{os.path.basename(png)}'>" if png else ""
        html = f"""<!doctype html><html><head><meta charset='utf-8'><title>EMG Review {ts}</title>
<style>body{{font-family:'Segoe UI',Arial;margin:32px;color:#111}}
h1{{color:#123a7a}} table{{border-collapse:collapse;margin:10px 0}}
td,th{{border:1px solid #ccc;padding:6px 16px;text-align:left}} th{{background:#eef3fb}}
.meta td{{border:none;padding:2px 14px 2px 0}} img{{max-width:100%;border:1px solid #ccc;margin-top:10px}}</style>
</head><body>
<h1>{UNIVERSITY} &mdash; EMG Review</h1>
<table class='meta'>
<tr><td><b>File</b></td><td>{os.path.basename(self.path)}</td></tr>
<tr><td><b>Subject</b></td><td>{self.meta.get('Subject', '') or '&mdash;'}</td></tr>
<tr><td><b>Trial</b></td><td>{self.meta.get('Trial', '') or '&mdash;'}</td></tr>
<tr><td><b>Duration</b></td><td>{dur:.1f} s @ {self.fs:.0f} S/s</td></tr>
</table>
<h3>Per-channel summary (whole recording)</h3>
<table><tr><th>Muscle</th><th>RMS mV</th><th>pk-pk mV</th><th>Med Hz</th><th>Mean Hz</th>
<th>iEMG mV&middot;s</th><th>% MVC</th><th>Lead-off</th></tr>{rows}</table>
<h3>Event markers</h3><ul>{marks}</ul>
{img}
</body></html>"""
        fn = os.path.abspath(f"review_report_{ts}.html")
        with open(fn, "w", encoding="utf-8") as f:
            f.write(html)
        try:
            os.startfile(fn)
        except Exception:
            pass
        return fn

    def closeEvent(self, ev):
        self._timer.stop()
        super().closeEvent(ev)
