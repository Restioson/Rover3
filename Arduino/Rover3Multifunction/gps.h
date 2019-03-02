#ifndef _GPS_TYPES
#define _GPS_TYPES
typedef struct Position {
  float latitude;
  float longitude;

  // Altitude in meters
  float altitude;
} Position;

typedef struct Course {
  float course;

  // Speed in meters per second
  float speed;
} Course;

typedef struct Datetime {
  unsigned short year;
  unsigned char month;
  unsigned char day;
  unsigned char hours;
  unsigned char minutes;
  unsigned char seconds;
  unsigned char hundredths;
} Datetime;
#endif

void setupGps();
Position getPos();
Course getCourse();
Datetime getDatetime();
