# NV_ABJ Copilot Instructions

## Project Overview

NV_ABJ is a **generalized Python framework** for controlling NV (nitrogen-vacancy) center experiments in the Ania B. Jayich Lab at UC Santa Barbara. It provides abstract interfaces, hardware drivers, experimental logic, and reusable UI components that work across multiple experimental setups.

**Key principle:** Experiment-specific configurations (like `LTSPM2_Interfaces/experimental_configuration`) instantiate hardware using classes from NV_ABJ with setup-specific addresses and parameters.

## Architecture

### Package Structure
```
NV_ABJ/
├── abstract_interfaces/     # ABCs defining hardware contracts
│   ├── connected_device.py  # Base: make_connection(), close_connection(), context manager
│   ├── microwave_source.py  # prime_sinusoidal_rf(), iterate_next_waveform()
│   ├── photon_counter.py    # get_counts_raw(), get_counts_raw_when_triggered()
│   ├── scanner.py           # set_position_m(), get_position_m()
│   ├── pulse_generator.py   # load(), start(), stop(), generate_sequence()
│   └── measurement_sequence.py  # generate_sequence(), counts_to_raw_counts(), experimental_setup()
├── hardware_interfaces/     # Concrete implementations by device type
│   ├── microwave_sources/sg380/     # SRS SG380 series
│   ├── photon_counter/ni_daq_counters/
│   ├── scanner/ni_daq_scanner/
│   ├── positioners/cacli_jpe/       # JPE piezo positioners
│   ├── pulse_generators/spbicl_pulse_blaster/
│   └── temperature_controller/lakeshore/
├── experimental_logic/
│   ├── confocal_scanning.py         # ConfocalControls for xy_scan, z_scan, tracking
│   └── sequence_generation/
│       ├── sequence_generation.py    # Sequence, SequenceSubset, SequenceDevice
│       └── sequences/single_laser_sequences/  # CWESR, RabiIq, PulsedEsr
├── user_interfaces/         # PyQt5 widgets for GUIs
│   ├── image_scan_widget/
│   ├── tracking_widget/
│   ├── z_scan_widget/
│   └── running_counts_widget/
├── analysis/               # Data analysis and curve fitting
│   ├── esr_analysis.py     # Multi-Lorentzian fitting
│   └── rabi_analysis.py    # Rabi oscillation analysis
└── utilities/
    ├── data_manager.py     # HDF5 save/load, file organization
    └── units.py            # Unit conversion utilities
```

## Critical Design Patterns

### 1. ConnectedDevice Context Manager
All hardware inherits from `ConnectedDevice` to ensure proper resource management:
```python
class ConnectedDevice(metaclass=ABCMeta):
    @abstractmethod
    def make_connection(self): ...
    @abstractmethod
    def close_connection(self): ...
    
    def __enter__(self):
        self.make_connection()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()
```

**Usage pattern:**
```python
with photon_counter_1 as pc:
    counts = pc.get_counts_raw_when_triggered(number_of_data_taking_cycles=20000)
# Connection auto-closes
```

### 2. SequenceDevice for Pulse Generation
Sequences define timing with devices that have addresses and delays:
```python
# Device definition (experiment-specific)
green_aom_trigger = SequenceDevice(
    address=2,                    # Pulse blaster channel
    device_label="Green AOM",
    delayed_to_on_ns=850,         # Hardware turn-on delay compensation
    device_status=False,
    inverted_output=False
)

# Sequence building
seq = Sequence()
seq.add_step(duration_ns=1000000, devices=[green_aom_trigger, rf_trigger])
seq.add_step(duration_ns=25,      devices=[green_aom_trigger, readout_trigger])
```

### 3. MeasurementSequence Pattern
Each measurement type implements `MeasurementSequence`:
```python
class CWESR(MeasurementSequence):
    def generate_sequence(self, readout_time_s, ...) -> Sequence:
        # Build and return pulse sequence
    
    def experimental_setup(self, rf_source, frequency_list_hz, ...):
        # Prime hardware before measurement loop
    
    def counts_to_raw_counts(self, data) -> NDArray:
        # Process raw DAQ data into meaningful counts
```

### 4. ConfocalControls Workflow
Central class for scanning and tracking:
```python
confocal_controls = ConfocalControls(scanner_x, scanner_y, scanner_z, photon_counter)

# XY imaging
counts, x_pos, y_pos = confocal_controls.xy_scan(
    dwell_time_s=0.01,
    x_positions=np.linspace(-5e-6, 5e-6, 50),
    y_positions=np.linspace(-5e-6, 5e-6, 50),
    z_position=0
)

# NV tracking
x, y, z, tracking_graphs = confocal_controls.tracking(x_pos, y_pos, z_pos, iterations=10)
```

