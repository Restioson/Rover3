#include <Arduino.h>

#define BRAKEVCC             0
#define CW                   1
#define CCW                  2
#define BRAKEGND             3
#define CS_THRESHOLD         100

enum direction {
  forward,
  backward,
  stationary,
};

/*  VNH2SP30 pin definitions
 xxx[0] controls '1' outputs
 xxx[1] controls '2' outputs */
int inApin[2] = {7, 4};  // INA: Clockwise input
int inBpin[2] = {8, 24};  // INB: Counter-clockwise input
int pwmpin[2] = {5, 6};  // PWM input
int cspin[2] = {2, 3};   // CS: Current sense ANALOG input
int enpin[2] = {0, 1};   // EN: Status of switches output (Analog pin)

// Motion
direction movement_direction = stationary;
unsigned int movement_speed = 0;

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

  movement_direction = stationary;
  movement_speed = 0;
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

  movement_speed = power;
  movement_direction = forward;

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

  movement_speed = power;
  movement_direction = forward;
}

void turnLeft(int power){
  stopMotors();

  Serial.print("Left ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CW, power/3);
  motorGo(1, CW, power);

  // speed? does it matter? // TODO
  movement_direction = forward;
}

void turnRight(int power) {
  stopMotors();

  Serial.print("Right ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CW, power);
  motorGo(1, CW, power/3);

  // speed?
  movement_direction = forward;
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
