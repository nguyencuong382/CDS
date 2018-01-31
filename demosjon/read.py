import json
import cv2
import xml.etree.ElementTree as ET
mau = ET.parse('mau.xml')
import os
from os.path import join, exists
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

def generate_xml(tree, new_objects, name_file, h, w):
	root = tree.getroot()
	root[1].text = name_file
	root[4][0].text = str(w)
	root[4][1].text =str(h)
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
def save(name_file, labels):
	name_file = './' + name_file
	with open(name_file, 'w') as f:
		for lab in labels:
			f.write(lab+'\n')

def load(nam_file):
	if(os.path.exists(nam_file)):
		labs = ''
		with open(nam_file, 'r') as f:
			labs= f.read()
			labs = labs.split('\n')
		return labs
	else:
		return []
def filter_objects_from_json(path_file_json, dest_file_json):
	with open(path_file_json, 'r') as f:
		s = f.read()

	js = json.loads(s)
	items = list(js.items())[0][1]

	# labels = load('labels.txt')
	# labels_not = load('labels_not.txt')
	# tri_labs = load('tri_labs.txt')
	# blue_labs = load('blue_labs.txt')
	# blue_labs = ['i5', 'i10', 'i13', 'i12']

	# labels_not = ['pm55', 'pm10', 'pa14', 'pg', 'il80', 'il60', 'il50', 'il100', 'il70', 'pl5', 'pl10', 'pl0', 'ps', 'ph2.8', 'pa12', 'pa13', 'pr20', 'il110', 'pr30', 'pr50', 'pr70', 'pr100', 'pr10', 'pm13', 'il90', 'p1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'ph2', 'p11', 'pb', 'ph3', 'p27', 'p26', 'p12', 'p25', 'p10', 'p5', 'p3', 'pm30', 'ph5', 'pm20', 'pa10', 'ph4.2', 'ph4.5', 'p22', 'ph3.5', 'pl110', 'p18', 'p16', 'p2', 'p17', 'pw3.2', 'ph2.2', 'p8', 'ph4.8', 'pm2.5', 'pr45', 'pw4', 'p28', 'ph5.3', 'pl35', 'ph2.9', 'ph4.3', 'pm2', 'ph3.2', 'ph2.5', 'p15', 'p20', 'pa8', 'pw4.5', 'ph2.1', 'pm5', 'pl25', 'pm15', 'p4', 'ph1.5', 'pw3.5', 'pm50', 'pw2.5', 'p13', 'pm8', 'pl3', 'ph2.4', 'pw4.2', 'pw2', 'ph5.5', 'ph3.8']
	# tri_labs = ['w32', 'ip', 'wo', 'w55', 'w57', 'w13', 'w59', 'w58', 'w63', 'w30', 'w22', 'w47', 'w35', 'w45', 'w8', 
	# 'w3', 'w21', 'w42', 'w41', 'w18', 'w20', 'w16', 'w15', 'w66', 'w12', 'w34', 'w5', 'w38', 'w10', 'w35', 'w46', 'w37',
	# 'w28', 'w24', 'w43', 'w56', 'w2']

	list_objects_json = {}
	for i in items.items():
		objs = i[1]['objects']
		if(len(objs) > 0):
			path = i[1]['path']
			new_objs = {}

			for obj in objs:
				lab = obj['category']
				box = obj['bbox']
				xmin = int(box['xmin'])
				ymin = int(box['ymin'])
				ymax = int(box['ymax'])
				xmax = int(box['xmax'])
				area = (xmax - xmin)*(ymax - ymin)
				if(area >= 250):
					new_objs[lab] = [xmin, ymin, xmax, ymax]

			if(len(new_objs) > 0):
				list_objects_json[path] = new_objs

	with open(dest_file_json, 'w') as f:
		json.dump(list_objects_json, f)

def check_label(label):
	labels_not = []
def see_label(path, label):
	print(label)
	img = cv2.imread(join(dirFolder, file_name), cv2.IMREAD_COLOR)
	cv2.rectangle(img, (box[0], box[1]) , (box[2], box[3]), (0,0,255), 3)
	img_ = cv2.resize(img, (960, 640))
	cv2.imshow('img', img_)
	cv2.waitKey()

def get_file_names(file_name):
	split = file_name.split('/')
	name_img = split[1]
	return name_img, name_img.split('.')[0]  + '.xml'

def filter_objects():
	dirFolder = '/media/quynh/Tài liệu/chinese data/data'
	file_json = 'annotations.json'
	dest_file_json = join(dirFolder, "ano.json")
	dest_folder = join(dirFolder, 'data_20')
	num_imgs = 0
	if not exists(dest_file_json):
		print('Filtering......')
		filter_objects_from_json(join(dirFolder, file_json), join(dirFolder, dest_file_json))
	if not exists(dest_folder):
		os.makedirs(dest_folder)

	print('loading........')
	with open(dest_file_json , 'r') as f:
		data = json.load(f)
	labels_not = load('tri_labs.txt')
	label_ok = load('labels_ok.txt')
	print(label_ok)
	# cv2.namedWindow('img', cv2.WINDOW_AUTOSIZE)
	for file_name, objs in data.items():
		new_objs = []
		for label, box in objs.items():
			if label in label_ok:
				new_objs.append(Box(box, label))
		if(len(new_objs) > 0):
			num_imgs += 1
			name_file_img, name_file_xml = get_file_names(file_name)
			
			img = cv2.imread(join(dirFolder, file_name), cv2.IMREAD_COLOR)
			cv2.imwrite(join(dest_folder, name_file_img), img)
			h, w = img.shape[0], img.shape[1]

			new_xml = generate_xml(mau, new_objs, name_file_img, h, w)
			new_xml.write(os.path.join(dest_folder,name_file_xml))
			print("done", num_imgs, file_name)

	cv2.destroyAllWindows()
def gen_code():
	labels = load('labels.txt')
	labels_not = []
	i = 0
	with open('config.txt', 'w') as f:
		num_items = len(labels)
		for x in range(num_items):
			if not labels[x] in labels_not:
				f.write('item {\n')
				f.write('\tid: {}\n' .format(i+1))
				f.write('\tname: \'{}\'\n' .format(labels[x]))
				f.write('}\n')
				i+=1
	i = 0
	with open('code.txt', 'w') as f:
		num_items = len(labels)
		for x in range(num_items):
			if not labels[x] in labels_not:
				f.write('if row_label == \'{}\':\n' .format(labels[x]))
				f.write('\treturn {}\n' .format(i+1))
				i+=1

def gen_code_yolo():
	labels = load('labels_ok.txt')
	classes_name =  []
	classes_num ={}
	for i, lab in enumerate(labels):
		classes_name.append(lab)
		classes_num[lab] = i
	print(classes_name)
	print(classes_num)
if __name__ == '__main__':
	# filter_objects()
	gen_code()
	gen_code_yolo()	