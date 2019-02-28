#include <Arduino.h>
#include <Wire.h>
#include "compass.h"

#define HMC6343_ADDRESS       0x19
#define HMC6343_HEADING_REG   0x50
#define POLL_INTERVAL 500

unsigned long next_poll = 0;
CompassData cached_data;

void setupCompass() {
    Wire.begin();
}

CompassData readCompass() {
  if (millis() < next_poll) {
     return cached_data;
  }

  byte highByte, lowByte;

  Wire.beginTransmission(HMC6343_ADDRESS);
  Wire.write(HMC6343_HEADING_REG);
  Wire.endTransmission();

  Wire.requestFrom(HMC6343_ADDRESS, 6);

  while(Wire.available() < 1); // Wait for bytes

  highByte = Wire.read();
  lowByte = Wire.read();
  float heading = ((highByte << 8) + lowByte) / 10.0;

  highByte = Wire.read();
  lowByte = Wire.read();
  float pitch = ((highByte << 8) + lowByte) / 10.0;

  highByte = Wire.read();
  lowByte = Wire.read();
  float roll = ((highByte << 8) + lowByte) / 10.0;

  next_poll = millis() + POLL_INTERVAL;

  cached_data = CompassData {
    .heading = heading,
    .pitch = pitch,
    .roll = roll,
  };

  return cached_data;
}
