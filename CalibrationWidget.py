import numpy as np

from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,\
QLabel,\
QPushButton,QLineEdit
from PyQt5.QtGui import QPixmap,QImage

from Constants import *

#from picamera import piCamera

class CalibrationWidget(QWidget):
	def __init__(self):
		super().__init__()	
		
		# left_layout=QVBoxLayout()
		# major_layout=QHBoxLayout()
		# right_layout=QVBoxLayout()
		
		self.get_calibration_button=QPushButton(self)
		self.get_calibration_button.setText('Снять\nкалибвку')
		#self.get_calibration_button.setFixedSize(100,50)
		
		self.label1=QLabel(self)
		self.label1.setText('Калибровочные\nкоэффициенты')
		#self.label1.setFixedSize(100,50)
		#self.label1.move(0,50)
		
		self.calibration_coeffs_tb=QLineEdit(self)
		self.calibration_coeffs_tb.setText('7,8,9')
		#self.calibration_coeffs_tb.setFixedSize(100,30)
		#self.calibration_coeffs_tb.move(0,105)
		# left_layout.addWidget(self.get_calibration_button)
		# left_layout.addWidget(QLabel('Калибровочные коэффициенты'))
		# left_layout.addWidget(self.calibration_coeffs_tb)

		# self.setLayout(major_layout)		

		self.label=QLabel(self)
		qImg=self.ndarray2qimage(np.zeros([PB_HEIGHT,PB_WIDTH,3],'uint8'))
		self.pixmap = QPixmap(QImage(qImg))
		self.label.setPixmap(self.pixmap)
		self.label.setFixedSize(PB_WIDTH,PB_HEIGHT);
		self.label.move(140,0);

		
		# major_layout.addLayout(left_layout)
		# major_layout.addLayout(right_layout)
	
	def take_picture(self):
		with piCamera() as camera:
			pass
	
	def ndarray2qimage(self,arr):
		arr2=np.require(arr,'uint8','C')
		format_=QImage.Format.Format_Indexed8
		#format_=QImage.Format.Format_RGB888
		return QImage(arr2,arr.shape[1],arr.shape[0],format_)


	
