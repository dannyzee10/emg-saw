# GUI Architecture Proposal (EMG Instrument)

## Current State
`gui/emg_plotter.py` is a single-file PyQt5 application that:
- Opens serial/simulated source.
- Applies filters via `dsp.dsp`.
- Plots real-time data using pyqtgraph.
- Handles start/stop and basic recording (CSV export).

## Proposed Modular Architecture

### Model
- `AcquisitionModel` (new) – wraps `communication.sources.SerialSource` or `SimSource`, maintains data buffer, emits signals on new data.
- `DspModel` – applies filter chain from `dsp.dsp`.

### View
- `MainWindow` – composes:
  - `PlotWidget` (pyqtgraph) for multi-channel display.
  - `ControlPanel` (buttons, combo boxes, status indicators).
  - `RecordingDialog` for file name/duration.

### Controller
- `MainController` – connects view events to model actions, manages threading.
- `RecordingController` – handles start/stop recording, file writing.

## Data Flow
Source → Model → (filter) → Signal → View update
User input → View → Controller → Model command

## Immediate Refactoring Steps
1. Extract source handling into `AcquisitionModel`.
2. Create `MainController` to manage source lifecycle.
3. Separate plot widget and controls into classes.
4. Keep `emg_plotter.py` as entry point that wires components.