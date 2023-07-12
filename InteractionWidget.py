import numpy as np
from time import time,sleep
import sys
import os
from PIL import Image
from scipy.ndimage import zoom

from PyQt5.QtCore import QThread

from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, \
	QHBoxLayout, QDoubleSpinBox, QTabWidget, QWidget, \
	QLabel, QCheckBox, QSpinBox
from PyQt5.QtGui import QPixmap,QImage

from Constants import *
from Camera import Producer


class InteractionWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.button_pressed=False
		#self.setFixedSize(WIDTH,HEIGHT-10)
		self.setGeometry(0,0,WIDTH,HEIGHT)
		
		left_layout = QVBoxLayout()
		right_layout = QVBoxLayout()
		major_layout = QHBoxLayout()
		self.exposure_speed_label = QLabel('Exposure\ntime')
		

		self.exposure_speed_edit = QSpinBox()

		self.exposure_speed_edit.setMaximumWidth(100)
		self.exposure_speed_edit.setPrefix('us: ')
		self.exposure_speed_edit.setMinimum(1)
		self.exposure_speed_edit.setMaximum(100000)

		self.exposure_speed_edit.setValue(init_exposure_speed)


		self.ROI_label = QLabel('ROI')
		self.ROI_check = QCheckBox()


		self.start_button = QPushButton('>', self)
		self.start_button.setMaximumWidth(50)
		self.start_button.clicked.connect(self.start_camera)


		self.save_button = QPushButton('Save', self)
		self.save_button.setMaximumWidth(50)

		self.x0_label = QLabel('x0')
		self.y0_label = QLabel('y0')
		self.delta_x_label = QLabel(u'\u0394 x')
		self.delta_y_label = QLabel(u'\u0394 y')


		left_layout.addWidget(self.exposure_speed_label)
		left_layout.addWidget(self.exposure_speed_edit)
		left_layout.addWidget(self.ROI_label)
		left_layout.addWidget(self.ROI_check)
		left_layout.addWidget(self.start_button)
		left_layout.addWidget(self.save_button)
		left_layout.addWidget(self.x0_label)
		left_layout.addWidget(self.y0_label)
		left_layout.addWidget(self.delta_x_label)
		left_layout.addWidget(self.delta_y_label)
		
		self.setLayout(major_layout)
		self.label = QLabel(self)

		#qImg=self.ndarray2qimage(np.zeros([init_resolution[0],init_resolution[1],3],'uint8'))
		qImg=self.ndarray2qimage(np.zeros([PB_HEIGHT,PB_WIDTH,3],'uint8'))
		self.pixmap = QPixmap(QImage(qImg))
		
		self.label.setPixmap(self.pixmap)
		self.label.setFixedSize(PB_WIDTH,PB_HEIGHT);
		self.label.move(120,0);
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
		
	def set_shutter_speed(self,val):
		self.worker.set_shutter_speed(val)
	
	def ndarray2qimage(self,arr):
		arr2=np.require(arr,'uint8','C')
		
		return QImage(arr2,arr.shape[1],arr.shape[0],QImage.Format.Format_Indexed8)

	def start_thread(self):
		self.button_pressed=True
		self.start_button.setText('||')
		self.thread=QThread()
		self.worker=Producer()
		self.worker.moveToThread(self.thread)
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
			self.start_button.setText('>')
			self.worker.stop()
			self.thread.quit()
			self.thread.wait()
	def on_image_ready(self,img_data):
		zoomed=img_data[0]#zoom(img_data[0],PB_WIDTH/img_data[0].shape[0])
		self.label.setPixmap(QPixmap(self.ndarray2qimage(zoomed)))#QPixmap(qImg))
		self.label.repaint()

