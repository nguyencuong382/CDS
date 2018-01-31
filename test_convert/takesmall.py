import cv2
import os
import xml.etree.ElementTree as ET
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

def find_all_objects(root):
	objects = []
	objs = root.findall('object')
	for obj in objs:
		old_box = []
		old_box.append(int(obj[4][0].text))
		old_box.append(int(obj[4][1].text))
		old_box.append(int(obj[4][2].text))
		old_box.append(int(obj[4][3].text))

		name = obj[0].text
		objects.append(Box(name = name, bndbox = old_box))
	return objects
def run(dirFile, isPutAllLabs = False, isSaparate = False):
	list_files = os.listdir(dirFile)
	list_imgs = []

	for file in list_files:
		split = file.split('.')
		if(split[len(split) - 1] == 'jpg'):
			list_imgs.append(file)

	list_objects = []
	for file in list_imgs:
		path_xml = os.path.join(dirFile, file.split('.')[0] + '.xml')
		if os.path.exists(path_xml):
			tree = ET.parse(path_xml)
			root = tree.getroot()
			objects = find_all_objects(root)
			if(len(objects) > 0):
				path_img = os.path.join(dirFile, file)
				list_objects.append([path_img, objects])

	dirFile = dirFile + '/../sub_img'
	path_lab_txt = os.path.join(dirFile, 'labels')
	image_labels_dir = os.path.join(dirFile, 'labels', 'image_labels_dir')
	if not os.path.exists(path_lab_txt):
		os.makedirs(path_lab_txt)
	if not os.path.exists(image_labels_dir):
		os.makedirs(image_labels_dir)

	list_labs = {}
	with open(os.path.join(path_lab_txt, 'labels.txt'), 'w') as f:
		for _ in list_objects:

			path_img = _[0]
			print(path_img)
			objects = _[1]
			img = cv2.imread(path_img, 1)

			for obj in objects:
				lab = obj.getName()
				box = obj.getBndbox()
				ratio = (box[2] - box[0])/(box[3]-box[1])
				if(ratio >= 0.35 and ratio <= 2.85):
					print(ratio)
					sub_img = img[box[1]:box[3], box[0]:box[2]]

					if isSaparate:
						path_lab = os.path.join(dirFile, lab)
						if not os.path.exists(path_lab):
							os.makedirs(path_lab)
					if not lab in list_labs:
						if(len(list_labs) > 0):
							f.write('\n'+lab)
						else:
							f.write(lab)
						list_labs[lab] = 0				

					num = list_labs[lab]
					name_sub_img = '{}{}.jpg' .format(lab, num)
					list_labs[lab] = num+1

					if isSaparate:
						cv2.imwrite(os.path.join(dirFile, lab, name_sub_img) , sub_img)
					if isPutAllLabs:
						path_sub_img = os.path.join(dirFile, 'images')
						if not os.path.exists(path_sub_img):
							os.makedirs(path_sub_img)
						cv2.imwrite(os.path.join(path_sub_img, name_sub_img), sub_img)

					with open(os.path.join(image_labels_dir, name_sub_img+'.txt'), 'w') as f_lab:
						f_lab.write(lab)
				


run('/home/quynh/Desktop/s', isSaparate = True, isPutAllLabs = False)
