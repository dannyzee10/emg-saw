"""AmpNormDialog — Noraxon MR real-time Amplitude Normalization + Smoothing config:
the envelope Smoothing (Algorithm = RMS / Mean-absolute, Window ms) that feeds the live
RMS-env and % MVC views, plus the display Amplitude range (% axis top).
"""
from pyqtgraph.Qt import QtWidgets

ALGOS = [("RMS", "rms"), ("Mean-absolute", "mean")]
WINDOWS = ["25 ms", "50 ms", "100 ms", "150 ms", "250 ms", "500 ms"]
AMPS = ["100%", "120%", "150%", "200%"]


class AmpNormDialog(QtWidgets.QDialog):
    def __init__(self, algo="rms", window_ms=100.0, amp=120, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Amplitude Normalization / Smoothing")
        self.resize(420, 220)
        v = QtWidgets.QVBoxLayout(self)
        v.setSpacing(8)

        head = QtWidgets.QLabel("Envelope smoothing for the live RMS-env and % MVC views, "
                                "and the % display range (Amplitude).")
        head.setWordWrap(True)
        head.setStyleSheet("color:#bcd0ee;")
        v.addWidget(head)

        form = QtWidgets.QFormLayout()
        self.cmb_algo = QtWidgets.QComboBox()
        for label, key in ALGOS:
            self.cmb_algo.addItem(label, key)
        i = self.cmb_algo.findData(algo)
        self.cmb_algo.setCurrentIndex(max(0, i))
        form.addRow("Smoothing algorithm", self.cmb_algo)

        self.cmb_win = QtWidgets.QComboBox()
        self.cmb_win.addItems(WINDOWS)
        self.cmb_win.setCurrentText(f"{int(window_ms)} ms")
        form.addRow("Smoothing window", self.cmb_win)

        self.cmb_amp = QtWidgets.QComboBox()
        self.cmb_amp.addItems(AMPS)
        self.cmb_amp.setCurrentText(f"{int(amp)}%")
        form.addRow("Amplitude (range)", self.cmb_amp)
        v.addLayout(form)
        v.addStretch(1)

        ctl = QtWidgets.QHBoxLayout()
        ctl.addStretch(1)
        self.btn_cancel = QtWidgets.QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok = QtWidgets.QPushButton("Apply")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setDefault(True)
        ctl.addWidget(self.btn_cancel)
        ctl.addWidget(self.btn_ok)
        v.addLayout(ctl)

    def algo(self):
        return self.cmb_algo.currentData()

    def window_ms(self):
        try:
            return float(self.cmb_win.currentText().split()[0])
        except ValueError:
            return 100.0

    def amp(self):
        try:
            return int(self.cmb_amp.currentText().rstrip("%"))
        except ValueError:
            return 120
