#!/usr/bin/python3
#Imports
import log
import datahandler
import camerahandler
import clienthandler
import subprocess
import threading
import os
import traceback
import sys
import time

#Main class
class Main():
    
    #Initialiser
    def __init__(self):
        
        #Check if root
        if os.geteuid() != 0:
            
            #Print to stderr and exit
            sys.stderr.write("Script must be run as root!\n")
            sys.exit(1)
        
        #Check if usb is mounted
        if os.path.ismount("/mnt/missiondata"):
            
            #Initialise self.logger
            self.logger = log.Logger("/mnt/missiondata/log")
            
            #Initialise camera handler
            self.camera_handler = camerahandler.CameraHandler(self.logger)
        
        #If not, fall back to SD card:
        else:
            
            #Initialise self.logger
            self.logger = log.Logger("/mnt/missiondata/log")
            
            #Initialise camera handler
            self.camera_handler = camerahandler.CameraHandler(self.logger)

        
        #Initialise serial
        self.serial_data_handler = datahandler.SerialDataHandler(self.logger, self)
        
        #Initialise IP client handler
        self.ip_client_handler = clienthandler.IPClientHandler(self.logger)
        
        #Stop UV4L (if running)
        try:
            
            subprocess.call(["/etc/init.d/uv4l_raspicam", "stop"])
            self.logger.log("UV4L stopped", "INFO")
        
        except Exception:
            
            self.logger.log("Exception while attempting to stop UV4L:", "WARN")
            self.logger.log(traceback.format_exc(), "WARN")
            self.logger.log("Is UV4L installed?", "WARN")
        
        #Begin videoing
        self.camera_handler.begin_recording()
        
        self.logger.log("Rover3 script initialised", "INFO")
        
        #Block until connected to Arduino
        while True: 
        
            if self.serial_data_handler.connect_to_serial(): break
            time.sleep(5)
        
    #Mainloop of program
    def main_loop(self):
        
        #Loop
        while True:
            
            #Handle serial data
            try:
                
                self.serial_data_handler.handle()
            
            #Error!
            except:
                
                self.logger.log("Unhandled exception in main loop while handling serial data:", "ERROR")
                self.logger.log(traceback.format_exc(), "ERROR", newline = "")
        
    #Shutdown
    def shutdown(self):
        
        #Log
        self.logger.log("Shutting down...", "INFO")
        
        #Close camera
        try: 
            
            #Stop recording
            self.camera_handler.stop_recording()
            
            #Log
            self.logger.log("Camera successfully shut down", "INFO")
            
        except:
            
            self.logger.log("Error while attempting to shut down camera:", "ERROR")
            self.logger.log(traceback.format_exc(), "ERROR", newline = "")
            
        #Close log file
        try: self.logger.close()
        
        except:
            
            self.logger.log("Error while attemtping to close log file:", "ERROR")
            log_attempt =self.logger.log(traceback.format_exc(), "ERROR", newline = "")
            
            if log_attempt == False:
                
                print("Error while attemtping to close log file:")
                print(traceback.format_exc(), end = "")
        
        #Send shutdown command
        subprocess.call(["sudo", "halt"])
        
        #Exit process
        sys.exit(0)
        
        
        
        
#Run program
if __name__ == "__main__":
    
    #Create mainclass object and run mainloop
    try:
        
        main = Main()
        main.main_loop()
    
    #Error
    except Exception as error:
        
        print("Unhandled Exception in initialisation:", flush = True)
        print(traceback.format_exc())
