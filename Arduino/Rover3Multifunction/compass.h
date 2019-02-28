typedef struct CompassData {
  float heading;
  float pitch;
  float roll;
} CompassData;

void setupCompass();
CompassData readCompass();
