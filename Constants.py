import numpy as np
from enum import Enum

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
	
	return (8,int(rg*8),int(rb*8))
	

def calibrate(I,r,g,b,rx=1,ry=1,shift=3):#rx,ry-red pixel
	I[ry::2,rx::2]*=r
	I[1-ry::2,rx::2]*=g
	I[ry::2,1-rx::2]*=g
	I[1-ry::2,1-rx::2]*=b
	I>>=shift

use_calibration=True
eps=1
# (8,24,47)-<rtot>/<gtot>
# (8,21,34)-<rloc>/<gloc>
# (1,6,20)-table
calibration_coeffs=(8,21,34)
#max_I=1023*47
#path_to_calibration_im='1.npy'
cmap='gnuplot2'
WIDTH=780
HEIGHT=600
PB_WIDTH=640
PB_HEIGHT=480
um=1.12
init_exposure_speed=2000
#init_resolution=(2592,1944)#(640,480)#(2592,1944)#(640,480)
raw_resolution=(3280,2464) 
preview_framerate=30
preview_resolution=(640,480)#(2592,1944)
start_mode=Mode.RAW

pause_symbol=U'\u25A0'#U'\u24F8'
play_symbol=U'\u25BA'
