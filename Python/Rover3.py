import sys
import datetime
import ctypes
import ctypes.utils
import time

### _linux_set_time taken from stackoverflow.com

def _linux_set_time(time_tuple):
	CLOCK_REALTIME = 0
 	class timespec(ctypes.Structure):
       		 _fields_ = [("tv_sec", ctypes.c_long),
                   	    ("tv_nsec", ctypes.c_long)]

    		librt = ctypes.CDLL(ctypes.util.find_library("rt"))
	
    		ts = timespec()
    		ts.tv_sec = int( time.mktime( datetime.datetime( *time_tuple[:6]).timetuple() ) )
   	 	ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond

    		# http://linux.die.net/man/3/clock_settime
    		librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))

class Rover3():
	def __init__(self):
		self.tag = ''
		self.data = ''
		self.latitude = ''
		self.longitude = ''
		self.course = ''
		self.speed = ''
		self.heading = ''
		self.year = ''
		self.month = ''
		self.day = ''
		self.hour = ''
		self.minute = ''
		self.second = ''
		self.milisecond = ''
	
	def parse(self):
		string = self.data
		string = string.replace(',',' ')
		string = string.split()
		
		self.tag = string.pop(0)
		
		if self.tag == 'GPS':
			self.latitude = string.pop(0)
			self.longitude = string.pop(0)
			self.course = string.pop(0)
			self.speed = string.pop(0)
			self.heading = string.pop(0)
		
		if self.tag == 'TIME':
			self.year = int(string.pop(0))
			self.month = int(string.pop(0))
			self.day = int(string.pop(0))
			self.hour = int(string.pop(0))
			self.minute = int(string.pop(0))
			self.second = int(string.pop(0))
			self.milisecond = int(string.pop(0))
			time_tuple = (self.year,self.month,self.day,self.hour,self.minute,self.second,self.milisecond)
			_linux_set_time(time_tuple)
