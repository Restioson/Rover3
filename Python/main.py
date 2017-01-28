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
        self.logger = log.Logger("/mnt/missiondata/log")
        
        #Initialise serial
        self.serial_data_handler = datahandler.SerialDataHandler(self.logger)
            
        #Initialise camera handler
        self.camera_handler = camerahandler.CameraHandler()
        
        #Initialise IP client handler
        self.ip_client_handler = clienthandler.IPClientHandler()
        
        #Stop UV4L (if running)
        subprocess.call(["/etc/init.d/uv4l_raspicam", "stop"])
        
        #Begin videoing
        self.camera_handler.begin_recording()
    
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
