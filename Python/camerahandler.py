#Camera handler


#Imports
import picamera
import time
import threading
import os

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
        
        #Init camera
        self.camera = picamera.PiCamera()
        
        self.logger.log("Camera powered on", "INFO")
        
        #Set up camera
        self.camera.vflip = True
        self.camera.resolution = (1920, 1080)
        self.camera.framerate = 25
        
        #Log
        self.logger.log("Camera handler started", "INFO")
        
        
    #Begins recording threads
    def begin_recording(self, directory = "/mnt/missiondata/video/"):
        
        #Find highest video file number
        highest = 0
        try:
            
            if os.path.isdir(directory):
                
                for file_name in os.listdir(directory):  
                
                    if int(file_name.split(".")[0]) > highest:
                        highest = int(file_name.split(".")[0])
                        
            else:
                os.makedirs(directory)
            
            #Set file_name
            self.file_name = datetime.datetime.now().strftime('{0}.h264'.format(str(highest + 1)))
            
        except Exception as error:
            self.file_name = "0.h264"
            self.logger.log("Error: {0}".format(str(error.args)), "WARN")
    
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
                
                #Sleep 1 second
                time.sleep(1)
            
            #Break loop
            except Exception as error:
                
                #Log and break
                self.logger.log("Video flushing stopped: {0}".format(str(error.args)), "ERROR")
                break
    
    #Begins, waits for 2h, and stops recording
    def wait_recording(self):
        
        #Begin recording
        self.camera.start_recording(self.file, format = "h264", quality = 25)
        
        #Let camera warm up
        time.sleep(2)
        
        #Wait for recording to finish
        self.camera.wait_recording(2 * 60 * 60)
        
        #Stop recording
        self.camera.stop_recording()
        
        #Close file
        self.file.close()
    
        #Log
        self.logger.log("Stopped recording as timer finished", "INFO")
        
    def stop_recording(self):
        
        #Stop recording
        self.camera.stop_recording()
        self.logger.log("Stopped recording explicitly")
