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
		rdln2 = ser.readline()
		if rdln == 'BREAK serial':
			state == 'OFF'
			ser.write('BREAK serial confirm')
			print('Ending (got "BREAK serial")...')
			sys.exit(0)
		else:
			Rover.data = rdln
			Rover.parse()
			Rover.data = rdln2
			Rover.parse()
	except KeyboardInterrupt:
		f.close()
		ser.close()
		print('Ending (got KeyboardInterrupt)...')
		sys.exit(0)
def mainloop():
	try:
		f = open('/home/pi/log/'+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log'), 'w')
	except IOError:
		os.system('mkdir ./log/')
		f = open(os.getcwd()+'/log/'+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log'), 'w')
	while state=='ON':
		try:
			update()
			f.write(' Time: '+'Year:'+str(Rover.year)+' Month:'+str(Rover.month)+' Day:'+str(Rover.day)+' Hour:'+str(Rover.hour)+' Minute:'+str(Rover.minute)+' Second:'+str(Rover.second))
			f.write(' Latitude: '+Rover.latitude)
			f.write(' Longitude: '+Rover.longitude)
			f.write(' Course: '+Rover.course)
			f.write(' Speed: '+Rover.speed)
			f.write(' Heading: '+Rover.heading)
			f.write(' Raw Data: '+Rover.data)
			f.write('\n')
			f.flush()

		except KeyboardInterrupt:
			f.close()
			ser.close()
			print('Ending (got KeyboardInterrupt)...')
			sys.exit(0)
		
mainloop()
