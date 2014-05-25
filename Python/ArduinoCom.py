import Rover3
import serial
import time
import datetime
import os
import thread
import sys
print('Starting...')
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
		rdln = ser.readline()
		if rdln == 'BREAK serial':
			state == 'OFF'
			ser.write('BREAK serial confirm')
			print('Ending (got "BREAK serial")...')
			sys.exit(0)
		else:
			Rover.data = rdln
			Rover.parse()
	except KeyboardInterrupt:
		f.close()
		ser.close()
		print('Ending (got KeyboardInterrupt)...')
		sys.exit(0)
def mainloop():
	try:
		f = open(os.getcwd()+'/log/'+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log'), 'w')
	except IOError:
		os.system('mkdir ./log/')
		f = open(os.getcwd()+'/log/'+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log'), 'w')
	while state=='ON':
		try:
			update()
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
			ser.close()
			print('Ending (got KeyboardInterrupt)...')
			sys.exit(0)
		
mainloop()
