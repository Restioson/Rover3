#Simple logger class

#Imports
import os
import datetime
import gzip
import enum

#Logger class   
class Logger():
    
    def __init__(self, directory):
        
        #File closed state variable
        self.closed = False
        
        #Initialise highest log file number starter value
        highest = 0
        
        #Find highest log file number
        try:
            
            if os.path.isdir(directory):
                
                for file_name in os.listdir(directory):  
                
                    if int(file_name.split(".")[0]) > highest:
                        highest = int(file_name.split(".")[0])
                        
            else:
                os.makedirs(directory)
                highest = 0
            
            #Set file_name
            self.file_name = datetime.datetime.now().strftime('{0}.log.gz'.format(str(highest+1)))
        except:
            self.file_name = "log.log.gz"
    
        #Create file path
        self.filepath = os.path.join(directory, self.file_name)
        
        #Create file object
        self.file = gzip.GzipFile(self.filepath, "wb")
        
        #Begin log file
        self.file.write("{0} [{1}] Began logging to {2}\n".format(datetime.datetime.now().strftime('[%Y-%m-%d_%H-%M-%S]'), "INFO", self.filepath))
        self.file.write("{0} [{1}] Using system time; GPS time not acquired yet. Time may be inaccurate".format(datetime.datetime.now().strftime('[%Y-%m-%d_%H-%M-%S]'), "INFO"))
        self.file.flush()
    
    #Logs to file
    def log(self, message, current_datetime = datetime.datetime.now(), tag = "INFO"):
        
        if not self.closed:
            
            #Create header
            header = current_datetime.strftime('[%Y-%m-%d_%H-%M-%S]')
            
            #Create message
            message = "{0} [{1}] {2}\n".format(header, tag, message)
        
            #Write message to file
            self.file.write(message)
            self.file.flush()
            
        else:
            raise Exception("Cannot write to a closed log file!")
    
    
    #Closes the file
    def close(self):
        
        self.file.close()
        self.closed = True
