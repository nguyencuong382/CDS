from PyQt5 import QtCore, QtGui, QtWidgets
import json
from os.path import join, exists

class Cache:
	def __init__():
		self.file_cache_name = 'cache.json'
		self.dir = ''
		self.current_img = 0

	def readCache():
		if not exists(self.file_cache_name):
			pass
class PresenterOpen:
	def __init__(self, view):
		self.view = view

	def processNewDir(self, new_dir, isInit = False):
		if(new_dir != ''):
			self.view.setLabelCurrentDir(new_dir)
			self.view.setTree(new_dir)
		else:
			pass
		if(isInit):
			pass
