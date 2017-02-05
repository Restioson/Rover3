#Simple logger class

#Imports
import os
import datetime
import lzma
import traceback

#Logger class   
class Logger():
    
    def __init__(self, directory):
        
        #File closed state variable
        self.closed = False
        
        #Initialise highest log file number starter value
        highest = 0
        
        #Error occured?
        error = False
        
        #Find highest log file number
        try:
            
            #Error happened?
            error_happened = False
                 
            #Check if dir exists
            if not os.path.isdir(directory): os.makedirs(directory)
                
            #Check if usb is mounted
            if os.path.ismount("/mnt/missiondata"):
                
                #Iter through files
                for file_name in os.listdir(directory):  
                        
                    #Check that file takes form of *.*
                    if len(file_name.split(".")) == 2:
                        
                        #Check that file is log file 
                        if file_name.split(".")[1] == "log":
                            
                            #Check that the filename is numerical
                            if file_name.split(".")[0].isdigit():
                            
                                #Check if filename is bigger than highest
                                if int(file_name.split(".")[0]) > highest:
                                    
                                    #If so, set highest to that
                                    highest = int(file_name.split(".")[0])
                                
            #Not mount point: fall back to /home/pi/missiondata
            else:
                
                #Fallback dir
                directory = "/home/pi/missiondata/log"
                
                #Check if dir exists
                if not os.path.isdir(directory): os.makedirs(directory)
                
                #Iter through files
                for file_name in os.listdir(directory):  
                    
                    #Check that file takes form of *.*
                    if len(file_name.split(".")) == 2:
                        
                        #Check that file is log file 
                        if file_name.split(".")[1] == "log":
                            
                            
                            #Check that the filename is numerical
                            if file_name.split(".")[0].isdigit():
                                
                                #Check if filename is bigger than highest
                                if int(file_name.split(".")[0]) > highest:
                                    
                                    #If so, set highest to that
                                    highest = int(file_name.split(".")[0])
            
            #Set file_name
            self.file_name = datetime.datetime.now().strftime('{0}.log'.format(str(highest+1)))
            
        #Exception
        except:
            
            error_happened = True
            error = traceback.format_exc()
            self.file_name = "0.log"

        #Create file path
        self.filepath = os.path.join(directory, self.file_name)
        
        
        #Create file object
        self.file = open(self.filepath, "wb")
        
        #Begin log file
        self.log("Began logging to {0}".format(self.filepath), "INFO")
        self.log("Using system time; GPS time not acquired yet. Time may be inaccurate", "WARN")
        
        #Error occured
        if error_happened:
            
            self.log("Exception while attempting to open log file:", "WARN")
            self.log(error, "WARN")
            self.log("Is the flash drive mounted? Do we have write-access?", "WARN") 
    
    #Logs to file
    def log(self, message,  tag = "INFO", newline = "\n"):
        
        if not self.closed:
            
            #Create header
            header = datetime.datetime.now().strftime('[%Y-%m-%d_%H-%M-%S]')
            
            #Create message
            message_formatted = "{0} [{1}] {2}{3}".format(header, tag, message, newline)
        
            #Write message to file
            self.file.write(message_formatted.encode("utf-8"))
            self.file.flush()
            
            #Print to stdout
            print("{0} [{1}] {2}".format(header, tag, message))
            
        else:
            
            print("{0} [ERROR] Log file has been closed, but an attempt to log has been made!".format(datetime.datetime.now().strftime('[%Y-%m-%d_%H-%M-%S]')))
            return False
    
    
    #Closes the file
    def close(self):
        
        self.log("Log file is being closed", "INFO")
        self.file.close()
        self.closed = True
