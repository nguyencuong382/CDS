import cv2
import numpy as np
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import math

class GUI:
    def __init__(self):
        self.mouseX = 0
        self.mouseY = 0
        self.name_img = ''
        self.tmp_mouseX = 0
        self.tmp_mouseY = 0
        self.image_org = np.zeros((512,512,3), np.uint8)
        self.image = self.image_org.copy()
        self.boxes = []
        self.size_box = 300
        cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback('image', self.mouse_event)
    def getImgOrgin(self):
        return self.image_org
    def getNameImg(self):
        return self.name_img
    def getXY(self):
        return self.mouseX, self.mouseX
    def getTmpXY(self):
        return self.tmp_mouseX, self.tmp_mouseY
    def getBoxes(self):
        return self.boxes
    def reset(self):
        self.size_box = 300
        self.boxes = []
    def delBox(self):
        num_boxes = len(self.boxes)
        if(num_boxes > 0):
            del self.boxes[num_boxes - 1]
        self.mouse_event(-1,self.tmp_mouseX, self.tmp_mouseY, 0, 'update')
    def getSizeBox(self):
        return self.size_box
    def setSizeBox(self, size_box):
        self.size_box = size_box
        self.mouse_event(0,self.tmp_mouseX, self.tmp_mouseY,0,0)

    def setImg(self, image, name = ''):
        if(len(name) > 0):
            self.name_img = name
        self.image_org = image.copy()
        self.image = image.copy()
        cv2.imshow('image', self.image)
        self.mouse_event(0,self.tmp_mouseX, self.tmp_mouseY,0,0)

    def draw_rect(self, img, x, y, isClick = False):
        haf = int(self.size_box/2)
        x1, y1 = x-haf,y-haf
        x2, y2 = x+haf,y+haf

        h, w = img.shape[0], img.shape[1]
        if(x1 < 0):
            x1 = 0
            x2 = self.size_box

        if(x2 > w):
            x2 = w
            x1 = w - self.size_box

        if(y2 > h):
            y2 = h
            y1 = h - self.size_box

        if(y1 < 0):
            y1 = 0
            y2 = self.size_box
        cv2.rectangle(img, (x1,y1), (x2,y2), (0, 255, 0), 2)
        if(isClick):
            return img, [x1,y1,x2,y2]
        return img
    
    def mouse_event(self,event,x,y,flags,param):

        if event == cv2.EVENT_MOUSEMOVE:
            img = self.image.copy()
            img = self.draw_rect(img, x, y)
            cv2.imshow('image',img)
            self.tmp_mouseX = x
            self.tmp_mouseY = y
           
        if event == cv2.EVENT_LBUTTONDOWN:
            # self.image = self.image_org.copy()
            self.image, box = self.draw_rect(self.image, x, y, isClick = True)
            self.boxes.append(box)
            cv2.imshow('image',self.image)
            self.mouseX = x
            self.mouseY = y
        if(param == 'update'):
            tmp_img = self.image_org.copy()
            for box in self.boxes:
                cv2.rectangle(tmp_img, (box[0],box[1]), (box[2],box[3]), (0,255,0), 2)
            self.image = tmp_img.copy()
            cv2.imshow('image', self.image)

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

def find_name_tail(array_split, mark = '.'):
    num_elements = len(array_split)
    if(num_elements < 2):
        return -1, -1
    name = ''
    tail = ''
    if(num_elements == 2):
        name = array_split[0]
        tail = array_split[1]
    else:
        end = num_elements-1
        for i in range(end):
            if(i == end - 1):
                name += array_split[i]
            else:
                name += array_split[i] + mark
        tail = array_split[num_elements - 1]
    return name, tail

def take_name_files(path):
    list_files = os.listdir(path)
    file_ok = []
    for name_file in list_files:
        split = name_file.split('.')
        name, tail = find_name_tail(array_split = split)
        if(tail == 'jpg'):
            file_ok.append(name)
    return file_ok
def show(img, name_file):
    cv2.namedWindow(name_file, cv2.WINDOW_AUTOSIZE)
    cv2.imshow(name_file, img)
    cv2.waitKey()
    cv2.destroyWindow(name_file)

def check_if_box_in(new_box, sub_old_box):
    if(sub_old_box[0] > new_box[0] and sub_old_box[1] > new_box[1]
        and sub_old_box[2] < new_box[2] and sub_old_box[3] < new_box[3]):
        return True
    return False

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
def generate_xml(tree, new_objects, new_name_file, new_h, new_w):
    root = tree.getroot()
    root.find('size')[0].text = str(new_w)
    root.find('size')[0].text = str(new_h)
    for filename in root.iter('filename'):
        filename.text = new_name_file
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

def calculate_box(img, name_file, boxes, dir_, new_dir = 'cut', start = 1):
    path_xml = os.path.join(dir_, name_file+'.xml')
    path_new = os.path.join(dir_, new_dir)
    if not os.path.exists(path_new):
        os.makedirs(path_new)
    if(os.path.exists(path_xml)):
        tree = ET.parse(path_xml)
        root = tree.getroot()
        old_objects = find_all_objects(root)

        for box in boxes:
            print(box)
            x1 = box[0]
            y1 = box[1]
            x2 = box[2]
            y2 = box[3]
            new_img = img[y1:y2, x1:x2]

            new_objects = []
            for obj in old_objects:
                sub_old_box = obj.getBndbox()
                if(check_if_box_in(box, sub_old_box)):
                    new_sub_box = []
                    new_sub_box.append(sub_old_box[0] - box[0])
                    new_sub_box.append(sub_old_box[1] - box[1])
                    new_sub_box.append(sub_old_box[2] - box[0])
                    new_sub_box.append(sub_old_box[3] - box[1])
                    new_objects.append(Box(name = obj.getName(), bndbox = new_sub_box))
            if(len(new_objects) > 0):
                new_name_file = '{}_{}.jpg' .format(name_file, start)
                tree = generate_xml(tree, new_objects, new_name_file, box[3] - box[1], box[2]-box[0])
                print(tree)
                tree.write(os.path.join(path_new, '{}_{}.xml' .format(name_file, start)))
                cv2.imwrite(os.path.join(path_new, new_name_file), new_img)
                start+=1
    else:
        print('No file xml with {}'.format(name_file+'.jpg'))

