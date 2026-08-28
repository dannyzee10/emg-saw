# EMG SAW Agent Roster

## Brain Agent (Orchestrator) – Systems Architect
- **Role:** Owns architecture, checkpoints, stop-the-line authority.
- **Duties:** Coordinates other agents, enforces SAFe methodology, reviews specs, approves merges.
- **Exit State:** "Architecture approved – ready for implementation"
- **Tools:** Read, Grep, Bash, Write (limited)

## Specialist Agents

### Firmware Engineer (FW)
- **Focus:** STM32F103 firmware (C/C++, HAL, CubeMX), ADC/DMA, UART protocol, timing.
- **Exit State:** "Firmware ready for integration test"
- **Tools:** Read, Write, Edit, Bash (flash/debug)

### GUI Engineer (GUI)
- **Focus:** PyQt5 + pyqtgraph application, MVC, real-time plotting, recording controls.
- **Exit State:** "GUI ready for acceptance test"
- **Tools:** Read, Write, Edit, Bash

### DSP/Signal Engineer (DSP)
- **Focus:** Filter design (notch, bandpass), metrics (RMS, median frequency, onset), scipy/signal.
- **Exit State:** "DSP validated with unit tests"
- **Tools:** Read, Write, Edit, Bash (run tests)

### Hardware/AFE Engineer (HW)
- **Focus:** Analog front-end (electrodes, buffers, INA, driven guard), ADS1299 upgrade, PCB.
- **Exit State:** "Hardware design reviewed and documented"
- **Tools:** Read, Write (schematics docs), Grep

### Test & Validation Engineer (QA)
- **Focus:** Unit tests, HIL simulation, bench validation, signal quality metrics.
- **Exit State:** "All acceptance criteria verified"
- **Tools:** Read, Write, Edit, Bash (run tests, scripts)

## Collaboration Rules
- Round Table at start/end of each session.
- Checkpoints (CP) after each significant change.
- Gate reviews before merging to `main`.
- Pattern discovery MANDATORY before writing new code.
- Use SAFe Epic/Feature/Story tracking in `specs/`.