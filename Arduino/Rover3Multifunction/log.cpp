#include "log.h"
#include "gps.h"
#include <Arduino.h>

#define STATUS_INTERVAL 1000

long next_serial_status = 0;

void writeStatus(Status status) {
  if (millis() <  next_serial_status) {
    return;
  }
  // Date/Time
  // char timeStr[25];

  // sprintf(
  //   timeStr,
  //   "%02d-%02d-%02d %02d:%02d:%02d",
  //   dt.year, dt.month, dt.day,
  //   dt.hours, dt.minutes, dt.seconds,
  // );

  Datetime dt = status.datetime;

  String log_message = "DATA "
    + String(status.position.latitude, 10) + " "
    + String(status.position.longitude, 10) + " "
    + String(status.position.altitude, 1) + " "
    + String(status.course.course, 2) + " "
    + String(status.compass.heading, 1) + " "
    + String(status.course.speed, 3) + " "
    + String(dt.year) + " "
    + String(dt.month) + " "
    + String(dt.day) + " "
    + String(dt.hours) + " "
    + String(dt.minutes) + " "
    + String(dt.seconds) + " "
    + "0 "  // temperature - TODO this sensor is broken
    + "0 "  // humidity
    + String(status.compass.pitch, 1) + " "
    + String(status.compass.roll, 1) + " "
    + String(status.forward_distance) + " "
    + String(status.backwards_distance, 1);

   // USB debugging
   Serial.println(log_message);

   // RPi
   Serial1.println(log_message);

   next_serial_status = millis() + STATUS_INTERVAL;
}
