import cv2
import os


def cut(img, x1=0, y1=0, x2=0, y2=0):
	y1 += 350
	x2, y2 = img.shape[0] - 250 , img.shape[1]
	crop_img = img[x1:x2, y1:y2]
	return crop_img
def resize(image):
	h, w = image.shape[0], image.shape[1]
	image = cv2.resize(image, (int(w/2.5),int(h/2)))
	return image
def run(path='./', dest_path = './ok_frame', dest_exp = 'exeption',start_frame_ok = 38, 
	start_frame_exp = 7, start_frame = 1):
	if not os.path.exists(dest_path):
		os.makedirs(dest_path)

	if not os.path.exists(os.path.join(dest_path, dest_exp)):
		os.makedirs(os.path.join(dest_path, dest_exp))
	video = cv2.VideoCapture(path)

	buffer_frame = []
	num_frame_max = 200
	current_max_frame = 0
	current_pos_frame = 0
	num_frame  = 0

	num_frame_saved_ok = 0
	num_frame_saved_exp = 0
	MODE = 'PAUSE'

	while(num_frame < start_frame):
		rat, frame = video.read()
		frame = resize(frame)
		num_frame += 1

	rat, frame = video.read()
	frame = resize(frame)
	if(rat):
		buffer_frame.append(frame)
		current_max_frame += 1
	cv2.imshow('window', buffer_frame[current_pos_frame]) 
	while(1):
		if(MODE == 'PLAY'):
			rat, frame = video.read()
			frame = resize(frame)
			if(rat):
				if(current_max_frame == num_frame_max):
					del buffer_frame[0]
				else:
					current_max_frame += 1
					current_pos_frame += 1
				frame = cut(frame)
				buffer_frame.append(frame)
				cv2.imshow('window', buffer_frame[current_pos_frame])
				
			else:
				break
		else:
			pass
		
		k = 0
		if(MODE == 'PLAY'):
			k = cv2.waitKey(30) & 0xff
		else:
			k = cv2.waitKey() & 0xff
		
		if(k == 27):
			break
		if(k == 121):
			MODE = 'PAUSE'
			
			cv2.imwrite('{}/{}.jpg'.format(dest_path, num_frame_saved_ok+start_frame_ok), buffer_frame[current_pos_frame])
			print("Saved {}.jpg --> {}" .format(num_frame_saved_ok+start_frame_ok, dest_path))
			num_frame_saved_ok+=1

			rat, frame = video.read()
			frame = resize(frame)
			if(rat):
				if(len(buffer_frame) == num_frame_max):
					del buffer_frame[0]
				else:
					current_max_frame += 1
					current_pos_frame += 1
				frame = cut(frame)
				buffer_frame.append(frame)
			else:
				break
			cv2.imshow('window', buffer_frame[current_pos_frame])
		if(k == 101): #E
			MODE = 'PAUSE'
			cv2.imwrite('{}/{}/{}.jpg'.format(dest_path, dest_exp, num_frame_saved_exp+start_frame_exp), buffer_frame[current_pos_frame])
			print("Saved {}.jpg --> {}" .format(num_frame_saved_exp+start_frame_exp, os.path.join(dest_path,dest_exp)))
			num_frame_saved_exp+=1

			rat, frame = video.read()
			frame = resize(frame)
			if(rat):
				if(current_max_frame == num_frame_max):
					del buffer_frame[0]
				else:
					current_max_frame += 1
					current_pos_frame += 1
				frame = cut(frame)
				buffer_frame.append(frame)
			else:
				break
			cv2.imshow('window', buffer_frame[current_pos_frame])


		if(k == 81):
			current_pos_frame -= 1
			if(current_pos_frame <0):
				current_pos_frame = 0
			cv2.imshow('window', buffer_frame[current_pos_frame])
			MODE = 'PAUSE'
		if(k == 83):
			rat, frame = video.read()
			frame = resize(frame)
			if(rat):
				if(current_pos_frame == len(buffer_frame) - 1):
					for i in range(20):
						rat, frame = video.read()
						frame = resize(frame)
						if not rat:
							return 0
					if(len(buffer_frame) == num_frame_max):
						del buffer_frame[0]
					frame = cut(frame)
					buffer_frame.append(frame)
				else:
					current_pos_frame += 1
			else:
				break
				
			cv2.imshow('window', buffer_frame[current_pos_frame-1])
			MODE = 'PAUSE'

		if(k == 32):
			if(MODE == 'PLAY'):
				MODE = 'PAUSE'
			else:
				MODE = 'PLAY'

	video.release()
	cv2.destroyAllWindows()
	print(start_frame_ok+ num_frame_saved_ok, start_frame_exp + num_frame_saved_exp)

run('/home/quynh/Downloads/MVI_1063.avi', start_frame_ok=0, start_frame_exp = 0, start_frame = 1)

# cv2.imwrite('../data/{}.jpg'.format(n_imgs), red)
