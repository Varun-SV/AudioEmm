# AudioEmm Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
cd code
streamlit run main_app.py
```

The app opens automatically at `http://localhost:8501`

---

## 🎧 Using Device Equalizer

### What it does:
Makes headphone/speaker A sound like headphone/speaker B

### How to use:
1. **Click** "Device Equalizer" in the sidebar
2. **Upload** an audio file recorded through **YOUR device** (Source)
3. **Upload** the **SAME audio** recorded through the **TARGET device**
4. **Give names** to both (e.g., "My Sony Headphones", "Apple AirPods Pro")
5. **Click** "Analyze & Calculate Equalizer"
6. **Review** the EQ curve showing what frequencies to boost/cut

### Pro Tips:
- Use high-quality audio files (WAV or FLAC best)
- Use the exact same song for both recordings
- Record in quiet rooms
- The positive values = boost those frequencies
- The negative values = cut those frequencies

### Example:
Want your $100 headphones to sound like $500 headphones?
1. Record same song on $100 headphones
2. Record same song on $500 headphones
3. Upload both
4. AudioEmm shows you what EQ adjustments to apply!

---

## 🏠 Using Room Simulator

### What it does:
Shows how your room affects sound based on dimensions and materials

### How to use:
1. **Click** "Room Simulator" in the sidebar
2. **Set room dimensions:**
   - Length: how far the room is (m)
   - Width: how wide the room is (m)
   - Height: ceiling height (m)
3. **Choose materials:**
   - Floor: hardwood, carpet, concrete
   - Walls: drywall, carpet, curtain, concrete, glass
   - Ceiling: drywall, carpet, concrete
4. **Place speaker and listener:**
   - Speaker: where your speaker is in the room
   - Listener: where you sit/stand to listen
5. **Click** "Simulate Room Acoustics"
6. **View results:**
   - RT60: How long sound takes to become quiet (lower = better for most use cases)
   - Distance: Direct path from speaker to listener
   - Reflections: Sound bouncing off room surfaces

### Pro Tips:
- Measure your room accurately (use laser measure if possible)
- Match materials to what's actually in your room
- Listen sweet spot is 1-3 meters from speaker
- More absorption (carpet, curtains) = shorter RT60 = less reverberation
- Hard surfaces (glass, concrete) = longer RT60 = more reverberation

### Example:
Your living room is 6m × 5m × 3m with hardwood floor and drywall walls:
1. Set dimensions: 6m × 5m × 3m
2. Select: hardwood floor, drywall walls, drywall ceiling
3. Place speaker at corner (0.5, 0.5, 1)
4. Place listener at listening position (2, 2, 1.2)
5. See how RT60 ≈ 0.4 seconds (good for music)

If it's too reverberant:
- Add carpet (absorbs sound)
- Add curtains (absorbs high frequencies)
- Re-simulate to see improvement

---

## 📊 Understanding the Results

### Device Equalizer Results:

**Frequency Response Graph:**
- Blue line = Your device
- Orange line = Target device
- Where they differ = frequency-dependent differences

**EQ Curve Graph:**
- Green line = Adjustments needed
- Above zero = Boost those frequencies
- Below zero = Cut those frequencies
- The amount = how much boost/cut in dB

### Room Simulator Results:

**Key Metrics:**
- **Direct Sound Distance (m):** Straight line from speaker to you
- **Direct Sound Delay (ms):** How long sound takes to reach you
- **RT60 (seconds):** Time for sound to become inaudible (60 dB quieter)
- **Room Volume (m³):** Total cubic meters in your room

**Early Reflections Table:**
- Reflection #: Which bounce (1st, 2nd, etc.)
- Distance (m): Total path length (speaker → wall → listener)
- Delay (ms): How long after direct sound
- Amplitude Factor: How loud vs. direct sound

---

## 🔧 Customizing Configuration

Edit `code/config/config.json` to:

### Add New Devices:
```json
"audio_devices": {
    "my_device": {
        "name": "My Device Name",
        "frequencies": [],
        "db_values": []
    }
}
```

### Change Default Room Settings:
```json
"room_settings": {
    "dimensions": {"length": 6, "width": 5, "height": 3}
}
```

### Adjust Audio Analysis:
```json
"audio_analyzer": {
    "sample_rate": 44100,
    "chunk_size": 1024
}
```

---

## 📝 Best Practices

### For Best Device Equalizer Results:
1. ✅ Use lossless audio (WAV, FLAC)
2. ✅ Record same song through both devices
3. ✅ Keep microphone at same position
4. ✅ Record in same quiet environment
5. ✅ Use natural-sounding reference tracks
6. ❌ Don't use heavily compressed audio
7. ❌ Don't change settings between recordings

### For Best Room Simulator Results:
1. ✅ Measure room dimensions accurately
2. ✅ Identify actual materials in room
3. ✅ Account for furniture placement
4. ✅ Use realistic listening position
5. ✅ Consider objects on shelves as absorption
6. ❌ Don't ignore furniture and objects
7. ❌ Don't assume all walls are the same

---

## ❓ FAQ

**Q: How accurate is the Device Equalizer?**
A: It's as accurate as your audio recordings. Use high-quality source material and same recording conditions.

**Q: Can I use Spotify/YouTube audio?**
A: Yes, but results will be less accurate due to compression. Lossless formats are preferred.

**Q: What RT60 is "good"?**
A: Depends on room use:
- Speech: 0.3-0.5 seconds
- Music: 0.4-0.8 seconds
- Concert hall: 1.5-2.0 seconds

**Q: Why is my EQ curve weird?**
A: Possible reasons:
- Poor audio recordings
- Different source material
- Noise in recordings
- One device has strong coloration

**Q: How do I apply the EQ to my music player?**
A: Audio players like Foobar2000, VLC, or Equalizer APO can use custom EQ curves.

**Q: Can I simulate a different room after running simulation?**
A: Yes! Just adjust sliders and click "Simulate" again.

**Q: Is the room simulation perfectly accurate?**
A: No, it's an approximation. Real rooms have complex interactions not captured here (diffusion, edge effects, etc.).

---

## 🆘 Need Help?

1. Check the **About** page in the app for detailed explanations
2. Read `README.md` for technical details
3. Review `PROJECT_RESTRUCTURE.md` for architecture overview
4. Check error messages carefully (they usually indicate the issue)

---

**Happy audio exploring! 🎵**
