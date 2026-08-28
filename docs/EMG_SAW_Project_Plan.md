# EMG Acquisition + GUI System – SAW Project Plan

## Goal
Extend the existing `emg-realtime` instrument into a full clinical/research platform:
- Real-time multi-channel EMG visualization
- DSP pipeline (filters, RMS, MVC, median frequency)
- Recording & report generation
- Hardware upgrade path to ADS1299

## Decisions
- Stack: Python + PyQt5 + pyqtgraph + pyserial + numpy/scipy
- Hardware: custom discrete AFE + STM32F103 internal ADC (UART), upgrade to ADS1299
- SAW methodology: SAFe Epic/Feature/Story + Round Table + checkpoints

## Epics
1. **EPIC-1: Establish SAW Workspace and Baseline**  
   - Set up folder structure, agents, skills, docs.  
   - Import existing `emg-realtime` code as baseline.

2. **EPIC-2: Firmware & Protocol Enhancements**  
   - Improve STM32 firmware (DMA, timing, error handling).  
   - Define robust UART protocol with framing and CRC.

3. **EPIC-3: GUI Instrumentation**  
   - Refactor GUI to MVC architecture.  
   - Add: recording controls, channel configuration, filter settings, spectrum display, MVC/onset detection, report generation.

4. **EPIC-4: Signal Quality & DSP**  
   - Implement real-time filter chain (notch 50/60 Hz, bandpass 20–450 Hz).  
   - Add metrics: RMS, median frequency, onset timing.  
   - Calibration/validation with known signals.

5. **EPIC-5: Hardware Upgrade – ADS1299**  
   - Design AFE board or integrate module.  
   - Update firmware for SPI + 24-bit.  
   - Keep PC-side protocol backward compatible where possible.

6. **EPIC-6: Testing & Validation**  
   - Unit tests for DSP, protocol.  
   - HIL testing with simulator.  
   - Bench validation with signal generator and real muscle contractions.

## Milestones
- M1: SAW workspace ready, baseline code imported (this checkpoint)
- M2: Firmware protocol v2 implemented and tested
- M3: GUI refactored, recording + report working
- M4: ADS1299 prototype streaming data into GUI
- M5: Full validation complete, documentation done

## SAFe Ceremonies
- PI planning per epic
- Sprint demo after each story
- Retro after each feature