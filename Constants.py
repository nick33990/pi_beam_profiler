from enum import Enum

class Mode(Enum):
	RAW=0
	PREVIEW=1

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
WIDTH=600
HEIGHT=440
PB_WIDTH=420
PB_HEIGHT=300
um=1.12
init_exposure_speed=2000
#init_resolution=(2592,1944)#(640,480)#(2592,1944)#(640,480)
raw_resolution=(3280,2464) 
preview_framerate=30
preview_resolution=(640,480)#(2592,1944)
start_mode=Mode.RAW

pause_symbol=U'\u25A0'#U'\u24F8'
play_symbol=U'\u25BA'
