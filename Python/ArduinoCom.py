import Rover3
import serial
import time
import thread
import sys
import utils

try:
	port = sys.argv[1]
except:
	port = '/dev/ttyAMA0'

ser = serial.Serial(port, 57600, timeout=1.5) #Create a serial object
ser.readline() #Let the protocol handshake...

state = 'ON' #State of the mainloop

gps = Rover3.Rover3() #Make an instance of the 'Rover3' class for getting the GPS readings
timegps = Rover3.Rover3() #Make an instance of the 'Rover3' class for getting the GPS time readings
evrion = Rover3.Rover3() #Make an instance of the 'Rover3' class for getting the environment info (NOT YET IMPLEMENTED ON THE ARDUINO SIDE)


f = ''
def update():
	try:
		while True:
			rdln = ser.readline()
			if rdln != 'BREAK serial':
				gps.data = rdln
				gps.parse()
			if rdln == 'BREAK serial':
				state == 'OFF'
				ser.write('BREAK serial confirm')
				sys.exit()
	except KeyboardInterrupt:
		f.close()
		ser.close()		
def mainloop():
	f = open('RoverMission.log','ab')
	while state=='ON':
		try:
			time.sleep(10)	
			f.write('Latitude: '+gps.latitude)
			f.write(' Longitude: '+gps.longitude)
			f.write(' Course: '+gps.course)
			f.write(' Speed: '+gps.speed)
			f.write(' Heading: '+gps.heading)
			f.write('\n')
			print('Latitude:'+gps.latitude)
			print('Longitude:'+gps.longitude)
			print('Course:'+gps.course)
			print('Speed:'+gps.speed)
			print('Heading:'+gps.heading)
		except KeyboardInterrupt:
			f.close()
			break
			ser.close()
