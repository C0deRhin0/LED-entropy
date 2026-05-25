# Entropy Analysis — Serial Monitor Logs & Quality Assessment

## Overview

This document explains how to interpret the serial output from `LEDentropy.ino`, assess entropy quality, and log data for analysis. The Arduino outputs three noise source values per loop iteration, giving you real-time visibility into the hardware entropy generation.

## Serial Monitor Output Format

With `LEDentropy.ino` running, open the Serial Monitor (9600 baud). You will see lines like:

```
LDR: 742 | CapNoise: 134 | TransistorNoise: 207
LDR: 738 | CapNoise: 142 | TransistorNoise: 195
LDR: 751 | CapNoise: 128 | TransistorNoise: 211
```

### Field Description

| Field | Range | Source | Entropy Contribution |
|-------|-------|--------|----------------------|
| `LDR` | 0-1023 | Photoresistor on A1 | Environmental light fluctuations |
| `CapNoise` | 0-255 | Capacitor on A0 (modulo 256) | Electrical charge/discharge drift |
| `TransistorNoise` | 0-255 | 2N2222A on A2 (modulo 256) | Thermal white noise |

## Capturing Log Data

### Method 1: Arduino Serial Monitor

1. Open Serial Monitor (Tools  Serial Monitor, or Ctrl+Shift+M)
2. Set baud rate to **9600**
3. Select "Both NL & CR" line ending
4. Copy output and paste into a file

### Method 2: Command-Line Capture (Recommended)

```bash
# On Linux / macOS
cat /dev/cu.usbmodem* > entropy_log.csv &
# Or use screen
screen /dev/cu.usbmodem14201 9600
# Capture session output to a file (Ctrl+A, then H)
```

### Method 3: Arduino CLI Capture

```bash
arduino-cli monitor -p /dev/cu.usbmodem* -b arduino:avr:uno --config 9600 > capacitor_noise_log.csv
```

## Log Format for Analysis

Save captures as CSV files with this recommended format:

```csv
Timestamp,LDR,CapNoise,TransistorNoise
0,742,134,207
104,738,142,195
208,751,128,211
...
```

## Entropy Quality Indicators

### 1. Visual Inspection

- **Good entropy:** Values that appear random with no obvious pattern
- **Bad entropy:** Repeated sequences, stair-step patterns, or stuck values

### 2. Statistical Metrics

Run a basic Python check on your captured logs:

```python
import numpy as np

# Load CSV (timestamp, ldr, cap, transistor)
data = np.loadtxt('capacitor_noise_log.csv', delimiter=',', skiprows=1)
ldr = data[:, 1]
cap = data[:, 2]
transistor = data[:, 3]

# Basic statistics
for name, values in [('LDR', ldr), ('CapNoise', cap), ('Transistor', transistor)]:
    print(f"{name}:")
    print(f"  Mean: {values.mean():.1f}")
    print(f"  Std:  {values.std():.1f}")
    print(f"  Min:  {values.min()}")
    print(f"  Max:  {values.max()}")
    print(f"  Unique: {len(np.unique(values))} / {len(values)} samples")
```

### 3. Frequency Distribution

Plot a histogram to check for uniform distribution:

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))
for i, (name, values) in enumerate([('LDR', ldr), ('CapNoise', cap), ('Transistor', transistor)]):
    plt.subplot(1, 3, i+1)
    plt.hist(values, bins=50)
    plt.title(name)
plt.tight_layout()
plt.show()
```

- **Good:** Relatively flat distribution across the full range
- **Bad:** Clustered in one region (suggests bias or insufficient noise)

### 4. Autocorrelation Test

Low autocorrelation is a sign of good entropy:

```python
def autocorrelation(x, lag=1):
    return np.corrcoef(x[:-lag], x[lag:])[0, 1]

for name, values in [('LDR', ldr), ('CapNoise', cap), ('Transistor', transistor)]:
    ac = autocorrelation(values, lag=1)
    print(f"{name} autocorrelation (lag=1): {ac:.4f}")
```

- **Good:** |autocorrelation| < 0.1
- **Acceptable:** |autocorrelation| < 0.3
- **Poor:** |autocorrelation| > 0.3 (values are too predictable)

## Expected Entropy Quality by Configuration

| Configuration | Entropy Level | Autocorrelation | Uniformity |
|---------------|---------------|-----------------|------------|
| Floating A0 only | Low | ~0.3-0.5 | Poor |
| A0 + Capacitor | Medium | ~0.1-0.3 | Moderate |
| A0 + A1 (LDR) | Medium-High | ~0.05-0.2 | Good |
| A0 + A1 + A2 (full) | High | < 0.1 | Good |

## Reference Files

Sample logs from the development process are stored in:

- `/assets/capacitor_noise_log.csv` — capacitor + transistor validation log

## What Good Entropy Looks Like

```
# Example of high-quality capture:
LDR: 523 | CapNoise: 187 | TransistorNoise: 42
LDR: 498 | CapNoise: 55  | TransistorNoise: 199
LDR: 612 | CapNoise: 223 | TransistorNoise: 88
LDR: 455 | CapNoise: 12  | TransistorNoise: 167
LDR: 701 | CapNoise: 145 | TransistorNoise: 31
```

Notice: no two lines look alike, values span the full range, and there is no visible upward/downward trend.

## Troubleshooting Poor Entropy

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| Values stuck near 0 or 1023 | Circuit not connected properly | Check wiring per hardware_noise_wiring.md |
| Clear repeating pattern every N lines | Random seed not set or reset each loop | Verify randomSeed() is called once in setup() only |
| LDR values change only when touched | LDR is in too-bright or too-dark location | Adjust room lighting or reposition LDR |
| All three sources correlate perfectly | Pins shorted on breadboard | Check for accidental solder bridges or misplaced jumpers |
| Transistor noise always 0 | Transistor pinout wrong | Verify Collector  A2, Emitter  GND |
