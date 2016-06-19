#Simple logger class

#Imports
import os
import datetime
import gzip

#Main class
class Logger():
    
    #Initialiser
    def __init__(self, directory):
        
        #"Closed" state variable
        self.closed = False
        
        #Create filename
        self.filename = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log')
    
        #Create file path
        self.filepath = os.path.join(directory, filename)
        
        #Create file object
        self.file = gzip.GzipFile(self.filepath, "wb")
        
        #Write header
        self.file.write("{0} Began logging to {1}\n".format(datetime.datetime.now().strftime('[%Y-%m-%d_%H-%M-%S]'), self.filepath))
        self.file.flush()
    
    #Logs to file
    def log(self, message, header):
        
        if not self.closed:
            #Create message
            message = "{0} {1}\n".format(header, message)
        
            #Write message to file
            self.file.write(message)
            self.file.flush()
        else:
            raise Exception("Writing to a closed log file is forbidden")
    
    #Closes the file
    def close(self):
        
        self.file.close()
        self.closed = True
        
    
        
        