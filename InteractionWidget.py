import numpy as np
from time import time,sleep
import sys
import os
from PIL import Image
from scipy.ndimage import zoom

from PyQt5.QtCore import QThread

from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt, QTimer,QPoint,QEvent
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, \
	QHBoxLayout, QDoubleSpinBox, QTabWidget, QWidget, \
	QLabel, QCheckBox, QSpinBox,QLineEdit
from PyQt5.QtGui import QPixmap,QImage,QPainter,QPen

from Constants import *
#from BeamMath import *
from Camera import Producer

# from matplotlib.backends.backend_qt5agg import (
	# FigureCanvas,NavigationToolbar2QT as NavigationTool)
# from matplotlib.figure import Figure

from enum import Enum


class InteractionWidget(QWidget):
	def __init__(self,mode):
		super().__init__()
		self.mode=mode
		self.button_pressed=False
		self.disable_calculations=False
		
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

			#self.crop_edit.setBackColor(Qt
			#self.ROI_check = QCheckBox()


			self.x0_label = QLabel('x0')
			self.y0_label = QLabel('y0')
			self.delta_x_label = QLabel(u'\u0394 x')
			self.delta_y_label = QLabel(u'\u0394 y')

			self.save_button = QPushButton('Save', self)
			self.save_button.setMaximumWidth(50)

			left_layout.addWidget(self.ROI_label)
			#left_layout.addWidget(self.crop_edit)
			#left_layout.addWidget(self.ROI_check)
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
		
		self.prev=time()
		
		self.setLayout(major_layout)
		
		
		self.label = QLabel(self)
		#qImg=self.ndarray2qimage(np.zeros([init_resolution[0],init_resolution[1],3],'uint8'))
		qImg=self.ndarray2qimage(np.zeros([PB_HEIGHT,PB_WIDTH,3],'uint8'))
		self.pixmap = QPixmap(QImage(qImg))
		self.label.setPixmap(self.pixmap)
		self.label.setFixedSize(PB_WIDTH,PB_HEIGHT);
		self.label.move(120,0);
		# if mode==Mode.RAW:
			# dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
			# right_layout.addWidget(dynamic_canvas)
			# right_layout.addWidget(NavigationTool(dynamic_canvas, self))
			# self._dynamic_ax = dynamic_canvas.figure.subplots()
			# self.pmap=self._dynamic_ax.imshow(np.random.random((2464,3280)),vmin=0,vmax=255)
			# self.pmap.figure.canvas.draw()
		


		major_layout.addLayout(left_layout)
		major_layout.addLayout(right_layout)
		
		self.exposure_speed_edit.valueChanged.connect(self.set_shutter_speed)
		if mode==Mode.RAW:
			#self.painter = QPainter(self.label.pixmap())
			self.crop_edit=QLineEdit(self)
			#self.crop_edit.textChanged.connect(self.on_text_changed)
			self.crop_edit.setFixedSize(120,30)
			self.crop_edit.move(0,50)
			#self.crop_edit.setFontPointSize(10)
			self.crop_edit.setText(f"{0},{0},{raw_resolution[0]},{raw_resolution[1]}")
			self.save_button.clicked.connect(self.save_button_clicked)
			self.crop_edit.installEventFilter(self)
		self.update_grid(raw_resolution[0],raw_resolution[1])
		self.need_save=False
		
		self.mouse_pressed=False
		self.mouse_start_pos=QPoint(0,0)
		self.mouse_pos=QPoint(1,1)

		
	
	def mousePressEvent(self,event):
		super(InteractionWidget,self).mousePressEvent(event)
		
		self.mouse_pressed=True
		self.mouse_start_pos=event.pos()-QPoint(120,0)
		
		QWidget.mousePressEvent(self,event)
		
	def mouseMoveEvent(self,event):
		super(InteractionWidget,self).mouseMoveEvent(event)
		if self.mouse_pressed:
			self.mouse_pos=event.pos()-QPoint(120,0)
			
		QWidget.mouseMoveEvent(self,event)
	
	def draw_rect(self):
		painter1=QPainter(self.label.pixmap())
		painter1.setPen(QPen(Qt.red,1))
		x0=min(self.mouse_start_pos.x(),self.mouse_pos.x())
		y0=min(self.mouse_start_pos.y(),self.mouse_pos.y())
		w=abs(self.mouse_start_pos.x()-self.mouse_pos.x())
		h=abs(self.mouse_start_pos.y()-self.mouse_pos.y())
		painter1.drawRect(x0,y0,w,h)
		#self.label.repaint()
	
	def mouseReleaseEvent(self,event):
		super(InteractionWidget,self).mouseReleaseEvent(event)
		self.mouse_pressed=False
	
	def update_grid(self,w,h):
		self.I_grid,self.J_grid=np.meshgrid(\
			np.arange(w),\
			np.arange(h)
		)
		self.I_grid_sqr=self.I_grid*self.I_grid
		self.J_grid_sqr=self.J_grid*self.J_grid
	
	def eventFilter(self,obj,event):
		if event.type()==QEvent.KeyPress and obj is self.crop_edit:
			if event.key() ==Qt.Key_Return and self.crop_edit.hasFocus:
				crop_rect=[int(sp) for sp in self.crop_edit.text().split(',')]#[:-1]#.replace('\n','')
				if len(crop_rect)!=4:
					self.crop_edit.setText(self.init_crop_text)
					crop_rect=[int(sp) for sp in self.crop_edit.text().split(',')]
				self.worker.set_crop_rectangle(*crop_rect)
				self.update_grid(crop_rect[2],crop_rect[3])
				#print(crop_rect)
		return super().eventFilter(obj,event)
		
	def save_button_clicked(self):
		self.need_save=True
	# def on_text_changed(self):#,val):
		# spl=[int(sp) for sp in self.crop_edit.toPlainText().split(',')]
		# self.worker.set_crop_rectangle(spl[0],spl[1],spl[2],spl[3])
		# self.update_grid(spl[2],spl[3])
		# #print(val)
		
		
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
			self.thread.started.connect(self.worker.run_raw2)
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
		# self.pmap.set_data(img)
		# self.pmap.figure.canvas.draw()
		
		if self.need_save:
			np.save('1',img)
			self.need_save=False
		
		print(time()-self.prev)
		self.prev=time()
		
		if not (self.mode==Mode.PREVIEW or self.disable_calculations):
			#return 0
		
			P=np.sum(img,dtype='uint64')
			if img.shape[0]!=self.I_grid.shape[0] or img.shape[1]!=self.I_grid.shape[1]:
				print(f'img:{img.shape} \tgrid:{self.I_grid.shape}')
				return -1
		
			mx=np.sum(img*self.I_grid,dtype='uint64')
			my=np.sum(img*self.J_grid,dtype='uint64')
			Dx=np.sum(img*self.I_grid_sqr,dtype='uint64')
			Dy=np.sum(img*self.J_grid_sqr,dtype='uint64')
			mx/=P
			my/=P
			RMS_x=2*np.sqrt(Dx/P-mx*mx)
			RMS_y=2*np.sqrt(Dy/P-my*my)

			mx=int(mx)
			my=int(my)


			self.x0_label.setText(f'x0 : {mx}')
			self.y0_label.setText(f'y0 : {my}')
			self.delta_x_label.setText(f'\u0394x:{round(RMS_x,3)}')
			self.delta_y_label.setText(f'\u0394x:{round(RMS_y,3)}')


			xsect=img[my,:].copy()
			ysect=img[:,mx].copy()


			step=1
			h=50

			T0=time()

		
		
			xsect=np.vstack((np.linspace(0,PB_WIDTH,len(xsect)),xsect)).astype('uint16').T
			ysect=np.vstack((ysect,np.linspace(0,PB_HEIGHT,len(ysect)))).astype('uint16').T
			xsect[:,1]>>=2
			ysect[:,0]>>=2
		
			img=img[::2,::2]
			img=(img>>2).astype('uint8')
		tmp=QPixmap(self.ndarray2qimage(img))#.scaled(PB_WIDTH,PB_HEIGHT))
		self.label.setPixmap(tmp.scaled(PB_WIDTH,PB_HEIGHT))#QPixmap(qImg))
		
		if self.mouse_pressed:
			self.draw_rect()
		
		if not (self.mode==Mode.PREVIEW or self.disable_calculations):
			self.draw_section(ysect)
			self.draw_section(xsect)
		
		self.label.repaint()

	def draw_section(self,section):
		painter1=QPainter(self.label.pixmap())
		painter1.setPen(QPen(Qt.yellow,1))

		for i in range(1,len(section)):
			painter1.drawLine(section[i-1,0],section[i-1,1],section[i,0],section[i,1])


#pc peformance test:
#new frame:0.37019115447998047
#RMS:0.42464518547058105
#sect copy:0.0001342296600341797
#draw picture:0.06136441230773926
#draw section:0.027781963348388672
#new frame:0.005976676940917969

	
