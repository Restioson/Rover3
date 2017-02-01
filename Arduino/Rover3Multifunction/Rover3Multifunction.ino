// Rover v3 Multifunction: GPS, Tilt-compensated compass, ultrasonic range finder, temperature sensor, speaker, etc

// HMC6343 Compass: uses SDA/SCL on pins 20 and 21
#include <Wire.h>

// GPS: uses the Serial3 port on pins 14 and 15
#include <TinyGPS.h>

// XBEE: uses Serial2 port on pins 16 and 17
#include <XBee.h>

// Sound
#include "pitches.h"

// Speaker
#define SPEAKER_PIN          51

// Ultrasonic Range Finder (forward-facing)
#define MAXSONAR_ACTIVE_PIN  43
#define MAXSONAR_PWM_PIN     45

// Infrared range sensor (rear-facing)
#define IR_RANGE_PIN         15

float ir_sensor_value = 0;
float rear_range_cm = 0;

boolean debug = false;
 
// notes in the melody:

int melody[] = {
  NOTE_C4, NOTE_G3, NOTE_G3, NOTE_A3, NOTE_G3, 0, NOTE_B3, NOTE_C4 };

// note durations: 4 = quarter note, 8 = eighth note, etc.:
int noteDurations[] = {
  4, 8, 8, 4, 4, 4, 4, 4 };

// Compass
#define HMC6343_ADDRESS       0x19
#define HMC6343_HEADING_REG   0x50

float compass_heading = 0;
float compass_pitch = 0;
float compass_roll = 0;

// GPS
#define GPSBAUD               4800

// Create an instance of the TinyGPS object
TinyGPS gps;

// Motors

#define BRAKEVCC 0
#define CW   1
#define CCW  2
#define BRAKEGND 3
#define CS_THRESHOLD 100

/*  VNH2SP30 pin definitions
 xxx[0] controls '1' outputs
 xxx[1] controls '2' outputs */
int inApin[2] = {7, 4};  // INA: Clockwise input
int inBpin[2] = {8, 9};  // INB: Counter-clockwise input
int pwmpin[2] = {5, 6};  // PWM input
int cspin[2] = {2, 3};   // CS: Current sense ANALOG input
int enpin[2] = {0, 1};   // EN: Status of switches output (Analog pin)

int statpin = 13;

// RangeFinder
long fwd_range_cm;

// The address of the remote XBee
#define REMOTE_XBEE_ADDR     0x4256

// Char array of data being sent
uint8_t payload[] = { 'H', 'i', ' ', '\n', '\r' };

// 16-bit addressing: Enter address of remote XBee, typically the coordinator
Tx16Request tx = Tx16Request(REMOTE_XBEE_ADDR, payload, sizeof(payload));
TxStatusResponse txStatus = TxStatusResponse();

// create reusable response objects for responses we expect to handle 

// XBeeResponse response = XBeeResponse();
Rx16Response rx16 = Rx16Response();
Rx64Response rx64 = Rx64Response();

uint8_t option = 0;
uint8_t data = 0;

// Timing

unsigned long nextstatus_serial = 0;
int status_interval_serial = 1000;    // status interval in ms

unsigned long nextpoll_compass = 0;  // time of last poll
int poll_interval_compass = 500;     // poll interval in ms

XBee xbee = XBee();

int statusLed = 4;
int errorLed = 5;

boolean sonar_range = false;

int forward_speed = 0;
int back_speed = 0;

// Slowdown and stopping distances
int distance_stop = 50;
int distance_slowdown = 150;
int distance_rear_slowdown = 75;
int speed_slow = 60;

int shutdown_pi = 0;

// This is where you declare prototypes for the functions that will be 
// using the TinyGPS library.
void getgps(TinyGPS &gps);

// ********** SETUP ***********

