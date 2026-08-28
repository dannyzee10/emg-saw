# EMG Acquisition System Architecture

## Overview
The system comprises three layers:
1. **Analog Front-End (AFE)** – custom discrete electronics, electrodes, driven guard.
2. **Microcontroller (STM32F103)** – ADC sampling, DMA, UART transmission.
3. **Host PC (PyQt5 GUI)** – data reception, processing, visualization, storage.

## High-Level Block Diagram (text)
[EMG Electrodes] → [AFE: buffer + INA + filters] → [STM32 ADC (12-bit)] → [DMA buffer] → [UART] → [PC: pyserial] → [DSP pipeline] → [pyqtgraph display] → [file storage/report]

## Software Architecture (Host PC)
- **Model-View-Controller (MVC)**
  - Model: `AcquisitionModel` (serial port, data buffer, recording state)
  - View: `MainWindow` (pyqtgraph plots, controls, status bar)
  - Controller: `MainController` (coordinates model/view, commands)
- **Layers**
  - `communication`: SerialComm class (pyserial, framing, CRC)
  - `dsp`: FilterChain, MetricsCalculator
  - `gui`: widgets for plots, controls, dialogs
  - `storage`: Recorder (CSV/EDF), ReportGenerator

## Data Flow
1. STM32 samples all channels at configured rate (e.g., 2 kHz).
2. Samples packed into frames: [sync][ch1_2bytes][ch2_2bytes]...[CRC].
3. Sent over UART at high baud (e.g., 460800).
4. PC reads raw bytes, verifies CRC, unpacks into NumPy array.
5. Array pushed into circular buffer.
6. DSP applies notch + bandpass (scipy.signal).
7. Plot updated at ~60 Hz using pyqtgraph.
8. If recording, data written to file in chunks.

## Firmware Architecture (STM32)
- Timer triggers ADC conversion at fixed rate.
- DMA transfers ADC data to memory buffer.
- Main loop packs and sends via UART when buffer threshold reached.
- Hardware: STM32F103C8T6 (Blue Pill), internal ADC, USART.

## Upgrade Path: ADS1299
- Replace internal ADC with ADS1299 (24-bit, 8 ch, SPI).
- Firmware reads samples via SPI and sends over UART (or USB).
- PC protocol remains same (channels, sample rate maybe higher).