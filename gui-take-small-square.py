import sys
import os
import cv2
import xml.etree.ElementTree as ET
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLineEdit, QLabel, QShortcut, QAction, QComboBox, QStyleOptionComboBox
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen, QKeySequence
from rename import Filter
import time
class Box:
	def __init__(self, bndbox, name, pose = 'Unspecified', truncated = 0, difficult = 0):
		self.name = name
		self.pose = pose
		self.truncated = truncated
		self.difficult = difficult
		self.bndbox = bndbox
	def getName(self):
		return self.name
	def getPose(self):
		return self.pose
	def getTruncated(self):
		return self.truncated
	def getDifficult(self):
		return self.difficult
	def getBndbox(self):
		return self.bndbox
	def setName(self, name):
		self.name = name
	def setBndbox(self, new_box):
		self.bndbox = new_box
def indent(elem, level=0):
	i = "\n" + level*"  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

def generate_xml(tree, new_objects):
	root = tree.getroot()	
	objs = root.findall('object')
	for obj in objs:
		root.remove(obj)
	for obj in new_objects:
		new_obj = ET.Element('object')

		name = ET.Element('name')
		name.text = obj.getName()
		new_obj.append(name)

		pose = ET.Element('pose')
		pose.text = obj.getPose()
		new_obj.append(pose)

		truncated = ET.Element('truncated')
		truncated.text = str(obj.getTruncated())
		new_obj.append(truncated)

		difficult = ET.Element('difficult')
		difficult.text = str(obj.getDifficult())
		new_obj.append(difficult)

		box = obj.getBndbox()
		bndbox = ET.Element('bndbox')
		xmin = ET.Element('xmin')
		xmin.text = str(box[0])

		ymin = ET.Element('ymin')
		ymin.text = str(box[1])

		xmax = ET.Element('xmax')
		xmax.text = str(box[2])

		ymax = ET.Element('ymax')
		ymax.text = str(box[3])

		bndbox.append(xmin)
		bndbox.append(ymin)
		bndbox.append(xmax)
		bndbox.append(ymax)
		new_obj.append(bndbox)

		root.append(new_obj)
	indent(root)
	return tree

