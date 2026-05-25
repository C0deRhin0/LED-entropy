# LED-Entropy

> A hardware true random number generator inspired by [Cloudflare's LavaRand](https://blog.cloudflare.com/randomness-101-lavarand-in-production/) — using chaotic LED patterns, analog hardware noise, and optical capture to extract unpredictable entropy from physical phenomena.

## Overview

This project builds a complete physical entropy source — from breadboard LEDs to cryptographic seed output. Unlike software pseudo-random number generators (PRNGs) which are deterministic, this system derives randomness from fundamentally unpredictable physical processes: thermal noise in semiconductors, environmental light fluctuations, and chaotic LED fading patterns captured by a camera.

**The full pipeline:**

1. **Arduino Uno** drives 5 LEDs in chaotic, non-repeating fade patterns
2. **Hardware noise sources** (capacitor, transistor, floating pin) inject real analog unpredictability
3. **LDR (photoresistor)** brings environmental light into the randomness
4. **Raspberry Pi camera** captures the visual chaos at 30+ fps
5. **Python/OpenCV** extracts differential frame data
6. **SHA-256 hashing** converts raw entropy into cryptographic-quality seed material

## Repository Structure

```
codebase/
├── LEDentropy.ino              # Final hardware entropy source code
├── baseline_led.ino             # Sequential LED test
├── camera_capture_engine.py     # Python camera frame capture
├── entropy_core.py              # Entropy extraction algorithm
├── requirements.txt             # Python dependencies
├── docs/
│   ├── wiring_diagram.md              # 5-LED breadboard schematic
│   ├── hardware_assembly_checklist.md # Physical assembly checklist
│   ├── hardware_noise_wiring.md       # Capacitor + LDR + transistor circuits
│   ├── pi_setup_walkthrough.md        # Raspberry Pi and camera setup
│   ├── entropy_analysis.md            # Serial monitor logs and entropy quality
│   └── entropy_distillation_algorithm.md # Algorithmic entropy distillation
├── assets/                      # Proof photos (add your own)
├── CONTRIBUTING.md              # How to contribute
├── LICENSE                      # MIT License
└── README.md
```

## Hardware Requirements

| Component | Specification | Qty | Purpose |
|-----------|---------------|-----|---------|
| Arduino Uno | Rev3 or compatible | 1 | Control LEDs, read analog noise |
| LED | Standard 5mm (any color) | 5 | Visual entropy source |
| Resistor | 220Ω | 5 | Current limiting for LEDs |
| Resistor | 10kΩ | 1 | LDR voltage divider |
| Capacitor | 100µF 25V polarized | 1 | Analog noise generation |
| Transistor | 2N2222A NPN | 1 | Thermal white noise source |
| Photoresistor (LDR) | Standard CdS | 1 | Environmental light sensing |
| Breadboard | 830-point | 1 | Prototyping platform |
| Jumper wires | Male-to-male | ~20 | Connections |
| Raspberry Pi | 3B+ or newer | 1 | Run extraction software |
| Pi Camera | Module v2 or HQ | 1 | Capture LED array |

## Build Guide

### 1. Core Hardware Setup — Breadboard Array
**Goal:** Build and verify the 5-LED breadboard array.

| Step | Task | Key Output |
|------|------|------------|
| 1 | Physical fabrication — place LEDs, resistors, wiring | Breadboard assembly |
| 2 | Upload `baseline_led.ino` | Sequential LED test |

➡️ [Wiring Diagram](docs/wiring_diagram.md) | [Assembly Checklist](docs/hardware_assembly_checklist.md)

### 2. Hardware Noise Integration
**Goal:** Inject analog noise into the LED system for true unpredictability.

| Step | Task | Key Output |
|------|------|------------|
| 1 | Capacitor on A0 + transistor noise on A2 | Analog noise sources |
| 2 | LDR voltage divider on A1 | Environmental sensing |
| 3 | Chaotic PWM fading with combined noise | Upload `LEDentropy.ino` |

➡️ [Noise Wiring Guide](docs/hardware_noise_wiring.md) | [Entropy Analysis](docs/entropy_analysis.md)

### 3. Camera & Optical Capture
**Goal:** Mount the camera and establish a live frame pipeline.

| Step | Task | Key Output |
|------|------|------------|
| 1 | Pi setup, Python venv, dependencies | `requirements.txt` |
| 2 | Frame capture with `cv2.VideoCapture` | `camera_capture_engine.py` |

➡️ [Pi Setup Walkthrough](docs/pi_setup_walkthrough.md)

### 4. Entropy Distillation
**Goal:** Convert video frames into cryptographic-quality random numbers.

| Step | Task | Key Output |
|------|------|------------|
| 1 | Frame differencing with `cv2.absdiff` | Pixel change vectors |
| 2 | Bitstream assembly and uniformity testing | Raw entropy blocks |
| 3 | SHA-256 hashing + console output | `entropy_core.py` |

➡️ [Distillation Algorithm Guide](docs/entropy_distillation_algorithm.md)

## Quick Start

### 1. Upload the Baseline Test

```bash
# Open Arduino IDE, upload baseline_led.ino
# Verify all 5 LEDs cycle on/off in sequence
```

### 2. Build the Full Entropy System

```bash
# Add capacitor, LDR, and transistor per the wiring guide
# Upload LEDentropy.ino
# Open Serial Monitor (9600 baud) to see entropy values
```

### 3. Set Up the Camera Pi

```bash
# Follow pi_setup_walkthrough.md
cd codebase/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python camera_capture_engine.py
```

### 4. Extract Entropy

```bash
python entropy_core.py --input capture.mp4 --output entropy_seed.txt
```

## Entropy Sources

This project combines four independent sources of randomness:

| Source | Physical Principle | Analog Pin |
|--------|-------------------|------------|
| Floating pin | Electromagnetic interference pickup | A0 (no capacitor) |
| Capacitor | Charge/discharge analog drift | A0 (with 100µF) |
| Transistor (2N2222A) | Thermal noise in reverse-biased junction | A2 |
| Photoresistor (LDR) | Environmental light fluctuations | A1 |
| LED array | Chaotic PWM fading patterns | 3, 5, 6, 9, 10 |

## Key Design Principles

### Non-Blocking Timing
The Arduino sketch never uses `delay()`. All timing uses `millis()`-style patterns and hardware-noise-modulated micro-delays to keep the main loop cycling at maximum speed.

### Hardware Noise Seeding
`randomSeed()` is called **once** during `setup()` using combined analog reads from the capacitor and transistor pins. Repeated seeding in the main loop would destroy statistical distribution.

### Grayscale Optimization
All camera frames are converted to grayscale immediately on capture. Color channels carry no entropy weight and only consume processing overhead.

### Vectorized Frame Differencing
Frame comparison uses `cv2.absdiff()` on NumPy arrays — never nested Python loops over pixels.

## Project Status

| Section | Status |
|---------|--------|
| Core Hardware — Breadboard Array | ✅ Complete |
| Hardware Noise Integration | ✅ Complete |
| Camera & Optical Capture | ✅ Complete |
| Entropy Distillation | ✅ Complete |

## References

- [Cloudflare LavaRand Blog Post](https://blog.cloudflare.com/randomness-101-lavarand-in-production/)
- [Arduino PWM Documentation](https://www.arduino.cc/reference/en/language/functions/analog-io/analogwrite/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [NIST SP 800-90B](https://csrc.nist.gov/publications/detail/sp/800-90b/final) — Recommendation for Entropy Sources

## License

MIT License — see [LICENSE](LICENSE).

---

*Built with curiosity. Inspired by thermodynamics.*
