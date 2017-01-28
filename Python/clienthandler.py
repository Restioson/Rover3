#Handles IP client


#Imports
import SocketServer as socketserver

#Handler class
class IPClientHandler():

    #Init
    def __init__(self):
        
        #Initialise SocketServer to listen to incoming commands from client
        self.server = socketserver.TCPServer(("0.0.0.0", 1895), RequestHandler)
          
        #Start server thread
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
#Request handler class
class RequestHandler(socketserver.BaseRequestHandler):

    def handle(self, logger):
        self.data = self.request.recv(1024)
        
        logger.log("Got packet from IP client: '{0}'".format(self.data), tag = "INFO")
        
        if self.data == "start":
            
            subprocess.call([
                "sudo", "uv4l", 
                "--auto-video_nr",
                "--driver", "raspicam", 
                "--encoding", "h264", 
                "--width", "640", 
                "--height", "480", 
                "--vflip", "on", 
                "--framerate", "30", 
                "--server-option", "'--port=8080'",
                "--server-option", "'--max-queued-connections=30'",
                "--server-option", "'--max-streams=5'",
                "--server-option", "'--max-threads=40'"
             ])
        
        elif self.data == "stop":
            subprocess.call(["/etc/init.d/uv4l_raspicam", "stop"])
