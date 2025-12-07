# AudioEmm Architecture Diagram

## Application Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Web Interface                       │
│                      (ui_manager.py)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────┐    ┌──────────────────────────┐   │
│  │  Device Equalizer Page   │    │  Room Simulator Page     │   │
│  │                          │    │                          │   │
│  │  • Upload source audio   │    │  • Set room dimensions   │   │
│  │  • Upload target audio   │    │  • Select materials      │   │
│  │  • Calculate EQ curve    │    │  • Position speaker      │   │
│  │  • Visualize results     │    │  • Position listener     │   │
│  └────────┬─────────────────┘    │  • Run simulation        │   │
│           │                      │  • View metrics          │   │
│           │                      └────────┬──────────────────┘   │
│           │                               │                      │
└───────────┼───────────────────────────────┼──────────────────────┘
            │                               │
            ▼                               ▼
    ┌──────────────────────┐        ┌──────────────────────┐
    │  DeviceEqualizer()   │        │   RoomSimulator()    │
    │   (device_eq...)     │        │   (simulator.py)     │
    │                      │        │                      │
    │ • set_source_device()│        │ • set_materials()    │
    │ • set_target_device()│        │ • set_positions()    │
    │ • calculate_eq_curve│        │ • simulate_freq...() │
    │ • get_device_comp..│        │ • calculate_rt60()   │
    └────────┬─────────────┘        └────────┬─────────────┘
             │                              │
             ▼                              ▼
    ┌──────────────────────┐        ┌──────────────────────┐
    │   AudioAnalyzer()    │        │  Material Data       │
    │   (analyzer.py)      │        │  (simulator.py)      │
    │                      │        │                      │
    │ • analyze_file()     │        │ • Drywall: 0.1-0.05  │
    │ • get_freq_resp...() │        │ • Carpet: 0.2-0.6    │
    │ • smooth_array()     │        │ • Concrete: 0.01-0.02│
    │ • normalize...()     │        │ • Glass: 0.05-0.02   │
    └────────┬─────────────┘        └─────────────────────┘
             │
             ▼
    ┌──────────────────────┐
    │  Audio File (MP3,    │
    │  WAV, FLAC)          │
    └──────────────────────┘

```

## Module Dependencies

```
┌────────────────────────────────────────────────────────┐
│                 main_app.py (Entry)                    │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │   ui_manager.py       │
            │   (UIManager class)   │
            └─┬────────────────┬────┘
              │                │
      ┌───────▼──┐     ┌──────▼────────┐
      │ config   │     │  Streamlit    │
      │ module   │     │  (st)         │
      └──────────┘     └───────────────┘

┌─────────────────────────────────────────────────────────┐
│          lib/                (Core Modules)            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐  ┌──────────────────────────┐    │
│  │  audio/          │  │  equalizer/              │    │
│  │  └─ analyzer.py  │  │  └─ device_equalizer.py │    │
│  │     - FFT        │  │     - EQ Calculation     │    │
│  │     - Windowing  │  │     - Device profiles    │    │
│  │     - Normalize  │  │     - Comparison         │    │
│  └──────────────────┘  └──────────────────────────┘    │
│                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐    │
│  │  room_simulator/     │  │  utils/              │    │
│  │  └─ simulator.py     │  │  └─ config.py        │    │
│  │     - Sabine formula │  │     - JSON loading   │    │
│  │     - Reflections    │  │     - Config saving  │    │
│  │     - Materials      │  │     - Device mgmt    │    │
│  │     - RT60           │  │     - Defaults       │    │
│  └──────────────────────┘  └──────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Data Flow - Device Equalizer

```
User Action: Upload audio files and click "Analyze"
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  DeviceEqualizer.set_source_device│
        │  DeviceEqualizer.set_target_device│
        └───────────┬───────────────────────┘
                    │
                    ▼
        ┌───────────────────────────────────┐
        │ AudioAnalyzer.analyze_file()      │
        │                                   │
        │ • Load audio with librosa        │
        │ • FFT with Hann window          │
        │ • Convert to dB                 │
        │ • Return (frequencies, db_vals) │
        └───────────┬───────────────────────┘
                    │
        ┌───────────┴────────────┐
        │                        │
        ▼                        ▼
    Source Response         Target Response
    [freq, dB]             [freq, dB]
                               │
                    ┌──────────▼──────────┐
                    │ Interpolate to same │
                    │ frequency grid      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Calculate EQ curve: │
                    │ Target_dB - Source_dB
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Return comparison:  │
                    │ • Frequencies       │
                    │ • Source dB         │
                    │ • Target dB         │
                    │ • EQ curve          │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Visualize:          │
                    │ • Freq response plot│
                    │ • EQ curve plot     │
                    │ • Interpretation    │
                    └─────────────────────┘
```

## Data Flow - Room Simulator

