#Camera handler


#Imports
import picamera
import time
import threading
import os
import traceback
import datetime

#Camera handler class
class CameraHandler():
    
    #Init
    def __init__(self, logger):
        
        #Init variables
        self.file_name = None
        self.filepath = None
        self.file = None
        self.thread = None
        self.flush_thread = None
        self.logger = logger
        self.camera = None
        
        #Log
        self.logger.log("Camera handler started", "INFO")
        
        
    #Begins recording threads
    def begin_recording(self, directory = "/mnt/missiondata/video/"):
        
        #Init camera
        self.camera = picamera.PiCamera()
        self.logger.log("Camera powered on", "INFO")
        
        #Set up camera
        self.camera.vflip = True
        self.camera.resolution = (1920, 1080)
        self.camera.framerate = 25
        
        #Initialise highest video file number
        highest = 0
        
        #Find highest log file number
        try:
                 
            #Check if dir exists
            if not os.path.isdir(directory): os.makedirs(directory)
                
            #Check if usb is mounted
            if os.path.ismount("/mnt/missiondata"):
                
                #Iter through files
                for file_name in os.listdir(directory):  
                    
                    #Check that file takes form of *.*
                    if len(file_name.split(".")) == 2:
                        
                        #Check that file is log file 
                        if file_name.split(".")[1] == "h264":
                            
                            #Check that the filename is numerical
                            if file_name.split(".")[0].isdigit():
                            
                                #Check if filename is bigger than highest
                                if int(file_name.split(".")[0]) > highest:
                                    
                                    #If so, set highest to that
                                    highest = int(file_name.split(".")[0])
                                
            #Not mount point: fall back to /home/pi/missiondata
            else:
                
                #Fallback dir
                directory = "/home/pi/missiondata/video"
                
                #Check if dir exists
                if not os.path.isdir(directory): os.makedirs(directory)
                
                #Iter through files
                for file_name in os.listdir(directory):  
                    
                    #Check that file takes form of *.*
                    if len(file_name.split(".")) == 2:
                        
                        #Check that file is log file 
                        if file_name.split(".")[1] == "h264":
                            
                            #Check that the filename is numerical
                            if file_name.split(".")[0].isdigit():
                                
                                #Check if filename is bigger than highest
                                if int(file_name.split(".")[0]) > highest:
                                    
                                    #If so, set highest to that
                                    highest = int(file_name.split(".")[0])
            
            #Set file_name
            self.file_name = datetime.datetime.now().strftime('{0}.h264'.format(str(highest+1)))
            
        except:
            
            self.file_name = "0.h264"
            self.logger.log("Exception while attempting to begin camera recording:", "WARN")
            self.logger.log(traceback.format_exc(), "WARN")
    
        #Create file path
        self.filepath = os.path.join(directory, self.file_name)
        
        #Create file object
        self.file = open(self.filepath, "wb")
        
        #Create thread
        self.thread = threading.Thread(target = self.wait_recording)
        self.thread.daemon = True
        self.thread.start()
        
        #Create flush thread
        self.flush_thread = threading.Thread(target = self.flush_thread)
        self.flush_thread.daemon = True
        self.flush_thread.start()
        
        self.logger.log("Camera began recording to \"{0}\"".format(self.filepath), "INFO")
    
    #Flushes recording file
    def flush_thread(self):
        
        #Loop
        while True:
            
            #Attempt to flush and wait
            try:
                
                #Flush file
                self.file.flush()
                
                #Log
                self.logger.log("Video file flushed", "INFO")
            
            #Break loop
            except:
                
                #Log and break
                self.logger.log("Video flushing stopped:", "WARN")
                self.logger.log(traceback.format_exc(), "WARN")
                self.logger.log("Was the file closed?", "WARN")
                
                #Stop recording
                self.stop_recording()
                
                break
    
    #Begins, waits for 2h, and stops recording
    def wait_recording(self):

        #Begin recording
        self.camera.start_recording(self.file, format = "h264", quality = 25)
        
        #Let camera warm up
        time.sleep(2)
        
        #Record
        while 1: self.camera.wait_recording(2 * 60 * 60)
        
    def stop_recording(self):
        
        #Stop recording
        self.camera.stop_recording()
        self.camera.close()
        self.logger.log("Stopped recording explicitly", "INFO")
