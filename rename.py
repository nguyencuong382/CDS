import os
from pathlib import Path
import collections
import sys
import shutil
import xml.etree.ElementTree as ET

class Filter:
	def __init__(self, dir_, isLog = True):
		if(len(dir_) == 0):
			raise RuntimeError("No path of folder input")

		self.list_files = ''
		self.list_ok = ['jpg']
		self.list_convert = ['png','jpeg', 'JPG']
		self.list_except = ['py', 'xml']
		self.list_folder_except = ['ok', 'convert', 'unknown', 'no_xml']
		self.label = ['traffic_sign','traffic_light']
		self._file_ok = []
		self._files_convert = []
		self._files_except = []
		self._folders = []
		self._files_no_xml = []

		self._isLog = isLog
		self._totalFiles  = len(self.list_files)
		self._num_ok = 0
		self._dir = dir_

		self.filter(self._dir)
		
	def setDir(self, new_dir):
		self._dir = new_dir
		self.filter(self._dir)
	def getFilesOk(self):
		return self._file_ok
	@property
	def getFilesConvert(self):
		return self._files_convert
	@property
	def getFilesExcept(self):
		return self._files_except
	@property
	def getFolders(self):
		return self._folders
	@property
	def getFilesNoXml(self):
		return self._files_no_xml
	@property
	def getNumOk(self):
		return self._num_ok
	def check_name(self, name):
		for digit in name:
			if(digit < '0' or digit  > '9'):
				return False
		return True
	def find_name_tail(self, array_split, mark = '.'):
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

	def check_xml_exits(self, name, name_element = 'object'):
		name_file_xml = name+'.xml'
		path_xml = os.path.join(self._dir, name_file_xml)
		if(os.path.exists(path_xml)):
			tree = ET.parse(path_xml)
			root = tree.getroot()
			num_objs = root.findall(name_element)
			if(len(num_objs) > 0):
				return 1
		return 0

	def filter(self, dir_):
		self.list_files = os.listdir(dir_)
		files_number = {}
		files_alph = []
		files_convert = []
		files_except = []
		folders = []

		for name_file in self.list_files:
			if(os.path.isdir(os.path.join(self._dir,name_file))):
				if not name_file in self.list_folder_except:
					folders.append(name_file)
			else:
				split = name_file.split('.')
				if(len(split) > 1):
					name, tail = self.find_name_tail(split)

					if(tail in self.list_ok):
						if(self.check_name(name)):
							files_number[name_file] = int(name)
						else:
							files_alph.append(name_file)
						if not self.check_xml_exits(name):
							self._files_no_xml.append(name+'.'+tail)
					else:
						if(tail in self.list_convert):
							files_convert.append(name_file)
						else:
							if( (tail in self.list_except) == False):
								files_except.append(name_file)
				else:
					files_except.append(name_file)

		files_number = sorted(files_number, key=lambda x:files_number[x])

		files_alph.sort()

		for name_file in files_alph:
			files_number.append(name_file)

		self._file_ok = files_number
		self._files_convert = files_convert
		self._files_except = files_except
		self._folders = folders
		self._num_ok = len(self._file_ok)
		if(self._isLog):
			self.show()

	def find_name(self, i, list_new_names, match_names, list_check):

		new_name = list_new_names[i]
		if(new_name in self._file_ok):
			index = self._file_ok.index(new_name)
			match_names,  list_check= self.find_name(index, list_new_names, 
				match_names, list_check)

		match_names.append((new_name, self._file_ok[i]))
		list_check[i] = 0
		return match_names, list_check

	def take_oder_rename(self, pre, id_):
		list_new_names = []
		for i in range(id_, id_+self._num_ok):
			new_name = pre +'{}' .format(i)+ '.jpg'
			list_new_names.append(new_name)

		list_check = [1 for i in range(self._num_ok)]
		match_names = []
		# print(list_new_names)
		# print(self._file_ok)
		for i in range(len(self._file_ok)):
			if(list_check[i]):
				if(list_new_names[i] == self._file_ok[i]):
					match_names.append((list_new_names[i], self._file_ok[i]))
					print('yes')
				else:
					match_names, list_check= self.find_name(i, list_new_names, match_names, list_check)
		self._file_ok = list_new_names
		return match_names

	def rename(self, pre, id_):

		match_names = self.take_oder_rename(pre, id_)
		current_path = self._dir
		for couple in match_names:
			new_name = couple[0]
			old_name = couple[1]
			os.rename(os.path.join(current_path,old_name), os.path.join(current_path,new_name))
			sys.stdout.write("#")
			sys.stdout.flush()
		print()
		print("Renamed {} files" .format(len(match_names)))
		self.check_after_change()
	def rename_with_xml(self, pre, id_):
		match_names = self.take_oder_rename(pre, id_)

		current_path = self._dir
		num_xml = 0
		for couple in match_names:
			new_name = couple[0]
			old_name = couple[1]

			os.rename(os.path.join(current_path,old_name), os.path.join(current_path,new_name))
			old_name_xml = old_name.split('.')[0]+'.xml'

			if(os.path.exists(os.path.join(current_path, old_name_xml))):
				num_xml += 1
				new_name_xml = new_name.split('.')[0]+'.xml'

				tree = ET.parse(os.path.join(current_path,old_name_xml))
				root = tree.getroot()
				for filename in root.iter('filename'):
					filename.text = new_name
				os.remove(os.path.join(current_path,old_name_xml))

				tree.write(os.path.join(current_path,new_name_xml))
				
		print("Renamed {} image files" .format(len(match_names)))
		print("Renamed {} xml files" .format(num_xml))

	def rename_normal(self, pre, id_):

		current_path = self._dir
		for filename in self._files_convert:
			new_name = '{}{}.jpg' .format(pre, id_)
			old_name = filename
			id_+=1
			os.rename(os.path.join(current_path,old_name), os.path.join(current_path,new_name))

	def move(self, files, dest_folder):
		current_path = self._dir
		path = current_path + '/'+ dest_folder
		if not os.path.exists(path) :
			os.makedirs(path)
		num_file_xml = 0
		for name_file in files:
			src = current_path + '/' + name_file
			dest = path + '/' + name_file
			shutil.move(os.path.join(self._dir,src), os.path.join(self._dir,dest))


			name_file_xml = name_file.split('.')[0]+'.xml'
			src_xml = os.path.join(current_path, name_file_xml)
			if(os.path.exists(src_xml)):
				num_file_xml += 1
				dest_xml = os.path.join(path, name_file_xml)
				shutil.move(src_xml, dest_xml)
			
		print('Moved {} image files to ./{}' .format(len(files), dest_folder))
		print('Moved {} xml files to ./{}' . format(num_file_xml, dest_folder))

	def move_files(self, isMoveOk = False, isMoveConvert = False, isMoveUnknown =False, isMoveNoXml = False):
		if(isMoveOk):
			self.move(self._file_ok, self.list_folder_except[0])
		if(isMoveConvert):
			self.move(self._files_convert, self.list_folder_except[1])
		if(isMoveUnknown):
			self.move(self._files_except, self.list_folder_except[2])
		if(isMoveNoXml):
			self.move(self._files_no_xml, self.list_folder_except[3])
	def move_files_no_xml(self):
		pass
	def move_files_after_rename_with_xml(self, dest_folder = 'final'):
		path_des = os.path.join(self._dir, dest_folder)
		if not os.path.exists(path_des) :
			os.makedirs(path_des)
		for filename in self._file_ok:
			name, tail = filename.split('.')
			name_img = name+'_result'+'.jpg'
			path_img = os.path.join(self._dir, name_img)
			dest = os.path.join(self._dir, dest_folder, name+'.jpg')
			shutil.move(path_img, os.path.join(self._dir,dest))

			name_xml = name+'.xml'
			path_xml = os.path.join(self._dir, name_xml)
			tree = ET.parse(path_xml)
			root = tree.getroot()
			for filename_ in root.iter('filename'):
				filename_.text = name+'.jpg'
			shutil.move(path_xml, os.path.join(self._dir,dest_folder,name_xml))
	def rename_xml(self):
		for filename in self._file_ok:
			name, tail = filename.split('.')
			path_xml = os.path.join(self._dir, name+'.xml')
			tree = ET.parse(path_xml)
			root = tree.getroot()

			for filename_ in root.iter('filename'):
				filename_.text = name+'.jpg'
			tree.write(path_xml)

	def check_label_xml(self):
		list_blue = ['i5', 'i10', 'i13', 'i12', 'i1', 'i2', 'il30', 'ir30']
		list_ok = ['st', 'pne', 'blue']
		list_labs = []

		for filename in self._file_ok:
			name_file_xml = filename.split('.')[0]+'.xml'
			tree = ET.parse(os.path.join(self._dir,name_file_xml))
			root = tree.getroot()

			for obj in root.iter('object'):
				lab = obj[0].text
				# if obj[0].text != 'traffic_sign':
					# list_labs.append(obj[0].text)
					# print(obj[0].text)
					# print(filename)
					# obj[0].text = 'traffic_sign'
					# tree.write(os.path.join(self._dir,name_file_xml))
					# print(obj[0].text)
				if not lab in list_labs:
					print(lab)
					list_labs.append(lab)
					# print(filename)

	def check_after_change(self):
		
		self.filter(self._dir)

	def show(self):
		print('Files Ok; ', len(self._file_ok))
		print('Files need to be converted: ', len(self._files_convert))
		print('Files exception: ', len(self._files_except))
		print('Foldes exception: ', len(self._folders))
		# print('-----------Total-------------: ', self._totalFiles)
if __name__ == '__main__':
	
	run = Filter(dir_ = '/home/quynh/Desktop/sub_img/eo')
	

	run.rename('eoeo', 1)
	# run.move_files(0,0,0,1)
	# run.rename_with_xml('clone', 1)
	# run.move_files(1,1,1)
	# run.check_label_xml()
	# run.move_files_after_rename_with_xml()
	# run.check_label_xml()
