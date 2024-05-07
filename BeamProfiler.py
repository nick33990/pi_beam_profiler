import sys
import MainWindow
from PyQt5 import QtWidgets

if __name__=="__main__":
	app = QtWidgets.QApplication(sys.argv)
	widget = MainWindow.MainWindow()
	widget.resize(800, 600)
	widget.show()
	sys.exit(app.exec())
