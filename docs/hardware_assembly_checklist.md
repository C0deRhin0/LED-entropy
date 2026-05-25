# Physical Fabrication Checklist — Breadboard Assembly

## Mission
Initialize the physical base layer establishing the simple controllable hardware output structure.

## Hardware Assembly Tasks

### ☐ Task 1: LED Distribution
**Action:** Distribute five distinct LED diodes irregularly across the physical breadboard.

**Details:**
- Use 5mm LEDs (any color mix)
- Place irregularly — NOT in a straight line
- Irregular placement creates more visual chaos for entropy capture
- Ensure cathode (short leg) accessibility to ground rail

**Verification:** Count 5 LEDs inserted into breadboard holes.

---

### ☐ Task 2: Resistor Connection
**Action:** Connect five independent 220-ohm resistors to the positive (anode) legs of each respective LED.

**Details:**
- 220Ω resistors (color bands: Red-Red-Brown-Gold)
- Connect to the longer leg (anode/+) of each LED
- One resistor per LED — no sharing

**Verification:** Measure each resistor with multimeter (200-240Ω acceptable).

---

### ☐ Task 3: PWM Pin Wiring
**Action:** Run jumper wires linking the resistor endpoints to individual Arduino PWM output pins (3, 5, 6, 9, 10).

**Details:**
- Use male-to-male jumper wires
- Connect free end of each resistor to designated PWM pin
- Pin mapping:
  - LED 1 → Pin 3
  - LED 2 → Pin 5
  - LED 3 → Pin 6
  - LED 4 → Pin 9
  - LED 5 → Pin 10

**Verification:** Trace each wire from resistor to Arduino pin.

---

### ☐ Task 4: Ground Rail Wiring
**Action:** Wire the universal breadboard negative rail directly to the primary Arduino GND pin.

**Details:**
- Connect all LED cathodes (short leg) to the negative (blue) rail
- Run single jumper from GND rail to any Arduino GND pin
- Ensure continuity across entire ground rail

**Verification:** Use multimeter continuity mode to verify all cathodes share common ground.

---

### ☐ Task 5: Proof Photograph
**Action:** Photograph the raw physical breadboard assembly and commit the image.

**Details:**
- Capture clear, well-lit photo showing:
  - All 5 LEDs visible
  - Resistor connections visible
  - Jumper wires to Arduino pins
  - Ground rail connection
- Save as `breadboard_assembly.jpg` (or `.png`)
- Commit to `/assets/breadboard_assembly.jpg`

**Commands to commit proof:**
```bash
# Copy your photo to the assets folder, then:
cd project_primary
git add assets/breadboard_assembly.jpg
git commit -m "docs: add breadboard assembly proof photograph"
git log origin/main..main --oneline
```

---

## Deliverable Checklist

- [ ] 5 LEDs distributed irregularly on breadboard
- [ ] 5 × 220Ω resistors connected to LED anodes
- [ ] 5 jumper wires connecting resistors to PWM pins 3, 5, 6, 9, 10
- [ ] Ground rail connected to Arduino GND
- [ ] Proof photo committed to `/assets/breadboard_assembly.jpg`

## Expected Outcome
A controllable static 5-LED breadboard array driven safely by an Arduino Uno, ready for software testing in the next step.

## Next Steps
Once all tasks are complete, proceed to upload the baseline Arduino sketch (`baseline_led.ino`) to test the array.
