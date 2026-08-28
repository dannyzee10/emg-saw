import sys
import subprocess
from pathlib import Path
from PyQt5 import QtWidgets

ROOT = Path(__file__).resolve().parent
EXE_DIR = ROOT / "dist" / "EMG Acquisition"   # adjust if different

APP_BUTTONS = [
    ("EMG 1ch Sim", "EMG Acquisition.exe", "--sim --channels 1"),
    ("EMG 5ch Sim", "EMG Acquisition.exe", "--sim --channels 5"),
    ("EMG 1ch Real", "EMG Acquisition.exe", "--port COM8 --baud 921600 --channels 1 --fs 2000 --coupling DC"),
    ("EMG 5ch Real", "EMG Acquisition.exe", "--port COM8 --baud 921600 --channels 5 --fs 2000 --coupling AC"),
]

class Launcher(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EMG Acquisition Launcher")
        layout = QtWidgets.QVBoxLayout(self)
        for label, exe, args in APP_BUTTONS:
            btn = QtWidgets.QPushButton(label)
            btn.clicked.connect(lambda checked, e=exe, a=args: self.launch(e, a))
            layout.addWidget(btn)

    def launch(self, exe, args):
        path = EXE_DIR / exe
        if not path.exists():
            QtWidgets.QMessageBox.warning(self, "Missing", str(path))
            return
        cmd = f'"{path}" {args}'
        subprocess.Popen(cmd, shell=True)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Launcher()
    win.show()
    sys.exit(app.exec_())