class Window(QtWidgets.QMainWindow):
	def __init__(self):
		super(Window, self).__init__()
		self.setGeometry(100,50, 1600, 900)
		self.setWindowTitle("GUI")

		self.file_cache = 'cache.txt'
		self.dir_ = ''
		self.list_path_imgs = []
		self.pos_img = -1
		self.objects= []
		self.btn_open = self.button('open', self.func_open, y = 30)
		self.btn_move_no_xml = self.button('Move No Xml', self.func_move_no_xml, x = 500, y = 30)
		self.btn_take_traffic_sign = self.button('take traffic sign', self.func_take_traffic_sign, x = 500, y = 60)
		self.btn_take_traffic_light = self.button('take traffic light', self.func_take_traffic_light, x = 650, y = 60)
		self.txb_dir = self.textBox(x = 100, y=30, w=300)
		self.txb_name_img = self.textBox(x = 200, y=80, w=300)
		self.labels = []
		self.xml_path = ''
		self.fil = ''
		self.init()
		
		self.btn_next = self.button('next', self.func_next, x = 100, y = 80)
		self.btn_previous = self.button('previous', self.func_previous, x = 10, y = 80)
		
		self.lab_main_img = self.label(x = 10, y = 100, w= 1280, h = 960)
		self.lab_sub_imgs = []
		self.txb_sub_imgs = []
		
		for i in range(8):
			self.lab_sub_imgs.append(self.label(x = 1000, y =  i*100+i*30 + 20, w = 100, h = 100))
			self.txb_sub_imgs.append(self.comboBox(self.labels, self.func_combo ,x = 1120, y = i*100+i*30 + 60))
		

		saveAction  = QAction("Save", self)
		saveAction.setShortcut("Ctrl+S")
		saveAction.setStatusTip("Save File")
		saveAction.triggered.connect(self.func_keyboard)

		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu("File")
		fileMenu.addAction(saveAction)
		
		self.statusBar()
		self.show()
	def setDir(self, new_dir):
		self.dir_ = new_dir
		if(self.fil == ''):
			self.fil = Filter(new_dir)
		else:
			self.fil.setDir(new_dir)

	def updateItems(self, name):
		for cb in self.txb_sub_imgs:
			cb.addItem(name)
	def modify_labels_default(self, isRead = False, isWrite = False):
		path = 'default_labels.txt'
		if(isRead):
			if not os.path.exists(path):
				with open(path, 'w') as f:
					pass
			else:
				with open(path, 'r') as f:
					lines = f.readlines()
					for line in lines:
						self.labels.append(line.split('\n')[0])
		if(isWrite):
			with open('default_labels.txt', 'w') as f:
				for lab in self.labels:
					f.write(lab+'\n')
	def take_list_files(self):
		list_files = os.listdir(self.dir_)
		self.list_path_imgs= []
		self.pos_img = -1
		for filename in list_files:
			split = filename.split('.')
			if(len(split) > 1):
				if(split[1] == 'jpg'):
					self.list_path_imgs.append(filename)
	def init(self):
		self.modify_labels_default(isRead = True, isWrite = False)
		if not os.path.exists(self.file_cache):
			with open(self.file_cache, 'w') as f:
				pass
		else:
			with open(self.file_cache, 'r') as f:
				dir_ = f.readline()
				self.setDir(dir_)
				self.txb_dir.setText(self.dir_)
				if(len(self.dir_) > 0):
					self.take_list_files()

	def find_all_objects(self, root):
		self.objects = []
		objs = root.findall('object')
		for obj in objs:
			old_box = []
			old_box.append(int(obj[4][0].text))
			old_box.append(int(obj[4][1].text))
			old_box.append(int(obj[4][2].text))
			old_box.append(int(obj[4][3].text))
			
			name = obj[0].text
			self.objects.append(Box(name = name, bndbox = old_box))
		return self.objects

	def take_sub_imgs(self, name_img, pixmap_org):
		path_xml = os.path.join(self.dir_, name_img.split('.')[0]+'.xml')
		if(os.path.exists(path_xml)):
			self.xml_path = path_xml
			tree = ET.parse(path_xml)
			root = tree.getroot()
			objects = self.find_all_objects(root)
			num_objs = len(objects)
			for i in range(num_objs):
				box = objects[i].getBndbox()
				self.lab_main_img.setPixmap(pixmap_org)
								
				sub_img = pixmap_org.copy(box[0], box[1], box[2]-box[0],box[3]-box[1])
				sub_img = sub_img.scaled(100,100, QtCore.Qt.KeepAspectRatio)
				self.lab_sub_imgs[i].setPixmap(sub_img)
				name = objects[i].getName()

				if not name in self.labels:
					self.labels.append(name)
					self.updateItems(name)
				ind = self.labels.index(name)
				self.txb_sub_imgs[i].setCurrentIndex(ind)

			for i in range(num_objs, len(self.lab_sub_imgs)):
				self.lab_sub_imgs[i].setText('No label')
				self.txb_sub_imgs[i].clearEditText()
		else:
			for i in range(len(self.lab_sub_imgs)):
				self.lab_sub_imgs[i].setText('No label')
				self.txb_sub_imgs[i].clearEditText()
				

	def button(self, hint, function, x = 0, y = 0):
		btn = QtWidgets.QPushButton(hint, self)
		btn.clicked.connect(function)
		btn.resize(btn.minimumSizeHint())
		btn.move(x,y)
		return btn
	def textBox(self, x = 100, y = 0, w=100, h=40, text = ''):
		txb = QLineEdit(self)
		txb.move(x,y)
		txb.resize(w,h)
		txb.setText(text)
		return txb
	def label(self, x = 0, y = 0, w= 1280, h = 960):
		label = QLabel(self)
		label.move(x,y)
		label.resize(w,h)
		return label
	def comboBox(self, items, fuction, x = 0, y = 0, w = 200, h = 40):
		cb = QComboBox(self)
		for it in items:
			cb.addItem(it)
		cb.move(x,y)
		cb.resize(w,h)
		cb.setEditable(True)

		cb.currentIndexChanged.connect(fuction)
		return cb
		
	def func_open(self):
		dir_ = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory')
		self.setDir(dir_)
		if(len(self.dir_) > 0):
			with open(self.file_cache, 'w') as f:
				f.write(self.dir_)
			self.txb_dir.setText(self.dir_)
			self.take_list_files()
			print(self.list_path_imgs)

	def func_next(self):
		if(len(self.list_path_imgs) > 0):
			
			if(self.pos_img < len(self.list_path_imgs) - 1):
				self.pos_img += 1
			self.txb_name_img.setText(self.list_path_imgs[self.pos_img])
			path_img = os.path.join(self.dir_, self.list_path_imgs[self.pos_img])
			pixmap_org = QPixmap(path_img)
			# pixmap = pixmap.copy(0,0,6,6)
			self.take_sub_imgs(self.list_path_imgs[self.pos_img], pixmap_org)

			# self.penRectangle = QPen(QtCore.Qt.red)
			# # self.penRedBorder.setWidth(3)
			# self.painterInstance = QPainter(pixmap_org)
			# self.painterInstance.setPen(self.penRectangle)
			# self.painterInstance.drawRect(50,100,200,400)
			pixmap = pixmap_org.scaled(960,1280, QtCore.Qt.KeepAspectRatio)
			self.lab_main_img.setPixmap(pixmap)
		else:
			print("no img")
	def func_previous(self):
		if(len(self.list_path_imgs) > 0):
			
			if(self.pos_img > 0):
				self.pos_img -= 1
			self.txb_name_img.setText(self.list_path_imgs[self.pos_img])
			path_img = os.path.join(self.dir_, self.list_path_imgs[self.pos_img])
			pixmap_org = QPixmap(path_img)
			# pixmap = pixmap.copy(0,0,6,6)
			self.take_sub_imgs(self.list_path_imgs[self.pos_img], pixmap_org)

			# self.penRectangle = QPen(QtCore.Qt.red)
			# # self.penRedBorder.setWidth(3)
			# self.painterInstance = QPainter(pixmap_org)
			# self.painterInstance.setPen(self.penRectangle)
			# self.painterInstance.drawRect(50,100,200,400)
			pixmap = pixmap_org.scaled(960,1280, QtCore.Qt.KeepAspectRatio)
			self.lab_main_img.setPixmap(pixmap)
		else:
			print("no img")
	def func_combo(self, e):
		pass
	def func_keyboard(self, e):
		num_objs= len(self.objects)
		new_objs = []
		for i in range(num_objs):
			new_label= self.txb_sub_imgs[i].currentText()
			new_label = new_label.strip()
			if(len(new_label) > 0):
				obj = self.objects[i]
				obj.setName(new_label)
				new_objs.append(obj)
				if not new_label in self.labels:
					self.labels.append(new_label)
					self.updateItems(new_label)
		self.modify_labels_default(isRead = False, isWrite = True)
		if(len(self.xml_path) > 0):
			tree = ET.parse(self.xml_path)
			tree = generate_xml(tree, new_objs)
			tree.write(self.xml_path)
			print("Saved {}".format(self.xml_path))
	def func_take_traffic_sign(self, isRename = False):
		isRename = True
		new_name = 'traffic_sign'
		for path_img in self.list_path_imgs:
			path_xml = os.path.join(self.dir_, path_img.split('.')[0]+'.xml')
			new_objs = []
			tree = ET.parse(path_xml)
			root = tree.getroot()
			objects = self.find_all_objects(root)
			num_objs = len(objects)
			if(len(objects) > 0):
				for i in range(num_objs):
					name = objects[i].getName()
					if new_name in name:
						if(isRename):
							objects[i].setName(new_name)
						new_objs.append(objects[i])
				if(len(path_xml) > 0):
					tree = generate_xml(tree, new_objs)
					tree.write(path_xml)
					print("Saved {}".format(path_xml))
				for obj in new_objs:
					print(obj.getName())
			else:
				print("no objects")
	def func_take_traffic_light(self):
		isRename = True
		new_name = 'traffic_light'
		for path_img in self.list_path_imgs:
			path_xml = os.path.join(self.dir_, path_img.split('.')[0]+'.xml')
			new_objs = []
			tree = ET.parse(path_xml)
			root = tree.getroot()
			objects = self.find_all_objects(root)
			num_objs = len(objects)
			if(len(objects) > 0):
				for i in range(num_objs):
					name = objects[i].getName()
					if new_name in name:
						if(isRename):
							objects[i].setName(new_name)
						new_objs.append(objects[i])
				if(len(path_xml) > 0):
					tree = generate_xml(tree, new_objs)
					tree.write(path_xml)
					print("Saved {}".format(path_xml))
				for obj in new_objs:
					print(obj.getName())
			else:
				print("no objects")
	def func_move_no_xml(self):
		self.fil.move_files(0,0,0,1)
		self.list_path_imgs = self.take_list_files()
app = QtWidgets.QApplication(sys.argv)
GUI  = Window()
sys.exit(app.exec_())