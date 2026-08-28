"""
End-to-end HIL simulation for EMG acquisition pipeline.

Simulates STM32 firmware output (Protocol v2 frames) and feeds them through
the PC-side parser to verify integrity over a meaningful duration.

Run: python tests/test_hil_simulation.py
Exit: 0 on pass, 1 on failure.
"""

import sys
import time
import random
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from communication.protocol import encode_frame, FrameParser

FRAME_COUNT = 10000
NCH = 8


def simulate_firmware_output():
    """Generate a stream of v2 frames exactly as the firmware would."""
    for seq in range(FRAME_COUNT):
        # Simulate ADC values (e.g., resting baseline with noise)
        samples = [random.randint(0, 4095) for _ in range(NCH)]
        yield encode_frame(seq, samples, version=2)


def run_hil_simulation():
    parser = FrameParser(nch=NCH)
    recovered_frames = []
    start = time.perf_counter()

    for frame_bytes in simulate_firmware_output():
        for parsed in parser.feed(frame_bytes):
            recovered_frames.append(parsed)

    elapsed = time.perf_counter() - start

    # Verify all frames
    if len(recovered_frames) != FRAME_COUNT:
        return False, len(recovered_frames), elapsed, parser.crc_errors, parser.dropped

    # Check sequence and channel count
    for i, (seq, codes) in enumerate(recovered_frames):
        if seq != (i & 0xFFFF):
            return False, len(recovered_frames), elapsed, parser.crc_errors, parser.dropped
        if len(codes) != NCH:
            return False, len(recovered_frames), elapsed, parser.crc_errors, parser.dropped

    return True, len(recovered_frames), elapsed, parser.crc_errors, parser.dropped


def main():
    success, count, elapsed, crc_errors, dropped = run_hil_simulation()
    if success:
        print(f"✅ PASS: {count} frames recovered in {elapsed:.3f}s")
        print(f"   CRC errors: {crc_errors}, dropped: {dropped}")
        sys.exit(0)
    else:
        print(f"❌ FAIL: only {count} frames recovered, CRC errors: {crc_errors}, dropped: {dropped}")
        sys.exit(1)


if __name__ == "__main__":
    main()