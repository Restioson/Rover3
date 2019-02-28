#include <Arduino.h>
#include "motor.h"

// Write a command (to RPi)
void writeCommand(String cmd) {

   String cmdMessage = "CMD " + cmd + " ";

   // USB debugging
   Serial.println(cmdMessage);

   // RPi
   Serial1.println(cmdMessage);
}

void executeCommand(char command, long fwd_range_cm, long rear_range_cm) {
  switch (command) {
    case 'W' :
            Serial.println("Fwd"); // TODO
            range_override = false;
            if ((speed == 0) && (fwd_range_cm > DISTANCE_STOP)) {
                goForward(255);
            } else {
                Serial.println("Too close - ignoring move forward command");
            }
            break;

    case 'S' :
            range_override = false;
            if (rear_range_cm > DISTANCE_STOP) {
                goBack(150);
            } else {
                Serial.println("Too close - ignoring move back command");
            }
            break;

    case 'O' :
            // Forward with override
            range_override = true;
            goForward(150);
            Serial.println("Forward with sensor override");
            break;

    case 'L' :
            // Back with override
            range_override = true;
            goBack(150);
            Serial.println("Back with sensor override");
            break;

    case 'A' :
            range_override = false;
            turnLeft(250);
            break;

    case 'D' :
            range_override = false;
            turnRight(250);
            break;

    case '<' :
            pivotLeft(250);
            break;

    case '>' :
            pivotRight(250);
            break;

    case ' ' :
            range_override = false;
            stopMotors();
            break;

    case 'T' :
            testMotors();
            break;

    case '/' :
            //tone(SPEAKER_PIN, NOTE_G4, 250); // TODO
            writeCommand("SHUTDOWN");
            break;
  }
}
