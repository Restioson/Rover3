#include <Arduino.h>
#include "motor.h"
#include "sound.h"

#define BRAKEVCC             0
#define CW                   1
#define CCW                  2
#define BRAKEGND             3
#define CS_THRESHOLD         100

/*  VNH2SP30 pin definitions
 xxx[0] controls '1' outputs
 xxx[1] controls '2' outputs */
int inApin[2] = {7, 4};  // INA: Clockwise input
int inBpin[2] = {8, 24};  // INB: Counter-clockwise input
int pwmpin[2] = {5, 6};  // PWM input
int cspin[2] = {2, 3};   // CS: Current sense ANALOG input
int enpin[2] = {0, 1};   // EN: Status of switches output (Analog pin)

bool range_override = false;
Direction direction = STATIONARY;
unsigned int speed = 0;

void setupMotors() {
  // Initialize digital pins as outputs
  for (int i=0; i<2; i++) {
    pinMode(inApin[i], OUTPUT); // TODO some of this is breaking the LoRa?
    pinMode(inBpin[i], OUTPUT);
    pinMode(pwmpin[i], OUTPUT);
  }

  // Initialize brakes
  for (int i=0; i<2; i++) {
    digitalWrite(inApin[i], LOW);
    digitalWrite(inBpin[i], LOW);
  }
}

/* motorGo() will set a motor going in a specific direction
 the motor will continue going in that direction, at that speed
 until told to do otherwise.

 motor: this should be either 0 or 1, will selet which of the two
 motors to be controlled

 direct: Should be between 0 and 3, with the following result
 0: Brake to VCC
 1: Clockwise
 2: CounterClockwise
 3: Brake to GND

 pwm: should be a value between 0 and 255, higher the number, the faster
 it'll go
 */
void motorGo(uint8_t motor, uint8_t direct, uint8_t pwm) {
  if (motor <= 1) {
    if (direct <=4) {
      // Set inA[motor]
      if (direct <=1)
        digitalWrite(inApin[motor], HIGH);
      else
        digitalWrite(inApin[motor], LOW);

      // Set inB[motor]
      if ((direct==0)||(direct==2))
        digitalWrite(inBpin[motor], HIGH);
      else
        digitalWrite(inBpin[motor], LOW);

      analogWrite(pwmpin[motor], pwm);
    }
  }
}

void motorOff(int motor) {
  for (int i=0; i<2; i++) {
    digitalWrite(inApin[i], LOW);
    digitalWrite(inBpin[i], LOW);
  }

  analogWrite(pwmpin[motor], 0);
}

void stopMotors() {
  motorOff(0);
  motorOff(1);

  direction = STATIONARY;
  speed = 0;
}

void testMotors() {

  int speed = 500;

  motorGo(0, CW, speed);
  motorGo(1, CW, speed);
  delay(3000);

  motorOff(0);
  motorOff(1);
  delay(1500);

  motorGo(0, CCW, speed);
  motorGo(1, CCW, speed);
  delay(3000);

  if ((analogRead(cspin[0]) < CS_THRESHOLD) && (analogRead(cspin[1]) < CS_THRESHOLD))
    digitalWrite(13, HIGH); // status led pin

  motorOff(0);
  motorOff(1);

  delay(3000);
}

void goForward(int power) {
  stopMotors();

  speed = power;
  direction = FORWARDS;

  Serial.print("Forward ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CW, power);
  motorGo(1, CW, power * 0.87);
}

void goBack(int power) {
  stopMotors();

  Serial.print("Backwards ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CCW, power);
  motorGo(1, CCW, power * 0.87);

  speed = power;
  direction = BACKWARDS;
}

void turnLeft(int power){
  stopMotors();

  Serial.print("Left ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CW, power/3);
  motorGo(1, CW, power);

  // speed? does it matter? // TODO
  direction = FORWARDS;
}

void turnRight(int power) {
  stopMotors();

  Serial.print("Right ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CW, power);
  motorGo(1, CW, power/3);

  // speed?
  direction = FORWARDS;
}

void pivotLeft(int power) {
  stopMotors();

  Serial.print("PivotLeft ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CCW, power);
  motorGo(1, CW, power);
}

void pivotRight(int power) {
  stopMotors();

  Serial.print("PivotRight ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CW, power);
  motorGo(1, CCW, power);
}

void updateMotion(long forward_distance, long backwards_distance) {
  if ((forward_distance <= DISTANCE_STOP) && (speed == 0)) {
    Serial.println("Object closer than 40cm!");
    Serial.print("Speed: "); Serial.print(speed);
    Serial.print(" Range: "); Serial.println(forward_distance);;
    note(NOTE_B3, 10);
  }

  if (direction == FORWARDS) {
    if ((forward_distance <= DISTANCE_STOP) && (!range_override)) {
      Serial.println("Too close, forward obstacle - STOPPING!");
      Serial.print("Speed: "); Serial.print(speed);
      Serial.print(" Range: "); Serial.println(forward_distance);
      stopMotors();
      note(NOTE_G3, 10);
    } else if ((forward_distance >= DISTANCE_SLOWDOWN) && (speed < 255) && (direction == FORWARDS)) {
      speed = SPEED_FORWARD;
      Serial.println("No forward obstacles - SPEEDING UP!");
      Serial.print("Speed: "); Serial.print(speed);
      Serial.print(" Range: "); Serial.println(forward_distance);
      goForward(speed);
      note(NOTE_A3, 10);
    } else if ((forward_distance > DISTANCE_STOP) && (forward_distance < DISTANCE_SLOWDOWN) && (speed > SPEED_SLOW)) {
      speed = SPEED_SLOW;
      Serial.println("Close to forward obstacle - slowing down!");
      Serial.print("Speed: "); Serial.print(speed);
      Serial.print(" Range: "); Serial.println(forward_distance);
      goForward(speed);
      note(NOTE_C3, 10);
    }
  } else if (direction == BACKWARDS) {
    if ((speed > 0) && (backwards_distance < DISTANCE_STOP) && (!range_override)) {
      Serial.println("Too close, rear obstacle - STOPPING!");
      Serial.print("Speed: "); Serial.print(speed);
      Serial.print(" Range: "); Serial.println(backwards_distance);
      note(NOTE_G3, 10);
      stopMotors();
    }

    if ((speed > SPEED_SLOW) && (backwards_distance >= DISTANCE_STOP) && (backwards_distance < DISTANCE_SLOWDOWN)) {
      Serial.println("Close to rear obstacle - slowing down!");
      Serial.print("Speed: "); Serial.print(speed);
      Serial.print(" Range: "); Serial.println(backwards_distance);
      note(NOTE_C3, 10);
      goBack(SPEED_SLOW);
    }
  }
}
