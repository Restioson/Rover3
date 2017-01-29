#Handles IP client


#Imports

try: import SocketServer as socketserver #Python 2
except: import socketserver #Python 3

import threading

#Handler class
class IPClientHandler():

    #Init
    def __init__(self, logger):
        
        #Logger
        self.logger = logger
        
        #Initialise SocketServer to listen to incoming commands from client
        self.server = socketserver.TCPServer(("0.0.0.0", 1895), RequestHandler)
          
        #Start server thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        #Log
        self.logger.log("IP Client Handler started", "INFO")
        
#Request handler class
class RequestHandler(socketserver.BaseRequestHandler):

    def handle(self, logger):
        self.data = self.request.recv(1024)
        self.logger.log("Got packet from IP client: \"{0}\"".format(str(self.data)), "INFO")
        
        #Start streaming
        if self.data == "start":
            
            subprocess.call([
                "sudo", "uv4l", 
                "--auto-video_nr",
                "--driver", "raspicam", 
                "--encoding", "h264", 
                "--width", "640", 
                "--height", "480", 
                "--vflip", "on", 
                "--framerate", "25", 
                "--server-option", "'--port=8080'",
                "--server-option", "'--max-queued-connections=5'",
                "--server-option", "'--max-streams=5'",
                "--server-option", "'--max-threads=20'"
             ])
             
            self.logger.log("Started UV4L streaming", "INFO")
        
        #Stop UV4L stream
        elif self.data == "stop":
            
            subprocess.call(["/etc/init.d/uv4l_raspicam", "stop"])
            self.logger.log("Stopped UV4l streaning", "INFO")
        
        #Invalid command
        else:
            
            self.logger.log("Invalid command: \"{0}\"".format(str(self.data)), "WARN")
            
            