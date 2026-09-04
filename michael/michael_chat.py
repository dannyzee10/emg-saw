"""Michael — a one-click desktop chat window for the EMG lab assistant.

Double-click (via Michael.bat, or `python michael/michael_chat.py`) to open a window and talk to
Michael. Connection settings come from the environment (MICHAEL_URL / MICHAEL_TOKEN) or from
michael/michael.conf (key=value), so it just works on a double-click. Answers come from the shared
Ollama/Qwen brain over the tunnel; it falls back to scripted answers if the server is unreachable.

While Michael is composing a reply it shows a live EMG "contraction" trace, so waiting looks alive.
"""
import math
import os
import random
import ssl
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))


def _load_config():
    """Env wins; then michael/michael.conf (KEY=value); then a localhost default."""
    url = os.environ.get("MICHAEL_URL", "")
    token = os.environ.get("MICHAEL_TOKEN", "")
    conf = HERE / "michael.conf"
    if conf.exists():
        for line in conf.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            k, v = k.strip().upper(), v.strip()
            if k == "MICHAEL_URL" and not url:
                url = v
            elif k == "MICHAEL_TOKEN" and not token:
                token = v
    os.environ["MICHAEL_URL"] = url or "http://localhost:11434"
    os.environ["MICHAEL_TOKEN"] = token


_load_config()
from michael.michael import ask                      # noqa: E402  (config must be in env first)
from PyQt5 import QtCore, QtGui, QtWidgets            # noqa: E402


def _reachable():
    url = os.environ.get("MICHAEL_URL", "").rstrip("/")
    tok = os.environ.get("MICHAEL_TOKEN", "")
    ctx = ssl._create_unverified_context() if url.startswith("https") else None
    req = urllib.request.Request(url + "/api/tags", headers={"X-Michael-Token": tok})
    try:
        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
            return r.status == 200
    except Exception:
        return False


ROOM = {
    "goto:methods/filter": "Methods room · Filter",
    "goto:methods/smoothing": "Methods room · Smoothing",
    "goto:methods/rectify": "Methods room · Rectify",
    "goto:liveviz/mvc": "Live-Visualization · MVC",
    "goto:liveviz/baseline": "Live-Visualization · EMG Baseline",
    "goto:liveviz/raw": "Live-Visualization · raw EMG",
    "goto:review/review": "Review room",
    "goto:review/normalize": "Review room · Normalize",
    "goto:sensor/placement": "Sensor-Placement room",
    "goto:hall": "Main Hall",
}


class Worker(QtCore.QThread):
    done = QtCore.pyqtSignal(dict)

    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        if self.message == "__ping__":
            self.done.emit({"source": "llm" if _reachable() else "fallback", "answer": "", "action": None})
            return
        try:
            self.done.emit(ask(self.message, timeout=120))
        except Exception as e:
            self.done.emit({"answer": f"(error: {e})", "action": None, "source": "error"})


