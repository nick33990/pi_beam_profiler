import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QPushButton,QSpinBox
from PyQt5.QtCore import QThread

cam_availbale=True

if cam_availbale:
	from picamera.array import PiRGBArray,PiBayerArray
	from picamera import PiCamera
import time
from Constants import * 

class Producer(QtCore.QThread):
	image_ready=QtCore.pyqtSignal(object)

	def __init__(self,mode):
		QtCore.QThread.__init__(self)
		self.is_running=False
		self.resolution=init_resolution
		self.mode=mode
		if cam_availbale:
			self.camera = PiCamera()#(sensor_mode=2)
			
			self.camera.framerate = 10
			self.camera.shutter_speed=init_exposure_speed
			#self.camera.zoom=(0.5,0,0.5,1)
			print(f'ISO:{self.camera.ISO}\tShutter speed:{self.camera.shutter_speed}')
		
		#self.camera.iso=0
		#time.sleep(2)
		#self.camera.shutter_speed=self.camera.exposure_speed
		#self.camera.exposure_mode='off'
		
			#self.rawCapture = PiRGBArray(self.camera, size=init_resolution)
			if mode==Mode.RAW:
				self.rawCapture=PiBayerArray(self.camera, output_dims=3)
			elif mode==Mode.PREVIEW:
				self.camera.resolution = preview_resolution
				self.rawCapture=PiRGBArray(self.camera, size=preview_resolution)
		# allow the camera to warmup
			time.sleep(0.1)
		

	def __del__(self):
		self.wait()

	def run(self):
		if not self.is_running:
			self.is_running=True
		if cam_availbale:
			for frame in self.camera.capture_continuous(self.rawCapture, format="rgb", use_video_port=True):
				image = frame.array[:,:,0].copy()

				self.image_ready.emit(image)

				self.rawCapture.truncate(0)


				if self.is_running==False:
					self.camera.close()
					break
		else:
			while self.is_running:
				X,Y=np.meshgrid(np.arange(0,self.resolution[0],1),np.arange(0,self.resolution[1],1))
				mx=self.resolution[0]*0.5
				my=self.resolution[1]*0.5
				Dx=40#self.resolution[0]/20
				Dy=40#self.resolution[1]/10
				SNR=.9999
				I=np.exp(-.5*((X-mx)/Dx)**2-.5*((Y-my)/Dy)**2)*SNR
				I+=np.random.random(X.shape)*(1-SNR)
				I=(255*I).astype('uint8')
				self.image_ready.emit(I)


	#про raw-формат на 48-ой странице мануала:
	#только в полном разрешении, 10 бит, BGGR и проч
	def run_raw(self):
		if not self.is_running:
			self.is_running=True
		
		while self.is_running:
			
			self.camera.capture(self.rawCapture, 'jpeg', bayer=True)
			
			arr=self.rawCapture.demosaic()#.array
			arr=(arr>>2).astype('uint8')
			print(arr.shape)
			self.image_ready.emit(arr[:,:,0])
			self.rawCapture.truncate(0)
			#print(np.max(arr),arr.shape,arr.dtype)
			#img = Image.fromarray(output.astype(np.uint8))
			#img.save('my1.png')
	def stop(self):
		self.is_running=False

	################################
	
	def set_ISO(self,new_ISO):
		self.camera.ISO=new_ISO
	def set_shutter_speed(self,new_shutter_speed):
		self.camera.shutter_speed=new_shutter_speed
	def set_frame_rate(self,new_fps):
		self.camera.framerate=new_fps
