#Simple logger class

#Imports
import os
import datetime
import gzip

#Main class
class Logger():
    
    #Initialiser
    def __init__(self, directory):
        
        #File closed state variable
        self.closed = False
        
        #Initialise highest log file number starter value
        highest = 1
        
        #Find highest log file number
        try:
            if os.path.isdir(directory):
                for file_name in os.listdir(directory):  
                
                    #Taken from "tinyurl.com/numberInString", fmark's answer
                    if [int(character) for character in file_name.split() if character.isdigit()][0] > highest:
                        highest = [int(character) for character in file_name.split() if character.isdigit()][0]
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
        
        #Write header
        self.file.write("{0} Began logging to {1}\n".format(datetime.datetime.now().strftime('[%Y-%m-%d_%H-%M-%S]'), self.filepath))
        self.file.flush()
    
    #Logs to file
    def log(self, message, currentDatetime):
        
        if not self.closed:
            #Create message
            message = "{0} {1}\n".format(header, message)
        
            #Write message to file
            self.file.write(message)
            self.file.flush()
        else:
            raise Exception("Cannot write to a closed log file!")
    
    
    #Closes the file
    def close(self):
        
        self.file.close()
        self.closed = True
        
    
class DataLogger():
    
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
        
        #Write header
        self.file.write("{0} Began logging to {1}\n".format(datetime.datetime.now().strftime('[%Y-%m-%d_%H-%M-%S]'), self.filepath))
        self.file.flush()
    
    #Logs to file
    def log(self, data):
        
        if not self.closed:
            #Create message
            message = "{0} {1}\n".format(header, message)
        
            #Write message to file
            self.file.write(message)
            self.file.flush()
        else:
            raise Exception("Cannot write to a closed log file!")
    
    
    #Closes the file
    def close(self):
        
        self.file.close()
        self.closed = True