## Units Convention (Strict)
- **Positions:** meters (internal), micrometers (UI display)
- **Frequencies:** Hz
- **Time:** seconds (`_s` suffix) or nanoseconds (`_ns` suffix)
- **Power:** dBm (RF), Watts (optical)

## Hardware Implementation Guide

When adding new hardware, follow this template:

```python
from NV_ABJ.abstract_interfaces.microwave_source import MicrowaveSource

class NewSignalGenerator(MicrowaveSource):
    def __init__(self, address: str, ...):
        self.address = address
        self._connection = None
    
    def make_connection(self):
        # Open connection, store in self._connection
        pass
    
    def close_connection(self):
        self.turn_off_signal()
        # Close self._connection
        pass
    
    @property
    def frequency_range_hz(self) -> tuple:
        return (min_freq, max_freq)
    
    @property
    def amplitude_range_dbm(self) -> tuple:
        return (min_amp, max_amp)
    
    def prime_sinusoidal_rf(self, frequency_list_hz, rf_amplitude_dbm, ...):
        # Load frequency list for stepped execution
        pass
    
    def iterate_next_waveform(self):
        # Advance to next frequency in list
        pass
```

## DataManager Usage

```python
from NV_ABJ.utilities.data_manager import DataManager

# Initialize with default location
dm = DataManager(default_save_location=r"D:\data\measurements")

# Save measurement data
file_path = dm.save_measurement_sequence_data(
    data_dict={"frequency_list_hz": freqs, "initial_data": initial},
    measurement_name="cwesr",
    measurement_class_inputs={"rf_power": -12, ...},
    sequence_class=seq,
    number_of_measurements_per_point=1,
    number_of_points_per_sweep=50,
    number_of_sweeps=100
)

# Incrementally update during measurement
dm.update_hdf5(file_path, f"counts_per_second_{sweep_idx}", counts_array)

# Load data later
data = dm.load_hdf5(file_path)
```

## Development Workflow

### Rebuilding After Changes
```powershell
python nv_abj_installer.py
```
This uses `hatchling` to build and pip-install the package.

### Adding New Measurement Sequences
1. Create class in `experimental_logic/sequence_generation/sequences/`
2. Inherit from `MeasurementSequence`
3. Implement `generate_sequence()`, `experimental_setup()`, `counts_to_raw_counts()`

### Creating Analysis Classes
Pattern from `analysis/esr_analysis.py`:
```python
class NewAnalysis:
    def __init__(self, x_data, y_data, y_error):
        self.x_data = x_data
        self.y_data = y_data
        self.y_error = y_error
    
    def fit_function(self, x, *params): ...
    def fit_normal(self, n_features, export_xy_fit=False): ...
    def plot_fit(self, n_features): ...
```

## Key Dependencies
From `pyproject.toml`:
- `pyvisa`: GPIB/VISA instrument communication
- `nidaqmx`: National Instruments DAQ control
- `numpy`, `scipy`: Numerical computation and fitting
- `matplotlib`: Plotting
- `pyqt5`: GUI widgets
- `h5py`: HDF5 data storage
- `pandas`: Data manipulation

## Integration with Experiment Configs
Experiment repos (like LTSPM2_Interfaces) create `experimental_configuration/hardware_interfaces.py`:
```python
from NV_ABJ.hardware_interfaces.microwave_sources.sg380.sg380 import SG380
signal_generator_1 = SG380(gpib_address='GPIB0::27::INSTR')

from NV_ABJ.hardware_interfaces.scanner.ni_daq_scanner.ni_daq_scanner import NiDaqSingleAxisScanner
confocal_x = NiDaqSingleAxisScanner(
    conversion_volts_per_meter_setting=10/(50e-6),
    device_name_output="PXI1Slot5",
    channel_name_output="ao0",
    position_limits_m=(-50e-6, 50e-6)
)
```

## Common Pitfalls
1. **Always use context managers** for hardware to ensure cleanup
2. **Units are meters internally** - convert to/from micrometers only at UI boundaries
3. **Rebuild packages** after any source changes (`nv_abj_installer.py`)
4. **SequenceDevice delays** are in nanoseconds and compensate for hardware latency
5. **DataManager paths** use raw strings on Windows: `r"D:\path\to\data"`
