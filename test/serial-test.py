#!/usr/bin/python3
import serial
s = serial.Serial("/dev/ttyAMA0", 57600)
while 1: print(s.readline())
