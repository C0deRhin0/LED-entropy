# Raspberry Pi & Camera Setup Walkthrough

## Overview

This guide introduces the optical capture layer. A Raspberry Pi with a camera module is positioned to observe the chaotic LED array. The Pi runs a Python script that captures grayscale frames at 30 fps, preparing the visual data for entropy extraction.

## Hardware Requirements

| Component | Specification | Purpose |
|-----------|---------------|---------|
| Raspberry Pi | 3B+ or newer (Pi 4/5 recommended) | Runs capture and extraction software |
| Pi Camera | Module v2 or HQ | Capture LED array at high fps |
| Ribbon cable | 15-pin CSI | Connect camera to Pi |
| MicroSD card | 32GB+ (Class 10) | OS and storage |
| Power supply | 5V 3A USB-C (Pi 4/5) or microUSB (Pi 3) |
| Enclosure | Any box with opening | Shroud to control ambient light |

## Step-by-Step Setup

### Day 1: Embedded PC Preparation

#### 1. Install Raspberry Pi OS

```bash
# Download and flash Raspberry Pi OS Lite (64-bit recommended)
# Using Raspberry Pi Imager or balenaEtcher
# Enable SSH during flashing:
#   - Set hostname: led-entropy-pi
#   - Enable SSH with password auth or key
#   - Configure Wi-Fi credentials
```

Boot the Pi and verify network connectivity:

```bash
ssh pi@led-entropy-pi.local
# Default password: raspberry
sudo apt update && sudo apt upgrade -y
```

#### 2. Enable the Camera Interface

```bash
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
# Reboot: sudo reboot
```

On newer Pi OS versions using the libcamera stack:

```bash
# Verify camera detection
libcamera-hello --timeout 5000
# You should see a 5-second camera preview
```

#### 3. Mount the Camera

Physical mounting tips for entropy capture:

1. **Position the camera 15-20 cm from the LED array**
2. **Use a tripod or adjustable arm** for stable positioning
3. **Enclose the setup** in a box or shroud to control ambient light
4. **Aim directly at the center of the LED cluster** for maximum coverage
5. **Consider adding a diffuser** (thin white paper or translucent plastic) between LEDs and camera for smoother light patterns

**Desired physical arrangement:**
```
          [Shroud / Box]
    LEDs  ------------  Camera
    [██]               [📷]
      \               /
       \  15-20 cm  /
        ───────────
    [Arduino Uno]    [Raspberry Pi]
```

#### 4. Create Python Virtual Environment

```bash
# SSH into the Pi
ssh pi@led-entropy-pi.local

# Create project directory
mkdir -p ~/led-entropy && cd ~/led-entropy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### 5. Install Dependencies

From within the virtual environment:

```bash
pip install opencv-python numpy
```

Verify installation:

```bash
python -c "import cv2; print(f'OpenCV {cv2.__version__}')"
python -c "import numpy; print(f'NumPy {numpy.__version__}')"
```

Expected output:
```
OpenCV 4.9.0
NumPy 1.26.0
```

#### 6. Transfer Files to the Pi

```bash
# From your development machine
scp camera_capture_engine.py pi@led-entropy-pi.local:~/led-entropy/
scp requirements.txt pi@led-entropy-pi.local:~/led-entropy/
```

---

### Day 2: Live Frame Capture

#### 1. Initial Camera Test

Create a quick validation script:

```python
# test_camera.py
import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Could not open camera")
    exit(1)

ret, frame = cap.read()
if ret:
    cv2.imwrite("test_frame.png", frame)
    print(f"Captured test frame: {frame.shape}")
else:
    print("ERROR: Could not read frame")

cap.release()
```

Run it:

```bash
python test_camera.py
# Expected: Captured test frame: (480, 640, 3)
```

#### 2. Run the Capture Engine

```bash
python camera_capture_engine.py
```

This will:
- Open the camera at 640x480 resolution
- Capture frames at ~30 fps
- Convert each frame to grayscale
- Save a calibration frame as `lens_calibration_proof.png`
- Display live FPS counter in terminal
- Exit cleanly on Ctrl+C

#### 3. Verify Frame Capture

Check a captured frame:

```bash
python -c "
import cv2
img = cv2.imread('lens_calibration_proof.png', cv2.IMREAD_GRAYSCALE)
print(f'Frame shape: {img.shape}')
print(f'Pixel value range: {img.min()}-{img.max()}')
print(f'Mean pixel value: {img.mean():.1f}')
"
```

**Expected output:**
```
Frame shape: (480, 640)
Pixel value range: 12-243
Mean pixel value: 127.3
```

(Values will vary based on your actual lighting and LED brightness.)

#### 4. Camera Tuning

If the image is too dark or too bright, adjust these settings in `camera_capture_engine.py`:

```python
# In the setup section, uncomment and adjust:
cap.set(cv2.CAP_PROP_EXPOSURE, -4)    # Lower = faster exposure (darker)
cap.set(cv2.CAP_PROP_GAIN, 0)         # 0 = auto, positive = fixed gain
cap.set(cv2.CAP_PROP_BRIGHTNESS, 128) # 0-255
```

**Good capture criteria:**
- LEDs are clearly visible against the background
- No motion blur (fast enough shutter)
- Frame is not overexposed (LEDs should not be pure white blobs)

##  Physical Setup Checklist

- [ ] Raspberry Pi OS installed and SSH accessible
- [ ] Camera interface enabled in raspi-config
- [ ] Camera module physically mounted and stable
- [ ] Ribbon cable securely connected (gold pins facing away from Ethernet port)
- [ ] Python virtual environment created and activated
- [ ] `opencv-python` and `numpy` installed
- [ ] Camera detects at `/dev/video0` (check with `ls /dev/video*`)
- [ ] `camera_capture_engine.py` runs without errors
- [ ] Calibration frame saved as proof
- [ ] Proof photo committed: `/assets/hardware_bridge.jpg`

## Common Issues

| Problem | Diagnosis | Fix |
|---------|-----------|-----|
| `cv2.VideoCapture` returns False | Camera not detected | Run `ls /dev/video*` to check, enable camera in raspi-config |
| Low frame rate | CPU throttling or high resolution | Reduce resolution to 320x240, close background processes |
| Overexposed frames | Gain/Exposure too high | Fix exposure with `cap.set(cv2.CAP_PROP_EXPOSURE, ...)` |
| Pi overheating | No heatsink, enclosed case | Add heatsinks, ensure ventilation |
| Permission denied to /dev/video0 | User not in video group | `sudo usermod -a -G video pi` then logout/login |

## Next Step

Proceed to the **Entropy Distillation** guide — process captured frames into cryptographic-quality random numbers.
