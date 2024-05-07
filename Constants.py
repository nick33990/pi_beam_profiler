import numpy as np
from enum import Enum

pi_available=False
emulate_noise=10

class Mode(Enum):
	RAW=0
	PREVIEW=1
	CALIBRATION=2

def get_calibration_pixelwise(I,rx=1,ry=1,eps=1e-7):
	r=I[ry::2,rx::2]
	g1=I[1-ry::2,rx::2]
	g2=I[ry::2,1-rx::2]
	b=I[1-rx::2,1-ry::2]
	
	rg=.5*np.sum((g1>0)*(g2>0)*(r/(g1+eps)+r/(g2+eps)))
	rg/=np.sum(g1>0)
	
	rb=np.sum((b>0)*(r/(b+eps)))
	rb/=np.sum(b>0)
	
	#return 1.0,round(rg,3),round(rb,3)
	return (8,int(rg*8),int(rb*8))
	
def calibrate(I,r,g,b,rx=1,ry=1,shift=3):#rx,ry-red pixel
	# Imax=np.max(I)
	# print(Imax)
	# I=I.astype('float16')
	# print(np.max(I))
	
	I[ry::2,rx::2]*=r
	I[1-ry::2,rx::2]*=g
	I[ry::2,1-rx::2]*=g
	I[1-ry::2,1-rx::2]*=b
	
	I=I//int(r)
	return I


init_dir='/home/pi/Documents/my beam profiler/Project'
path_to_coeffs='Coeffs.txt'
use_calibration=True
eps=1

cam_exp_time=2000
cam_gain=False

cmap='turbo'
WIDTH=1000
HEIGHT=700
PB_WIDTH=int(640*1.18)
PB_HEIGHT=int(480*1.18)
um=1.12

raw_framerate=10
raw_framerate_long=5
raw_resolution=(3280,2464) 
preview_framerate=30
preview_resolution=(640,480)#(2592,1944)
start_mode=Mode.RAW

pause_symbol=U'\u25A0'#U'\u24F8'
play_symbol=U'\u25BA'
