void setupMotors();
void motorGo(uint8_t motor, uint8_t direct, uint8_t pwm);
void motorOff(int motor);
void stopMotors();
void testMotors();

void goForward(int power);
void goBack(int power);
void turnLeft(int power);
void turnRight(int power);
void pivotLeft(int power);
void pivotRight(int power);
