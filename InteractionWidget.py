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
from PyQt5.QtGui import QPixmap,QImage,QPainter,QPen,QColor

from Constants import *
from BeamMath import beam_math
from Camera import Producer

# from matplotlib.backends.backend_qt5agg import (
	# FigureCanvas,NavigationToolbar2QT as NavigationTool)
# from matplotlib.figure import Figure

from matplotlib import cm
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
		
		self.exposure_speed_label = QLabel('Время\nЭкспонирования')#('Exposure\ntime')		

		self.exposure_speed_edit = QSpinBox()
		self.exposure_speed_edit.setMaximumWidth(100)
		self.exposure_speed_edit.setPrefix('us: ')
		self.exposure_speed_edit.setMinimum(1)
		self.exposure_speed_edit.setMaximum(400000)

		self.exposure_speed_edit.setValue(init_exposure_speed)
		
		self.start_button = QPushButton(play_symbol, self)
		self.start_button.setMaximumWidth(50)
		self.start_button.clicked.connect(self.start_camera)
		
		#if mode==Mode.CALIBRATION:
		#	left_layout.addStretch()
		if True:#mode==Mode.RAW:
			self.background_edit=QSpinBox()
			self.background_edit.setMaximumWidth(100)
			self.background_edit.setMinimum(0)
			self.background_edit.setMaximum(1023)
			self.background_edit.setValue(0)
			
			self.ROI_label = QLabel('ROI')

			#self.crop_edit.setBackColor(Qt
			self.ROI_check = QCheckBox()
			self.ROI_check.setText('/2')
			self.calibration_check=QCheckBox()
			self.calibration_check.setText('Калибровка')
			
			self.x0_label = QLabel('x0')
			self.y0_label = QLabel('y0')
			self.delta_x_label = QLabel(u'\u0394 x')
			self.delta_y_label = QLabel(u'\u0394 y')

			self.save_button = QPushButton('Save', self)
			self.save_button.setMaximumWidth(50)
			
			self.zoomout_button=QPushButton('Zoom out',self)
			self.zoomout_button.setMaximumWidth(50)
			self.zoomout_button.clicked.connect(self.zoomout)
			
			self.awb_checkbox=QCheckBox()
			self.awb_checkbox.setText('Баланс белого')
			self.awb_checkbox.setChecked(True)
			self.awb_checkbox.stateChanged.connect(self.set_awb)
			
			self.gain_checkbox=QCheckBox()
			self.gain_checkbox.setText('Усиление')
			self.gain_checkbox.setChecked(True)
			self.gain_checkbox.stateChanged.connect(self.set_gain)

			#left_layout.addWidget(self.crop_edit)
			left_layout.addWidget(self.ROI_check)
			left_layout.addWidget(self.calibration_check)
			left_layout.addWidget(self.exposure_speed_label)
			left_layout.addWidget(self.exposure_speed_edit)
			left_layout.addWidget(QLabel('Уровень шума'))		
			left_layout.addWidget(self.background_edit)
			left_layout.addWidget(self.start_button)
			left_layout.addWidget(self.save_button)
			left_layout.addWidget(self.zoomout_button)
			left_layout.addWidget(self.awb_checkbox)
			left_layout.addWidget(self.gain_checkbox)
			if mode==Mode.CALIBRATION:
				self.get_calibration_button=QPushButton()
				self.get_calibration_button.setText('Снять\nкалибвку')
				self.get_calibration_button.clicked.connect(self.get_calibration)
				
				self.get_noise_button=QPushButton()
				self.get_noise_button.setText('Снять\шум')
				self.get_noise_button.clicked.connect(self.save_noise_map)
				#self.get_calibration_button.setMaximumWidth(50)
		
				self.label1=QLabel()
				self.label1.setText('Калибровочные\nкоэффициенты')
				#self.label1.setMaximumWidth(50)
				#self.label1.move(0,50)
		
				self.calibration_coeffs_tb=QLineEdit()
				self.calibration_coeffs_tb.setText(str(beam_math.calibration_coeffs))
				self.calibration_coeffs_tb.textChanged.connect(self.change_coeffs)
				#self.calibration_coeffs_tb.setMaximumWidth(60)
				#self.calibration_coeffs_tb.move(0,105)
				
				#left_layout.addStretch()
				left_layout.addWidget(self.get_calibration_button)
				left_layout.addWidget(self.get_noise_button)
				#left_layout.addStretch()
				left_layout.addWidget(self.label1)
				#left_layout.addStretch()
				left_layout.addWidget(self.calibration_coeffs_tb)
				#left_layout.addStretch()
				
				self.mask_pos=(0,0)
				self.mask_size=(1,1)
				self.mouse_button=0
				self.mask=[[0]]
				self.need_calibration=False
			elif mode==Mode.RAW:
				left_layout.addWidget(self.x0_label)
				left_layout.addWidget(self.y0_label)
				left_layout.addWidget(self.delta_x_label)
				left_layout.addWidget(self.delta_y_label)
			
		# elif mode==Mode.PREVIEW:
			# left_layout.addWidget(self.exposure_speed_label)
			# left_layout.addWidget(self.exposure_speed_edit)		
			# left_layout.addWidget(self.start_button)

		
		self.prev=time()
		
		
		###########################
		sm=cm.ScalarMappable(cmap=cmap)
		sm.norm.vmin,sm.norm.vmax=0,1
		self.rgbas=sm.to_rgba(np.linspace(0,1,256))
		self.rgbas=[QColor(int(255*r),int(255*g),int(255*b),int(255*a)).rgba() for r,g,b,a in self.rgbas]
		###########################
		
		
		self.label = QLabel()
		#qImg=self.ndarray2qimage(np.zeros([init_resolution[0],init_resolution[1],3],'uint8'))
		qImg=self.ndarray2qimage(np.zeros([PB_HEIGHT,PB_WIDTH,3],'uint8'))
		self.pixmap = QPixmap(QImage(qImg))
		self.label.setPixmap(self.pixmap)
		self.label.setFixedSize(PB_WIDTH,PB_HEIGHT);
		
		# if mode==Mode.PREVIEW:
			# beam_math.noise_map=[[10]]
		# print(beam_math.noise_map)
		#self.label.move(140,0);

		self.real_label_size=(PB_WIDTH,PB_HEIGHT)
		self.label_pos=(0,1)
		right_layout.addWidget(self.label)
		
		self.setLayout(major_layout)
	#for matplotlib widget, fps vv 1.5 times
		# if mode==Mode.RAW:
	
			# dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
			# right_layout.addWidget(dynamic_canvas)
			# right_layout.addWidget(NavigationTool(dynamic_canvas, self))
			# self._dynamic_ax = dynamic_canvas.figure.subplots()
			# self.pmap=self._dynamic_ax.imshow(np.random.random((2464,3280)),vmin=0,vmax=255)
			# self.pmap.figure.canvas.draw()
		
		
		self.crop_pos=QPoint(0,0)
		self.crop_size=QSize(raw_resolution[0],raw_resolution[1])

		major_layout.addLayout(left_layout)
		major_layout.addLayout(right_layout)
		
		self.exposure_speed_edit.valueChanged.connect(self.set_shutter_speed)
		# if mode==Mode.RAW:
			# #self.painter = QPainter(self.label.pixmap())
			# self.crop_edit=QLineEdit(self)
			# #self.crop_edit.textChanged.connect(self.on_text_changed)
			# self.crop_edit.setFixedSize(120,30)
			# self.crop_edit.move(0,80)
			# #self.crop_edit.setFontPointSize(10)
			# self.crop_edit.setText(f"{0},{0},{raw_resolution[0]},{raw_resolution[1]}")
			# self.save_button.clicked.connect(self.save_button_clicked)
			# self.crop_edit.installEventFilter(self)
			# self.calibration=None
			# if use_calibration:
				# self.calibration=np.load(path_to_calibration_im)

		self.calc=beam_math(raw_resolution[0],raw_resolution[1])
		
		self.need_save=False
		self.need_noise_save=False
		
		self.mouse_pressed=False
		self.mouse_start_pos=QPoint(0,0)
		self.mouse_pos=QPoint(1,1)
		
		self.rect_color=Qt.red
		############################################
		#self.button_pressed=True
		
		#if self.mode==start_mode:
			#self.init_camera()
			# self.init_camera()
			
	def change_coeffs(self):
		txt=self.calibration_coeffs_tb.text()
		txt=txt.replace('(','')
		txt=txt.replace(')','')
		txt=txt.replace("'","")
		beam_math.calibration_coeffs=[int(c) for c in txt.split(',')]
		print(beam_math.calibration_coeffs)
	def save_noise_map(self):
		print('at noise')
		self.need_noise_save=True
	
	def set_gain(self):
		self.worker.camera.close()
		self.close_camera()
		self.init_camera()
		# self.worker.camera.exposure_mode='auto' if self.gain_checkbox.isChecked() else 'off'
		# self.worker.camera.ISO=100
	def set_awb(self):
		self.worker.camera.awb_mode='auto' \
				if self.awb_checkbox.isChecked() else 'off'
	
	def init_camera(self):
		print('-----> init camera called at mode:',self.mode)
		self.thread=QThread()
		self.worker=Producer(self.mode,'auto' \
				if self.gain_checkbox.isChecked() else 'off')
		self.worker.moveToThread(self.thread)
		if self.mode==Mode.RAW or self.mode==Mode.CALIBRATION:
			self.thread.started.connect(self.worker.run_raw2)
		elif self.mode==Mode.PREVIEW:
			self.thread.started.connect(self.worker.run)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)
		self.worker.image_ready.connect(self.on_image_ready)
		
		print(self.mode,self.thread)
	
	def zoomout(self):
		self.crop_pos=QPoint(0,0)
		self.crop_size=QSize(raw_resolution[0],raw_resolution[1])
		
		self.calc.update_grid(self.crop_size.width(),self.crop_size.height())
	
	def pause_camera(self):
		pass
	
	def close_camera(self):
		print('stopping worker')
		self.worker.stop()
		print('quitting')
		self.thread.quit()
		print('waiting...')
		self.worker.stop()
		self.thread.wait()
		#del self.worker
	
	def get_calibration(self):
		print('at cal')
		self.need_calibration=True
	
	def mousePressEvent(self,event):
		super(InteractionWidget,self).mousePressEvent(event)
		
		if self.mode==Mode.CALIBRATION:
			self.rect_color=Qt.red if event.buttons()==Qt.LeftButton else Qt.cyan

		#print(event.buttons()==Qt.RightButton)
		# self.label_pos=
		# print(event.pos())
		# print(self.label.pos())
		self.mouse_start_pos=event.pos()-self.label.pos()
		
		if self.mouse_start_pos.x()>0 and \
			self.mouse_start_pos.y()>0 and\
			self.mouse_start_pos.x()<self.real_label_size[0] and\
			self.mouse_start_pos.y()<self.real_label_size[1]:

		
		#if self.mouse_start_pos.x()<120 or 
			self.mouse_pressed=True
		
		
		#print(self.mouse_start_pos,self.mouse_start_pos.x(),self.mouse_start_pos.x()/PB_WIDTH*3280)
		
		QWidget.mousePressEvent(self,event)
		
	def mouseMoveEvent(self,event):
		super(InteractionWidget,self).mouseMoveEvent(event)
		if self.mouse_pressed:
			self.mouse_pos=event.pos()-self.label.pos()
			
		QWidget.mouseMoveEvent(self,event)
	
	def draw_rect(self):
		painter1=QPainter(self.label.pixmap())

		painter1.setPen(QPen(self.rect_color,1))

		x0=min(self.mouse_start_pos.x(),self.mouse_pos.x())
		y0=min(self.mouse_start_pos.y(),self.mouse_pos.y())
		w=abs(self.mouse_start_pos.x()-self.mouse_pos.x())
		h=abs(self.mouse_start_pos.y()-self.mouse_pos.y())
		painter1.drawRect(x0,y0,w,h)
		#self.label.repaint()
	
	def tomod4(self,x,xm):
		if x<0:
			return 0
		elif x>xm:
			return xm
		else:
			return 4*(x//4)
	
	def mouseReleaseEvent(self,event):
		super(InteractionWidget,self).mouseReleaseEvent(event)
		
		if self.mouse_pressed:
			x0=min(self.mouse_start_pos.x(),self.mouse_pos.x())
			y0=min(self.mouse_start_pos.y(),self.mouse_pos.y())
			w=abs(self.mouse_start_pos.x()-self.mouse_pos.x())
			h=abs(self.mouse_start_pos.y()-self.mouse_pos.y())
		
			wreal=self.real_label_size[0]
			hreal=self.real_label_size[1]
			
			tmp_pos,tmp_size=QPoint(0,0),QSize(1,1)
			tmp_pos.setX(self.crop_pos.x()+\
				int(x0/wreal*self.crop_size.width()))
			tmp_pos.setY(self.crop_pos.y()+\
				int((y0/hreal)*self.crop_size.height()))
			tmp_size.setWidth(int(w/wreal*self.crop_size.width()))
			tmp_size.setHeight(int(h/hreal*self.crop_size.height()))
		
			if self.mode==Mode.CALIBRATION and self.rect_color==Qt.cyan:
				tmp_pos-=self.crop_pos
				# self.mask=np.zeros(self.calc.I_grid.shape,dtype='uint16')
				# self.mask[tmp_pos.y():tmp_pos.y()+tmp_size.height(),\
					# tmp_pos.x():tmp_pos.x()+tmp_size.width()]=1
				self.mask=	(self.calc.I_grid>tmp_pos.x())*\
							(self.calc.J_grid>tmp_pos.y())*\
							(self.calc.I_grid<(tmp_size.width()+tmp_pos.x()))*\
							(self.calc.J_grid<(tmp_size.height()+tmp_pos.y()))
			else:
				
				tmp_pos.setX(self.tomod4(tmp_pos.x(),raw_resolution[0]))
				tmp_pos.setY(self.tomod4(tmp_pos.y(),raw_resolution[1]))
				tmp_size.setWidth(self.tomod4(tmp_size.width(),raw_resolution[0]))
				tmp_size.setHeight(self.tomod4(tmp_size.height(),raw_resolution[1]))
			
			
				self.crop_pos=tmp_pos
				self.crop_size=tmp_size
				self.calc.update_grid(self.crop_size.width(),\
				self.crop_size.height())

			self.mouse_pressed=False

	
	def eventFilter(self,obj,event):
		if event.type()==QEvent.KeyPress:
			print(event.key())
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

		self.thread.start()
		

	def start_camera(self):
		if not self.button_pressed:
			print(self.mode)
			self.button_pressed=True
			#self.thread=QThread()
			#self.init_camera()
			#self.worker.moveToThread(self.thread)
			if not self.thread.isRunning():
				self.thread.start()
			else:
				self.worker.is_running=True
			#self.start_thread()
			self.start_button.setText(pause_symbol)
			self.gain_checkbox.setEnabled(False)
		else:
			self.button_pressed=False
			#self.worker.stop()
			#self.thread.quit()
			#self.thread.wait()
			self.worker.is_running=False
			self.start_button.setText(play_symbol)
			self.gain_checkbox.setEnabled(True)
			#self.worker.stop()

	
	def on_image_ready(self,img):
		# self.pmap.set_data(img)
		# self.pmap.figure.canvas.draw()

		
		print(time()-self.prev)
		self.prev=time()
		
		if not (self.mode==Mode.PREVIEW):
			#return 0
			
			if self.need_noise_save:
				beam_math.noise_map=img.copy()
				self.need_noise_save=False
				print(len(beam_math.noise_map))
			
			img=img[self.crop_pos.y():self.crop_pos.y()+self.crop_size.height(),\
					self.crop_pos.x():self.crop_pos.x()+self.crop_size.width()]
			if self.mode==Mode.CALIBRATION:
				if len(self.mask)>4:
					img*=self.mask
				if self.need_calibration:
					self.calibration_coeffs_tb.setText(str(get_calibration_pixelwise(img,1-self.crop_pos.x()%2,1-self.crop_pos.y()%2)))
					self.need_calibration=False
			
			
			if len(beam_math.noise_map)>5:
				img=img*(img>self.background_edit.value()*\
				beam_math.noise_map[self.crop_pos.y():self.crop_pos.y()+\
				self.crop_size.height(),\
				self.crop_pos.x():self.crop_pos.x()+self.crop_size.width()])
			# if self.crop_pos.x()>0:
				# print(self.crop_pos)
				# img[self.crop_pos.y():self.crop_pos.y()+self.crop_size.height(),\
					# self.crop_pos.x():self.crop_pos.x()+self.crop_size.width()]=1023
			# if use_calibration and self.calibration_check.isChecked():
				# img=img.astype('float32')/(eps+self.calibration[self.crop_pos.y():self.crop_pos.y()+self.crop_size.height(),\
					# self.crop_pos.x():self.crop_pos.x()+self.crop_size.width()])
				# #таким образом img от 0 до 1023, т.к. eps=1
				
				
				#img*=50
				
				#img=img.astype('uint16')
			if self.calibration_check.isChecked():
				calibrate(img,calibration_coeffs[0],\
							calibration_coeffs[1],\
							calibration_coeffs[2],\
							1-self.crop_pos.x()%2,\
							1-self.crop_pos.y()%2)
			
			#########################
					
			if self.need_save:
				np.save('1',img)
				self.need_save=False
				
			
			if not self.disable_calculations and self.mode==Mode.RAW:
				
				if img.shape[0]!=self.calc.I_grid.shape[0] or img.shape[1]!=self.calc.I_grid.shape[1]:
					print(f'img:{img.shape} \tgrid:{self.calc.I_grid.shape}')
					return -1
		
				P,mx,my,RMS_x,RMS_y=self.calc.RMS(img)

				mx=int(mx)
				my=int(my)


				self.x0_label.setText(f'x0 : {mx}')
				self.y0_label.setText(f'y0 : {my}')
				self.delta_x_label.setText(f'\u0394x:{round(RMS_x,3)}')
				self.delta_y_label.setText(f'\u0394y:{round(RMS_y,3)}')


				xsect=img[my,:].copy()
				ysect=img[:,mx].copy()


				step=1
				h=min(self.crop_size.width(),self.crop_size.height())//10


		
		
				xsect=np.vstack((np.linspace(0,PB_WIDTH,len(xsect)),xsect)).astype('uint16').T
				ysect=np.vstack((ysect,np.linspace(0,PB_HEIGHT,len(ysect)))).astype('uint16').T
				xsect[:,1]>>=2
				ysect[:,0]>>=2
			
				mx,my=(mx*PB_WIDTH)//img.shape[1],(my*PB_HEIGHT)//img.shape[0]
			if self.ROI_check.isChecked():
				img=img[::2,::2]
			#sprint(self.
			
		
			
		print(np.max(img),self.worker.camera.analog_gain,\
							self.worker.camera.digital_gain,\
							self.worker.camera.awb_mode,\
							self.worker.camera.exposure_mode)
			#img=(255*np.log(img.astype('float32')+1)).astype('uint8')
		if self.mode==Mode.RAW or self.mode==Mode.CALIBRATION:
			img=(img>>2).astype('uint8')
		img=self.ndarray2qimage(img)
		img.setColorTable(self.rgbas)
		tmp=QPixmap(img)#.scaled(PB_WIDTH,PB_HEIGHT))
		tmp=tmp.scaled(PB_WIDTH,PB_HEIGHT,Qt.KeepAspectRatio)
		self.label.setPixmap(tmp)#QPixmap(qImg))
		self.real_label_size=(tmp.size().width(),tmp.size().height())
		if self.mouse_pressed:
			self.draw_rect()

		if not (self.mode==Mode.PREVIEW or self.disable_calculations):
			pass
			# self.draw_section(ysect)
			# self.draw_section(xsect,mx,my,\
					# (RMS_x/self.crop_size.width())*PB_WIDTH,\
					# (RMS_y/self.crop_size.height())*PB_HEIGHT)
		
		self.label.repaint()

	def draw_section(self,section,mx=-1,my=-1,RMS_x=-1,RMS_y=-1):
		painter1=QPainter(self.label.pixmap())
		painter1.setPen(QPen(Qt.yellow,1))

		for i in range(1,len(section)):
			painter1.drawLine(section[i-1,0],section[i-1,1],section[i,0],section[i,1])
		painter1.setPen(QPen(Qt.red,1,Qt.DashLine))
		if mx!=-1:
			painter1.drawLine(mx,0,mx,PB_HEIGHT)
		if my!=-1:
			painter1.drawLine(0,my,PB_WIDTH,my)
		if RMS_x!=-1:
			painter1.drawEllipse(QPoint(mx,my),RMS_x,RMS_y)


#pc peformance test:
#new frame:0.37019115447998047
#RMS:0.42464518547058105
#sect copy:0.0001342296600341797
#draw picture:0.06136441230773926
#draw section:0.027781963348388672
#new frame:0.005976676940917969

	
