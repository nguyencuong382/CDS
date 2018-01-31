import os
from Ui import Ui_Label
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTreeWidgetItem
from PresenterOpen import PresenterOpen

class MainWindow(Ui_Label):
	def __init__(self, mainWindow):
		self.mainWindow = mainWindow
		self.setupUi(mainWindow)
		self.actionOpen.triggered.connect(self.func_open)

		self.presenterOpen = PresenterOpen(self)

	def setDir(self, name_dir):
		self.dir = name_dir
		
	def func_open(self):
		new_dir = QtWidgets.QFileDialog.getExistingDirectory(self.mainWindow, 'Select directory')
		self.presenterOpen.processNewDir(new_dir)

	def setLabelCurrentDir(self, new_dir):
		self.lineEdit.setText(new_dir)

	def setTree(self,new_dir):
		list_f = os.listdir(new_dir)
		for f in list_f:
			item = QTreeWidgetItem(self.treeWidget, [f])

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Label = QtWidgets.QMainWindow()
    ui = MainWindow(Label)
    Label.show()
    sys.exit(app.exec_())
