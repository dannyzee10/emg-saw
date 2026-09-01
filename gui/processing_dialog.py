"""ProcessingDialog — Noraxon MR 'Signal Processing' menu: build an ordered pipeline by
inserting Available operations into the Selected list, reorder/remove them, choose which
channels it applies to, and Remove All to clear. Returns the ordered op keys + channel scope.
"""
from pyqtgraph.Qt import QtCore, QtWidgets

from dsp.pipeline import OPS

_KEY = QtCore.Qt.UserRole


class ProcessingDialog(QtWidgets.QDialog):
    def __init__(self, current_keys, nch, muscle_names, channels="all", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Signal Processing")
        self.resize(640, 420)
        self._nch = nch
        v = QtWidgets.QVBoxLayout(self)
        v.setSpacing(8)

        hint = QtWidgets.QLabel("Insert operations into the pipeline (applied top -> bottom). "
                                "Reorder with Up/Down; Remove All to clear.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#bcd0ee;")
        v.addWidget(hint)

        cols = QtWidgets.QHBoxLayout()

        avail_box = QtWidgets.QVBoxLayout()
        avail_box.addWidget(QtWidgets.QLabel("Available operations"))
        self.avail = QtWidgets.QListWidget()
        for key, (label, _fn, _pct) in OPS.items():
            it = QtWidgets.QListWidgetItem(label)
            it.setData(_KEY, key)
            self.avail.addItem(it)
        self.avail.itemDoubleClicked.connect(lambda _it: self._insert())
        avail_box.addWidget(self.avail, 1)
        cols.addLayout(avail_box, 1)

        mid = QtWidgets.QVBoxLayout()
        mid.addStretch(1)
        self.btn_ins = QtWidgets.QPushButton("Insert →")
        self.btn_ins.clicked.connect(self._insert)
        self.btn_rem = QtWidgets.QPushButton("← Remove")
        self.btn_rem.clicked.connect(self._remove)
        self.btn_up = QtWidgets.QPushButton("Up")
        self.btn_up.clicked.connect(lambda: self._move(-1))
        self.btn_dn = QtWidgets.QPushButton("Down")
        self.btn_dn.clicked.connect(lambda: self._move(1))
        self.btn_clr = QtWidgets.QPushButton("Remove All")
        self.btn_clr.clicked.connect(self._remove_all)
        for b in (self.btn_ins, self.btn_rem, self.btn_up, self.btn_dn, self.btn_clr):
            mid.addWidget(b)
        mid.addStretch(1)
        cols.addLayout(mid)

        sel_box = QtWidgets.QVBoxLayout()
        sel_box.addWidget(QtWidgets.QLabel("Selected pipeline"))
        self.selected = QtWidgets.QListWidget()
        self.selected.itemDoubleClicked.connect(lambda _it: self._remove())
        for k in current_keys:
            self._add_selected(k)
        sel_box.addWidget(self.selected, 1)
        cols.addLayout(sel_box, 1)

        v.addLayout(cols, 1)

        chrow = QtWidgets.QHBoxLayout()
        chrow.addWidget(QtWidgets.QLabel("Apply to"))
        self.cmb_ch = QtWidgets.QComboBox()
        self.cmb_ch.addItem("All channels", "all")
        for c in range(nch):
            name = muscle_names[c] if c < len(muscle_names) else f"Ch{c+1}"
            self.cmb_ch.addItem(name, c)
        idx = 0 if channels == "all" else self.cmb_ch.findData(channels)
        self.cmb_ch.setCurrentIndex(max(0, idx))
        chrow.addWidget(self.cmb_ch)
        chrow.addStretch(1)
        self.btn_cancel = QtWidgets.QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok = QtWidgets.QPushButton("Apply")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setDefault(True)
        chrow.addWidget(self.btn_cancel)
        chrow.addWidget(self.btn_ok)
        v.addLayout(chrow)

    # ---------------------------------------------------------------- ops
    def _add_selected(self, key):
        if key not in OPS:
            return
        it = QtWidgets.QListWidgetItem(OPS[key][0])
        it.setData(_KEY, key)
        self.selected.addItem(it)

    def _insert(self):
        it = self.avail.currentItem()
        if it is not None:
            self._add_selected(it.data(_KEY))

    def _remove(self):
        row = self.selected.currentRow()
        if row >= 0:
            self.selected.takeItem(row)

    def _remove_all(self):
        self.selected.clear()

    def _move(self, delta):
        row = self.selected.currentRow()
        new = row + delta
        if row < 0 or new < 0 or new >= self.selected.count():
            return
        it = self.selected.takeItem(row)
        self.selected.insertItem(new, it)
        self.selected.setCurrentRow(new)

    # ---------------------------------------------------------------- result
    def selected_keys(self):
        return [self.selected.item(i).data(_KEY) for i in range(self.selected.count())]

    def channels(self):
        return self.cmb_ch.currentData()
