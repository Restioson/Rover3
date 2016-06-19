#Serial connection class

#Imports
import serial
from subprocess import call

#Arduino-RaspberryPi serial connection class
class ArduinoSerialConnection():
    
    #Initialiser
    def __init__(self, port='delf/ttyAMA0', baud=57600, handshaketimeout=1.5):
        
        #Variables
        self.port = port
        self.baud = baud
        
        #Whether the time has been set
        self.timeset = False
        
        #Initialise serial connection
        self.serial = serial.Serial(port, baud, timeout=handshaketimeout)
        
        #Handshake
        self.serial.readline()
    
    #Sends message
    def write(self, message):
        self.serial.write(message)
    
    #Waits for message and parses it
    def parse(self):
        
        message = self.serial.readline()
        
        #Split message
        message = data.split()
        
        #Dictionary to store parsed data in
        data = {}
        
        #Parse telemetry data
        data["latitude"] = message.pop(0)
        data["longitude"] = message.pop(0)
        data["altitude"] = message.pop(0)
        data["course"] = message.pop(0)
        data["heading"] = message.pop(0)
        data["speed"] = message.pop(0)

            
        #Parse time data
        data["year"] = message.pop(0)
        data["month"] = message.pop(0)
        data["day"] = message.pop(0)
        data["hour"] = message.pop(0)
        data["minute"] = message.pop(0)
        data["second"] = message.pop(0)
        
        #Parse environment data
        data["temperature"] = message.pop(0)
        data["humidity"] = message.pop(0)
        data["pitch"] = message.pop(0)
        data["roll"] = message.pop(0)
        data["objdistfront"] = message.pop(0)
        data["objdistback"] = message.pop(0)
        
        #Other data, e.g things the arudino process wants to get logged
        data["other"] = " ".join(map(str, message))
        
        #Set time
        if not self.timeset:
            call(["sudo", "date", "+%Y-%m-%d %T", "--set", "{0}-{1}-{2} {3}:{4}:{5}".format(data["year"], data["month"], data["day"], data["hour"], data["minute"], data["second"])])
            self.timeset = True
        
        return data