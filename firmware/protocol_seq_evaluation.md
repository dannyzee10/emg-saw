# Sequence Number Width Evaluation

## Date
2026-08-27

## Context
- Protocol frame includes an 8-bit sequence number.
- Frame rate = 2 kHz (TIM2 sample clock, one frame per sample set).
- Each frame carries 8 channel codes.

## Calculation
- Sequence range: 0–255 (256 values).
- Frames per second: 2000.
- Time to wrap = 256 / 2000 = **0.128 seconds**.

## Impact
- If sequence number is used for lost-frame detection or reordering, the receiver cannot distinguish frames beyond 0.128 s.
- For real-time plotting, this is not critical; the GUI displays samples as they arrive.
- For recording or offline analysis, a repeated sequence makes it impossible to detect dropped frames over longer periods.

## Recommendation
- Upgrade protocol to **16-bit sequence number** in the next firmware/PC protocol revision.
- Alternatively, add a timestamp field (milliseconds) to each frame if higher precision is needed.
- Keep backward compatibility by adding a protocol version byte.

## Action Items
- [ ] Firmware: change `build_frame()` to include 16-bit sequence.
- [ ] PC side: update `FrameParser` to parse 16-bit sequence.
- [ ] Update round-trip test to cover wrap at 65536 frames (optional stress test).

## Status
Pending approval from Systems Architect.