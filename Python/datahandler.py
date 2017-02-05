#Handles data & serial from arduino


#Imports
import subprocess
import sys
import time
import traceback
import serial
import datetime

#Handler class
class SerialDataHandler():
    
    #Init
    def __init__(self, logger, main):
        
        #Whether time is set to GPS UTC
        self.time_set = False
        
        #Logger
        self.logger = logger
        
        #Main
        self.main = main
        
        #Log
        self.logger.log("Serial data handler started", "INFO")
        
    def connect_to_serial(self):
        
        try:
            
            #Initialise serial connection
            self.serial = serial.Serial("/dev/ttyAMA0", 57600, timeout=1.5)
            
            #Handshake
            self.serial.readline()
            
            #Read 1 line of data
            data = self.serial.readline()
            
            #Log
            if data == b'': self.logger.log("Could not connect to serial", "WARN")
            
            else: self.logger.log("Connected to Arduino via /dev/ttyAMA0", "INFO")
            
            #Return whether serial connected
            return data != b''
        
        #Error
        except:
            
            self.logger.log("Exception while attempting to connect to serial:", "ERROR")
            self.logger.log(traceback.format_exc(), "ERROR")
            self.logger.log("Is the port in use?", "ERROR")
    
    def handle_data(self, message):
        
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
        
        #Set time
        if not self.time_set: self.set_time(data)
                
        #Create data log format
        log_message_format = "".join([
            "Latitude: {0}; ",
            "Longitude: {1}; ",
            "Altitude: {2}; ",
            "Course: {3}; ",
            "Heading: {4}; ",
            "Speed: {5}; ",
            "Temperature: {6}; ",
            "Humidity: {7}; ",
            "Pitch: {8}; ",
            "Roll: {9}; ",
            "ObjectDistanceFront: {10}; ",
            "ObjectDistanceBack: {11};"
        ])
    
        #Create message
        log_message = log_message_format.format(
            data["latitude"], 
            data["longitude"], 
            data["altitude"], 
            data["course"], 
            data["heading"], 
            data["speed"], 
            data["temperature"],
            data["humidity"], data["pitch"], 
            data["roll"], 
            data["objdistfront"], 
            data["objdistback"], 
        )
        
        #Log
        self.logger.log(log_message, "DATA")
    
    #Handle commands
    def handle_command(self, message):
        
        #Handle
        
        #Shutdown
        if message[0] == "SHUTDOWN": 
            
            #Log
            self.logger.log("Shutdown command received", "INFO")
            
            #Shut down
            self.main.shutdown()
        print(message)
    
    #Handles incoming data
    def handle(self):
            
        #Parse data
        try:
            
            #Raw data
            data_raw = str(self.serial.readline())
            
            #Remove unecessary quotes and b
            message_raw = data_raw.replace("b", "", 1).replace("'", "", 1).replace("'", "", -1)
            
            #Split message
            message = message_raw.split(" ")
            
            #Data
            if message[0] == "DATA": self.handle_data(message[1:])
            
            #CMD
            elif message[0] == "CMD": self.handle_command(message[1:])
            
            #Other
            else: 
                
                #Log
                self.logger.log("Bad packet: \"{0}\". Unimplemented serial packet?".format(message_raw), "WARN")
                self.logger.log("Packet header: \"{0}\"".format(message[0]))
            
        #Exception
        except:
            
            self.logger.log("Exception while parsing \"{0}\":".format(data_raw), "ERROR")
            self.logger.log(traceback.format_exc(), "ERROR", newline = "")       
    
    #Sets time according to GPS
    def set_time(self, data):
        
        #Try set the system time to GPS time
        try:
            
            #Check date is valid
            if int(data["year"]) > 2000:
                
                #Create datetime object
                gps_datetime = datetime.datetime(int(data["year"]), int(data["month"]), int(data["day"]), int(data["hour"]), int(data["minute"]), int(data["second"]))
                    
                #Sets the time according to GPS reading
                subprocess.check_call(["sudo", "date", "--set", "{0}".format(gps_datetime.strftime("%Y-%m-%d %H:%M:%S"))])
            
            #Set variable tracking whether using gps time to true
            self.time_set = True
        
            #Log
            self.logger.log("System time set to GPS time", "INFO")
        
        #Error
        except:
            
            #Log
            self.logger.log("Exception while setting system time:", "ERROR")
            self.logger.log(traceback.format_exc(), "ERROR", newline = "")