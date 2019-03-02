#ifndef _COMPASS_TYPES
#define _COMPASS_TYPES
typedef struct CompassData {
  float heading;
  float pitch;
  float roll;
} CompassData;
#endif

void setupCompass();
CompassData readCompass();
