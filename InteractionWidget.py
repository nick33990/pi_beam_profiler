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

import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import (
	# FigureCanvas,NavigationToolbar2QT as NavigationTool)
# from matplotlib.figure import Figure

from matplotlib import cm
from enum import Enum

show_factor_2=False
enable_draw_sect=True

class InteractionWidget(QWidget):
	def __init__(self,mode):
		super().__init__()
		self.mode=mode
		self.button_pressed=False
		self.disable_calculations=False
		
		#self.setFixedSize(WIDTH,HEIGHT-10)
		self.setGeometry(0,0,WIDTH,HEIGHT)
		
		left_layout = QVBoxLayout()
		right_layout = QHBoxLayout()
		major_layout = QHBoxLayout()
		
		self.exposure_speed_label = QLabel('Экспонированиe')#('Exposure\ntime')		

		self.exposure_speed_edit = QSpinBox()
		self.exposure_speed_edit.setMaximumWidth(100)
		self.exposure_speed_edit.setPrefix('us: ')
		self.exposure_speed_edit.setMinimum(1)
		self.exposure_speed_edit.setMaximum(400000)

		self.exposure_speed_edit.setValue(beam_math.cam_exp_time)
		
		self.start_button = QPushButton(play_symbol, self)
		self.start_button.setMaximumWidth(50)
		self.start_button.clicked.connect(self.start_camera)
		
		#if mode==Mode.CALIBRATION:
		#	left_layout.addStretch()

		if True:#mode==Mode.RAW:
			self.background_edit=QCheckBox('Вычитать шум')

			if not pi_available:
				self.beam_edit=QCheckBox('aoaoa')
			# self.background_edit.setMaximumWidth(100)
			# self.background_edit.setMinimum(0)
			# self.background_edit.setMaximum(1023)
			# self.background_edit.setValue(0)
			
			self.ROI_label = QLabel('ROI')

			#self.crop_edit.setBackColor(Qt
			if show_factor_2:
				self.ROI_check = QCheckBox()
				self.ROI_check.setText('/2')
			self.cnt=0
			self.temp_label=QLabel("temp=0.0'C")
			self.update_pi_temperatre()
			
			self.calibration_check=QCheckBox()
			self.calibration_check.setText('Дебаер калибровкой')

			self.fft_check=QCheckBox()
			self.fft_check.setText('Дебаер FFТ')
			
			self.log_checkBox=QCheckBox('log10')
			self.log_checkBox.stateChanged.connect(self.change_scale)
			self.log_scale=False
			
			# self.x0_label = QLabel('x0')
			# self.y0_label = QLabel('y0')
			self.delta_x_label = QLabel(u'\u0394 x')
			self.delta_y_label = QLabel(u'\u0394 y')
			
			if mode!=Mode.CALIBRATION:
				self.save_button = QPushButton('Save', self)
				self.save_button.setMaximumWidth(50)
				self.dir_edit=QLineEdit('1',self)
				self.dir_edit.setMaximumWidth(100)
				
				self.dir_edit.move(200,PB_HEIGHT+45)
				self.save_button.move(310,PB_HEIGHT+45)
				
				
			self.zoomout_button=QPushButton('Zoom out',self)
			self.zoomout_button.setMaximumWidth(100)
			self.zoomout_button.clicked.connect(self.zoomout)
			
			if mode==Mode.PREVIEW:
				self.awb_checkbox=QCheckBox()
				self.awb_checkbox.setText('Баланс белого')
				self.awb_checkbox.setChecked(True)
				self.awb_checkbox.stateChanged.connect(self.set_awb)
			
			self.gain_checkbox=QCheckBox()
			self.gain_checkbox.setText('Усиление')
			self.gain_checkbox.setChecked(beam_math.cam_exp_mode)
			self.gain_checkbox.stateChanged.connect(self.set_gain)
#add start
			#left_layout.addStretch()
			#left_layout.addWidget(self.crop_edit)
			if show_factor_2:
				left_layout.addWidget(self.ROI_check)
			left_layout.addWidget(self.temp_label)
			if self.mode!=Mode.PREVIEW:
				left_layout.addWidget(self.calibration_check)
				left_layout.addWidget(self.fft_check)
			if self.mode!=Mode.PREVIEW:
				if not pi_available:
					left_layout.addWidget(self.beam_edit)
				left_layout.addWidget(self.background_edit)
			left_layout.addWidget(self.exposure_speed_label)
			left_layout.addWidget(self.exposure_speed_edit)
			#left_layout.addWidget(QLabel('Уровень шума'))		

			left_layout.addWidget(self.start_button)
#save		# if mode!=Mode.CALIBRATION:
				# left_layout.addWidget(self.save_button)
				# left_layout.addWidget(self.dir_edit)
			left_layout.addWidget(self.zoomout_button)
			if mode==Mode.PREVIEW:
				left_layout.addWidget(self.awb_checkbox)
			left_layout.addWidget(self.gain_checkbox)
			left_layout.addWidget(self.log_checkBox)
			if mode==Mode.CALIBRATION:
				self.get_calibration_button=QPushButton()
				self.get_calibration_button.setText('Снять\nкалибвку')
				self.get_calibration_button.clicked.connect(self.get_calibration)
				
				self.reset_mask_button=QPushButton()
				self.reset_mask_button.setText('Сброс маски')
				self.reset_mask_button.clicked.connect(self.reset_mask)
				
				self.get_noise_button=QPushButton()
				self.get_noise_button.setText('Снять\шум')
				self.get_noise_button.clicked.connect(self.save_noise_map)
				#self.get_calibration_button.setMaximumWidth(50)
		
				self.label1=QLabel()
				self.label1.setText('Калибровочные\nк-ты')

		
				self.calibration_coeffs_tb=QLineEdit()
				self.calibration_coeffs_tb.setText(str(beam_math.calibration_coeffs))
				self.calibration_coeffs_tb.textChanged.connect(self.change_coeffs)

				left_layout.addWidget(self.get_calibration_button)
				left_layout.addWidget(self.reset_mask_button)
				left_layout.addWidget(self.get_noise_button)

				left_layout.addWidget(self.label1)

				left_layout.addWidget(self.calibration_coeffs_tb)

				
				self.mask_pos=(0,0)
				self.mask_size=(1,1)
				self.mouse_button=0
				self.mask=[[0]]
				self.need_calibration=False
			elif mode==Mode.RAW:
				self.draw_sect_checkbox=QCheckBox('Рисовать сечения')
				self.units_checkbox=QCheckBox('Пересчёт в мкм')
				self.units_checkbox.stateChanged.connect(self.change_units)
				self.units_val,self.units_txt=1.0,'пик'
				
				left_layout.addWidget(self.draw_sect_checkbox)
				left_layout.addWidget(self.units_checkbox)


				# left_layout.addWidget(self.x0_label)
				# left_layout.addWidget(self.y0_label)
				self.max_I_label=QLabel('max I : ')
#ddddd
				self.tmp_label=QLabel()
				left_layout.addWidget(self.tmp_label)
				
				left_layout.addWidget(self.max_I_label)
				left_layout.addWidget(self.delta_x_label)
				left_layout.addWidget(self.delta_y_label)
#add end
			#left_layout.addStretch()
			left_layout.setAlignment(Qt.AlignTop)
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
		if self.mode!=Mode.PREVIEW:
			qImg=self.ndarray2qimage(np.zeros([PB_HEIGHT,PB_WIDTH],'uint8'))
		else:
			qImg=self.ndarray2qimage(np.zeros([PB_HEIGHT,PB_WIDTH,3],'uint8'))
		pixmap = QPixmap(QImage(qImg))
		self.label.setPixmap(pixmap)
		self.label.setFixedSize(PB_WIDTH,PB_HEIGHT);
		
		self.cmap_label=QLabel()
		cmap_arr=np.zeros((PB_HEIGHT,12),dtype='uint8')
		cmap_arr+=np.linspace(255,0,PB_HEIGHT,dtype='uint8')[:,None]
		
		qImg=self.ndarray2qimage(cmap_arr)
		qImg.setColorTable(self.rgbas)
		pixmap = QPixmap(QImage(qImg))
		self.cmap_label.setPixmap(pixmap)
		self.cmap_label.setFixedSize(12,PB_HEIGHT);
		# if mode==Mode.PREVIEW:
			# beam_math.noise_map=[[10]]
		# print(beam_math.noise_map)
		#self.label.move(140,0);

		self.real_label_size=(PB_WIDTH,PB_HEIGHT)
		self.label_pos=(0,1)
		right_layout.addWidget(self.label)
		right_layout.addWidget(self.cmap_label)
		# if mode!=Mode.CALIBRATION:
			# right_layout.addWidget(self.save_button)
			# right_layout.addWidget(self.dir_edit)
		
		self.setLayout(major_layout)

		
		
		self.crop_pos=QPoint(0,0)
		
		self.init_size=QSize(raw_resolution[0],raw_resolution[1]) if\
				mode!=Mode.PREVIEW else QSize(preview_resolution[0],preview_resolution[1])
		self.crop_size=self.init_size
		
		major_layout.addLayout(left_layout)
		major_layout.addLayout(right_layout)
		

		self.exposure_speed_edit.valueChanged.connect(self.set_shutter_speed)
	
		if self.mode!=Mode.CALIBRATION:
			self.save_button.clicked.connect(self.save_button_clicked)
			#self.label.installEventFilter(self)
			# self.crop_edit.installEventFilter(self)
			# self.calibration=None
			# if use_calibration:
			
				# self.calibration=np.load(path_to_calibration_im)
		if mode==Mode.RAW or mode==Mode.CALIBRATION:
			self.calc=beam_math(raw_resolution[0],raw_resolution[1])
		
		self.need_save=False
		self.need_noise_save=False
		
		self.mouse_pressed=False
		self.mouse_start_pos=QPoint(0,0)
		self.mouse_pos=QPoint(1,1)
		
		self.rect_color=Qt.red


	def change_scale(self,state):
		self.log_scale=state

	def change_units(self,state):
		print(1.0,'пик' if state==0 else um,'мкм')
		(self.units_val,self.units_txt)=(1.0,'пик') if state==0 else (um,'мкм')
		
	
	def reset_mask(self):
		self.mask=np.ones((raw_resolution[1],raw_resolution[0]),dtype='uint16')
	
	def change_coeffs(self):
		txt=self.calibration_coeffs_tb.text()
		txt=txt.replace('(','')
		txt=txt.replace(')','')
		txt=txt.replace("'","")
		try:
			beam_math.calibration_coeffs=[int(c) for c in txt.split(',')]
		except:
			return
		print(beam_math.calibration_coeffs)
	def save_noise_map(self):
		print('at noise')
		self.need_noise_save=True
	
	def set_gain(self):
		beam_math.cam_exp_mode=self.gain_checkbox.isChecked()
		if pi_available:
			self.worker.camera.close()
			self.close_camera()
			self.init_camera()

		# self.worker.camera.exposure_mode='auto' if self.gain_checkbox.isChecked() else 'off'
		# self.worker.camera.ISO=100
#awb
	def set_awb(self):
		# if not self.awb_checkbox.isChecked():
			# self.worker.awb_gains=(1,7)
		self.worker.camera.awb_mode='auto' \
				if self.awb_checkbox.isChecked() else 'cloudy'
	
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
		self.worker.io_exception.connect(self.handle_io_exception)
		
		print(self.mode,self.thread)
	
	def handle_io_exception(self):
		print('i/o exception\n\n\n')
		self.worker.is_running=False
		self.worker.camera.close()
		self.close_camera()
		
		sleep(1)
		
		self.init_camera()
		if not self.thread.isRunning():
			self.thread.start()
		self.worker.is_running=True
		
	def zoomout(self):
		self.crop_pos=QPoint(0,0)
		self.crop_size=self.init_size
		
		if self.mode!=Mode.PREVIEW:
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
				# tmp_pos-=self.crop_pos
			
				pass
			else:
				
				tmp_pos.setX(self.tomod4(tmp_pos.x(),raw_resolution[0]))
				tmp_pos.setY(self.tomod4(tmp_pos.y(),raw_resolution[1]))
				tmp_size.setWidth(self.tomod4(tmp_size.width(),raw_resolution[0]))
				tmp_size.setHeight(self.tomod4(tmp_size.height(),raw_resolution[1]))
			
			
				self.crop_pos=tmp_pos
				self.crop_size=tmp_size
				if self.mode!=Mode.PREVIEW:
					self.calc.update_grid(self.crop_size.width(),\
					self.crop_size.height())
			
			if self.mode==Mode.CALIBRATION and self.rect_color==Qt.cyan:
				tmp_I,tmp_J=np.mgrid[0:raw_resolution[1],0:raw_resolution[0]]
				
				self.mask=	(tmp_I>tmp_pos.y())*\
							(tmp_J>tmp_pos.x())*\
							(tmp_I<(tmp_size.height()+tmp_pos.y()))*\
							(tmp_J<(tmp_size.width()+tmp_pos.x())) 
			self.mouse_pressed=False


	
		
	def save_button_clicked(self):

		self.need_save=True
		
		
	def set_shutter_speed(self,val):
		print('at es-->')
		if pi_available:
			self.worker.set_shutter_speed(val)
		beam_math.cam_exp_time=val
		print(cam_exp_time)

	def print_smt(self):
		print(self.worker)
	def ndarray2qimage(self,arr):
		arr2=np.require(arr,'uint8','C')
		format_=QImage.Format.Format_Indexed8 if self.mode!=Mode.PREVIEW else QImage.Format.Format_RGB888
		#format_=QImage.Format.Format_RGB888
		#print(self.mode,arr.shape)
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
		if pi_available and self.worker.camera.closed:
			return

#температура
		if self.cnt%10==0:
			self.update_pi_temperatre()
			self.cnt=0
		self.cnt+=1
#временно
		self.tmp_label.setText(f'{np.random.random()}')#self.worker.camera.exposure_speed)

#1/фпс
		print(time()-self.prev)
		self.prev=time()
		
		if self.need_noise_save:
			beam_math.noise_map=img.copy()
			self.need_noise_save=False
			print(len(beam_math.noise_map))
			
#обрезка
		img=img[self.crop_pos.y():self.crop_pos.y()+self.crop_size.height(),\
					self.crop_pos.x():self.crop_pos.x()+self.crop_size.width()]
		
#для эмуляции
		if self.beam_edit.isChecked():
			img*=0
		if not pi_available:
			img+=np.random.randint(0,emulate_noise,img.shape,dtype='uint16')
		
		if not (self.mode==Mode.PREVIEW):
#обновление калибровочных коэффициентов
			if self.mode==Mode.CALIBRATION:
				if len(self.mask)>4:
					img*=self.mask[self.crop_pos.y():self.crop_pos.y()+self.crop_size.height(),\
					self.crop_pos.x():self.crop_pos.x()+self.crop_size.width()]
				if self.need_calibration:
					self.calibration_coeffs_tb.setText(str(get_calibration_pixelwise(img,1-self.crop_pos.x()%2,1-self.crop_pos.y()%2)))
					self.need_calibration=False
			
#вычитание шума			
			if len(beam_math.noise_map)>5 and self.background_edit.isChecked():
				img=img*(img>\
				beam_math.noise_map[self.crop_pos.y():self.crop_pos.y()+\
				self.crop_size.height(),\
				self.crop_pos.x():self.crop_pos.x()+self.crop_size.width()])
#дебаер калибровкой
			if self.calibration_check.isChecked():
				img=calibrate(img,beam_math.calibration_coeffs[0],\
							beam_math.calibration_coeffs[1],\
							beam_math.calibration_coeffs[2],\
							1-self.crop_pos.x()%2,\
							1-self.crop_pos.y()%2)
#дебарер БПФ
			if self.fft_check.isChecked():
				img=img.astype('float32')
				tmp_max=np.max(img)
				img=beam_math.fft_debayer(img)
				img=img*tmp_max/np.max(img)
				img=img.astype('uint16')
			#########################
#сохранение					
			if self.need_save:
				np.save(os.path.join(init_dir,self.dir_edit.text()),img)
				self.need_save=False
				
#сечения			
			if not self.disable_calculations and self.mode==Mode.RAW:
				
				if img.shape[0]!=self.calc.I_grid.shape[0] or img.shape[1]!=self.calc.I_grid.shape[1]:
					print(f'img:{img.shape} \tgrid:{self.calc.I_grid.shape}')
					return -1
		
				
				# self.x0_label.setText(f'x0 : {int(mx*self.units_val)} {self.units_txt}')
				# self.y0_label.setText(f'y0 : {int(my*self.units_val)} {self.units_txt}')
				# self.delta_x_label.setText(f'\u0394x:{round(RMS_x*self.units_val,3)} {self.units_txt}')
				# self.delta_y_label.setText(f'\u0394y:{round(RMS_y*self.units_val,3)} {self.units_txt}')

				mx=np.argmax(img)

				
				my=mx//img.shape[1]
				mx=mx%img.shape[1]
				# mx=int(mx)
				# my=int(my)

				xsect=img[my,:].copy()
				ysect=img[:,mx].copy()


				step=1
				h=raw_resolution[1]//40#min(self.crop_size.width(),self.crop_size.height())//40


				
				fwhmx=beam_math.FWHM(xsect)
				fwhmy=beam_math.FWHM(ysect)
				max_I=np.max(img)
				self.max_I_label.setText(f'max I:{max_I}')
				if max_I==1023:
					self.max_I_label.setStyleSheet('background-color:red')
				else:
					self.max_I_label.setStyleSheet('background-color:white')
				self.delta_x_label.setText(f'\u0394x:{round(fwhmx*self.units_val,3)} {self.units_txt}')
				self.delta_y_label.setText(f'\u0394y:{round(fwhmy*self.units_val,3)} {self.units_txt}')

		
		if self.mode==Mode.RAW or self.mode==Mode.CALIBRATION:
			if self.log_scale:
				m=np.max(img)
				img=np.log10(1+img)*m/(np.log10(1+m))
				img=img.astype('uint16')
#отрисовка
			#img=(img>>2).astype('uint8')
		tmp=self.ndarray2qimage((img>>2).astype('uint8'))
		tmp.setColorTable(self.rgbas)
		tmp=QPixmap(tmp)#.scaled(PB_WIDTH,PB_HEIGHT))
		tmp=tmp.scaled(PB_WIDTH,PB_HEIGHT,Qt.KeepAspectRatio)
		self.label.setPixmap(tmp)#QPixmap(qImg))
		self.real_label_size=(tmp.size().width(),tmp.size().height())
		if self.mouse_pressed:
			self.draw_rect()
		if self.mode==Mode.RAW:
			xsect=np.vstack((np.linspace(0,self.real_label_size[0],len(xsect)),h*(xsect/1023))).astype('uint16').T
			ysect=np.vstack((h*(ysect/1023),np.linspace(0,self.real_label_size[1],len(ysect)))).astype('uint16').T
			if not (self.mode==Mode.PREVIEW or self.disable_calculations):
				if self.mode==Mode.RAW and self.draw_sect_checkbox.isChecked():#enable_draw_sect:	
					self.draw_section(ysect)
					self.draw_section(xsect,\
						int(mx*self.real_label_size[0]/self.crop_size.width()),\
						int(my*self.real_label_size[1]/self.crop_size.height()),
						int(fwhmx*self.real_label_size[0]/self.crop_size.width())//2,\
						int(fwhmy*self.real_label_size[1]/self.crop_size.height())//2)
		
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
	
	def update_pi_temperatre(self):
		if pi_available:
			self.temp_label.setText(os.popen('vcgencmd measure_temp').readline()[:-1])

