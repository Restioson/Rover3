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
        
        #List files in directory
        
        #Highest log file number
        highest = 1
        
        #Find highest log file number
        try:
            if os.path.isdir(directory):
                for filename in os.listdir(directory):  
                    #Taken from "tinyurl.com/numberInString", fmark's answer
                    if [int(character) for character in filename.split() if character.isdigit()][0] > highest:
                        highest = [int(character) for character in filename.split() if character.isdigit()][0]
            else:
                os.makedirs(directory)
                highest = 0
            
            #Set filename
            self.filename = datetime.datetime.now().strftime('{0}.log.gz'.format(str(highest+1)))
        except:
            self.filename = "log.log.gz"
    
        #Create file path
        self.filepath = os.path.join(directory, self.filename)
        
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
        
    
        
        