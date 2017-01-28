#Camera handler


#Imports
import picamera
import time
import threading
import os

#Camera handler class
class CameraHandler():
    
    #Init
    def __init__(self):
        
        #Init variables
        self.file_name = None
        self.filepath = None
        self.file = None
        self.thread = None
        self.flush_thread = None
        
        #Init camera
        self.camera = picamera.PiCamera()
        
        #Set up camera
        self.camera.vflip = True
        self.camera.resolution = (1920, 1080)
        self.camera.framerate = 25
        
    #Begins recording threads
    def begin_recording(self, directory = "/mnt/missiondata/video/"):
        
        #Find highest video file number
        try:
            
            if os.path.isdir(directory):
                
                for file_name in os.listdir(directory):  
                
                    if int(file_name.split(".")[0]) > highest:
                        highest = int(file_name.split(".")[0])
                        
            else:
                os.makedirs(directory)
                highest = 0
            
            #Set file_name
            self.file_name = datetime.datetime.now().strftime('video{0}.h264'.format(str(highest + 1)))
            
        except:
            self.file_name = "video.h264"
    
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
            
            try:
                #Flush file
                self.file.flush()
            
                #Sleep 1 second
                time.sleep(1)
            
            except:
                break
    
    #Begins, waits for, and stops recording
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
