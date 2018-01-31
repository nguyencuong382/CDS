import os
from PIL import Image
import time
import cv2

def run(dirFIle):
	list_files = os.listdir(dirFIle)
	for file in list_files:
		t = time.time()
		imga = cv2.imread(os.path.join(dirFIle, file), 1)
		print(time.time()-t)
		try:
			t = time.time()
			with Image.open(os.path.join(dirFIle, file)) as img:
				print(time.time() - t)
				print('yest')
		except:
			print('no')

run('/home/nguyencuong/Desktop/test_convert/img/images')