#include "TinyGPS++.h"
#include "gps.h"

#define GPS_POLL_INTERVAL 1000
#define GPS_BAUDRATE      4800

TinyGPSPlus gps;
unsigned long gps_next_poll = 0;
Position position;
Course course;
Datetime datetime;

void updateGps() {
  if (millis() > gps_next_poll) {
    Serial3.begin(GPS_BAUDRATE);

    // TODO timeout
    while (!Serial3.available());
    int c = Serial3.read();

    while (!gps.encode(c)) {
      while (!Serial3.available());
      c = Serial3.read();
    }

    gps_next_poll = millis() + GPS_POLL_INTERVAL;

    if (gps.location.isUpdated() && gps.location.isValid()) {
      position.latitude = gps.location.lat();
      position.longitude = gps.location.lng();
    } else if (!gps.location.isValid()) {
      Serial.println("GPS location invalid");
    }

    if (gps.altitude.isUpdated() && gps.altitude.isValid()) {
      position.altitude = gps.altitude.meters();
    } else if (!gps.altitude.isValid()) {
      Serial.println("GPS altitude invalid");
    }

    if (gps.date.isUpdated() && gps.date.isValid()) {
      datetime.year = gps.date.year();
      datetime.month = gps.date.month();
      datetime.day = gps.date.day();
    } else if (!gps.date.isValid()) {
      Serial.println("GPS date invalid");
    }

    if (gps.time.isUpdated() && gps.time.isValid()) {
      datetime.hours = gps.time.hour();
      datetime.minutes = gps.time.minute();
      datetime.seconds = gps.time.second();
    } else if (!gps.time.isValid()) {
      Serial.println("GPS time invalid");
    }

    if (gps.speed.isUpdated() && gps.speed.isValid()) {
      course.speed = gps.speed.mps();
    } else if (!gps.speed.isValid()) {
      Serial.println("GPS speed invalid");
    }

    if (gps.course.isUpdated() && gps.course.isValid()) {
      course.course = gps.course.deg();
    } else if (!gps.course.isValid()) {
      Serial.println("GPS course invalid");
    }
  }
}

void setupGps() {
  Serial3.begin(GPS_BAUDRATE);
}

Position getPos() {
  updateGps();
  return position;
}

Course getCourse() {
  updateGps();
  return course;
}

Datetime getDatetime() {
  updateGps();
  return datetime;
}
