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

Rover3 = Rover3.Rover3() #Make an instance of the 'Rover3' class


f = ''
def update():
	try:
		while True:
			rdln = ser.readline()
			if rdln != 'BREAK serial':
				if rdln != 'REC start' or rdln != 'REC end':
					Rover3.data = rdln
					Rover3.parse()
				if rdln == 'REC start':
					os.system('sudo raspivid -vf -n -o video.h264')
				if rdln == 'REC stop':
					os.system('sudo killall raspivid')
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
			f.write('Latitude: '+Rover3.latitude)
			f.write(' Longitude: '+Rover3.longitude)
			f.write(' Course: '+Rover3.course)
			f.write(' Speed: '+Rover3.speed)
			f.write(' Heading: '+Rover3.heading)
			f.write('\n')
			print('Latitude:'+Rover3.latitude)
			print('Longitude:'+Rover3.longitude)
			print('Course:'+Rover3.course)
			print('Speed:'+Rover3.speed)
			print('Heading:'+Rover3.heading)
		except KeyboardInterrupt:
			f.close()
			break
			ser.close()