void setup () {

  // Compass
  Wire.begin(); // Initialize the I2C bus

  // GPS
  Serial3.begin(GPSBAUD);

  // Pin modes: motors
  
  // Range finder
  
  pinMode(MAXSONAR_PWM_PIN, INPUT);
  pinMode(MAXSONAR_ACTIVE_PIN, OUTPUT);
  
  sonar_range = true;
  digitalWrite(MAXSONAR_ACTIVE_PIN, HIGH);
  
  // Create an XBee object at the top of your sketch
  // Serial2: pins 16 & 17 (Arduino Mega ADK)  
  xbee.setSerial(Serial2);
  
  // Tell XBee to start Serial
  xbee.begin(9600);

  // Motors
  
  pinMode(statpin, OUTPUT);

  // Initialize digital pins as outputs
  for (int i=0; i<2; i++)
  {
    pinMode(inApin[i], OUTPUT);
    pinMode(inBpin[i], OUTPUT);
    pinMode(pwmpin[i], OUTPUT);
  }
  // Initialize braked
  for (int i=0; i<2; i++)
  {
    digitalWrite(inApin[i], LOW);
    digitalWrite(inBpin[i], LOW);
  }
  
  // Wait 10 seconds
  delay(5000);
  
  // Serial - Raspberrry Pi
  Serial1.begin(57600);
  Serial1.println("EST serial");
  Serial1.println("LOG Rover startup!");
  
  // Serial - USB serial console (debugging)
  Serial.begin(115200);
  Serial.println("Rover Multifunction Start!");

  // Startup tune
  playMelody();

}

// ********** MAIN ***********

