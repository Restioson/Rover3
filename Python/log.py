#Simple logger class

#Imports
import os
import datetime
import lzma

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
            
            if os.path.isdir(directory):
                
                for file_name in os.listdir(directory):  
                
                    if len(file_name.split(".")) == 3:
                        
                        if file_name.split(".")[1] == "log" and file_name.split(".")[2] == "lzma":
                        
                            if int(file_name.split(".")[0]) > highest:
                                
                                highest = int(file_name.split(".")[0])
                        
            else:
                os.makedirs(directory)
                highest = -1
            
            #Set file_name
            self.file_name = datetime.datetime.now().strftime('{0}.log.lzma'.format(str(highest+1)))
            
        except Exception as e:
            error = e
            self.file_name = "0.log.lzma"
    
        #Create file path
        self.filepath = os.path.join(directory, self.file_name)
        
        
        #Create file object
        self.file = lzma.LZMAFile(self.filepath, "wb")
        self.uncompressed_file = open(os.path.join(directory, "current.log"), "w")
        
        #Begin log file
        self.log("Began logging to {2}\n".format(self.filepath), "INFO")
        self.log("Using system time; GPS time not acquired yet. Time may be inaccurate\n", "WARN")
        
        #Error occured
        if error:
            
            self.log("Exception while attempting to open log file: {0}".format(str(error.args)), "WARN")
    
    #Logs to file
    def log(self, message,  tag = "INFO"):
        
        if not self.closed:
            
            #Create header
            header = datetime.datetime.now().strftime('[%Y-%m-%d_%H-%M-%S]')
            
            #Create message
            message = "{0} [{1}] {2}\n".format(header, tag, message)
        
            #Write message to file
            self.file.write(message.encode("utf-8"))
            self.file.flush()
            self.uncompressed_file.write(message)
            self.uncompressed_file.flush()
            
        else:
            
            print("{0} [ERROR] Log file has been closed, but an attempt to log has been made!".format(datetime.datetime.now().strftime('[%Y-%m-%d_%H-%M-%S]')))
    
    
    #Closes the file
    def close(self):
        
        self.log("Log file is being closed", "INFO")
        self.file.close()
        self.closed = True
