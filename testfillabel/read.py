import cv2
import os

def run(dirFile):
	list_file = os.listdir(dirFile)
	list_imgs=[]
	for file in list_file:
		split = file.split('.')
		if(split[len(split) - 1] == 'jpg'):
			list_imgs.append(file)
	for file in list_imgs:
		print(file)
		cv2.namedWindow('window', 1)
		img = cv2.imread(os.path.join(dirFile, file), 1)
		img = ~img
		img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		cv2.imwrite(os.path.join(dirFile, file), img)
		print('done: ', file)
		# cv2.imshow('window', img)
		# k  = cv2.waitKey() & 0xff
		# if(k == 27):
		# 	break
	cv2.destroyAllWindows()
run('/home/quynh/Desktop/object-dection-ssd/object_detection/images/test')