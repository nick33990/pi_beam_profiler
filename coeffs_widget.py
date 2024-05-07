import pandas as pd
from PyQt5.QtCore import QThread

from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt, QTimer,QPoint,QEvent
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, \
	QHBoxLayout, QDoubleSpinBox, QTabWidget, QWidget, \
	QLabel, QCheckBox, QSpinBox,QLineEdit,QTableWidget,QTableWidgetItem
from PyQt5.QtGui import QPixmap,QImage,QPainter,QPen,QColor

from Constants import *
from BeamMath import beam_math

class coeffs_widget(QWidget):
	def __init__(self):
		super().__init__()
		layout=QVBoxLayout()
		
		coeffs=pd.read_csv(path_to_coeffs,sep=':',header=None)
		self.table=QTableWidget(len(coeffs),2)
		self.table.verticalHeader().setVisible(False)
		self.table.setHorizontalHeaderLabels(['Длина волны','Коэффициенты'])
		self.table.setMinimumWidth(320)
		self.table.setMaximumWidth(320)

		for i in range(len(coeffs)):
			for j in range(2):
				s=str(coeffs[j].iloc[i])
				self.table.setItem(i,j,QTableWidgetItem(s))

		for i in [0,1]:
			self.table.setColumnWidth(i,160)
		layout.addWidget(self.table)
		#layout.addWidget(QLabel('Метка'))
		self.label_edit=QLineEdit()
		self.label_edit.setPlaceholderText('Метка')
		self.label_edit.setMaximumWidth(320)
		layout.addWidget(self.label_edit)
		
		self.add_coeff_button=QPushButton('Добавить текущии коэффициенты')
		self.add_coeff_button.setMaximumWidth(300)
		self.add_coeff_button.clicked.connect(self.on_coeff_button_clicked)
		layout.addWidget(self.add_coeff_button)
		
		self.rm_coeff_button=QPushButton('Удалить строку')
		self.rm_coeff_button.setMaximumWidth(300)
		self.rm_coeff_button.clicked.connect(self.on_rm_coeff_button_clicked)
		layout.addWidget(self.rm_coeff_button)
		
		self.save_changes_button=QPushButton('Сохранить таблицу в файл')
		self.save_changes_button.setMaximumWidth(300)
		self.save_changes_button.clicked.connect(self.save_to_file)
		layout.addWidget(self.save_changes_button)
		
		self.setLayout(layout)

	def on_coeff_button_clicked(self):
		n=self.table.rowCount()
		self.table.insertRow(n)
		self.table.setItem(n,0,QTableWidgetItem(self.label_edit.text()))
		self.table.setItem(n,1,\
		QTableWidgetItem(str(beam_math.calibration_coeffs)))
		
	def on_rm_coeff_button_clicked(self):
		for i in range(self.table.rowCount()):
			if self.table.item(i,0).text()==self.label_edit.text():
				self.table.removeRow(i)
				break
	
	def save_to_file(self):
		with open(path_to_coeffs,'w') as f:
			for i in range(self.table.rowCount()):
				s=f'{self.table.item(i,0).text()}:{self.table.item(i,1).text()}\n'
				f.write(s)
		f.close()
