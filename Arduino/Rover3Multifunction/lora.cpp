#include <SPI.h>
#include <RH_RF95.h>

#define LORA_SS_PIN          53
#define LORA_PACKET_SIZE     16

RH_RF95 rf95(LORA_SS_PIN);
uint8_t buf[LORA_PACKET_SIZE] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

void setupRemote() {
  // Set up the LoRa
  if (!rf95.init()) {
    Serial.println("LoRa init failed");
  } else {
    Serial.println("LoRa successfully initialised");
  }

  rf95.setPromiscuous(true);
}

// Reads the LoRa data into a buffer and returns whether it was read
bool readLoRa(uint8_t buf[], uint8_t len) {
  if (rf95.available()) {
    if (rf95.recv(buf, &len)) {
      Serial.print("RSSI: ");
      Serial.println(rf95.lastRssi(), DEC);

      return true;
    }
  }

  return false;
}

char readRemoteCommand() {
  if (readLoRa(buf, LORA_PACKET_SIZE)) {
    return (char)buf[0];
  } else {
    return '\0';
  }
}
