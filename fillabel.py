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
def run(dirFile):
	list_files = os.listdir(dirFile)
	list_xml = []
	
	for file in list_files:
		split = file.split('.')
		if(split[len(split)-1] == 'xml'):
			list_xml.append(file)
	for file in list_xml:
		tree = ET.parse(os.path.join(dirFile, file))
		root = tree.getroot()
		objects = find_all_objects(root)
		new_objs = []
		for obj in objects:
			if(obj.getName() != 'traffic_light'):
				new_objs.append(obj)
		tree = generate_xml(tree, new_objs)
		tree.write(os.path.join(dirFile, file))
		print('done: ', file)


run('/home/quynh/Desktop/P')