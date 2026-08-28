"""
Unit tests for EmgFilters DSP functions.

Validates:
- Notch filter attenuation at 50 Hz
- RMS envelope amplitude tracking
- Multichannel handling

Run: python tests/test_dsp.py
Exit: 0 on pass, 1 on failure
"""

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dsp.dsp import EmgFilters


class TestEmgFilters(unittest.TestCase):
    def setUp(self):
        self.fs = 2000.0
        self.filters = EmgFilters(self.fs)

    def test_notch_50hz_attenuation(self):
        """50 Hz sine should be attenuated by more than 20 dB."""
        fs = self.fs
        t = np.arange(int(fs * 2)) / fs          # 2 seconds
        x = np.sin(2 * np.pi * 50.0 * t).reshape(-1, 1)

        y = self.filters.apply_notch(x, 50)

        # Discard edge transients from filtfilt
        trim = int(0.5 * fs)
        x_rms = np.sqrt(np.mean(x[trim:-trim] ** 2))
        y_rms = np.sqrt(np.mean(y[trim:-trim] ** 2))

        attenuation_db = 20 * np.log10(y_rms / x_rms)
        self.assertLess(attenuation_db, -20.0,
                        f"Notch attenuation insufficient: {attenuation_db:.2f} dB")

    def test_rms_envelope_amplitude(self):
        """RMS envelope of a 100 Hz sine (amplitude 1) should be ~0.707 V."""
        fs = self.fs
        t = np.arange(int(fs * 1)) / fs
        x = np.sin(2 * np.pi * 100.0 * t).reshape(-1, 1)

        env = self.filters.rms_envelope(x, win_ms=100.0)

        # Skip initial convolution ramp-up
        trim = int(0.2 * fs)
        mean_env = float(np.mean(env[trim:]))
        expected = 1.0 / np.sqrt(2.0)
        self.assertAlmostEqual(mean_env, expected, delta=0.1,
                               msg=f"RMS envelope mean {mean_env:.4f}, expected {expected:.4f}")

    def test_multichannel_rms_envelope(self):
        """RMS envelope should preserve number of channels."""
        fs = self.fs
        t = np.arange(int(fs * 1)) / fs
        x = np.column_stack([
            np.sin(2 * np.pi * 100.0 * t),
            np.sin(2 * np.pi * 100.0 * t),
        ])
        env = self.filters.rms_envelope(x)
        self.assertEqual(env.shape, x.shape)


if __name__ == "__main__":
    unittest.main()