##This Code will connect to and emulate the remote control
import sys
import serial
import sys
import pygame
import thread
print('Starting...')
print("Sometimes the ports get wacky! Mine is COM8!")
port = int(input('Port > '))-1
pygame.init()
ser = serial.Serial(port, 115200, timeout=1.5) #Create a serial object
ser.readline() #Let the protocol handshake...
screen = pygame.display.set_mode((640,480))
pygame.display.set_caption('Rover Controller')
def read(a,b):
    global text
    while True:
        text = ser.read(512)
        #print text
thread.start_new_thread(read,('a','b'))
myfont = pygame.font.SysFont("monospace", 15)
text = ''
label = myfont.render(text, 12, (255,255,255))
screen.blit(label, (0, 0))
while True: 
        for event in pygame.event.get(): #Event loop
            keyinput = pygame.key.get_pressed()
            if keyinput[pygame.K_UP]:
                 ser.write('u')
                 print('forward')
            if keyinput[pygame.K_DOWN]:
                ser.write('d')
                print('back')
            if keyinput[pygame.K_LEFT]:
                ser.write('l')
                print('left')
            if keyinput[pygame.K_RIGHT]:
                ser.write('r')
                print('right')
            if keyinput[pygame.K_RETURN]:
                ser.write('E')
                print('enter')

            if keyinput[pygame.K_UP] == False:
                ser.write('e')
                print('end')
            if keyinput[pygame.K_DOWN] == False:
                ser.write('e')
                print('end')
            if keyinput[pygame.K_LEFT] == False:
                ser.write('e')
                print('end')
            if keyinput[pygame.K_RIGHT] == False:
                ser.write('e')
                print('end')
            if keyinput[pygame.K_RETURN] == False:
                ser.write('e')
                print('end')
            if event.type == pygame.QUIT:
                ser.write('e')
                ser.close()
                sys.exit(0)

        screen.blit(label, (0, 0))
        pygame.display.flip()

                