```
User Action: Set room params and click "Simulate"
                            │
                            ▼
        ┌────────────────────────────────────┐
        │  RoomSimulator.__init__()           │
        │  set_materials()                   │
        │  set_speaker_position()            │
        │  set_listener_position()           │
        └────────────────┬────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  simulate_frequency_response()     │
        └────┬──────────┬──────────┬─────────┘
             │          │          │
             ▼          ▼          ▼
    ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
    │ calculate_  │  │ calculate_   │  │ calculate_   │
    │ direct_     │  │ reverberation│  │ early_       │
    │ sound()     │  │ _time()      │  │ reflections()│
    │             │  │              │  │              │
    │ • Distance  │  │ Sabine:      │  │ • Reflection│
    │   (m)       │  │ RT60=0.161*V │  │   points    │
    │ • Delay     │  │      /A      │  │ • Distance  │
    │   (s)       │  │              │  │ • Delay     │
    │ • Amplitude │  │ • Volume (m³)│  │ • Amplitude │
    │   factor    │  │ • Absorption │  │   factor    │
    └─────────────┘  └──────────────┘  └──────────────┘
             │               │                │
             └───────┬───────┴────────┬───────┘
                     │                │
                     ▼                ▼
            ┌──────────────────────────────┐
            │  Aggregate Results Dict:     │
            │                              │
            │  • direct_sound {}           │
            │  • reverberation_time        │
            │  • early_reflections []      │
            │  • room_characteristics {}   │
            └────────────┬─────────────────┘
                         │
            ┌────────────▼─────────────┐
            │ Display Results:         │
            │                          │
            │ • Metrics (distance,    │
            │   delay, RT60)          │
            │ • Reflection table       │
            │ • Room info cards        │
            └──────────────────────────┘
```

## Class Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                    AudioAnalyzer                         │
├─────────────────────────────────────────────────────────┤
│ Attributes:                                             │
│  - sr: int (sample rate)                                │
│  - chunk_size: int                                      │
│                                                          │
│ Methods:                                                │
│  + analyze_file(path) -> (freq, db)                    │
│  + get_frequency_response_curve(path, smooth) -> tuple │
│  + _smooth_array(arr, window) -> arr [static]          │
│  + normalize_response(db_vals) -> arr [static]         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  DeviceEqualizer                        │
├─────────────────────────────────────────────────────────┤
│ Attributes:                                             │
│  - analyzer: AudioAnalyzer                              │
│  - source_profile: dict                                 │
│  - target_profile: dict                                 │
│  - eq_curve: np.ndarray                                 │
│                                                          │
│ Methods:                                                │
│  + load_device_profile(path, name) -> dict             │
│  + set_source_device(path, name) -> None               │
│  + set_target_device(path, name) -> None               │
│  + calculate_eq_curve() -> np.ndarray                  │
│  + get_eq_curve() -> np.ndarray                        │
│  + apply_eq_to_audio(signal, sr) -> signal            │
│  + get_device_comparison() -> dict                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              RoomSimulator                              │
├─────────────────────────────────────────────────────────┤
│ Attributes:                                             │
│  - dimensions: RoomDimensions                           │
│  - materials: dict                                      │
│  - speaker_pos: Vector3D                                │
│  - listener_pos: Vector3D                               │
│  - speed_of_sound: float = 343 m/s                      │
│                                                          │
│ Methods:                                                │
│  + set_materials(materials) -> None                     │
│  + set_speaker_position(pos) -> None                    │
│  + set_listener_position(pos) -> None                   │
│  + calculate_direct_sound() -> dict                     │
│  + calculate_reverberation_time(volume) -> float        │
│  + calculate_early_reflections(max) -> list             │
│  + simulate_frequency_response() -> dict                │
│  + get_room_config() -> dict                            │
│  - _validate_position(pos) -> None                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 Supporting Classes                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  RoomDimensions:                                        │
│    - length: float, width: float, height: float        │
│                                                          │
│  Vector3D:                                              │
│    - x: float, y: float, z: float                       │
│    + distance_to(other) -> float                        │
│                                                          │
│  Material:                                              │
│    + get_absorption(material, freq_range) -> float     │
│                                                          │
│  ConfigManager:                                         │
│    + get(key, default) -> Any                           │
│    + set(key, value) -> None                            │
│    + save_config() -> None                              │
│    + add_device(name, profile) -> None                  │
│    + get_device(name) -> dict                           │
│    + list_devices() -> list                             │
└─────────────────────────────────────────────────────────┘
```

## File Organization

```
AudioEmm/
│
├── Root Level
│   ├── README.md                    [Project overview]
│   ├── QUICK_START.md               [5-min getting started]
│   ├── PROJECT_RESTRUCTURE.md       [Architecture guide]
│   ├── RESTRUCTURE_SUMMARY.md       [This summary]
│   ├── requirements.txt             [Dependencies]
│   └── LICENSE
│
└── code/
    ├── main_app.py                  [ENTRY POINT]
    │   └── imports: lib.ui_manager.run_app()
    │
    ├── config/
    │   └── config.json              [Configuration]
    │
    └── lib/
        ├── __init__.py              [Module exports]
        ├── ui_manager.py            [Streamlit UI]
        │
        ├── audio/                   [Audio Module]
        │   ├── __init__.py
        │   └── analyzer.py
        │       └── AudioAnalyzer class
        │
        ├── equalizer/               [Equalizer Module]
        │   ├── __init__.py
        │   └── device_equalizer.py
        │       └── DeviceEqualizer class
        │
        ├── room_simulator/          [Simulator Module]
        │   ├── __init__.py
        │   └── simulator.py
        │       ├── RoomSimulator class
        │       ├── RoomDimensions class
        │       ├── Vector3D class
        │       └── Material class
        │
        └── utils/                   [Utils Module]
            ├── __init__.py
            └── config.py
                └── ConfigManager class
```
