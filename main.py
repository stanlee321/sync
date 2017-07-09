# -*- coding: utf-8 -*-
import ast
import cv2
from datetime import datetime
import glob
from utils import check_folder, get_json_from_api, get_plate_region, get_plates, read_data
import os
from pandas.io.json import json_normalize
import threading
import time
import scipy.misc
import matplotlib.pyplot as plt
import numpy as np
import moviepy.editor as mpe



path_to_images = 'casosReportados/'
path_to_cut_images = 'placasAreconocer/'
name_to_workdir = 'WORKDIR'



"""
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
"""

class InformationAPIprocess(object):
	 """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """
	def __init__(self,  path_to_images = 'casosReportados/',\
	 					path_to_cut_images = 'placasAreconocer/',\
	 					name_to_workdir = 'WORKDIR', interval = 1 ):

		self.path_to_images = path_to_images
		self.path_to_cut_images = path_to_cut_images
		self.name_to_workdir = name_to_workdir

		self.interval = interval
        thread = threading.Thread(target=self.check_if_is_files, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start() 									# Start the execution



	# Check if file is empy and move files to workdir

	def check_files_existence(self):
		global files_exist
		files_exist = check_folder(self.path_to_images,'jpg')
		return files_exist

	def move_files_to_work_dir(self, files_exist):
		
		if files_exist :
			try:
				os.mkdir(self.path_to_images)
			except Exception as e:
				print('folder already exist')

			files = read_data(self.path_to_images + '*.jpg')
			print('len files', len(files))
			files_cut = read_data(self.path_to_cut_images + '*.png')
			print('len files', len(files_cut))

			for file  in files:
				namen = file[0]	#path to the image
				img = file[1]	# image as array
				code = file[3] # NAME TO THE FOLDER NAME
				date = file[2]	# NAME TO FILE NAME.jpg
						
				try:
					os.mkdir(self.name_to_workdir+'/{}'.format(code))
				except Exception as e:
					print('folders {} exist already'.format(self.name_to_workdir+'/{}'.format(code)))
				try:
					os.mkdir(self.name_to_workdir+'/{}/{}'.format(code,'video'))
				except Exception as e:
					print('folder {} already exist'.format(self.name_to_workdir+'/{}/{}'.format(code,'video')))



				scipy.misc.imsave(self.name_to_workdir+'/{}/video/{}.jpg'.format(code,date), img)

				# CREATE VIDEO
				#create_video_from_images(name_to_workdir+'/{}/video/'.format(code))
	#

				print('Done imgs and movie')
			for cutted in files_cut:

				cut_namen = cutted[0]
				cut_img  = cutted[1]
				cut_code = cutted[3]	# NAME TO THE FOLDER NAME
				cut_date = cutted[2]	# NAME TO FILE NAME.jpg

				scipy.misc.imsave(self.name_to_workdir+'/{}/{}.jpg'.format(cut_code, cut_date), cut_img)

				get_information_of_images(files_exist, cut_namen, cut_code, cut_date)

				print('Done cut_img')
		
		else:
			print('There is not files in dir... /{}'.format(self.path_to_images))
			return False

		#files_exist, images = check_folder(self.path_to_images)


	### Work on workdir and use the API

	# Check workdir files

	def get_information_of_images(self, file_exist, image, idd, date):
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
				np.save(self.name_to_workdir+'/{}/'.format(idd)+'full_log_{}_{}.npy'.format(idd,date), information_of_the_image_as_json_file)
				
				with open(self.name_to_workdir+'/{}/'.format(idd)+'{}_{}.txt'.format(idd,date),'a') as f:
					line = '{} {} {} {} {}'.format(idd, date, prob, plate, region)
					f.write(line)
				# Save image with plate region labeled
				font = cv2.FONT_HERSHEY_SIMPLEX

				px0 = region[0]['x']
				py0 = region[0]['y']
				px1 = region[2]['x']
				py1 = region[2]['y']

				textx = region[0]['x']
				texty = region[0]['y']

				img = cv2.imread(image)
				img = cv2.rectangle(img,(px0,py0),(px1,py1),(0,255,0),3)
				img = cv2.putText(img,plate,(textx,int(texty*0.95)), font, 1,(0,255,3),2,cv2.LINE_AA)
				scipy.misc.imsave(self.name_to_workdir+'/{}/'.format(idd)+'{}_{}.jpg'.format(idd,date),img)
				
	def check_if_is_files(self):

		files_exist = self.check_files_existence

		while files_exist:
			# Files has veen moved to worddir?
			move_files_to_work_dir(files_exist)
			time.sleep(self.interval)

		#else:
		print('I am out')


	


if __name__=='__main__':
	example = ThreadingExample()
	time.sleep(3)
	print('Checkpoint')
	time.sleep(2)
	print('Bye')





	