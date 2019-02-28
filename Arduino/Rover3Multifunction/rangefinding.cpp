#include <Arduino.h>

// Ultrasonic Range Finder (forward-facing)
#define MAXSONAR_ACTIVE_PIN  43
#define MAXSONAR_PWM_PIN     45

// Infrared range sensor (rear-facing)
#define IR_RANGE_PIN         15

void setupRangefinding() {
  pinMode(MAXSONAR_PWM_PIN, INPUT);
  pinMode(MAXSONAR_ACTIVE_PIN, OUTPUT);
  digitalWrite(MAXSONAR_ACTIVE_PIN, HIGH);
}

// Returns the forward range
long forward_rangefind() {
  long pulse = pulseIn(MAXSONAR_PWM_PIN, HIGH);

  // 58uS per cm (MB12XX series)
  long forward_range = pulse / 58;

  return forward_range; // TODO act on this information... slow down etc

}

// Returns the backwards range
long backwards_rangefind() {
  long ir_sensor_value = analogRead(IR_RANGE_PIN);
  return 10650.08 * pow(ir_sensor_value,-0.935) - 10;
}
