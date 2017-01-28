#Imports
import log
import datahandler
import camerahandler
import clienthandler
import subprocess
import threading

#Main class
class Main():
    
    #Initialiser
    def __init__(self):
        
        #Initialise logger
        self.logger = log.Logger("/home/pi/log/")
        
        #Initialise serial
        self.serial_data_handler = datahandler.SerialDataHandler()
            
        #Initialise camera handler
        self.camera_handler = camerhandler.CameraHandler()
        
        #Initialise IP client handler
        self.ip_client_handler = clienthandler.IPClientHandler()
        
        #Stop UV4L (if running)
        subprocess.call(["/etc/init.d/uv4l_raspicam", "stop"])
    
    #Mainloop of program
    def main_loop(self):
        
        #Loop
        while True:
            
            #Handle serial data
            self.serial_data_handler.handle()  
        
#Run program
if __name__ == "__main__":
    
    #Create mainclass object
    main = Main()
    
    #main_loop
    main.main_loop()
