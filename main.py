# -*- coding: utf-8 -*-

from utils import check_folder, get_json_from_api, get_plate_region, get_plates, read_data
import os
import scipy.misc
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt
import numpy as np
import ast
import moviepy.editor as mpe
import glob
# Global variables
files_exist = False

# Check if file is empy and move files to workdir

path_to_images = 'casosReportados/'
path_to_cut_images = 'placasAreconocer/'
name_to_workdir = 'WORKDIR'


def create_video_from_images(path_to_convert_tovideo):
	print(path_to_convert_tovideo)
	img_glob = path_to_convert_tovideo + '*.jpg'
	# Get images that were dumped during training
	filenames = []
	for fname in sorted(glob.glob(img_glob)):
		files.append([fname,img,code,date])
	filenames = sorted(filenames)
	print(len(filenames))
	assert filenames >=1
	date = filenames[-1].split("/")[1][0:18]

	assert len(filenames) >= 1

	fps  = 30

	# Create video file from PNGs
	print("Producing video file...")
	filename  = os.path.join(path_to_convert_tovideo, '{}.mp4'.format(date))
	clip      = mpe.ImageSequenceClip(filenames, fps=fps)
	clip.write_videofile(filename)
	print("Done! video created")


def check_files_existence():
	global files_exist
	files_exist = check_folder(path_to_images,'jpg')
	return files_exist

def move_files_to_work_dir(files_exist):
	
	if files_exist :
		try:
			os.mkdir(path_to_images)
		except Exception as e:
			print('folder already exist')

		files = read_data(path_to_images + '*.jpg')
		print('len files', len(files))
		files_cut = read_data(path_to_cut_images + '*.png')
		print('len files', len(files_cut))
		for file  in files:
			namen = file[0]	#path to the image
			img = file[1]	# image as array
			code = file[3] # NAME TO THE FOLDER NAME
			date = file[2]	# NAME TO FILE NAME.jpg
					
			try:
				os.mkdir(name_to_workdir+'/{}'.format(code))
			except Exception as e:
				print('folders {} exist already'.format(name_to_workdir+'/{}'.format(code)))
			try:
				os.mkdir(name_to_workdir+'/{}/{}'.format(code,'video'))
			except Exception as e:
				print('folder {} already exist'.format(name_to_workdir+'/{}/{}'.format(code,'video')))



			scipy.misc.imsave(name_to_workdir+'/{}/video/{}.jpg'.format(code,date), img)

			# CREATE VIDEO
			#create_video_from_images(name_to_workdir+'/{}/video/'.format(code))
#

			print('Done imgs and movie')
		for cutted in files_cut:

			cut_namen = cutted[0]
			cut_img  = cutted[1]
			cut_code = cutted[3]	# NAME TO THE FOLDER NAME
			cut_date = cutted[2]	# NAME TO FILE NAME.jpg

			scipy.misc.imsave(name_to_workdir+'/{}/{}.jpg'.format(cut_code, cut_date), cut_img)

			get_information_of_images(files_exist, cut_namen, cut_code, cut_date)

			print('Done cut_img')
	
	else:
		print('There is not files in dir... /{}'.format(path_to_images))
		moved = False
		return moved

	#files_exist, images = check_folder(path_to_images)


### Work on workdir and use the API

# Check workdir files

def get_information_of_images(file_exist, image, idd, date):
	# Check if there is images in WORKDIR
	# if there's image ...
	there_is_img = files_exist

	if there_is_img :

		# idd and date from taked image
		
		information_of_the_image_as_json_file = get_json_from_api(image)

		information_of_the_image_as_json_file = information_of_the_image_as_json_file.replace('false','False')

		print(image +' , information done!')
		information_of_the_image_as_json_file = ast.literal_eval(information_of_the_image_as_json_file)

		# Transform result json to pandas df from the api , just the key == 'region' , the rest
		# does not bother us.
		result_pandas_df = json_normalize(information_of_the_image_as_json_file, 'results')
		# Possible plates from the above result in the format i.e :
		#								{'confidence': 94.38839, 'matches_template': 0, 'plate': '2070GKD'},
		#							    {'confidence': 81.850777, 'matches_template': 0, 'plate': '207QGKD'},

		possible_plates = get_plates(result_pandas_df)

		# Working on the max confidence
		prob = possible_plates[0]['confidence']
		plate = possible_plates[0]['plate']
		print('IAM HERE')

		# Possible region of interest in the format i.e : [{'x': 147, 'y': 135},
 		#												  {'x': 349, 'y': 156},
		#												  {'x': 338, 'y': 246},
		#												  {'x': 138, 'y': 224}]

		possible_region = get_plate_region(result_pandas_df)

		# Working on the max confidence
		region = possible_region

		if len(result_pandas_df) == 0:
			print('The API cant abble to detect any plate in the image')
		else:
			print('The posible plates are:')
			print(possible_plates)
			print('saving the max PROB. confidence to txt log ...')
			# full log
			np.save(name_to_workdir+'/{}/'.format(idd)+'full_log_{}_{}.npy'.format(idd,date), information_of_the_image_as_json_file)
			with open(name_to_workdir+'/{}/'.format(idd)+'{}_{}.txt'.format(idd,date),'a') as f:
				line = '{} {} {} {} {}'.format(idd, date, prob, plate, region)
				f.write(line)
		


if __name__ == '__main__':

	files_exist = check_files_existence()

	if files_exist:
		# Files has veen moved to worddir?

		move_files_to_work_dir(files_exist)
	
	else:
		print('working...')
