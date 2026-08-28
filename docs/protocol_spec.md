# EMG UART Protocol Specification

## Version
1.0 (baseline)

## Purpose
Defines the byte-level protocol used between the STM32F103 firmware and the PC-side Python application (`communication/protocol.py`). This spec is the contract for all firmware and PC implementations.

## Physical Layer
- **Interface:** UART (USART1)
- **Baud rate:** 921600
- **Data bits:** 8
- **Parity:** None
- **Stop bits:** 1
- **Flow control:** None

## Frame Structure

Every frame is a fixed-size binary packet.

| Field         | Size (bytes) | Description                              |
|---------------|--------------|------------------------------------------|
| Header        | 1            | Sync byte `0xAA`                         |
| Sequence      | 1            | 8-bit frame counter (0–255, wraps)       |
| Channel data  | 16           | 8 channels × 2 bytes (big-endian)        |
| CRC           | 2            | CRC-16/CCITT-FALSE over all preceding    |
| **Total**     | **20**       | (May differ if header included; see note)|

**Note:** The debug output showed encoded frame length = 21 bytes. The extra byte is likely a second header or length byte. The canonical field order is defined in `communication/protocol.py` `encode_frame()`. Update this table after reviewing the exact implementation.

## Channel Data Format
- 8 channels per frame.
- Each channel is a 12-bit ADC value (0–4095), stored as unsigned 16-bit big-endian.
- Channel order matches physical ADC channels (0–7).

## CRC Algorithm
- **Name:** CRC-16/CCITT-FALSE
- **Polynomial:** 0x1021
- **Initial value:** 0xFFFF
- **No reflection, no final XOR**
- CRC is calculated over all bytes from Header through Channel data (excluding CRC field itself).
- CRC bytes are appended in big-endian order.

## Sequence Number Behavior
- Increments by 1 for each frame.
- Wraps from 255 to 0.
- Used only for ordering/loss detection; not for timing.

## Error Handling
- PC-side `FrameParser` discards any frame with invalid CRC.
- On CRC mismatch, parser resyncs by scanning for next sync byte.
- Firmware should not send partial frames; DMA ensures continuous transfer.

## Upgrade Path (Version 2)
- Add a **protocol version byte** after the header to allow future changes.
- Change sequence number to **16-bit** (2 bytes) to avoid wrap every 0.128 s.
- Consider adding a 32-bit timestamp for precise timing.
- Maintain backward compatibility by using version byte to select parser.

## Reference Implementation
- PC: `communication/protocol.py` (class `FrameParser`, functions `encode_frame`, `crc16_ccitt`)
- Firmware docs: `firmware/stm32_firmware.md`, `firmware/cp4_binary_dma.md`

## Validation
- Round-trip test: `tests/test_protocol_roundtrip.py`
- Expected result: 1000 frames recovered with matching channel data and sequence modulo 256.

## Status
Approved by Systems Architect for baseline. Version 2 changes pending T-004.
## Version 2 (Current)
- Sync word: `0xAA 0x56`
- Sequence: 16-bit little-endian (range 0–65535)
- Frame length: `6 + 2*NCH` bytes
- CRC: CRC-16/CCITT-FALSE over body (seq + samples)
- Parser auto-detects v1/v2 by second sync byte.

## Version 1 (Legacy)
- Sync word: `0xAA 0x55`
- Sequence: 8-bit (range 0–255)
- Frame length: `5 + 2*NCH` bytes
- Still supported by parser for backward compatibility.
# EMG UART Protocol Specification

## Version
2.0 (current), with backward compatibility for 1.0

## Purpose
Defines the byte-level protocol used between the STM32F103 firmware and the PC-side Python application (`communication/protocol.py`). This spec is the contract for all firmware and PC implementations.

## Physical Layer
- **Interface:** UART (USART1)
- **Baud rate:** 921600
- **Data bits:** 8
- **Parity:** None
- **Stop bits:** 1
- **Flow control:** None

## Frame Structure – Version 2 (Current)

| Field         | Size (bytes) | Description                              |
|---------------|--------------|------------------------------------------|
| Sync High     | 1            | `0xAA`                                   |
| Sync Low      | 1            | `0x56` (v2 marker)                       |
| Sequence      | 2            | 16-bit unsigned, little-endian (0–65535) |
| Channel data  | 2 × NCH      | NCH × int16 little-endian                |
| CRC           | 2            | CRC-16/CCITT-FALSE over seq + data       |
| **Total**     | **6 + 2×NCH**|                                          |

## Frame Structure – Version 1 (Legacy)

| Field         | Size (bytes) | Description                              |
|---------------|--------------|------------------------------------------|
| Sync High     | 1            | `0xAA`                                   |
| Sync Low      | 1            | `0x55` (v1 marker)                       |
| Sequence      | 1            | 8-bit unsigned (0–255, wraps)            |
| Channel data  | 2 × NCH      | NCH × int16 little-endian                |
| CRC           | 2            | CRC-16/CCITT-FALSE over seq + data       |
| **Total**     | **5 + 2×NCH**|                                          |

## Channel Data Format
- NCH = 8 channels per frame.
- Each channel is a 12-bit ADC value (0–4095), stored as signed 16-bit little-endian.
- Channel order matches physical ADC channels (0–7).

## CRC Algorithm
- **Name:** CRC-16/CCITT-FALSE
- **Polynomial:** 0x1021
- **Initial value:** 0xFFFF
- **No reflection, no final XOR**
- CRC is calculated over the body: sequence + channel data (excludes sync and CRC).
- CRC bytes are appended little-endian.

## Sequence Number Behavior
- Version 1: increments by 1, wraps 255 → 0.
- Version 2: increments by 1, wraps 65535 → 0.
- Used for ordering/loss detection; not for timing.

## Error Handling
- PC-side `FrameParser` discards any frame with invalid CRC.
- On CRC mismatch, parser resyncs by scanning for next valid sync word.
- Firmware should not send partial frames; DMA ensures continuous transfer.

## Version Detection
- PC parser auto-detects version by second sync byte:
  - `0x55` → v1
  - `0x56` → v2
- Both versions can be parsed in the same stream, though firmware should send only one.

## Reference Implementation
- PC: `communication/protocol.py`
- Firmware: `firmware/src/main.c` (skeleton)
- Tests: `tests/test_protocol_roundtrip.py`

## Validation
- Round-trip tests for v1 and v2 pass.
- v2 wrap-around test (65534 → 65535 → 0) passes.

## Status
Approved by Systems Architect. Version 2 is current.