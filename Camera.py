import io
import numpy as np
from numpy.lib.stride_tricks import as_strided
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
		self.resolution=preview_resolution
		self.mode=mode
		self.cropx=0
		self.cropy=0
		self.cropw=raw_resolution[0]
		self.croph=raw_resolution[1]
		if cam_availbale:
			self.camera = PiCamera()#(sensor_mode=2)
			
			self.camera.framerate = 10
			self.camera.shutter_speed=init_exposure_speed
			#self.camera.zoom=(0.5,0,0.5,1)
			print(f'ISO:{self.camera.ISO}\nShutter speed:{self.camera.shutter_speed}\nresolution:{self.camera.resolution}')
		
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
			print(self.camera.resolution)
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
			
			#arr=self.rawCapture.array
			#arr=self.rawCapture.demosaic()-very slow (4 sec)
			

			arr=(arr>>2).astype('uint8')

			self.image_ready.emit(arr[:,:,0])
			self.rawCapture.truncate(0)
			#print(np.max(arr),arr.shape,arr.dtype)
			#img = Image.fromarray(output.astype(np.uint8))
			
			#img.save('my1.png')
	def set_crop_rectangle(self,x,y,w,h):
		if x+w>raw_resolution[0]:
			w=w-x
		if y+h>raw_resolution[1]:
			h=h-x
		self.cropx,self.cropy,self.cropw,self.croph=x,y,w,h
		
	def run_raw2(self):#из мануала (5.6 сек -> при конверсии одной плоскости только r) 
		if not self.is_running:
			self.is_running=True
		stream=io.BytesIO()
		while self.is_running:
			self.camera.capture(stream,'jpeg',bayer=True)
			ver = {
				'RP_ov5647': 1,
				'RP_imx219': 2,
			}[self.camera.exif_tags['IFD0.Model']]
			
			offset = {
				1: 6404096,
				2: 10270208,
			}[ver]
			data = stream.getvalue()[-offset:]
			#print(data[:4]) ->b'BRCM'
			#assert data[:4] == 'BRCM'
			data = data[32768:]
			data = np.fromstring(data, dtype=np.uint8)
			
			reshape, crop = {
				1: ((1952, 3264), (1944, 3240)),
				2: ((2480, 4128), (2464, 4100)),
				}[ver]
			data = data.reshape(reshape)[:crop[0], :crop[1]]

			data = data.astype(np.uint16) << 2
			for byte in range(4):
				data[:, byte::5] |= ((data[:, 4::5] >> (byte * 2)) & 0b11)
			data = np.delete(data, np.s_[4::5], 1)
			
			
			#print(self.cropy,self.cropx,self.croph,self.cropw)
			data=data[self.cropy:self.cropy+self.croph,self.cropx:self.cropx+self.cropw]
			#print(data.shape)
			
			#self.image_ready.emit(data[1::2,0::2]>>2)
			
			rgb = np.zeros(data.shape + (3,), dtype=data.dtype)
			rgb[1::2, 0::2, 0] = data[1::2, 0::2] # Red
			rgb[0::2, 0::2, 1] = data[0::2, 0::2] # Green
			rgb[1::2, 1::2, 1] = data[1::2, 1::2] # Green
			rgb[0::2, 1::2, 2] = data[0::2, 1::2] # Blue
			
			bayer = np.zeros(rgb.shape, dtype=np.uint8)
			bayer[1::2, 0::2, 0] = 1 # Red
			bayer[0::2, 0::2, 1] = 1 # Green
			bayer[1::2, 1::2, 1] = 1 # Green
			bayer[0::2, 1::2, 2] = 1 # Blue
			
			output = np.empty(rgb.shape, dtype=rgb.dtype)
			window = (3, 3)
			borders = (window[0] - 1, window[1] - 1)
			border = (borders[0] // 2, borders[1] // 2)
			rgb = np.pad(rgb, [
				(border[0], border[0]),
				(border[1], border[1]),
				(0, 0),
			], 'constant')
			
			bayer = np.pad(bayer, [
				(border[0], border[0]),
				(border[1], border[1]),
				(0, 0),
			], 'constant')
			
			for plane in range(1):
				p = rgb[..., plane]
				b = bayer[..., plane]
				pview = as_strided(p, shape=(
					p.shape[0] - borders[0],
					p.shape[1] - borders[1]) + window, strides=p.strides * 2)
				bview = as_strided(b, shape=(
					b.shape[0] - borders[0],
					b.shape[1] - borders[1]) + window, strides=b.strides * 2)
				psum = np.einsum('ijkl->ij', pview)
				bsum = np.einsum('ijkl->ij', bview)
				output[..., plane] = psum // bsum
			output = (output >> 2).astype(np.uint8)
			
			self.image_ready.emit(output[:,:,0])
	
			
	def stop(self):
		self.is_running=False

	################################
	
	def set_ISO(self,new_ISO):
		self.camera.ISO=new_ISO
	def set_shutter_speed(self,new_shutter_speed):
		self.camera.shutter_speed=new_shutter_speed
	def set_frame_rate(self,new_fps):
		self.camera.framerate=new_fps
