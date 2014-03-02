import sys
import time
class Rover3():
	def __init__(self):
		##Misc.
		self.tag = ''
		self.data = ''
		##Navigation
		self.latitude = ''
		self.longitude = ''
		self.course = ''
		self.speed = ''
		self.heading = ''
		##Time
		self.year = ''
		self.month = ''
		self.day = ''
		self.hour = ''
		self.minute = ''
		self.second = ''
		self.millisecond = ''
		self.time_ = '' 
		self.time = ''
		##Environment
		self.temperature = ''
		self.pitch = ''
		self.roll = ''
		self.humidity
		self.objdistfront
		
	def parse(self):
		string = self.data
		string = string.split()
		self.tag = string.pop(0)
		try:
			string = ''+string[0]+' '+string[1]
		except:
			string = ''+string[0]
		if self.tag == 'GPS':
			#Parse the GPS readings
			string = string.replace(',',' ')
			string = string.split()
			#Record the values
			self.latitude = string.pop(0) #Latitude, positive = 
			self.longitude = string.pop(0)
			self.course = string.pop(0)
			self.speed = string.pop(0)
			self.heading = string.pop(0)
		
		if self.tag == 'TIME':
			#Parse the input
			string = string.replace(':',' ')
			string = string.replace('-',' ')
			string = string.split()
			#Record the values
			self.year = int(string.pop(0))	#Year
			self.month = int(string.pop(0))	#Month in '01' format eg. June = 06
			self.day = int(string.pop(0))	#Day of month, eg 10 (month)
			self.hour = int(string.pop(0))	#Hour, eg. 24
			self.minute = int(string.pop(0))#Minutes ,pretty self-explanatory
			self.second = int(string.pop(0))#Seconds...you MUST know this one!
			self.millisecond = int(string.pop(0))#Milliseconds!
			time_tuple = (self.year,self.month,self.day,self.hour,self.minute,self.second,self.millisecond)#A tuple of all the times!
			self.time_ = ('Year:'+str(self.year)+' Month:'+str(self.month)+' Day:'+str(self.day)+' Hour:'+str(self.hour)+' Minute:'+str(self.minute)+' Second:'+str(self.second))#A string time...
		
		if self.tag == "ENVIRON":
			#Parse the environment info
			string = string.split()
			self.temperature = string[0]  #Temperature in degrees Celsius
			self.humidity = string[1]
			self.pitch = string[2]
			self.roll = string[3]
			self.objdistfront = string[4]
			
		if self.tag == "LOG":
			#Parse the log data
			self.log = self.log + string
			