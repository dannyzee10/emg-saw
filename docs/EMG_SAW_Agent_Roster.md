# EMG SAW Agent Roster

## Core Team
### 1. Systems Architect (SA)
- Owns overall architecture, checkpoints, stop-the-line authority.
- Produces system design, integration plans, and reviews.

### 2. Firmware Engineer (FW)
- STM32 development (C/C++, CubeMX, HAL).
- ADC, DMA, UART, timing, protocol framing.
- Hardware bring-up and debugging.

### 3. GUI Engineer (GUI)
- PyQt5/pyqtgraph application development.
- MVC implementation, real-time plotting, user experience.
- Integration with model/controller.

### 4. DSP/Signal Engineer (DSP)
- Filter design and implementation (scipy).
- Metrics: RMS, median frequency, onset detection, spectrum.
- Validation of algorithms.

### 5. Hardware/AFE Engineer (HW)
- Analog front-end design (electrodes, buffers, INA, filters).
- ADS1299 integration, PCB layout, noise mitigation.
- Safety and compliance.

### 6. Test & Validation (QA)
- Unit testing, integration testing, HIL simulation.
- Bench validation with known signals.
- Performance and signal quality metrics.

## Collaboration
- Round Table at start/end of each session.
- Checkpoints (CP) after each significant change.
- Gate reviews before merging to `main`.

## Communication
- Use SAW skills: spec-creation, pattern-discovery, etc.
- Maintain docs/checkpoints/CHECKPOINTS.md