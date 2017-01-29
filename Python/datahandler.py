#Handles data & serial from arduino


#Imports
import subprocess
import sys
import time
import serial

#Handler class
class SerialDataHandler():
    
    #Init
    def __init__(self, logger):
        
        #Whether time is set to GPS UTC
        self.time_set = False
        
        #Logger
        self.logger = logger
        
        #Connect to serial
        try: 
        
            connect_to_serial()
            self.logger.log("Connected to serial", "INFO")
            
        except: 
        
            self.serial = None
            self.logger.log("Could not connect to serial", "WARN")
    
    def connect_to_serial(self):
        
        #Initialise serial connection
        self.serial = serial.Serial("/dev/ttyAMA0", 57600, timeout=1.5)
        
        #Handshake
        self.serial.readline()
        
    def parse(self, data):
        
        #Split message
        message = data.split()
        
        #Dictionary to store parsed data in
        data = {}
        
        #Header
        data["serial-header"] = message.pop(0)
        
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
        
        #Other data, e.g command
        data["other"] = message.pop(0)
        
        return data
        
    
    def handle(self):
            
        #Handle data if connected to serial
        if self.serial:
            
            #Parse data
            try:
                
                data_raw = str(self.serial.readline())
                data = self.parse(data_raw)
                
                #Set time
                if not self.time_set:
                    
                    #Try set the system time to GPS time
                    try:
                        
                        #Sets the time according to GPS reading
                        subprocess.check_call(["sudo", "date", "+%Y-%m-%d %T", "--set", "{0}-{1}-{2} {3}:{4}:{5}".format(
                            data["year"], 
                            data["month"], 
                            data["day"], 
                            data["hour"], 
                            data["minute"], 
                            data["second"]
                            )])
                        
                        #Set variable tracking whether using gps time to true
                        self.timeSet = True
                    
                        #Log
                        self.logger.log("System time set to GPS time", "INFO")
                    
                    #Error
                    except Exception as error:
                        
                        #Log
                        self.logger.log("Exception while setting system time: \"{0}\"".format(str(error.args)), "ERROR")
            
                #Create data log format
                log_message_format = "".join([
                    "Latitude: {0}; ",
                    "Longitude: {1}; ",
                    "Altitude: {2}; ",
                    "Course: {3}; ",
                    "Heading: {4}; ",
                    "Speed: {5}; ",
                    "Temperature: {5}; ",
                    "Humidity: {7}; ",
                    "Pitch: {8}; ",
                    "Roll: {9}; ",
                    "ObjectDistanceFront: {10}; ",
                    "ObjectDistanceBack: {11}; ",
                    "Other: {12};\n"
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
                    data["other"]
                )
                
                #Log
                self.logger.log(log_message, "DATA")
                
                #Shutdown Pi
                if data["other"] == "CMD:SHUTDOWN":
                    
                    self.logger.log("Received shutdown command, shutting down", "INFO")
                    
                    #Send halt command
                    subprocess.call(["sudo", "halt"])
                    
                    #Exit program
                    sys.exit(0)
            
            #Exception
            except Exception as error:
                
                self.logger.log("Exception while parsing \"{0}\": \"{1}\"".format(data_raw, str(error.args)), "ERROR")                    
        
        #Try connect to serial
        else:
            
            try: 
                time.sleep(2.5)
                self.connect_to_serial()
                self.logger.log("Connected to serial", "INFO")
            except Exception as error: self.logger.log("Failed to connect to serial: \"{0}\"".format(str(error.args)), "WARN")
