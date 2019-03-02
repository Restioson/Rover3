#include "gps.h"
#include "compass.h"

typedef struct Status {
  Position position;
  Course course;
  Datetime datetime;
  CompassData compass;
  long forward_distance;
  long backwards_distance;
} Status;

void writeStatus(Status status);
