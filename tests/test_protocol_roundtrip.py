"""
Round-trip tests for UART protocol integrity.
Covers both legacy v1 (8-bit seq) and current v2 (16-bit seq).

Run: python tests/test_protocol_roundtrip.py
Exit: 0 on all pass, 1 on any failure.
"""

import sys
import time
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from communication.protocol import encode_frame, FrameParser


def run_roundtrip_test(frame_count: int, nch: int, version: int):
    """Feed `frame_count` frames into parser and verify integrity."""
    frames = []
    for seq in range(frame_count):
        codes = [random.randint(0, 4095) for _ in range(nch)]
        frame_bytes = encode_frame(seq, codes, version=version)
        frames.append((seq, codes, frame_bytes))

    parser = FrameParser(nch=nch)
    recovered = []
    start = time.perf_counter()
    for _, _, fb in frames:
        for parsed in parser.feed(fb):
            recovered.append(parsed)
    elapsed = time.perf_counter() - start

    if len(recovered) != frame_count:
        return False, len(recovered), elapsed

    mask = 0xFF if version == 1 else 0xFFFF
    for (exp_seq, exp_codes, _), (rec_seq, rec_codes) in zip(frames, recovered):
        if (exp_seq & mask) != rec_seq:
            return False, len(recovered), elapsed
        if exp_codes != rec_codes:
            return False, len(recovered), elapsed
    return True, len(recovered), elapsed


def main():
    nch = 8
    tests = [
        ("v1 1000 frames", 1000, 1),
        ("v2 1000 frames", 1000, 2),
        ("v2 wrap-around", 3, 2),          # small test, we'll manually check wrap
    ]

    all_passed = True
    for name, count, ver in tests:
        if name == "v2 wrap-around":
            # Explicitly test wrap: seq 65534, 65535, 0
            parser = FrameParser(nch=nch)
            seqs = [65534, 65535, 0]
            for s in seqs:
                codes = [100] * nch
                fb = encode_frame(s, codes, version=2)
                out = list(parser.feed(fb))
                if len(out) != 1 or out[0][0] != s or out[0][1] != codes:
                    print(f"❌ FAIL: {name} - seq {s} mismatch: got {out}")
                    all_passed = False
                    break
            else:
                print(f"✅ PASS: {name}")
            continue

        success, count_rec, elapsed = run_roundtrip_test(count, nch, ver)
        if success:
            print(f"✅ PASS: {name} - {count_rec} frames in {elapsed:.3f}s")
        else:
            print(f"❌ FAIL: {name} - only {count_rec} frames recovered")
            all_passed = False

    if all_passed:
        print("\nAll protocol tests passed.")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()