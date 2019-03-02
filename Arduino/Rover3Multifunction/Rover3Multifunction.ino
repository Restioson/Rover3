#include "motor.h"
#include "remote.h"
#include "rangefinding.h"
#include "compass.h"
#include "command.h"
#include "gps.h"
#include "log.h"
#include "sound.h"

#define LOGGING_BAUD 115200

void setup() {
  // Serial - USB serial console (debugging)
  Serial.begin(LOGGING_BAUD);
  while (!Serial) ;

  setupRemote();
  setupRangefinding();
  setupCompass();
  setupGps();
  setupMotors();

  // Serial1 - Raspi serial console
  Serial1.begin(57600);
  Serial1.println("EST serial");
  Serial1.println("LOG Rover startup!");

  playMelody();
  Serial.println("Rover Multifunction Start!");
}

void loop() {
  char command = readRemoteCommand();

  long forward_distance = forward_rangefind();
  long backwards_distance = backwards_rangefind();

  if (command != '\0') {
    Serial.print("Remote command: \"");
    Serial.print(command);
    Serial.println("\"");

    executeCommand(command, forward_distance, backwards_distance);
  }

  if (Serial1.available()) {
    command = Serial1.read();

    Serial.print("Raspi command: \"");
    Serial.print(command);
    Serial.println("\"");

    executeCommand(command, forward_distance, backwards_distance);
  }

  updateMotion(forward_distance, backwards_distance);

  Status status = Status {
    .position = getPos(),
    .course = getCourse(),
    .datetime = getDatetime(),
    .compass = readCompass(),
    .forward_distance = forward_distance,
    .backwards_distance = backwards_distance,
  };

  writeStatus(status);
}
