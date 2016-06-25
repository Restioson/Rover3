#Imports
import time
import log
import arduinoserial
import SocketServer as socketserver
import subprocess
import threading

#Main class
class Main():
    
    #Initialiser
    def __init__(self):
    
        #Stop UV4L
        subprocess.call(["/etc/init.d/uv4l_raspicam", "stop"])
        
        #Server
        self.server = socketserver.TCPServer(("0.0.0.0", 1895), RequestHandler)
        
        #Initialise logger
        self.logger = log.Logger("/home/pi/log/")
        
        #Initialise serial
        try:    
            self.serial = arduinoserial.ArduinoSerialConnection()
        except:
            self.serial = False
    
    #Mainloop of program
    def mainloop(self):
        
        #Start server thread
        serverThread = threading.Thread(target=self.server.serve_forever)
        serverThread.daemon = True
        serverThread.start()
        
        #Loop
        if self.serial != False:
            while True:
            
                #Waits for data and then parses
                data = self.serial.parse()
            
                #Create message format
                logmessageFormat = "Latitude: {0}\nLongitude: {1}\nAltitude: {2} Course: {3}\nHeading: {4}\nSpeed: {5}\nTemperature: {5}\nHumidity: {7}\nPitch: {8}\nRoll: {9}\nObjectDistanceFront: {10}\nObjectDistanceBack: {11}\nOther: {12}"
            
                #Create message
                logmessage = messageFormat.format(data["latitude"], data["longitude"], data["altitude"], data["course"], data["heading"], data["speed"], data["temperature"], data["humidity"], data["pitch"], data["roll"], data["objdistfront"], data["objdistback"], data["other"])
            
                #Create header
                logheader = "[{0}:{1}:{2}_{3}-{4}-{5}]".format(data["hour"], data["minute"], data["second"], data["year"], data["month"], data["day"])
                
                #Log
                self.logger.log(logmessage, logheader)
        else:
            while True: pass #Keep daemon running

            
#Request handler class
class RequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024)
        
        if self.data == "start":
            subprocess.call(["sudo", "uv4l", "--config-file=/etc/uv4l/uv4l_raspicam.conf"])
        
        elif self.data == "stop":
            subprocess.call(["/etc/init.d/uv4l_raspicam", "stop"])

            
        

if __name__ == "__main__":
    
    #Create mainclass object
    main = Main()
    
    #Mainloop
    main.mainloop()
            
