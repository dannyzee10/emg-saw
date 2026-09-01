"""NormalizeDialog — Noraxon MR offline Amplitude Normalization config: choose the reference
(=100 %) source — Peak / Mean / MVC / Manual / Other record — optionally restricted to the
picked time window, and the display Amplitude range (% axis top).
"""
from pyqtgraph.Qt import QtWidgets

MODES = [("Peak", "peak"), ("Mean", "mean"), ("MVC", "mvc"),
         ("Manual", "manual"), ("Other record", "other")]


class NormalizeDialog(QtWidgets.QDialog):
    def __init__(self, has_window, has_mvc, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Amplitude Normalization")
        self.resize(480, 320)
        self._has_mvc = has_mvc
        v = QtWidgets.QVBoxLayout(self)
        v.setSpacing(8)

        head = QtWidgets.QLabel("Normalize the RMS envelope to a reference (= 100 %). "
                                "Pick the reference source, an optional window, and the % range.")
        head.setWordWrap(True)
        head.setStyleSheet("color:#bcd0ee;")
        v.addWidget(head)

        form = QtWidgets.QFormLayout()
        self.cmb_mode = QtWidgets.QComboBox()
        for label, key in MODES:
            self.cmb_mode.addItem(label, key)
        if not has_mvc:
            i = self.cmb_mode.findData("mvc")
            self.cmb_mode.model().item(i).setEnabled(False)     # no MVC set -> greyed out
        self.cmb_mode.currentIndexChanged.connect(self._sync_enabled)
        form.addRow("Normalize to", self.cmb_mode)

        self.ed_manual = QtWidgets.QLineEdit("100")
        self.ed_manual.setToolTip("Manual reference amplitude in mV = 100 %")
        form.addRow("Manual (mV)", self.ed_manual)

        other = QtWidgets.QHBoxLayout()
        self.ed_other = QtWidgets.QLineEdit()
        self.ed_other.setPlaceholderText("another emg_*.csv — its peak = 100 %")
        self.btn_browse = QtWidgets.QPushButton("Browse…")
        self.btn_browse.clicked.connect(self._browse)
        other.addWidget(self.ed_other, 1)
        other.addWidget(self.btn_browse)
        wrap = QtWidgets.QWidget()
        wrap.setLayout(other)
        form.addRow("Other record", wrap)

        self.cmb_amp = QtWidgets.QComboBox()
        self.cmb_amp.addItems(["100%", "120%", "150%", "200%"])
        self.cmb_amp.setCurrentText("120%")
        form.addRow("Amplitude (range)", self.cmb_amp)
        v.addLayout(form)

        self.chk_window = QtWidgets.QCheckBox("Restrict Peak/Mean to the picked window")
        self.chk_window.setChecked(has_window)
        self.chk_window.setEnabled(has_window)
        if not has_window:
            self.chk_window.setToolTip("Enable '▭ Pick Window' on the review first to use this")
        v.addWidget(self.chk_window)
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

        self._sync_enabled()

    def _sync_enabled(self):
        m = self.mode()
        self.ed_manual.setEnabled(m == "manual")
        self.ed_other.setEnabled(m == "other")
        self.btn_browse.setEnabled(m == "other")

    def _browse(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Reference recording", "", "EMG CSV (emg_*.csv);;All files (*.*)")
        if path:
            self.ed_other.setText(path)

    # ---------------------------------------------------------------- result
    def mode(self):
        return self.cmb_mode.currentData()

    def manual_mv(self):
        try:
            return float(self.ed_manual.text())
        except ValueError:
            return None

    def other_path(self):
        return self.ed_other.text().strip()

    def use_window(self):
        return self.chk_window.isChecked()

    def amp_range(self):
        try:
            return int(self.cmb_amp.currentText().rstrip("%"))
        except ValueError:
            return 120
