import os
import numpy as np
import cv2

black = np.zeros((850,1800,3), np.uint8)

frame = ''
rec= []
crop= False
img =''
a=0
b=0
pos=0
max_a=0
temp_rows=0
def click_crop(event, x, y, flags, param):
	global rec,a,b,temp_rows

	if event == cv2.EVENT_LBUTTONDOWN:
		rec= [(x,y)]	
	elif event == cv2.EVENT_LBUTTONUP:
		rec.append((x,y))
		cv2.rectangle(frame, rec[0], rec[1], (255,0,255), 1)
		cv2.imshow("window", frame)
		clone= frame.copy()
		img_cropped = clone[rec[0][1]:rec[1][1], rec[0][0]:rec[1][0]]
		rows,cols,_ = img_cropped.shape
		black[a:a+rows, b:b+cols ] = img_cropped

		if param==0:
			b=cols
		else:
			b=cols+param

		max_a= max(temp_rows, rows)
		
		temp_rows= rows
		if b>= 1500:
			a+=max_a
			b=0
		cv2.imshow('res',black)
		cv2.imwrite("image.jpg", black)

def mouse(img, pos):
	clone= img.copy()
	pos= b
	cv2.setMouseCallback("window", click_crop, pos)

def find_video(path, pos):
	video =  cv2.VideoCapture(path)
	cv2.namedWindow('window', cv2.WINDOW_AUTOSIZE)
	
	MODE = 'PAUSE'

	global frame
	rat, frame = video.read()
	if not rat:
		return
	while(1):
		if(MODE == 'PLAY'):
			rat, frame = video.read()
			if rat:
				# process(1)
				cv2.imshow("window", frame)
			else:
				break
		
		k = 0
		if(MODE == 'PLAY'):
			k = cv2.waitKey(30) & 0xff
		else:
			k = cv2.waitKey() & 0xff
		
		if(k == 27):
			break
		if(k == 32):
			if(MODE == 'PLAY'):
				MODE = 'PAUSE'
				mouse(frame, pos)
			else:
				MODE = 'PLAY'

if __name__ == '__main__':
	
	find_video('MVI_1061.avi', pos)
 
	
