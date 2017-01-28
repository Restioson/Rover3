#Imports
import log
import datahandler
import camerahandler
import clienthandler
import subprocess
import threading
import os

#Main class
class Main():
    
    #Initialiser
    def __init__(self):
        
        #Check if usb is mounted
        if os.path.ismount("/mnt/missiondata"):
            
            #Initialise logger
            self.logger = log.Logger("/mnt/missiondata/log")
            
            #Initialise camera handler
            self.camera_handler = camerahandler.CameraHandler(self.logger)
        
        #If not, fall back to SD card:
        else:
            
            #Initialise logger
            self.logger = log.Logger("/home/pi/missiondata/log")
            
            #Initialise camera handler
            self.camera_handler = camerahandler.CameraHandler(self.logger, directory = "/home/pi/missiondata/video")

        
        #Initialise serial
        self.serial_data_handler = datahandler.SerialDataHandler(self.logger)
        
        #Initialise IP client handler
        self.ip_client_handler = clienthandler.IPClientHandler(self.logger)
        
        #Stop UV4L (if running)
        subprocess.call(["/etc/init.d/uv4l_raspicam", "stop"])
        
        #Begin videoing
        self.camera_handler.begin_recording()
        
        logger.log("Rover3 script initialised", "INFO")
    
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
