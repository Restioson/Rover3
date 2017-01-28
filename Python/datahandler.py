#Handles data & serial from arduino

class SerialDataHandler():
    
    #Init
    def __init__(self, logger):
        
        #Whether time is set to GPS UTC
        self.time_set = False
        
        #Logger
        self.logger = self.logger
        
        #Connect to serial
        try: 
            connect_to_serial()
            self.logger.log("Connected to serial", "INFO")
        except: self.serial = None
    
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
        
        #XBee transmissions since last serial exchange
        data["xbeeDataReceived"] = message.pop(0)
        data["xbeeDataSent"] = message.pop(0)
        
        #Other data, e.g things the arudino process wants to get logged
        data["other"] = message.pop(0)
        
        return data
        
    
    def handle(self):
            
        #Handle data if connected to serial
        if self.serial:
            
            #Parse data
            data = self.parse(self.serial.readline())

            #Set time
            if not self.time_set:
                
                subprocess.call(["sudo", "date", "+%Y-%m-%d %T", "--set", "{0}-{1}-{2} {3}:{4}:{5}".format(data["year"], data["month"], data["day"], data["hour"], data["minute"], data["second"])]) #Sets the time according to GPS reading
                
                self.timeSet = True
                
                #Log
                self.logger.log("System time set to GPS time", "INFO")
            
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
            self.logger.log(logmessage, "DATA")
        
        #Try connect to serial
        else:
            
            try: 
                connect_to_serial()
                self.logger.log("Connected to serial", "INFO")
            except: pass
