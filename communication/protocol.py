"""
Wire protocol shared by the STM32 firmware and the laptop plotter.

Version 1 (legacy):
    byte 0      : 0xAA          sync high
    byte 1      : 0x55          sync low (v1 marker)
    byte 2      : seq (uint8)   increments every frame; wraps 255->0
    byte 3..    : NCH * int16 little-endian  raw ADC codes
    last 2      : crc16-ccitt little-endian over bytes [2 .. end-of-payload]

Version 2 (current):
    byte 0      : 0xAA          sync high
    byte 1      : 0x56          sync low (v2 marker)
    byte 2..3   : seq (uint16 little-endian)  wraps 65535->0
    byte 4..    : NCH * int16 little-endian  raw ADC codes
    last 2      : crc16-ccitt little-endian over bytes [2 .. end-of-payload]

Frame length v1 = 5 + 2*NCH
Frame length v2 = 6 + 2*NCH

The parser auto-detects the version by the second sync byte and can
parse a mixed stream (though firmware should send only one version).
"""

from __future__ import annotations

import struct
from collections import deque
from itertools import islice

SYNC1 = 0xAA
SYNC2_V1 = 0x55
SYNC2_V2 = 0x56


def crc16_ccitt(data: bytes, crc: int = 0xFFFF) -> int:
    """CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF). Matches the C code in firmware/."""
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc & 0xFFFF


def encode_frame(seq: int, samples, version: int = 2) -> bytes:
    """Build one frame. `version` = 1 for legacy 8-bit seq, 2 for 16-bit seq."""
    if version == 1:
        body = struct.pack("<B", seq & 0xFF) + b"".join(
            struct.pack("<h", int(s)) for s in samples
        )
        crc = crc16_ccitt(body)
        return bytes((SYNC1, SYNC2_V1)) + body + struct.pack("<H", crc)
    elif version == 2:
        body = struct.pack("<H", seq & 0xFFFF) + b"".join(
            struct.pack("<h", int(s)) for s in samples
        )
        crc = crc16_ccitt(body)
        return bytes((SYNC1, SYNC2_V2)) + body + struct.pack("<H", crc)
    else:
        raise ValueError(f"Unsupported protocol version: {version}")


class FrameParser:
    """Streaming parser that auto-detects protocol version per frame.
    Yields (seq, [codes]) for every valid frame and tracks drop/crc stats."""

    def __init__(self, nch: int):
        self.nch = nch
        self._buf = deque()
        # stats
        self.crc_errors = 0
        self.dropped = 0
        self.frames_ok = 0
        self._last_seq = None
        self._last_version = None   # 1 or 2; used for gap mask

    def feed(self, chunk: bytes):
        self._buf.extend(chunk)
        while True:
            frame = self._try_extract()
            if frame is None:
                return
            yield frame

    def _try_extract(self):
        buf = self._buf
        while True:
            # find sync word (first byte must be SYNC1)
            while len(buf) >= 2 and buf[0] != SYNC1:
                buf.popleft()
            if len(buf) < 2:
                return None

            # determine version from second sync byte
            if buf[1] == SYNC2_V1:
                version = 1
                body_len = 1 + 2 * self.nch
                frame_len = 2 + body_len + 2
                seq_mask = 0xFF
            elif buf[1] == SYNC2_V2:
                version = 2
                body_len = 2 + 2 * self.nch
                frame_len = 2 + body_len + 2
                seq_mask = 0xFFFF
            else:
                # not a valid sync pair; discard first byte and continue
                buf.popleft()
                continue

            if len(buf) < frame_len:
                return None

            raw = bytes(islice(buf, frame_len))
            body = raw[2:2 + body_len]
            crc_rx = raw[frame_len - 2] | (raw[frame_len - 1] << 8)
            if crc16_ccitt(body) != crc_rx:
                self.crc_errors += 1
                buf.popleft()
                continue

            # consume the good frame
            for _ in range(frame_len):
                buf.popleft()

            if version == 1:
                seq = body[0]
            else:  # version == 2
                seq = struct.unpack("<H", body[0:2])[0]

            codes = list(struct.unpack("<%dh" % self.nch, body[body_len-2*self.nch:]))
            if self._last_seq is not None:
                # If version changed, just reset gap tracking (shouldn't happen)
                if version != self._last_version:
                    self._last_seq = seq
                    self._last_version = version
                else:
                    gap = (seq - self._last_seq - 1) & seq_mask
                    self.dropped += gap
            self._last_seq = seq
            self._last_version = version
            self.frames_ok += 1
            return seq, codes