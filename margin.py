import os
import numpy as np
import cv2
kernel = np.ones((3,3), np.uint8)

high =  (255,255,255)

def show(img):
  window = 'window'
  cv2.namedWindow(window, cv2.WINDOW_AUTOSIZE)
  cv2.imshow(window, img)
  cv2.waitKey()
  cv2.destroyAllWindows()

def region_of_interest(img, vertices):
	mask = np.zeros_like(img)
	if len(img.shape) > 2:
		channel_count = img.shape[2]
		ignore_mask_color = (255,) * channel_count
	else:
		ignore_mask_color = 255

	cv2.fillPoly(mask, vertices, ignore_mask_color)
	masked_image = cv2.bitwise_and(img, mask)
	return masked_image

def find_traffic(img, low1, high):
	width, height, _ = img.shape

	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

	# hsv = cv2.GaussianBlur(hsv, (5, 5), 0, 0)
	mask1 = cv2.inRange(hsv, low1, high)
	mask = mask1
	# mask = cv2.medianBlur(mask,5)

	mask = cv2.GaussianBlur(mask, (3, 3), 0, 0)
	mask = cv2.dilate(mask, kernel, iterations=1)
	# cv2.imshow("ssdfadf", mask)
	im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	if( len(contours)>0):
		cv2.drawContours(mask, contours, -1, (255,255,255), thickness=cv2.FILLED)
	# cv2.imshow("asdf", mask)
		print (low1)
	return  mask

def contour(mask, img):
	im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	if (len(contours) > 0):
		areaArray = []
		for c in contours:
			epsilon = 0.06 * cv2.arcLength(c, True)
			approx = cv2.approxPolyDP(c, epsilon, True)
			areaArray.append(approx)
			x, y, w, h = cv2.boundingRect(approx)
			cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), 2)
	return img

def precesss(img, low, high):
	mask= find_traffic(img, low, high)
	cv2.imshow('mask', mask)
	img2 = img.copy()
	img3= contour(mask, img2)
	cv2.imshow('window', img3)



def get_track():
	x = cv2.getTrackbarPos('H_low', 'window')
	y = cv2.getTrackbarPos('S_low', 'window')
	z = cv2.getTrackbarPos('V_low', 'window')

	return (x, y, z)

frame = ''

def process(x):
	global frame
	low= get_track()
	precesss(frame,low, high)

def create_track():
	# low = (101,14,96)
	# low = (105, 83, 96)
	# low = (101, 67, 82)
	# low = (83, 107, 96)
	low = (107, 87, 83)
	cv2.createTrackbar('H_low', 'window',low[0], 255, process)
	cv2.createTrackbar('S_low', 'window', low[1], 255, process)
	cv2.createTrackbar('V_low', 'window', low[2], 255, process)

def find_video(path):
	video =  cv2.VideoCapture(path)
	cv2.namedWindow('window', cv2.WINDOW_AUTOSIZE)
	create_track()
	
	MODE = 'PAUSE'

	global frame
	rat, frame = video.read()
	if not rat:
		return
	while(1):
		if(MODE == 'PLAY'):
			rat, frame = video.read()
			if rat:
				process(1)
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
			else:
				MODE = 'PLAY'

def test_imgs():
	global frame
	frame = cv2.imread("Picture1.jpg", 1)
	cv2.namedWindow('window', cv2.WINDOW_AUTOSIZE)
	create_track()
	process(1)
	cv2.waitKey()

if __name__ == '__main__':
	# find_video('test_video/test111.mp4')
	# find_video('test_video/MVI_1049.avi')	
	# find_video('test_video/MVI_1061.avi')
	# find_video('test_video/MVI_1062.avi')
	# find_video('test_video/MVI_1063.avi')
	find_video('test_video/MVI_1054.avi')
	# test_imgs() 
	
