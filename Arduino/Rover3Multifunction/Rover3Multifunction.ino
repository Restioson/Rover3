#include "motor.h"
#include "remote.h"
#include "rangefinding.h"

#define LOGGING_BAUD         115200

void setup() {
  // Serial - USB serial console (debugging)
  Serial.begin(LOGGING_BAUD);
  while (!Serial) ;

  setupRemote();
  setupRangefinding();
  setupMotors();

  Serial.println("Rover Multifunction Start!");
}

void loop() {
  char command = readCommand();

  if (command != '\0') {
    Serial.print("Command: \"");
    Serial.print(command);
    Serial.println("\"");
  }

  int forward_distance = forward_rangefind();
  // Serial.print("Forward distance: ");
  // Serial.println(forward_distance);
}
