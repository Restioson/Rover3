##PYTHON.py##

import sys
import os
		
#Variable links...
showerr = SHOWERR

#Functions

def println(string, showerror=True):
	''' A non-version specific version of "print()" or "print 'stuff'" '''
	if showerror == True:
		sys.stdout.write(string)
	
	else:
		try:
			sys.stdout.write(string+'\n+')
			return True
		except:
			return False

def get_out():
	return sys.stdout.read()
	
def exec_cmd(cmd):
	os.system(cmd)
	
def dyn_cmd(cmd):
	exec(cmd)