#Imports
import datetime
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
        
        #SocketServer to listen to incoming commands from client
        self.server = socketserver.TCPServer(("0.0.0.0", 1895), RequestHandler)
        
        #Initialise logger
        self.logger = log.Logger("/home/pi/log/")
        
        #Initialise serial
        try:    
            self.serial = arduinoserial.ArduinoSerialConnection()
        except:
            self.serial = False
    
    #main_loop of program
    def main_loop(self):
        
        #Start server thread
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        #Loop
        if self.serial != False:
            while True:
            
                #Waits for data and then parses
                data = self.serial.parse()
            
                #Create data log format
                log_message_format = "".join([
                    "Latitude: {0}\n",
                    "Longitude: {1}\n",
                    "Altitude: {2}\n",
                    "Course: {3}\n",
                    "Heading: {4}\n",
                    "Speed: {5}\n",
                    "Temperature: {5}\n",
                    "Humidity: {7}\n",
                    "Pitch: {8}\n",
                    "Roll: {9}\n",
                    "ObjectDistanceFront: {10}\n",
                    "ObjectDistanceBack: {11}\n",
                    "Other: {12}"
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
            
                #Create header
                logheader = "[{0}:{1}:{2}_{3}-{4}-{5}]".format(data["hour"], data["minute"], data["second"], data["year"], data["month"], data["day"])
                
                #Get time and create datetime object from it
                current_datetime = datetime.datetime(
                    data["year"], 
                    data["month"], 
                    data["day"], 
                    data["hour"], 
                    data["minute"], 
                    data["second"], 
                    data["day"]
                )
                
                #Log
                self.logger.log(logmessage, logheader)
        else:
            while True: pass #Keep daemon running

            
#Request handler class
class RequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024)
        
        print("Got packet: '{0}'".format(self.data))
        
        if self.data == "start":
            
            subprocess.call([
                "sudo", "uv4l", 
                "--auto-video_nr",
                "--driver", "raspicam", 
                "--encoding", "h264", 
                "--width", "640", 
                "--height", "480", 
                "--vflip", "on", 
                "--framerate", "30", 
                "--server-option", "'--port=8080'",
                "--server-option", "'--max-queued-connections=30'",
                "--server-option", "'--max-streams=5'",
                "--server-option", "'--max-threads=29'"
             ])
        
        elif self.data == "stop":
            subprocess.call(["/etc/init.d/uv4l_raspicam", "stop"])

            
        

if __name__ == "__main__":
    
    #Create mainclass object
    main = Main()
    
    #main_loop
    main.main_loop()
            