def run(dir_):
    gui = GUI()

    list_files = take_name_files(dir_)
    print(list_files)
    current_pos = -1
    num_files_ok = len(list_files)
    while(1):
        k = cv2.waitKey() & 0xff
        tmp_mouseX, tmp_mouseY = gui.getTmpXY()
        mouseX, mouseY = gui.getXY()
        if(k == 27):
            break
        if(k==32):
            boxes = gui.getBoxes()
            if(len(boxes) > 0):
                calculate_box(gui.getImgOrgin(), gui.getNameImg(), boxes, dir_)
            else:
                print('No Box to save')
        # print(k)
        if(k==113): #Q
            if(current_pos > 0):
                current_pos -= 1
            img = cv2.imread(os.path.join(dir_, list_files[current_pos]+'.jpg'))
            gui.reset()
            gui.setImg(img, list_files[current_pos])
            # print(current_pos)

        if(k==101): #E
            if(current_pos < num_files_ok-1):
                current_pos += 1
            img = cv2.imread(os.path.join(dir_, list_files[current_pos]+'.jpg'))
            gui.reset()
            gui.setImg(img, list_files[current_pos])
            # print(current_pos)

        if(k==93): #]
            gui.setSizeBox(gui.getSizeBox()+10)

        if(k==91): #[
            new_size_box = gui.getSizeBox()-10
            if(new_size_box < 10):
                new_size_box = 10
            gui.setSizeBox(new_size_box)

        if(k==122):
            gui.delBox()

    cv2.destroyAllWindows()

def take_box_from_video(dir_, name_video, dir_save = 'external_data',name_file_save='boxes.npy', start = 1000,):
    dir_video = os.path.join(dir_, name_video)
    path_save = os.path.join(dir_, dir_save)
    if not os.path.exists(path_save):
        os.makedirs(path_save)
    video = cv2.VideoCapture(dir_video)
    for i in range(start):
        rat, frame = video.read()
        if not rat:
            return 0
    gui = GUI()
    while(1):
        k = cv2.waitKey() & 0xff
        if(k == 27):
            break
        if(k==32):
            list_box = np.array(gui.getBoxes())
            np.save(os.path.join(path_save, name_file_save), list_box)
            print("saved: ", list_box)


        if(k==101): #E
            rat, frame = video.read()
            if(rat):
                gui.reset()
                gui.setImg(frame, 'frame')
            else:
                break

        if(k==93): #]
            gui.setSizeBox(gui.getSizeBox()+10)

        if(k==91): #[
            new_size_box = gui.getSizeBox()-10
            if(new_size_box < 10):
                new_size_box = 10
            gui.setSizeBox(new_size_box)

        if(k==122):
            gui.delBox()
    video.release()
    cv2.destroyAllWindows()

class BoxVideo:
    def __init__(self, dir_, boxes = []):
        if(len(boxes) == 0):
            self.boxes = np.load(dir_)
        else:
            self.boxes = boxes
        print(self.boxes)
        self.isInitWindows = False
    def take(self, img):
        self.sub_imgs = []
        for box in self.boxes:
            sub_img = img[box[1]:box[3], box[0]:box[2]]
            self.sub_imgs.append(sub_img)
        return self.sub_imgs
    def initWindows(self, num_sub_imgs):
        x = 300
        y=300
        for i in range(num_sub_imgs):
            cv2.namedWindow('sub{}'.format(i), cv2.WINDOW_AUTOSIZE)
            cv2.moveWindow('sub{}'.format(i), x, y)
            x+=300
            y+=300
        self.isInitWindows = True

    def show(self, sub_imgs):
        num_sub_imgs = len(sub_imgs)
        if not self.isInitWindows:
            self.initWindows(num_sub_imgs)

        for i in range(num_sub_imgs):
            cv2.imshow('sub{}'.format(i), self.sub_imgs[i])
    def end(self):
        cv2.destroyAllWindows()

def load_boxes(dir_):
    boxes = np.load(dir_)
    print(boxes)

# run('/home/quynh/Desktop/p')
# take_box_from_video('/home/quynh/Desktop/object-dection-ssd/object_detection/test_video', 'test111.mp4')
# load_boxes('/home/quynh/Desktop/data_not/video/external_data/boxes.npy')

def test_video_with_boxes():
    boxVideo = BoxVideo(dir_ = '/home/quynh/Desktop/object-dection-ssd/object_detection/test_video/external_data/boxes.npy')
    path_video = '/home/quynh/Desktop/object-dection-ssd/object_detection/test_video/test111.mp4'
    video = cv2.VideoCapture(path_video)
    cv2.namedWindow('video', cv2.WINDOW_AUTOSIZE)
    while(1):
        rat, frame = video.read()
        if(rat):
            cv2.imshow('video', frame)
            sub_imgs = boxVideo.take(frame)
            boxVideo.show(sub_imgs)
            k = cv2.waitKey(30) & 0xff
            if(k==32):
                break
        else:
            break
    cv2.destroyAllWindows()
test_video_with_boxes()