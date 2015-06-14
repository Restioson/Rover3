
//Analog read pins
const int xPin = 0;
const int yPin = 1;

//to hold the caculated values
int x;
int y;
int z;

// XBEE
#include <XBee.h>

// The address of the Rover XBee
#define ROVER_XBEE_ADDR 0x6524
// #define ROVER_XBEE_ADDR 0xffff

// Create an array for holding the data you want to send.
uint8_t payload[] = { ' ' };

// 16-bit addressing: Enter address of remote XBee, typically the coordinator
Tx16Request tx = Tx16Request(ROVER_XBEE_ADDR, payload, sizeof(payload));
TxStatusResponse txStatus = TxStatusResponse();

// create reusable response objects for responses we expect to handle 

// XBeeResponse response = XBeeResponse();
Rx16Response rx16 = Rx16Response();
Rx64Response rx64 = Rx64Response();

uint8_t option = 0;
uint8_t data = 0;

unsigned long last_sent = millis();

XBee xbee = XBee();

enum Direction { FORWARD, BACK, LEFT, RIGHT, STOP };

Direction newDirection = STOP;
Direction currentDirection = STOP;
Direction joystickDirection = STOP;

// Serial movement commands
int serialcom = 0;

// ********** SETUP ***********

void setup () {

  // Serial  
  Serial.begin(115200);

  // Create an XBee object at the top of your sketch    
  xbee.setSerial(Serial3);
  
  // Tell XBee to start Serial
  xbee.begin(9600);

  xbeeCheck();
  
  // Wait 3 seconds
  delay(3000);

    
  Serial.println("Rover Remote Control Start!");
}

// ********** MAIN ***********

void loop ()
{
  
  if (!serialcom) {
      newDirection = STOP;
  }

  // Read joystick position data
  int x = analogRead(xPin);
  int y = analogRead(yPin);

  // Output the values
  Serial.print("Joystick x: ");
  Serial.print(x);
  Serial.print(" | y: ");
  Serial.println(y);
  
  // Forward: 25 < x < 70
  // Backwards: 300 < x < 350
  // Left: 300 <  y < 350
  // Right: 25 < y < 70

  // Decide which direction to go
  
  if ( y >= 700 ) {
     newDirection = FORWARD;
     serialcom = 0;
  } 
  
  if ( y<= 200 ) {
     newDirection = BACK;
     serialcom = 0;
  } 

  if (newDirection == STOP) {  
    if ( x <= 100 ) {
       newDirection = LEFT;
       serialcom = 0;
    } 
  
    if ( x >= 700  ) {
       newDirection = RIGHT;
       serialcom = 0;
    }
  }

  // Read serial data if available and if there isn't a joystick position
  if (Serial.available() > 0) {
      // read the incoming byte:
      int incomingByte = Serial.read();
    
      switch (incomingByte) {
        
          case 'U':
            newDirection = FORWARD;
            serialcom = 1;
            break;
            
          case 'D':
            newDirection = BACK;
            serialcom = 1;
            break;
            
          case 'L':
            newDirection = LEFT;
            serialcom = 1;
            break;     
       
          case 'R':
            newDirection = RIGHT;
            serialcom = 1;
            break;
              
          case 'e':
            newDirection = STOP;
            serialcom = 0;
            break;
      }
   } 
   
  // Send the command to the rover
  if (newDirection != currentDirection) {
    
     switch (newDirection) {
     
       case FORWARD:
            Serial.println("Go forward!");
            sendCommand('W');
            break;
          
       case BACK:  
            Serial.println("Go back!"); 
            sendCommand('S');
            break;

       case LEFT:
            Serial.println("Go left!"); 
            sendCommand('A');
            break;
            
       case RIGHT:
            Serial.println("Go right!"); 
            sendCommand('D');
            break;
     
       case STOP:
            Serial.println("STOP!"); 
            sendCommand(' ');
            break;
            
     }
     
     currentDirection = newDirection; 
  }

  delay(250); //just here to slow down the serial output - Easier to read
  
  
}

// ********** FUNCTIONS ***********

void sendCommand(char cmd)
{
  
  payload[0] = cmd;
  Serial.print("Sending cmd: [");
  Serial.print(cmd);
  Serial.println("]");
  
  // 16-bit addressing: Enter address of remote XBee, typically the coordinator
  Tx16Request tx = Tx16Request(ROVER_XBEE_ADDR, payload, sizeof(payload));

  xbee.send(tx);
  
      // after sending a tx request, we expect a status response
      // wait up to 5 seconds for the status response
      if (xbee.readPacket(5000)) {
        // got a response!
  
        // should be a znet tx status            	
    	if (xbee.getResponse().getApiId() == TX_STATUS_RESPONSE) {
    	   xbee.getResponse().getZBTxStatusResponse(txStatus);
    		
    	   // get the delivery status, the fifth byte
           if (txStatus.getStatus() == SUCCESS) {
            	// success.  time to celebrate
                Serial.println("success!");
           } else {
            	// the remote XBee did not receive our packet. is it powered on?
               Serial.println("did not receive packet");
           }
        }      
      } else if (xbee.getResponse().isError()) {
        Serial.print("error reading packet.  Error code: ");  
        Serial.println(xbee.getResponse().getErrorCode());
        // or flash error led
      } else {
        // local XBee did not provide a timely TX Status   Radio is not configured properly or connected
        Serial.println("unknown error");
      }

  
}

void xbeeCheck()
{
  
  
}
