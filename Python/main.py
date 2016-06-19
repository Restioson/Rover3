#Imports
import rover3
import time
import log
import arduinoserial

#Main class
class Main():
    
    #Initialiser
    def __init__(self):
        
        #Initialise Rover class
        self.rover = rover3.Rover3()
        
        #Initialise logger
        self.logger = log.Logger("/home/pi/log/")
        
        #Initialise serial
        self.serial = arduinoserial.ArduinoSerialConnection()
    
    #Mainloop of program
    def mainloop(self):
        
        #Loop
        while True:
            
            #Waits for data and then parses
            data = self.serial.parse()
            
            #Create message format
            logmessageFormat = "Latitude: {0}\nLongitude: {1}\nCourse: {2}\nHeading: {3}\nSpeed: {4}\nTemperature: {5}\nHumidity: {6}\nPitch: {7}\nRoll: {8}\nObjectDistanceFront: {9}\nObjectDistanceBack: {10}"
            
            #Create message
            logmessage = messageFormat.format(data["latitude"], data["longitude"], data["course"], data["heading"], data["speed"], data["temperature"], data["humidity"], data["pitch"], data["roll"], data["objdistfront"], data["objdistback"])
            
            #Create header
            logheader = "[{0}:{1}:{2}_{3}-{4}-{5}]".format(data["hour"], data["minute"], data["second"], data["year"], data["month"], data["day"]
            
            #Log
            self.logger.log(logmessage, logheader)

if __name__ == "__main__":
    
    #Create mainclass object
    main = Main()
    
    #Mainloop
    main.mainloop()
            
