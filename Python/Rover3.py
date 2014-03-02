import sys
import time
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
		self.time_ = '' 
		self.time = ''
	
	def parse(self):
		string = self.data
		string = string.split()
		self.tag = string.pop(0)
		try:
			string = ''+string[0]+' '+string[1]
		except:
			string = ''+string[0]
		if self.tag == 'GPS':
			string = string.replace(',',' ')
			string = string.split()
			self.latitude = string.pop(0)
			self.longitude = string.pop(0)
			self.course = string.pop(0)
			self.speed = string.pop(0)
			self.heading = string.pop(0)
		
		if self.tag == 'TIME':
			string = string.replace(':',' ')
			string = string.replace('-',' ')
			string = string.split()
			self.year = int(string.pop(0))
			self.month = int(string.pop(0))
			self.day = int(string.pop(0))
			self.hour = int(string.pop(0))
			self.minute = int(string.pop(0))
			self.second = int(string.pop(0))
			self.milisecond = int(string.pop(0))
			time_tuple = (self.year,self.month,self.day,self.hour,self.minute,self.second,self.milisecond)
			self.time_ = ('Year:'+str(self.year)+' Month:'+str(self.month)+' Day:'+str(self.day)+' Hour:'+str(self.hour)+' Minute:'+str(self.minute)+' Second:'+str(self.second))
