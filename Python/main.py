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
        self.serial_data_handler = datahandler.SerialDataHandler(self.logger)
        
        #Initialise IP client handler
        self.ip_client_handler = clienthandler.IPClientHandler(self.logger)
        
        #Stop UV4L (if running)
        try:
            
            subprocess.call(["/etc/init.d/uv4l_raspicam", "stop"])
            self.logger.log("UV4L stopped", "INFO")
        
        except Exception as error:
            
            self.logger.log("Exception while attempting to stop UV4L: \"{0}\". UV4L may not be installed".format(str(error.args)), "WARN")
        
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
                self.logger.log(traceback.format_exc(), "ERROR")
        
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
