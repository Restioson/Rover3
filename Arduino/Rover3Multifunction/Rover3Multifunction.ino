#include "motor.h"
#include "remote.h"
#include "rangefinding.h"
#include "compass.h"
#include "command.h"

#define LOGGING_BAUD 115200

void setup() {
  // Serial - USB serial console (debugging)
  Serial.begin(LOGGING_BAUD);
  while (!Serial) ;

  setupRemote();
  setupRangefinding();
  setupCompass();
  setupMotors();

  Serial.println("Rover Multifunction Start!");
}

void loop() {
  char command = readCommand();

  long forward_distance = forward_rangefind();
  long backwards_distance = backwards_rangefind();

  if (command != '\0') {
    Serial.print("Command: \"");
    Serial.print(command);
    Serial.println("\"");

    executeCommand(command, forward_distance, backwards_distance);
  }

  CompassData compass = readCompass();
  // TODO
  Serial.print("Head: ");
  Serial.print(compass.heading);
  Serial.print(" Pitch: ");
  Serial.print(compass.pitch);
  Serial.print(" Roll: ");
  Serial.println(compass.roll);
}