void loop ()
{
  
  // Range Finder

  if (sonar_range) {
      if (debug) Serial.println("Reading forward range finder");
      
      fwd_range_cm = getForwardRangeCm();

      if ((fwd_range_cm <= distance_stop) && (forward_speed == 0)) {
          Serial.println("Object closer than 40cm!");
          Serial.print("Speed: ");
          Serial.println(forward_speed);
          Serial.print("Range: ");
          Serial.println(fwd_range_cm);
          tone(SPEAKER_PIN, NOTE_B3, 10);
      } else

      if ((fwd_range_cm <= distance_stop) && (forward_speed > 0)) {
          Serial.println("Too close, forward obstacle - STOPPING!");
          Serial.print("Speed: ");
          Serial.println(forward_speed);
          Serial.print("Range: ");
          Serial.println(fwd_range_cm);
          tone(SPEAKER_PIN, NOTE_G3, 10);
          stopMotors();
      } else
      
      if ((fwd_range_cm >= distance_slowdown) && (forward_speed < 255) && (forward_speed > 0)) {
          forward_speed = 255;
          goForward(forward_speed);
          Serial.println("No forward obstacles - SPEEDING UP!");
          Serial.print("Speed: ");
          Serial.println(forward_speed);
          Serial.print("Range: ");
          Serial.println(fwd_range_cm);
          tone(SPEAKER_PIN, NOTE_A3, 10);
      } 
      
      else 
    
      if ((fwd_range_cm > distance_stop) && (fwd_range_cm < distance_slowdown) && (forward_speed > speed_slow )) { 
          forward_speed = speed_slow;
          goForward(forward_speed);
          tone(SPEAKER_PIN, NOTE_C8, 10);
          Serial.println("Close to forward obstacle - SLOWING down!");
          Serial.print("Speed: ");
          Serial.println(forward_speed);
          Serial.print("Range: ");
          Serial.println(fwd_range_cm);
      } 

  }
   
 // Rear IR sensor
  ir_sensor_value = analogRead(IR_RANGE_PIN);
  rear_range_cm = 10650.08 * pow(ir_sensor_value,-0.935) - 10;
 
  if ((back_speed > 0) && (rear_range_cm < distance_stop)) {
          Serial.println("Too close, rear obstacle - STOPPING!");
          Serial.print("Speed: ");
          Serial.println(back_speed);
          Serial.print("Range: ");
          Serial.println(rear_range_cm);
          tone(SPEAKER_PIN, NOTE_G3, 10);
          stopMotors();
  }
  
  if ((back_speed > speed_slow) && (rear_range_cm >= distance_stop) && (rear_range_cm < distance_rear_slowdown)) {
          Serial.println("Too close, rear obstacle - slowing down!");
          Serial.print("Speed: ");
          Serial.println(back_speed);
          Serial.print("Range: ");
          Serial.println(rear_range_cm);
          tone(SPEAKER_PIN, NOTE_G3, 10);
          goBack(speed_slow);
  }


  // Compass: heading, pitch, roll
  if (debug) Serial.println("Reading compass data");
  readCompass();
  
  // GPS
  if (debug) Serial.println("Reading GPS data");
  readGPS();
  
  // Command input
  data = '_';
  
  // XBee

  if (debug) Serial.println("Reading XBEE data");
  xbee.readPacket();
  
  if (xbee.getResponse().isAvailable()) {
    // got something
    
    Serial.print("Got XBEE packet... ");
    
    if (xbee.getResponse().getApiId() == RX_16_RESPONSE || xbee.getResponse().getApiId() == RX_64_RESPONSE) {
      // got a rx packet
      
      if (xbee.getResponse().getApiId() == RX_16_RESPONSE) {
              xbee.getResponse().getRx16Response(rx16);
      	option = rx16.getOption();
      	data = rx16.getData(0);
      } else {
              xbee.getResponse().getRx64Response(rx64);
      	option = rx64.getOption();
      	data = rx64.getData(0);
      }
      
      // TODO check option, rssi bytes    
      flashLed(statusLed, 1, 10);
      
      // set dataLed PWM to value of the first byte in the data
      // analogWrite(dataLed, data);
      Serial.print("xbeedata: ");
      Serial.write(data);
      Serial.write(" ");
      Serial.println(data, DEC);
      Serial.println();

      // Add data to list of packets received
      // TODO xbeePacketsReceived[sizeof(xbeePacketsReceived)] = data;
    } else 
    
    if (xbee.getResponse().isError()) {
      Serial.print("error reading packet.  Error code: ");  
      Serial.println(xbee.getResponse().getErrorCode());
      // or flash error led
    } 
  }
  
  // Raspberry Pi input
  if (Serial1.available()) {
    if (debug) Serial.println("Reading RPi data");
    data = Serial1.read();
    
    Serial.print("rpidata: ");
    Serial.print(data);
    Serial.write(" ");
    Serial.println(data, DEC);
    Serial.println();
  }
  
  // Execute command
  
  if (data != '_') {
      
      tone(SPEAKER_PIN, NOTE_C4, 50);
      
      switch (data) {
        
      case 'W' :
              if ((forward_speed == 0) && (fwd_range_cm > distance_stop)) {
                  forward_speed = 255;
              }
              goForward(forward_speed);
              break;
      
      case 'S' : 
              if (rear_range_cm > distance_stop) {
                  goBack(150);
              } else {
                  Serial.println("Too close - ignoring move back command");
              }
              break;
     
      case 'A' :   
              turnLeft(250);
              break;
     
      case 'D' :
              turnRight(250);
              break;
        
      case '<' :
              pivotLeft(250);
              break;

      case '>' :
              pivotRight(250);
              break;

      case ' ' :
               stopMotors();
              break;

      case 'T' :
              testMotors();
              break;

      case '/' :
              shutdownPi();
              break;

//      default:
//              flashLed(errorLed, 1, 25);
//              Serial.print("unexpected command: ");
//              Serial.println(data, DEC);
              
      }
      
    } 
    
  writeStatus();
  
//  delay(10);
}

// ********** FUNCTIONS ***********

void shutdownPi()
{
  shutdown_pi = 1;
}

