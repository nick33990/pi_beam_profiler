import numpy as np
from time import time,sleep
import sys
import os
from PIL import Image

from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, \
	QHBoxLayout, QDoubleSpinBox, QTabWidget, QWidget, \
	QLabel, QCheckBox, QSpinBox

from Constants import *
from InteractionWidget import InteractionWidget
#from CalibrationWidget import CalibrationWidget

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
		self.tab.addTab(tab_3,'CALIBRATION')
		self.tab.currentChanged.connect(self.on_tab_changed)
		self.prev_tab=0

		self.setCentralWidget(self.tab)
		
	def on_tab_changed(self,val):
		#val=1<=>активана previes итд
		print(val,self.prev_tab)
		#try:
		if True:
			if self.prev_tab==0:
				self.interaction_widget_tab_1.worker.camera.close()
				self.interaction_widget_tab_1.close_camera()
			elif self.prev_tab==1:
				self.interaction_widget_tab_2.worker.camera.close()
				self.interaction_widget_tab_2.close_camera()
			elif self.prev_tab==2:
				self.calibration_widget.worker.camera.close()
				self.calibration_widget.close_camera()
			else:
				print('prev how')
			if val==1:
				self.interaction_widget_tab_2.init_camera()#print_smt()
			elif val==0:
				self.interaction_widget_tab_1.init_camera()#print_smt()
			elif val==2:
				self.calibration_widget.init_camera()
			#self.centralWidget().widget(1).print_smt()
		# except:
			# print('aaaaa')
			# self.prev_tab=val
		self.prev_tab=val
			#self.centralWidget.widget[0].camera.close()
