import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QPushButton,QSpinBox
from PyQt5.QtCore import QThread
from picamera.array import PiRGBArray,PiBayerArray
from picamera import PiCamera
import time
from Constants import * 

class Producer(QtCore.QThread):
	image_ready=QtCore.pyqtSignal(object)

	def __init__(self):
		QtCore.QThread.__init__(self)
		self.is_running=False
		
		self.camera = PiCamera()
		self.camera.resolution = init_resolution
		self.camera.framerate = 15
		self.camera.shutter_speed=init_exposure_speed
		print(f'ISO:{self.camera.ISO}\tShutter speed:{self.camera.shutter_speed}')
		
		#self.camera.iso=0
		#time.sleep(2)
		#self.camera.shutter_speed=self.camera.exposure_speed
		#self.camera.exposure_mode='off'
		
		self.rawCapture = PiRGBArray(self.camera, size=init_resolution)

		# allow the camera to warmup
		time.sleep(0.1)
		

	def __del__(self):
		self.wait()

	def run(self):
		if not self.is_running:
			self.is_running=True

		for frame in self.camera.capture_continuous(self.rawCapture, format="rgb", use_video_port=True):
			image = frame.array[:,:,0].copy()
			imax=np.argmax(image)
			xc,yc=imax%image.shape[1],imax//image.shape[1]
			xsect=image[yc,:]
			ysect=image[:,xc]
			#image[yc,:]=255
			#image[:,xc]=255
			step=2
			h=30
			for i in range(0,image.shape[0]-step,step):
				image[i:i+step,(ysect[i]*h)//255]=255
			for i in range(0,image.shape[1]-step,step):
				image[90+(xsect[i]*h)//255,i:i+step]=255
			print(np.min(xsect))
			#print(np.max(xsect),np.max((xsect*100)/255))
			#arr2=np.require(image,np.uint8,'C')
			#qImg=QtGui.QImage(arr2,640,480,QtGui.QImage.Format_RGB888)
			self.image_ready.emit([image])

			self.rawCapture.truncate(0)


			if self.is_running==False:
				self.camera.close()
				break
	def run_raw(self):
		if not self.is_running:
			self.is_running=True
		output=PiBayerArray(self.camera, output_dims=3)
		while self.is_running:
			
			self.camera.capture(output, 'jpeg', bayer=True)
			arr=output.array
			arr=(arr>>2).astype('uint8')
			
			self.image_ready.emit([arr])
			output.truncate(0)
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
