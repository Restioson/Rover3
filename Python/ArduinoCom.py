import Rover3
import serial
import time
import thread
import sys

ser = serial.Serial('/dev/ttyAMA0',57600,timeout=1.5)
ser.readline()
state = 'ON'
gps = Rover3.Rover3()
f = ''
def check():
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
thread.start_new_thread(check,())
mainloop()
