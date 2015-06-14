##This Code will connect to and emulate the remote control
import sys
import serial
import sys
import pygame
import thread
import time
print('Starting...')
port = 8

pygame.init()
ser = serial.Serial(int(port)-1, 115200, timeout=1.5) #Create a serial object
ser.readline() #Let the protocol handshake...
screen = pygame.display.set_mode((640,480))
pygame.display.set_caption('Rover Controller')
def read(a,b):
    global text
    while True:
        text = ser.read(512)
def alive(a,b):
    global ser
    while True:
        ser.write('a')
        time.sleep(1)
thread.start_new_thread(alive,('a','b'))
thread.start_new_thread(read,('a','b'))
myfont = pygame.font.SysFont("monospace", 15)
text = ''
surface = pygame.Surface((640,420))
surface.fill((0,0,0))
lastcmd = ''
while True: 
        for event in pygame.event.get(): #Event loop
            keyinput = pygame.key.get_pressed()

            if keyinput[pygame.K_UP]:
                ser.write('U')
                print('forward')
                lastcmd = 'm'
                 
            if keyinput[pygame.K_DOWN]:
                ser.write('D')
                print('back')
                lastcmd = 'm'
                
            if keyinput[pygame.K_LEFT]:
                ser.write('L')
                print('left')
                lastcmd = 'm'
                
            if keyinput[pygame.K_RIGHT]:
                ser.write('R')
                print('right')
                lastcmd = 'm'
                
#            if keyinput[pygame.K_RETURN]:
#                print('enter')

            if keyinput[pygame.K_UP] == False and keyinput[pygame.K_DOWN] == False and keyinput[pygame.K_LEFT] == False and keyinput[pygame.K_RIGHT] == False:
                end = True
                
            if event.type == pygame.QUIT:
                ser.write('e')
                ser.close()
                sys.exit(0)
            
            if lastcmd != 'e' and end == True:
                print('Sending end cmd')
                ser.write('e')
                lastcmd = 'e'
                
            end = False
        screen.blit(surface,(0,0))
        screen.blit(myfont.render(text, 12, (255,255,255)), (0, 0))
        pygame.display.flip()

                