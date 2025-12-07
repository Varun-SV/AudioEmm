# AudioEmm
**Emulate any audio device's sound and simulate room acoustics**

## 🎵 Overview

AudioEmm is a sophisticated audio emulation and room acoustic simulation platform. It lets you experience how different audio devices would sound without buying them, and understand how your room affects audio playback.

### Two Core Features:

#### 1. 🎧 **Device Equalizer**
Transform your current audio device to sound like any other device.

**The Problem:** You want to know if that $500 headphone sounds worth it before buying. You have your current device and want to know how Device B would sound.

**The Solution:** AudioEmm analyzes the frequency response of both devices and creates a custom equalizer curve that makes your device sound like the target device.

**How it works:**
- Upload reference audio recordings from both your source device and target device
- AudioEmm performs FFT analysis on both recordings
- Calculates the frequency response difference
- Generates an EQ curve showing exactly which frequencies to boost or cut
- Apply the equalization and hear how Device B would sound

#### 2. 🏠 **Room Acoustic Simulator**
Understand how your room's dimensions and materials affect sound.

**The Problem:** A speaker sounds different in different rooms. How would my speaker sound in my new listening room?

**The Solution:** AudioEmm simulates sound propagation in your designed room space.

**Features:**
- Define room dimensions (length, width, height)
- Select materials for floor, walls, and ceiling
- Place speaker and listener positions anywhere in the room
- Calculates:
  - Direct sound path and delay
  - Early reflections from room surfaces
  - Reverberation time (RT60) using Sabine formula
  - Sound pressure changes due to distance (inverse square law)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Streamlit
- NumPy
- Librosa
- Matplotlib
- Sounddevice (optional, for frequency sweep testing)

### Installation

1. Clone the repository
```bash
git clone https://github.com/Varun-SV/AudioEmm.git
cd AudioEmm
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
streamlit run code/main_app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📁 Project Structure

```
code/
├── main_app.py                 # Entry point
├── config/
│   └── config.json            # Configuration file
├── lib/
│   ├── ui_manager.py          # Streamlit UI management
│   ├── audio/
│   │   ├── __init__.py
│   │   └── analyzer.py        # Audio analysis & frequency extraction
│   ├── equalizer/
│   │   ├── __init__.py
│   │   └── device_equalizer.py # EQ curve calculation
│   ├── room_simulator/
│   │   ├── __init__.py
│   │   └── simulator.py       # Room acoustic simulation
│   └── utils/
│       ├── __init__.py
│       └── config.py          # Configuration management
```

## 🔬 Technical Details

### Audio Analysis
- **FFT Analysis:** Uses Fast Fourier Transform to decompose audio into frequency components
- **Windowing:** Applies Hann window to reduce spectral leakage
- **Normalization:** Normalizes frequency responses for fair comparison
- **Averaging:** Averages frequency responses across the audio duration for stability

### Equalization
- **Frequency Response Difference:** Calculates target_dB - source_dB at each frequency
- **Linear Interpolation:** Ensures EQ curve matches frequency bins of audio playback
- **dB to Linear Conversion:** Converts EQ curve from dB to linear gains
- **Phase Preservation:** Uses magnitude-only approach to preserve audio phase

### Room Acoustics
- **Sabine Formula:** RT60 = 0.161 × V / A
  - V = room volume (m³)
  - A = total absorption (m²)
- **Inverse Square Law:** Sound amplitude decreases with distance squared
- **Material Absorption:** Pre-defined absorption coefficients for common materials at different frequency ranges
- **Early Reflections:** Traces sound paths to first-order reflections from room surfaces

## 📊 Usage Examples

### Device Equalizer Example
1. Select "Device Equalizer" from sidebar
2. Upload a recording from your current headphone (e.g., Sony WH-1000XM4)
3. Upload the same audio from your target headphone (e.g., Apple AirPods Pro)
4. Click "Analyze & Calculate Equalizer"
5. Review the frequency response comparison chart
6. Examine the EQ curve showing required adjustments
7. Apply the EQ to your audio player

### Room Simulator Example
1. Select "Room Simulator" from sidebar
2. Set your room dimensions (e.g., 6m × 4m × 3m)
3. Choose materials (hardwood floor, drywall walls, drywall ceiling)
4. Place speaker at one corner and listener at 2m distance
5. Click "Simulate Room Acoustics"
6. Review RT60, direct sound delay, and early reflections
7. Adjust speaker/listener position and materials to optimize acoustics

## 💡 Tips for Best Results

### Device Equalizer
- Use **lossless audio formats** (FLAC, WAV) for accurate analysis
- Use **the same song** for both source and target recordings
- Record in **quiet environments** to minimize noise
- Ensure **good microphone placement** when recording reference audio
- Test EQ with various music genres to ensure natural sound

### Room Simulator
- **Measure dimensions** accurately (use laser measure if possible)
- **Identify actual materials** in your room (carpet, hardwood, tile, etc.)
- Consider **furniture placement** - use closest matching material type
- **Sweet spot** for listening is typically 1-3 meters from speaker
- Experiment with **multiple positions** to find optimal sound

## 🔧 Configuration

Edit `code/config/config.json` to customize:
- Default room dimensions
- Available audio devices
- Audio analysis parameters (sample rate, chunk size)
- Room material definitions

## 📈 Future Enhancements

- [ ] Real-time audio playback with EQ applied
- [ ] Multi-device comparison (3+ devices)
- [ ] Advanced room models (diffusion, absorption by frequency)
- [ ] Audio file upload and EQ preview
- [ ] Export EQ settings for use in DAWs/players
- [ ] Frequency sweep testing for device profiling
- [ ] Room impulse response modeling
- [ ] Listening position optimization algorithm

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**AudioEmm** - Making Audio Science Accessible
