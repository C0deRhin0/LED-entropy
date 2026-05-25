// ------------------------------
// Hardware Entropy LEDs
// LDR + Capacitor + Transistor Noise
// ------------------------------
// Upload this to Arduino Uno after completing the noise source wiring.
// Open Serial Monitor at 9600 baud to observe entropy sources.
//
// Pin Map:
//   LEDs:     3, 5, 6, 9, 10  (PWM)
//   A0:       100uF capacitor noise
//   A1:       LDR + 10k resistor (voltage divider)
//   A2:       2N2222A transistor thermal noise

int leds[] = {3, 5, 6, 9, 10};
int numLeds = 5;

int ldrPin = A1;          // LDR environmental sensor
int noisePin = A0;        // Capacitor / floating pin for hardware noise
int transistorPin = A2;   // 2N2222A transistor noise

void setup() {
  // Initialize LED pins as outputs
  for (int i = 0; i < numLeds; i++) {
    pinMode(leds[i], OUTPUT);
  }

  // Serial for monitoring entropy sources
  Serial.begin(9600);

  // Seed Arduino random with combined hardware noise.
  // Called ONCE — repeated seeding destroys statistical distribution.
  int seed = analogRead(noisePin) + analogRead(transistorPin);
  randomSeed(seed);
}

void loop() {
  // -------------------------------------------------------
  // 1. Read LDR — environmental entropy
  // -------------------------------------------------------
  int ldrValue = analogRead(ldrPin);                     // 0-1023
  int sensorBrightness = map(ldrValue, 0, 1023, 0, 255); // scale to 0-255

  Serial.print("LDR: ");
  Serial.print(ldrValue);

  // -------------------------------------------------------
  // 2. Read hardware noise sources
  // -------------------------------------------------------
  int capNoise = analogRead(noisePin) % 256;
  int transistorNoise = analogRead(transistorPin) % 256;
  int combinedNoise = (capNoise + transistorNoise) / 2;

  Serial.print(" | CapNoise: ");
  Serial.print(capNoise);
  Serial.print(" | TransistorNoise: ");
  Serial.println(transistorNoise);

  // -------------------------------------------------------
  // 3. Combine LDR + hardware noise for final brightness
  // -------------------------------------------------------
  int finalBrightness = (sensorBrightness + combinedNoise) / 2;

  // -------------------------------------------------------
  // 4. Update 2-3 random LEDs with chaotic fading
  // -------------------------------------------------------
  int updates = random(2, 4);
  for (int u = 0; u < updates; u++) {
    int ledIndex = random(0, numLeds);

    // Smooth fade to final brightness
    int currentVal = analogRead(noisePin) % 10; // random starting point
    int stepDir = (currentVal < finalBrightness) ? 5 : -5;

    while (
      (stepDir > 0 && currentVal < finalBrightness) ||
      (stepDir < 0 && currentVal > finalBrightness)
    ) {
      // Scale brightness with LDR for direct sensitivity
      int adjustedBrightness = (currentVal * sensorBrightness) / 255;
      analogWrite(leds[ledIndex], adjustedBrightness);

      // Random delay from combined hardware noise
      int smallNoise =
          (analogRead(noisePin) + analogRead(transistorPin)) % 5 + 1;
      delay(smallNoise);

      currentVal += stepDir;

      // Clamp to valid PWM range
      if (currentVal > 255) currentVal = 255;
      if (currentVal < 0) currentVal = 0;
    }

    // 20% chance for random brightness "pop"
    if (random(0, 10) < 2) {
      int popBrightness = (random(0, 255) * sensorBrightness) / 255;
      analogWrite(leds[ledIndex], popBrightness);
    }
  }
}
