#Serial connection class

#Imports
import serial

#Arduino-RaspberryPi serial connection class
class ArduinoSerialConnection():
    
    #Initialiser
    def __init__(self, port='delf/ttyAMA0', baud=57600, handshaketimeout=1.5):
        
        #Variables
        self.port = port
        self.baud = baud
        
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
        data["course"] = message.pop(0)
        data["speed"] = message.pop(0)
        data["heading"] = message.pop(0)
            
        #Parse time data
        data["year"] = int(message.pop(0))
        data["month"] = int(message.pop(0))
        data["day"] = int(message.pop(0))
        data["hour"] = int(message.pop(0))
        data["minute"] = int(message.pop(0))
        data["second"] = int(message.pop(0))
        
        #Parse environment data
        data["temperature"] = message.pop(0)
        data["humidity"] = message.pop(0)
        data["pitch"] = message.pop(0)
        data["roll"] = message.pop(0)
        data["objdistfront"] = message.pop(0)
        data["objdistback"] = message.pop(0)
        
        #Other data, e.g things the arudino process wants to get logged
        data["other"] = " ".join(map(str, message))
        
        return data