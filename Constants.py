from enum import Enum

class Mode(Enum):
	RAW=0
	PREVIEW=1

WIDTH=600
HEIGHT=440
PB_WIDTH=420
PB_HEIGHT=300
um=1.12
init_exposure_speed=20000
#init_resolution=(2592,1944)#(640,480)#(2592,1944)#(640,480)
raw_resolution=(3280,2464) 
preview_resolution=(640,480)#(2592,1944)

pause_symbol=U'\u25A0'#U'\u24F8'
play_symbol=U'\u25BA'
