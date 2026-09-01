"""RecordingController – manages CSV recording independent of the GUI."""

import os
import time


class RecordingController:
    """Handles opening, writing, and closing a CSV file for raw EMG data."""

    def __init__(self, fs, nch, vref):
        self.fs = fs
        self.nch = nch
        self.vref = vref
        self.file = None
        self.path = None            # absolute path of the CSV currently/last written
        self.count = 0

    @property
    def active(self):
        return self.file is not None

    def start(self, subject="", trial="", notes="", muscles=None):
        """Open a new CSV file and write metadata header."""
        if self.file:
            self.stop()
        fname = time.strftime("emg_%Y%m%d_%H%M%S.csv")
        self.file = open(fname, "w", newline="")
        self.path = os.path.abspath(fname)
        self.file.write(f"# Subject: {subject}\n")
        self.file.write(f"# Trial: {trial}\n")
        self.file.write(f"# Notes: {notes}\n")
        muscles_str = ", ".join(muscles) if muscles else ", ".join(f"Ch{i+1}" for i in range(self.nch))
        self.file.write(f"# Muscles: {muscles_str}\n")
        self.file.write(f"# fs={self.fs:.0f} Hz, nch={self.nch}, vref={self.vref} V\n")
        self.file.write("t_s," + ",".join(f"ch{c+1}_code" for c in range(self.nch)) + "\n")
        self.count = 0

    def stop(self):
        if self.file:
            self.file.close()
            self.file = None

    def write_samples(self, new_data, base_t):
        """Write a chunk of raw samples to the file. `new_data` shape (n_samples, nch)."""
        if not self.file:
            return
        for i in range(new_data.shape[0]):
            t = base_t + i / self.fs
            row = f"{t:.6f}," + ",".join(str(int(x)) for x in new_data[i]) + "\n"
            self.file.write(row)
            self.count += 1

    def write_marker(self, label, elapsed):
        """Write a marker line (preceded by #) to the file."""
        if self.file:
            self.file.write(f"# MARKER {label} t={elapsed:.3f}\n")