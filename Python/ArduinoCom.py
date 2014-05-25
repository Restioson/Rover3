import Rover3
import serial
import time
import datetime
import os
import thread
import sys
import utils #Unimplemented!

try:
	port = sys.argv[1]
except:
	port = '/dev/ttyAMA0'

ser = serial.Serial(port, 57600, timeout=1.5) #Create a serial object
ser.readline() #Let the protocol handshake...

state = 'ON' #State of the mainloop

Rover = Rover3.Rover3() #Make an instance of the 'Rover' class


f = ''
def update():
	try:
		while True:
			rdln = ser.readline()
			if rdln != 'BREAK serial':
				if rdln != 'REC start' or rdln != 'REC end':
					Rover.data = rdln
					Rover.parse()
			if rdln == 'BREAK serial':
				state == 'OFF'
				ser.write('BREAK serial confirm')
				sys.exit()
	except KeyboardInterrupt:
		f.close()
		ser.close()		
def mainloop():
	f = open(os.getcwd()+'/log/'+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log'), 'w')
	while state=='ON':
		try:
			time.sleep(10)	
			f.write(' Latitude: '+Rover.latitude)
			f.write(' Longitude: '+Rover.longitude)
			f.write(' Course: '+Rover.course)
			f.write(' Speed: '+Rover.speed)
			f.write(' Heading: '+Rover.heading)
			f.write(' Raw Data: '+Rover.data)
			f.write('\n')
			print('Latitude:'+Rover.latitude)
			print('Longitude:'+Rover.longitude)
			print('Course:'+Rover.course)
			print('Speed:'+Rover.speed)
			print('Heading:'+Rover.heading)
			print('Raw Data:'+Rover.data)
		except KeyboardInterrupt:
			f.close()
			break
			ser.close()
