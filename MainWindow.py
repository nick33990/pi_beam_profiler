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

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow,self).__init__()

		self.setFixedSize(QSize(WIDTH, HEIGHT))
		self.setWindowTitle("BEAM PROFILER")

		main_layout = QHBoxLayout()
		layout_tab_1 = QHBoxLayout()
		layout_tab_2 = QHBoxLayout()

		self.tab = QTabWidget()

		tab_1 = QWidget()
		tab_1.setLayout(layout_tab_1)
			
		tab_2 = QWidget()
		tab_2.setLayout(layout_tab_2)

		self.interaction_widget_tab_1 = InteractionWidget(Mode.RAW)
		# image_widget_tab_1 = ImageWidget(1000)

		layout_tab_1.addWidget(self.interaction_widget_tab_1)
		# layout_tab_1.addWidget(image_widget_tab_1)
		
		interaction_widget_tab_2=InteractionWidget(Mode.PREVIEW)
		layout_tab_2.addWidget(interaction_widget_tab_2)

		self.tab.currentChanged.connect(self.on_tab_changed)


		self.tab.addTab(tab_1, 'RAW')
		self.tab.addTab(tab_2, 'PREVIEW')


		self.setCentralWidget(self.tab)
	
	def on_tab_changed(self,val):
		#val=1<=>активана previes итд
		if val==1:
			
			self.interaction_widget_tab_1.worker.camera.close()#print_smt()
			#self.centralWidget().widget(1).print_smt()
			#self.centralWidget.widget[0].camera.close()
