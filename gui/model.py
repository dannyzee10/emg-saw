"""
AcquisitionModel — wraps a data source (SerialSource / SimSource / AsciiSource)
and maintains a ring buffer of recent raw ADC samples. Emits Qt signals for
lifecycle and new data.
"""

from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np


class AcquisitionModel(QObject):
    new_data = pyqtSignal(object)          # ndarray of shape (n_samples, nch)
    source_error = pyqtSignal(str)
    source_started = pyqtSignal()
    source_stopped = pyqtSignal()

    def __init__(self, source, nch, fs, buffer_seconds=6.0):
        super().__init__()
        self.source = source
        self.nch = nch
        self.fs = fs
        self.buffer_seconds = buffer_seconds
        self.buffer_n = int(buffer_seconds * fs)
        self.ring = np.zeros((self.buffer_n, nch), dtype=float)
        self.filled = 0

    def start(self):
        self.source.start()
        self.source_started.emit()

    def stop(self):
        self.source.stop()
        self.source_stopped.emit()

    def read_new(self):
        """Read new samples from the underlying source and update ring buffer."""
        data = self.source.read_new()
        if data is not None and data.shape[0] > 0:
            n = data.shape[0]
            if n >= self.buffer_n:
                self.ring[:] = data[-self.buffer_n:]
                self.filled = self.buffer_n
            else:
                self.ring[:-n] = self.ring[n:]
                self.ring[-n:] = data
                self.filled = min(self.buffer_n, self.filled + n)
            self.new_data.emit(data)
        return data