class Wave(QtWidgets.QWidget):
    """A small scrolling EMG trace shown while Michael thinks — a relaxed baseline that bursts into
    'contractions', so the wait looks like live muscle activity."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(44)
        self.setStyleSheet("background:#0b1a12; border:1px solid #2a4030; border-radius:6px;")
        self.n = 240
        self.buf = [0.0] * self.n
        self.t = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)

    def start(self):
        self.t = 0
        self.timer.start(28)
        self.show()

    def stop(self):
        self.timer.stop()

    def _tick(self):
        self.t += 1
        phase = (self.t % 55) / 55.0                    # a contraction roughly every ~1.5 s
        env = math.exp(-((phase - 0.5) ** 2) / 0.015)   # smooth rise-and-fall (contraction envelope)
        amp = 0.06 + 0.92 * env                         # relaxed baseline -> strong burst -> relax
        s = amp * (random.random() * 2 - 1)             # EMG = random spikes under the envelope
        self.buf.append(s)
        self.buf = self.buf[-self.n:]
        self.update()

    def paintEvent(self, _):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        w, h = self.width(), self.height()
        mid = h / 2.0
        p.setPen(QtGui.QPen(QtGui.QColor("#172a1e"), 1))
        p.drawLine(0, int(mid), w, int(mid))
        p.setPen(QtGui.QPen(QtGui.QColor("#39d353"), 1.5))
        path = QtGui.QPainterPath()
        for i, s in enumerate(self.buf):
            x = i / (self.n - 1) * w
            y = mid - s * (h * 0.40)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        p.drawPath(path)


class Chat(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Michael — EMG Lab Assistant")
        self.resize(560, 660)
        self.setStyleSheet("background:#0d1f16; color:#e6eefc; font-family:'Segoe UI',Arial;")
        self._threads = []
        v = QtWidgets.QVBoxLayout(self)

        head = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Michael")
        title.setStyleSheet("font-size:18px; font-weight:bold; color:#8fd0a0;")
        sub = QtWidgets.QLabel("EMG Lab Assistant")
        sub.setStyleSheet("color:#8aa0c0; font-size:12px;")
        self.dot = QtWidgets.QLabel("connecting…")
        self.dot.setStyleSheet("color:#e3b341; font-weight:bold;")
        head.addWidget(title)
        head.addWidget(sub)
        head.addStretch(1)
        head.addWidget(self.dot)
        v.addLayout(head)

        self.view = QtWidgets.QTextEdit()
        self.view.setReadOnly(True)
        self.view.setStyleSheet("background:#0b1a12; border:1px solid #2a4030; border-radius:6px;"
                                "padding:8px; font-size:13px;")
        v.addWidget(self.view, 1)

        # "thinking" bar — an animated EMG contraction trace while Michael composes a reply
        self.thinkbar = QtWidgets.QWidget()
        tb = QtWidgets.QHBoxLayout(self.thinkbar)
        tb.setContentsMargins(0, 4, 0, 0)
        self.think_lbl = QtWidgets.QLabel("Michael is thinking")
        self.think_lbl.setStyleSheet("color:#8fd0a0; font-size:12px;")
        self.think_lbl.setFixedWidth(150)
        self.wave = Wave()
        tb.addWidget(self.think_lbl)
        tb.addWidget(self.wave, 1)
        self.thinkbar.hide()
        v.addWidget(self.thinkbar)

        self._dots = 0
        self._dot_timer = QtCore.QTimer(self)
        self._dot_timer.timeout.connect(self._anim_dots)

        row = QtWidgets.QHBoxLayout()
        self.inp = QtWidgets.QLineEdit()
        self.inp.setPlaceholderText("Ask Michael…  e.g. how do I set MVC?")
        self.inp.setStyleSheet("background:#12241a; border:1px solid #2a4030; border-radius:6px;"
                               "padding:8px; color:#e6eefc; font-size:13px;")
        self.inp.returnPressed.connect(self.send)
        self.btn = QtWidgets.QPushButton("Send")
        self.btn.setStyleSheet("QPushButton{background:#2e7d32;color:#fff;font-weight:bold;"
                               "padding:8px 18px;border-radius:6px;border:none;}"
                               "QPushButton:hover{background:#388e3c;}"
                               "QPushButton:disabled{background:#1e3a24;color:#6f8f78;}")
        self.btn.clicked.connect(self.send)
        row.addWidget(self.inp, 1)
        row.addWidget(self.btn)
        v.addLayout(row)

        self._say("Michael", "Hi! I'm Michael, your EMG lab assistant. Ask me anything about placing "
                  "sensors, filtering, smoothing, MVC, recording, or reviewing your data.", "#8fd0a0")
        QtCore.QTimer.singleShot(150, lambda: self._run("__ping__"))

    def _say(self, who, text, color):
        self.view.append(f'<p style="margin:6px 0;"><b style="color:{color}">{who}:</b> {text}</p>')
        sb = self.view.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _anim_dots(self):
        self._dots = (self._dots + 1) % 4
        self.think_lbl.setText("Michael is thinking" + "." * self._dots)

    def _run(self, message):
        w = Worker(message)
        self._threads.append(w)
        w.done.connect(self._pong if message == "__ping__" else self._answer)
        w.finished.connect(lambda: self._threads.remove(w) if w in self._threads else None)
        w.start()

    def _set_status(self, online):
        if online:
            self.dot.setText("online"); self.dot.setStyleSheet("color:#39d353; font-weight:bold;")
        else:
            self.dot.setText("offline (scripted)"); self.dot.setStyleSheet("color:#e3b341; font-weight:bold;")

    def _pong(self, res):
        self._set_status(res.get("source") == "llm")

    def _thinking(self, on):
        if on:
            self.thinkbar.show()
            self.wave.start()
            self._dots = 0
            self.think_lbl.setText("Michael is thinking")
            self._dot_timer.start(350)
        else:
            self.wave.stop()
            self._dot_timer.stop()
            self.thinkbar.hide()

    def send(self):
        msg = self.inp.text().strip()
        if not msg:
            return
        self._say("You", msg, "#7fb3ff")
        self.inp.clear()
        self.inp.setEnabled(False)
        self.btn.setEnabled(False)
        self._thinking(True)
        self._run(msg)

    def _answer(self, res):
        self._thinking(False)
        ans = res.get("answer", "")
        hint = ROOM.get(res.get("action"))
        if hint:
            ans += f'<br><span style="color:#8aa0c0">&#8627; {hint}</span>'
        self._say("Michael", ans, "#8fd0a0")
        self.inp.setEnabled(True)
        self.btn.setEnabled(True)
        self.inp.setFocus()
        self._set_status(res.get("source") == "llm")


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    w = Chat()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
