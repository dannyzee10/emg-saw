"""
Data sources for the plotter.

Every source runs a background thread that fills a thread-safe buffer with raw
ADC sample-sets (shape: N x NCH, int). The GUI thread calls read_new() at ~60 Hz
to drain whatever arrived. Producer (I/O) and consumer (drawing) are decoupled;
that is what keeps the plot smooth and lossless at high sample rates.

  SerialSource : reads framed binary from the STM32 (protocol.FrameParser)
  AsciiSource  : reads "v0,v1,...\\n" lines (Arduino-plotter style, easy STM32 printf)
  SimSource    : synthetic EMG so the whole UI runs with no board connected
"""

from __future__ import annotations

import sys
import threading
import time

import numpy as np

from .protocol import FrameParser

# Short read timeout so data is delivered to the GUI in small, frequent pieces
# (large timeouts make it arrive in lumps -> the sweep head jumps instead of gliding).
SERIAL_READ_TIMEOUT = 0.008


def _open_serial(port, baud, timeout):
    """Open the serial port exactly like a plain read that is known to work here.

    Open with DTR/RTS held low so the port-open cannot pulse a reset on the MCU
    (verified against the CP4 binary stream: clean continuous read, 0 errors).
    """
    import serial
    s = serial.Serial()
    s.port = port
    s.baudrate = baud
    s.timeout = timeout
    s.dtr = False
    s.rts = False
    s.open()
    return s


class _BufferedSource:
    """Common ring-collection + thread plumbing."""

    def __init__(self, nch: int):
        self.nch = nch
        self._lock = threading.Lock()
        self._pending = []            # list of [codes] awaiting the GUI
        self._thread = None
        self._stop = threading.Event()
        # exposed stats
        self.dropped = 0
        self.crc_errors = 0
        self.frames_ok = 0

    def start(self):
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    def read_new(self) -> np.ndarray:
        """Return all sample-sets collected since the last call, shape (n, nch)."""
        with self._lock:
            if not self._pending:
                return np.empty((0, self.nch), dtype=np.int32)
            out = np.asarray(self._pending, dtype=np.int32)
            self._pending = []
        return out

    def _push(self, codes):
        with self._lock:
            self._pending.append(codes)

    def _run(self):
        raise NotImplementedError


class SerialSource(_BufferedSource):
    def __init__(self, port: str, baud: int, nch: int):
        super().__init__(nch)
        self.port = port
        self.baud = baud
        self.parser = FrameParser(nch)

    def _run(self):
        ser = None
        while not self._stop.is_set():
            try:
                if ser is None:
                    ser = _open_serial(self.port, self.baud, SERIAL_READ_TIMEOUT)
                    ser.reset_input_buffer()   # drop stale backlog, sync on fresh frames
                chunk = ser.read(4096)
                if not chunk:
                    continue
                for _seq, codes in self.parser.feed(chunk):
                    self._push(codes)
                self.dropped = self.parser.dropped
                self.crc_errors = self.parser.crc_errors
                self.frames_ok = self.parser.frames_ok
            except Exception as e:
                print(f"[serial] {type(e).__name__}: {e}", file=sys.stderr, flush=True)
                try:
                    if ser is not None:
                        ser.close()
                except Exception:
                    pass
                ser = None
                time.sleep(0.5)
        if ser is not None:
            ser.close()


class AsciiSource(_BufferedSource):
    """Fallback for a quick STM32 `printf("%d,%d\\n", ...)` bring-up."""

    def __init__(self, port: str, baud: int, nch: int):
        super().__init__(nch)
        self.port = port
        self.baud = baud

    def _run(self):
        buf = b""
        ser = None
        while not self._stop.is_set():
            try:
                if ser is None:
                    ser = _open_serial(self.port, self.baud, SERIAL_READ_TIMEOUT)
                    ser.reset_input_buffer()   # drop stale backlog, read only fresh data
                    buf = b""
                chunk = ser.read(4096)
                if not chunk:
                    continue
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    parts = line.strip().split(b",")
                    if len(parts) < self.nch:
                        continue
                    try:
                        codes = [int(p) for p in parts[: self.nch]]
                    except ValueError:
                        continue
                    self._push(codes)
                    self.frames_ok += 1
            except Exception as e:
                # report (don't hide) then reopen and keep going
                print(f"[serial] {type(e).__name__}: {e}", file=sys.stderr, flush=True)
                try:
                    if ser is not None:
                        ser.close()
                except Exception:
                    pass
                ser = None
                time.sleep(0.5)
        if ser is not None:
            ser.close()


class SimSource(_BufferedSource):
    """Synthetic sEMG: baseline noise + intermittent bursts (band-limited noise
    amplitude-modulated), centered at ADC mid-scale so it travels the same
    volts-conversion path as real data. Each channel bursts on its own cadence."""

    def __init__(self, nch: int, fs: float, bits: int = 12):
        super().__init__(nch)
        self.fs = fs
        self.mid = (1 << bits) // 2
        self.full = (1 << bits) - 1
        self._phase = np.random.rand(nch) * 10.0

    def _run(self):
        dt = 1.0 / self.fs
        chunk_dt = 0.010                      # generate 10 ms at a time, real-time paced
        n_per_chunk = max(1, int(self.fs * chunk_dt))
        rng = np.random.default_rng()
        t = 0.0
        next_wall = time.perf_counter()
        # per-channel burst envelope state
        env = np.zeros(self.nch)
        while not self._stop.is_set():
            block = np.zeros((n_per_chunk, self.nch))
            for i in range(n_per_chunk):
                # slow burst gating: each channel toggles active periodically
                gate = 0.5 * (1 + np.sin(2 * np.pi * 0.4 * (t + self._phase)))
                gate = (gate > 0.6).astype(float)
                env = 0.98 * env + 0.02 * gate           # smooth on/off
                emg = env * rng.standard_normal(self.nch) * 0.35   # burst noise
                baseline = rng.standard_normal(self.nch) * 0.01    # rest noise
                sig = emg + baseline                                # ~ +-1 range
                codes = self.mid + sig * (self.mid * 0.9)
                block[i] = np.clip(codes, 0, self.full)
                t += dt
            with self._lock:
                self._pending.extend(block.astype(np.int32).tolist())
                self.frames_ok += n_per_chunk
            # pace to real time
            next_wall += chunk_dt
            sleep = next_wall - time.perf_counter()
            if sleep > 0:
                time.sleep(sleep)
            else:
                next_wall = time.perf_counter()
