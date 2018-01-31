from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from collections import namedtuple, OrderedDict
import os
import re
import numpy as np

def split(df, group):
	data = namedtuple('data', ['filename', 'object'])
	gb = df.groupby(group)
	return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]

import pandas as pd
sign_map = {'traffic_sign': 1, 'pedestrianCrossing': 2}

path_csv_test = './test__labels.csv'
test_labels = []
with open('test__labels.csv', 'r') as f:
	for line in f:
		line = line[:-1]  # strip trailing newline
		test_labels.append(line)

image_files = os.listdir('test')
for image_file in image_files:

	class_list = []
	box_coords_list = []
	for line in test_labels:
		if re.search(image_file, line):
			fields = line.split(',')

			# Get sign name and assign class label
			sign_name = fields[3]
			if sign_name != 'traffic_sign' and sign_name != 'pedestrianCrossing':
				continue  # ignore signs that are neither stop nor pedestrianCrossing signs
			sign_class = sign_map[sign_name]
			class_list.append(sign_class)

			# Resize image, get rescaled box coordinates
			box_coords = np.array([int(x) for x in fields[4:8]])
			print(image_file,sign_class, box_coords)