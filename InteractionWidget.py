import numpy as np
from time import time,sleep
import sys
import os
from PIL import Image
from scipy.ndimage import zoom

from PyQt5.QtCore import QThread

from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt, QTimer,QPointF
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, \
	QHBoxLayout, QDoubleSpinBox, QTabWidget, QWidget, \
	QLabel, QCheckBox, QSpinBox
from PyQt5.QtGui import QPixmap,QImage,QPainter,QPen

from Constants import *
#from BeamMath import *
from Camera import Producer

from enum import Enum

class InteractionWidget(QWidget):
	def __init__(self,mode):
		super().__init__()
		self.mode=mode
		self.button_pressed=False
		#self.setFixedSize(WIDTH,HEIGHT-10)
		self.setGeometry(0,0,WIDTH,HEIGHT)
		
		left_layout = QVBoxLayout()
		right_layout = QVBoxLayout()
		major_layout = QHBoxLayout()
		
		self.exposure_speed_label = QLabel()#('Exposure\ntime')		

		self.exposure_speed_edit = QSpinBox()
		self.exposure_speed_edit.setMaximumWidth(100)
		self.exposure_speed_edit.setPrefix('us: ')
		self.exposure_speed_edit.setMinimum(1)
		self.exposure_speed_edit.setMaximum(100000)

		self.exposure_speed_edit.setValue(init_exposure_speed)
		
		self.start_button = QPushButton(play_symbol, self)
		self.start_button.setMaximumWidth(50)
		self.start_button.clicked.connect(self.start_camera)

		
		if mode==Mode.RAW:
			self.ROI_label = QLabel('ROI')
			self.ROI_check = QCheckBox()


			self.x0_label = QLabel('x0')
			self.y0_label = QLabel('y0')
			self.delta_x_label = QLabel(u'\u0394 x')
			self.delta_y_label = QLabel(u'\u0394 y')

			self.save_button = QPushButton('Save', self)
			self.save_button.setMaximumWidth(50)

			left_layout.addWidget(self.ROI_label)
			left_layout.addWidget(self.ROI_check)
			left_layout.addWidget(self.exposure_speed_label)
			left_layout.addWidget(self.exposure_speed_edit)		
			left_layout.addWidget(self.start_button)
			left_layout.addWidget(self.save_button)
			left_layout.addWidget(self.x0_label)
			left_layout.addWidget(self.y0_label)
			left_layout.addWidget(self.delta_x_label)
			left_layout.addWidget(self.delta_y_label)
			
		elif mode==Mode.PREVIEW:
			left_layout.addWidget(self.exposure_speed_label)
			left_layout.addWidget(self.exposure_speed_edit)		
			left_layout.addWidget(self.start_button)
		
		self.setLayout(major_layout)
		self.label = QLabel(self)
		self.prev=0
		#qImg=self.ndarray2qimage(np.zeros([init_resolution[0],init_resolution[1],3],'uint8'))
		qImg=self.ndarray2qimage(np.zeros([PB_HEIGHT,PB_WIDTH,3],'uint8'))
		self.pixmap = QPixmap(QImage(qImg))
		
		self.label.setPixmap(self.pixmap)
		self.label.setFixedSize(PB_WIDTH,PB_HEIGHT);
		self.label.move(120,0);
		
		if mode==Mode.RAW:
			self.I_grid,self.J_grid=np.meshgrid(\
			np.arange(raw_resolution[0]),\
			np.arange(raw_resolution[1]))
			self.I_grid_sqr=self.I_grid*self.I_grid
			self.J_grid_sqr=self.J_grid*self.J_grid
		#self.painter=QPainter(self.label.pixmap())
		#self.label.setStyleSheet("QLabel"
		#"{"
		#"border:4px solid darkgreen;"
		#"background:lightgreen;"
		#"}")
		
		#self.label.height=100

		
		#elf.label.move(0,-100);
		
		#right_layout.addWidget(self.label)


		major_layout.addLayout(left_layout)
		major_layout.addLayout(right_layout)
		
		self.exposure_speed_edit.valueChanged.connect(self.set_shutter_speed)
		
		#self.painter = QPainter(self.label.pixmap())
		
	def set_shutter_speed(self,val):
		self.worker.set_shutter_speed(val)
	def print_smt(self):
		print(self.worker)
	def ndarray2qimage(self,arr):
		arr2=np.require(arr,'uint8','C')
		format_=QImage.Format.Format_Indexed8
		#format_=QImage.Format.Format_RGB888
		return QImage(arr2,arr.shape[1],arr.shape[0],format_)

	def start_thread(self):
		self.button_pressed=True
		self.start_button.setText(pause_symbol)
		self.thread=QThread()
		self.worker=Producer(self.mode)
		self.worker.moveToThread(self.thread)
		if self.mode==Mode.RAW:
			self.thread.started.connect(self.worker.run_raw)
		elif self.mode==Mode.PREVIEW:
			self.thread.started.connect(self.worker.run)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)
		self.worker.image_ready.connect(self.on_image_ready)
		self.thread.start()
		

	def start_camera(self):
		if not self.button_pressed:
			self.start_thread()
		else:
			self.button_pressed=False
			self.start_button.setText(play_symbol)
			self.worker.stop()
			self.thread.quit()
			self.thread.wait()
	
	def on_image_ready(self,img):
		tmp=QPixmap(self.ndarray2qimage(img))#.scaled(PB_WIDTH,PB_HEIGHT))
		self.label.setPixmap(tmp.scaled(PB_WIDTH,PB_HEIGHT))#QPixmap(qImg))
		if self.mode==Mode.PREVIEW:
			return 0
		#zoomed=img_data[0]#zoom(img_data[0],PB_WIDTH/img_data[0].shape[0])
		#print(time()-self.prev)
		#self.prev=time()
		#print(f'new frame:{time()-self.prev}')
		#T0=time()

		#xc,yc=center_max(img)
		#RMS_x,RMS_y,mx,my=RMS(img)
		
		P=np.sum(img,dtype='uint64')
		mx=np.sum(img*self.I_grid,dtype='uint64')
		my=np.sum(img*self.J_grid,dtype='uint64')
		Dx=np.sum(img*self.I_grid_sqr,dtype='uint64')
		Dy=np.sum(img*self.J_grid_sqr,dtype='uint64')
		mx/=P
		my/=P
		RMS_x=2*np.sqrt(Dx/P-mx*mx)
		RMS_y=2*np.sqrt(Dy/P-my*my)
		#x,my,RMS_x,RMS_y=100,100,0,0
		mx=int(mx)
		my=int(my)
		#print(f'RMS:{time()-T0}')
		#T0=time()

		self.x0_label.setText(f'x0 : {mx}')
		self.y0_label.setText(f'y0 : {my}')
		self.delta_x_label.setText(f'\u0394x:{round(RMS_x,3)}')
		self.delta_y_label.setText(f'\u0394x:{round(RMS_y,3)}')
		#print(f'labels:{time()-T0}')
		#T0=time()

		xsect=img[my,:].copy()
		ysect=img[:,mx].copy()
		#print(f'sect copy:{time()-T0}')
		#T0=time()

		step=1
		h=50
		# for i in range(0,img.shape[0]-step,step):
		# 	img[i:i+step,(ysect[i]*h)//255]=255
		# for i in range(0,img.shape[1]-step,step):
		# 	img[(xsect[i]*h)//255,i:i+step]=255

		# img[my,:]=255
		# img[:,mx]=255
		
		#print(time()-self.prev)
		
		#print(f'draw picture:{time()-T0}')
		T0=time()

		
		
		xsect=np.vstack((np.linspace(0,PB_WIDTH,len(xsect)),xsect)).astype('uint16').T
		ysect=np.vstack((ysect,np.linspace(0,PB_HEIGHT,len(ysect)))).astype('uint16').T
		xsect[:,1]>>=2
		ysect[:,0]>>=2
		self.draw_section(ysect)
		self.draw_section(xsect)
		
		self.label.repaint()
		#print(f'draw section:{time()-T0}')
		#T0=time()
		#self.prev=T0

	def draw_section(self,section):
		painter1=QPainter(self.label.pixmap())
		painter1.setPen(QPen(Qt.yellow,1))

		#if True:#self.painter.begin(self.label.pixmap()):
		#	self.painter.setPen(QPen(Qt.yellow,3))
		#	self.painter.drawLine(0,0,PB_WIDTH,PB_HEIGHT)
		#	#self.painter.end()
		#print(np.min(section[:,0]),np.max(section[:,0]),np.min(section[:,1]),np.max(section[:,1]))
		for i in range(1,len(section)):
			painter1.drawLine(section[i-1,0],section[i-1,1],section[i,0],section[i,1])


#pc peformance test:
#new frame:0.37019115447998047
#RMS:0.42464518547058105
#sect copy:0.0001342296600341797
#draw picture:0.06136441230773926
#draw section:0.027781963348388672
#new frame:0.005976676940917969

	
