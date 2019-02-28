#include <Arduino.h>

#define MAXSONAR_ACTIVE_PIN  43
#define MAXSONAR_PWM_PIN     45

bool fwd_rangefinder = true;

void setupRangefinding() {
  pinMode(MAXSONAR_PWM_PIN, INPUT);
  pinMode(MAXSONAR_ACTIVE_PIN, OUTPUT);
  digitalWrite(MAXSONAR_ACTIVE_PIN, HIGH);
}

// Returns the forward range, or -1 if disabled
int forward_rangefind() {
  if (!fwd_rangefinder) {
    return -1;
  }

  int pulse = pulseIn(MAXSONAR_PWM_PIN, HIGH);

  // 58uS per cm (MB12XX series)
  int forward_range = pulse / 58;

  return forward_range; // TODO act on this information... slow down etc

}
