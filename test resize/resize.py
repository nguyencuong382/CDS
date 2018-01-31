import os
import cv2
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

def generate_xml(tree, new_objects, h, w):
	root = tree.getroot()	
	objs = root.findall('object')
	root[4][0].text = str(w)
	root[4][1].text = str(h)
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
def find_max_obj(objects):
	max_area = 0
	index = 0
	for i in range(len(objects)):
		obj = objects[i]
		box = obj.getBndbox()
		area = (box[2] - box[0])*(box[3] - box[1])
		if(area > max_area):
			max_area = area
			index = i
	return objects[index]
def find_new_area(box, h, w, w_d, h_d):

	center_x = int((box[0]+box[2])/2)
	center_y = int((box[1]+box[3])/2)

	new_xmin =0
	new_ymin =0
	new_xmax =0
	new_ymax =0
	
	gap_x_left = center_x
	gap_x_right = w - center_x
	hatf_w_d = int(w_d/2)
	if(gap_x_left >= hatf_w_d and gap_x_right >= hatf_w_d):
		new_xmin = center_x-hatf_w_d
		new_xmax = center_x+hatf_w_d
	if(gap_x_left < hatf_w_d):
		new_xmin = 0
		new_xmax = center_x + w_d - gap_x_left
	if(gap_x_right < hatf_w_d):
		new_xmin = center_x - (w_d - gap_x_right)
		new_xmax = w

	gap_y_top = center_y
	gap_y_low = h - center_y
	hatf_h_d = int(h_d/2)
	if(gap_y_top >= hatf_h_d and gap_y_low >= hatf_h_d):
		new_ymin = center_y - hatf_h_d
		new_ymax = center_y + hatf_h_d
	if(gap_y_top < hatf_h_d):
		new_ymin = 0
		new_ymax = center_y + h_d - gap_y_top
	if(gap_y_low < hatf_h_d):
		new_ymin = center_y - (h_d - gap_y_low)
		new_ymax = h

	return [new_xmin, new_ymin, new_xmax, new_ymax]

def check_if_box_in(new_box, sub_old_box):
    if(sub_old_box[0] > new_box[0] and sub_old_box[1] > new_box[1]
        and sub_old_box[2] < new_box[2] and sub_old_box[3] < new_box[3]):
        return True
    return False
def run(dirFile):
	dest_folder = os.path.join(dirFile, 'resized')
	if not os.path.exists(dest_folder) :
		os.makedirs(dest_folder)

	w_d = 1000
	h_d = 1000
	list_file = os.listdir(dirFile)
	list_imgs =[]
	for file in list_file:
		split = file.split('.')
		if(split[len(split)-1]=='jpg'):
			list_imgs.append(file)
	num_imgs = len(list_imgs)
	i = 0
	for file in list_imgs:
		name_xml = file.split('.')[0]+'.xml'
		path_xml = os.path.join(dirFile, name_xml)
		if(os.path.exists(path_xml)):
			tree = ET.parse(path_xml)
			root = tree.getroot()
			objects = find_all_objects(root)
			if(len(objects) > 0):

				max_obj = find_max_obj(objects)
				# box =max_obj.getBndbox()

				img = cv2.imread(os.path.join(dirFile, file), cv2.IMREAD_COLOR)
				h, w = img.shape[0], img.shape[1]
				min_ = min(h,w)
				if(w_d > min_):
					w_d = min_
					h_d = min_

				# img = cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0,255,255), 3)
				# img = cv2.resize(img, (1000,1000))
				new_are = find_new_area(max_obj.getBndbox(), h, w, w_d, h_d)

				# xmin = new_box[0]
				# ymin = new_box[1]
				# xmax = new_box[2]
				# ymax = new_box[3]
				# new_img = cv2.rectangle(new_img,(xmin,ymin),(xmax,ymax),(0,255,0),3)
				# new_img = cv2.resize(new_img, (int(new_img.shape[1]/2), int(new_img.shape[0]/2)))
				x1 = new_are[0]
				y1 = new_are[1]
				x2 = new_are[2]
				y2 = new_are[3]
				new_img = img[y1:y2, x1:x2]

				new_objs = []

				for obj in objects:
					box = obj.getBndbox()
					if check_if_box_in(new_are, box):
						n_b = [box[0] - new_are[0], box[1] - new_are[1], box[2] - new_are[0], box[3] - new_are[1]]
						obj.setBndbox(n_b)
						new_objs.append(obj)

				
				new_tree = generate_xml(tree, new_objs, new_img.shape[0], new_img.shape[1])

				cv2.imwrite(os.path.join(dest_folder, file), new_img)
				new_tree.write(os.path.join(dest_folder, name_xml))

				i += 1
				print('done {}/{}: {}--->{}:{}' .format(i,num_imgs,file,w_d,h_d))
				# cv2.namedWindow('window', cv2.WINDOW_AUTOSIZE)
				# cv2.imshow('window', new_img)
				# cv2.waitKey()
				# cv2.destroyAllWindows()
	

run('/media/quynh/Tài liệu/chinese data/data/data_20')