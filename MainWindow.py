import numpy as np
from time import time,sleep
import sys
import os
from PIL import Image
import pandas as pd

from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt, QTimer, QEvent,QPoint
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, \
	QHBoxLayout, QDoubleSpinBox, QTabWidget, QWidget, \
	QLabel, QCheckBox, QSpinBox, QTextEdit, QTableWidget,QTableWidgetItem

from Constants import *
from InteractionWidget import InteractionWidget
from coeffs_widget import coeffs_widget

from BeamMath import beam_math
class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow,self).__init__()

		self.setFixedSize(QSize(WIDTH, HEIGHT))
		self.setWindowTitle("BEAM PROFILER")

		main_layout = QHBoxLayout()
		layout_tab_1 = QHBoxLayout()
		layout_tab_2 = QHBoxLayout()
		layout_tab_3=QHBoxLayout()

		self.tab = QTabWidget()

		tab_1 = QWidget()
		tab_1.setLayout(layout_tab_1)
			
		tab_2 = QWidget()
		tab_2.setLayout(layout_tab_2)

		tab_3 = QWidget()
		tab_3.setLayout(layout_tab_3)
		
		tab_4=QWidget()
		layout_tab_4=QHBoxLayout()
		tab_4.setLayout(layout_tab_4)
		layout_tab_4.addWidget(coeffs_widget())
		
		self.interaction_widget_tab_1 = InteractionWidget(Mode.RAW)
		# image_widget_tab_1 = ImageWidget(1000)

		layout_tab_1.addWidget(self.interaction_widget_tab_1)
		# layout_tab_1.addWidget(image_widget_tab_1)
		
		self.interaction_widget_tab_2=InteractionWidget(Mode.PREVIEW)
		layout_tab_2.addWidget(self.interaction_widget_tab_2)
		
		self.calibration_widget=InteractionWidget(Mode.CALIBRATION)#CalibrationWidget()
		layout_tab_3.addWidget(self.calibration_widget)
		
		if start_mode==Mode.RAW:
			self.interaction_widget_tab_1.init_camera()
		else:
			self.interaction_widget_tab_2.init_camera()
		
		self.tab.addTab(tab_1, 'RAW')
		self.tab.addTab(tab_2, 'PREVIEW')
		self.tab.addTab(tab_3, 'CALIBRATION')
		self.tab.addTab(tab_4, 'CALIBRATION COEFFS')
		
		self.tab.currentChanged.connect(self.on_tab_changed)
		self.prev_tab=0

		self.setCentralWidget(self.tab)

		#self.tab.installEventFilter(self)

	def on_tab_changed(self,val):
		#val=1<=>активана previes итд
		print(val,self.prev_tab)
		#print(cam_exp_time	)
		#try:да, сделано не очень
		if True:
			if self.prev_tab==0:
				self.interaction_widget_tab_1.button_pressed=False
				self.interaction_widget_tab_1.worker.is_running=False
				self.interaction_widget_tab_1.start_button.setText(play_symbol)
				self.interaction_widget_tab_1.gain_checkbox.setEnabled(True)
				
				if pi_available:
					self.interaction_widget_tab_1.worker.camera.close()
					self.interaction_widget_tab_1.close_camera()
			elif self.prev_tab==1:
				self.interaction_widget_tab_2.button_pressed=False
				self.interaction_widget_tab_2.worker.is_running=False
				self.interaction_widget_tab_2.start_button.setText(play_symbol)
				self.interaction_widget_tab_2.gain_checkbox.setEnabled(True)
				
				if 	pi_available:
					self.interaction_widget_tab_2.worker.camera.close()
					self.interaction_widget_tab_2.close_camera()
			elif self.prev_tab==2:
				self.calibration_widget.button_pressed=False
				self.calibration_widget.worker.is_running=False
				self.calibration_widget.start_button.setText(play_symbol)
				self.calibration_widget.gain_checkbox.setEnabled(True)
				
				if pi_available:
					self.calibration_widget.worker.camera.close()
					self.calibration_widget.close_camera()
			else:
				print('prev how')
			if val==1:
				self.interaction_widget_tab_2.init_camera()#print_smt()

			elif val==0:
				self.interaction_widget_tab_1.init_camera()#print_smt()
				self.interaction_widget_tab_1.exposure_speed_edit.setValue(beam_math.cam_exp_time)
				self.interaction_widget_tab_1.gain_checkbox.setChecked(beam_math.cam_exp_mode)
				#self.interaction_widget_tab_1.
			elif val==2:
				self.calibration_widget.init_camera()
				self.calibration_widget.exposure_speed_edit.setValue(beam_math.cam_exp_time)
				self.calibration_widget.gain_checkbox.setChecked(beam_math.cam_exp_mode)

		self.prev_tab=val
			#self.centralWidget.widget[0].camera.close()

	def move_xy(self,dirx,diry,crop_pos,crop_size,resolution=raw_resolution):
		shift=min(crop_size.width(),crop_size.height())//20
		if shift==0:
			shift=1
		newx=crop_pos.x()+dirx*shift
		newy=crop_pos.y()+diry*shift
		
		if newx<0:
			newx=1
		elif newx+crop_size.width()>resolution[0]:
			newx=crop_size.width()-1

		if newy<0:
			newy=1
		elif newy+crop_size.height()>resolution[1]:
			newy=crop_size.height()-1
		return QPoint(newx,newy)

	def keyPressEvent(self,e):
		dirx,diry=0,0
		if e.key()==Qt.Key_W:
			diry=1
		elif e.key()==Qt.Key_S:
			diry=-1
		elif e.key()==Qt.Key_D:
			dirx=-1
		elif e.key()==Qt.Key_A:
			dirx=1
		else:
			return

		if self.prev_tab==0:#это ужасно
			self.interaction_widget_tab_1.crop_pos=self.move_xy(dirx,diry,\
				self.interaction_widget_tab_1.crop_pos,\
				self.interaction_widget_tab_1.crop_size)
		elif self.prev_tab==1:
			self.interaction_widget_tab_2.crop_pos=self.move_xy(dirx,diry,\
				self.interaction_widget_tab_2.crop_pos,\
				self.interaction_widget_tab_2.crop_size,
				resolution=preview_resolution)
		elif self.prev_tab==2:
			self.calibration_widget.crop_pos=self.move_xy(dirx,diry,\
				self.calibration_widget.crop_pos,\
				self.calibration_widget.crop_size)


