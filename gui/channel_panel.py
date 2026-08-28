"""ChannelPanel – left sidebar with per-channel information cards and MVC controls."""

from PyQt5 import QtCore, QtWidgets

CH_COLORS = ["#00e0ff", "#7CFC00", "#ff5050", "#ffb000", "#c080ff",
             "#ff80c0", "#80ffd0", "#ffd000"]

# electrode connection status dot colors (Phase A lead-off indicator)
STATUS_COLORS = {"good": "#39d353", "poor": "#e3b341", "open": "#f85149",
                 "none": "#556677"}


class ChannelPanel(QtWidgets.QFrame):
    """Encapsulates channel cards with muscle name, RMS/pk-pk labels, progress bars,
    an electrode status dot, and MVC set/clear buttons."""

    def __init__(self, nch, muscle_names=None, parent=None):
        super().__init__(parent)
        self.nch = nch
        self.muscle_names = muscle_names or [f"Ch{c+1}" for c in range(nch)]
        self.cards = []  # list of dicts with widgets for each channel

        self.setObjectName("chpanel")
        self.setFixedWidth(228)
        self._build_ui()

    def _build_ui(self):
        col = QtWidgets.QVBoxLayout(self)
        col.setContentsMargins(8, 8, 8, 8)
        col.setSpacing(8)

        hdr = QtWidgets.QLabel("CHANNELS")
        hdr.setObjectName("panelHdr")
        col.addWidget(hdr)

        mvc_row = QtWidgets.QHBoxLayout()
        self.btn_mvc = QtWidgets.QPushButton("Set MVC")
        self.btn_mvc.setToolTip("Hold a max contraction, then click to set 100% MVC reference")
        self.btn_mvc_clr = QtWidgets.QPushButton("Clear")
        mvc_row.addWidget(self.btn_mvc)
        mvc_row.addWidget(self.btn_mvc_clr)
        col.addLayout(mvc_row)

        for c in range(self.nch):
            color = CH_COLORS[c % len(CH_COLORS)]
            card = QtWidgets.QFrame()
            card.setObjectName("chcard")
            card.setStyleSheet(f"#chcard {{ border-left:4px solid {color}; }}")
            cl = QtWidgets.QVBoxLayout(card)
            cl.setContentsMargins(8, 6, 8, 6)
            cl.setSpacing(3)

            # name row: electrode status dot + editable muscle name
            name_row = QtWidgets.QHBoxLayout()
            name_row.setContentsMargins(0, 0, 0, 0)
            name_row.setSpacing(6)
            dot = QtWidgets.QLabel()
            dot.setObjectName("statusDot")
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(f"background:{STATUS_COLORS['none']}; border-radius:5px;")
            dot.setToolTip("electrode status")
            name_edit = QtWidgets.QLineEdit(self.muscle_names[c])
            name_edit.setObjectName("muscle")
            name_edit.textChanged.connect(lambda text, i=c: self._on_muscle_edit(i, text))
            name_row.addWidget(dot)
            name_row.addWidget(name_edit, 1)
            cl.addLayout(name_row)

            rms_label = QtWidgets.QLabel("RMS  —")
            rms_label.setObjectName("rmsBig")
            rms_label.setStyleSheet(f"color:{color};")
            cl.addWidget(rms_label)

            sub_label = QtWidgets.QLabel("pk-pk —    medF —")
            sub_label.setObjectName("subStat")
            cl.addWidget(sub_label)

            bar = QtWidgets.QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedHeight(8)
            bar.setStyleSheet(f"QProgressBar::chunk {{ background:{color}; }}")
            cl.addWidget(bar)

            col.addWidget(card)
            # use keys matching the old emg_plotter.py expectations
            self.cards.append({
                "name": name_edit,
                "rms": rms_label,
                "sub": sub_label,
                "bar": bar,
                "dot": dot,
            })

        col.addStretch(1)

    def set_status(self, idx, state, quality=None):
        """Set the per-channel electrode status dot: 'good' | 'poor' | 'open'."""
        if 0 <= idx < len(self.cards):
            color = STATUS_COLORS.get(state, STATUS_COLORS["none"])
            dot = self.cards[idx]["dot"]
            dot.setStyleSheet(f"background:{color}; border-radius:5px;")
            tip = f"electrode: {state}"
            if quality is not None:
                tip += f"  ({quality:.0f}%)"
            dot.setToolTip(tip)

    def _on_muscle_edit(self, idx, text):
        if 0 <= idx < len(self.muscle_names):
            self.muscle_names[idx] = text or f"Ch{idx+1}"