void turnLeft(int power)
{
  stopMotors();
  
  Serial.print("Left ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CW, power/3);
  motorGo(1, CW, power);

  // TODO
}

void turnRight(int power)
{
  stopMotors();
  
  Serial.print("Right ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CW, power);
  motorGo(1, CW, power/3);

  // TODO
}

void pivotLeft(int power)
{
  stopMotors();

  Serial.print("PivotLeft ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CW, power);
  motorGo(1, CCW, power);

  // TODO
}

void pivotRight(int power)
{
  stopMotors();

  Serial.print("PivotRight ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CCW, power);
  motorGo(1, CW, power);

  // TODO
}



void goForward(int power)
{
  
  stopMotors();
  
  forward_speed = power;
  
  Serial.print("Forward ");
  Serial.print(power);
  Serial.print(" ...\n");

  motorGo(0, CW, power);
  motorGo(1, CW, power * 0.87);
    
  // enable range finder
  digitalWrite(MAXSONAR_ACTIVE_PIN, HIGH);
  sonar_range = true;
  
}

void goBack(int power)
{
 
  stopMotors();
  
  Serial.print("Backwards ");
  Serial.print(power);
  Serial.print(" ...\n"); 

  motorGo(0, CCW, power);
  motorGo(1, CCW, power * 0.87);
  
  back_speed = power;
  
}

void stopMotors()
{
  motorOff(0);
  motorOff(1);
  
  forward_speed = 0;
  back_speed = 0;
  
  // Switch off the sonar range finder
  
  // digitalWrite(MAXSONAR_ACTIVE_PIN, LOW);
  // sonar_range = false;
  
}

// Startup sound

void playMelody()
{
  // iterate over the notes of the melody:
  for (int thisNote = 0; thisNote < 8; thisNote++) {

    // to calculate the note duration, take one second 
    // divided by the note type.
    //e.g. quarter note = 1000 / 4, eighth note = 1000/8, etc.
    int noteDuration = 1000/noteDurations[thisNote];
    tone(SPEAKER_PIN, melody[thisNote],noteDuration);

    // to distinguish the notes, set a minimum time between them.
    // the note's duration + 30% seems to work well:
    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    // stop the tone playing:
    noTone(8);
  }
}

void flashLed(int pin, int times, int wait) {
    
  /*
    for (int i = 0; i < times; i++) {
      digitalWrite(pin, HIGH);
      delay(wait);
      digitalWrite(pin, LOW);
      
      if (i + 1 < times) {
        delay(wait);
      }
    }
  */
}

// ******* COMPASS *********

void readCompass() {

  if (millis() < nextpoll_compass) {
     return; 
  }
  
  byte highByte, lowByte;
  
  Wire.beginTransmission(HMC6343_ADDRESS);    // Start communicating with the HMC6343 compasss
  Wire.write(HMC6343_HEADING_REG);             // Send the address of the register that we want to read
  Wire.endTransmission();
  
  Wire.requestFrom(HMC6343_ADDRESS, 6);    // Request six bytes of data from the HMC6343 compasss
  
  while(Wire.available() < 1);             // Busy wait while there is no byte to receive
  highByte = Wire.read();              // Reads in the bytes and convert them into proper degree units.
  lowByte = Wire.read();
  compass_heading = ((highByte << 8) + lowByte) / 10.0; // the heading in degrees
  highByte = Wire.read();
  lowByte = Wire.read();
  
  compass_pitch = ((highByte << 8) + lowByte) / 10.0;   // the pitch in degrees
  highByte = Wire.read();
  lowByte = Wire.read();
  
  compass_roll = ((highByte << 8) + lowByte) / 10.0;    // the roll in degrees
  
  nextpoll_compass = millis() + poll_interval_compass;
}

// ******* GPS *********

// The getgps function will get and print the values we want.
void getgps(TinyGPS &gps)
{
  // To get all of the data into varialbes that you can use in your code, 
  // all you need to do is define variables and query the object for the 
  // data. To see the complete list of functions see keywords.txt file in 
  // the TinyGPS and NewSoftSerial libs.
  

  /*
  // Same goes for date and time
  int year;
  byte month, day, hour, minute, second, hundredths;
  gps.crack_datetime(&year,&month,&day,&hour,&minute,&second,&hundredths);
  // Print data and time
  Serial.print("Date: "); Serial.print(month, DEC); Serial.print("/"); 
  Serial.print(day, DEC); Serial.print("/"); Serial.print(year);
  Serial.print("  Time: "); Serial.print(hour, DEC); Serial.print(":"); 
  Serial.print(minute, DEC); Serial.print(":"); Serial.print(second, DEC); 
  Serial.print("."); Serial.print(hundredths, DEC);
  //Since month, day, hour, minute, second, and hundr
  */
/*

  // Here you can print the altitude and course values directly since 
  // there is only one value for the function
  Serial.print("Altitude (meters): "); Serial.print(gps.f_altitude());  
  Serial.print("  ");
  // Same goes for course
  Serial.print("Course (degrees): "); Serial.print(gps.f_course());
  Serial.print("  ");
  
  // And same goes for speed
  Serial.print("Speed(kmph): "); Serial.print(gps.f_speed_kmph());
  Serial.println();

*/  
  // Here you can print statistics on the sentences.
  unsigned long chars;
  unsigned short sentences, failed_checksum;
  gps.stats(&chars, &sentences, &failed_checksum);
  
  //Serial.print("Failed Checksums: ");Serial.print(failed_checksum);
  //Serial.println(); Serial.println();
}


// ***** MOTORS *******

void testMotors()
{
  
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
    digitalWrite(statpin, HIGH);
    
  motorOff(0);
  motorOff(1);
  
  delay(3000);
}

void motorOff(int motor)
{
  // Initialize braked
  for (int i=0; i<2; i++)
  {
    digitalWrite(inApin[i], LOW);
    digitalWrite(inBpin[i], LOW);
  }
  analogWrite(pwmpin[motor], 0);
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
void motorGo(uint8_t motor, uint8_t direct, uint8_t pwm)
{
  if (motor <= 1)
  {
    if (direct <=4)
    {
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


// Return the forward range distance in cm

long getForwardRangeCm() {
  
  // Read range from rangefinder    
  long pulse = pulseIn(MAXSONAR_PWM_PIN, HIGH);
  
  // 58uS per cm (MB12XX series)
   return pulse/58;
}

// Get GPS update if available

void readGPS() {
  
  while(Serial3.available())     // While there is data on the RX pin...
  {
      int c = Serial3.read();    // load the data into a variable...
      if(gps.encode(c))      // if there is a new valid sentence...
      {
        getgps(gps);         // then grab the data.
      }
  }
}

// Output current status

void writeStatus() {
  
  if (millis() >  nextstatus_serial) {
    
    // Write status to Serial

    // GPS position
    float gps_latitude, gps_longitude;
    gps.f_get_position(&gps_latitude, &gps_longitude);
  
    // GPS date/time
    int year;
    byte month, day, hour, minutes, second, hundredths;
    unsigned long fix_age;
 
    gps.crack_datetime(&year, &month, &day, &hour, &minutes, &second, &hundredths, &fix_age);
  
    // Date/Time
    char timeStr[25];
    sprintf(timeStr, "%02d-%02d-%02d %02d:%02d:%02d", year, month, day, hour, minutes, second);
    
    // *****************

    // Get other data to send
    String otherData = "none"; // ***** PLACEHOLDER *****
  
    if (shutdown_pi) {
       otherData = "CMD:SHUTDOWN";
    }

    String logMessage = "DATA "
      + String(gps_latitude, 5) + " "
      + String(gps_longitude, 5) + " "
      + String(gps.f_altitude())+ " "
      + String(gps.f_course()) + " "
      + String(compass_heading) + " "
      + String(gps.f_speed_kmph()) + " "
      + String(year) + " "
      + String(month) + " "
      + String(day) + " "
      + String(hour) + " "
      + String(minutes) + " "
      + String(second) + " "
      + "unknown "  // temperature
      + "unknown "  // humidity
      + String(compass_pitch) + " "
      + String(compass_roll) + " "
      + String(fwd_range_cm) + " "
      + String(rear_range_cm) + " "
      + String(otherData) + " ";
  
     // USB debugging
     Serial.println(logMessage);
     
     // RPi
     Serial1.println(logMessage);

     nextstatus_serial = millis() + status_interval_serial;
  }

  return;
}
