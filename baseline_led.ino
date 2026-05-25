// Baseline LED Mapping — Sequential Toggle
// Sequentially toggles each LED ON then OFF before advancing.

const int kLedPins[] = {3, 5, 6, 9, 10};
const int kLedCount = sizeof(kLedPins) / sizeof(kLedPins[0]);

// 15ms interval keeps visible sequencing without blocking.
const unsigned long kToggleIntervalMicros = 15000;
int currentLedIndex = 0;
bool ledIsOn = false;
unsigned long lastToggleMicros = 0;

void setup() {
  for (int i = 0; i < kLedCount; i++) {
    pinMode(kLedPins[i], OUTPUT);
    digitalWrite(kLedPins[i], LOW);
  }

  lastToggleMicros = micros();
}

void loop() {
  unsigned long now = micros();

  if (now - lastToggleMicros < kToggleIntervalMicros) {
    return;
  }

  lastToggleMicros = now;
  digitalWrite(kLedPins[currentLedIndex], ledIsOn ? HIGH : LOW);

  if (ledIsOn) {
    currentLedIndex = (currentLedIndex + 1) % kLedCount;
  }

  ledIsOn = !ledIsOn;
}
