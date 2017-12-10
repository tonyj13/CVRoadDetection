# Authors:
# Christopher Britt
# Tony Jimogaon
#
# Final Project (Fall 2017)
#
# Usage:
#   Place this script on the directory with the target video.
#   For using different test videos, change the 'edited_road_vid.wmv' variable
#   to the file name of the desired test video.
#
# Linux users: Will NOT work on default OpenCV installations
#	since it lacks default ffmpeg codec support. Use on Windows instead.
#
# Parameters: none

import cv2
import numpy as np
from matplotlib import pyplot as plt
import sys
import time

# open up the video
cap = cv2.VideoCapture('edited_road_vid.wmv')

# check to see if the video opened
if (cap.isOpened() == False):
	sys.exit("Unable to open video")

# get the frame width
frame_width = int(cap.get(3))
# get the frame height
frame_height=int(cap.get(4))

# make a mask of nothing but 0's to remove the stuff we dont care about
mask = np.zeros((frame_height,frame_width),dtype = "uint8")
# keep track of the frames for mod math
count = 0

# make a rectangle on the mask of the stuff we care about
# it has to be in RGB since converting all the frame to greyscale and then masking it will take more time than masking and then converting
cv2.rectangle(mask,(0,int(12*frame_height/20)),(frame_width,frame_height-50),(255,255,255),-1)

# this keeps the loop running while there is video.
while(cap.isOpened()):
	# get the frame
	ret, frame = cap.read()

	# scans every 10th frame to update blackmask
	if (count%10 ==  0):
		# add the mask for the dumb rectangle
		result_frame = cv2.bitwise_and(frame,frame,mask=mask)
		# convert to grayscale
		gray_frame = cv2.cvtColor(result_frame, cv2.COLOR_BGR2GRAY)
		# blur out the lines so only the long strong lines show
		blurred = cv2.bilateralFilter(gray_frame,6,50,50)
		# use canny edge to detect the edges
		edges = cv2.Canny(blurred,30,100)
		# find line segments using probablisiic Hough transform (more effecient apparently)
		lines = cv2.HoughLinesP(edges,1,np.pi/180,60,maxLineGap=1)

		#this divides the data into left and half planes
		left_data_set = np.array([0,0,0,0])
		right_data_set = np.array([0,0,0,0])

		for i in range(len(lines)):
			x1, y1, x2, y2 = lines[i][0]
			# gets rid of purely horizontal and vertical lines to remove artifacts
			if (y1 - y2 > 1 or y1 - y2 < -1) and (x2 - x1 > 1 or x2 - x1 < -1):
				# draws the lines on the frame for this pass
				cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)

				# points on left half of screen
				if (x2 < frame_width/2):
					left_data_set = np.vstack((left_data_set,lines[i][0]))

				# points on right
				if (x2> frame_width/2):
					right_data_set = np.vstack((right_data_set,lines[i][0]))

		#removes the random zero I added to format the arrays
		left_data_set = np.delete(left_data_set,0,axis =0)
		right_data_set = np.delete(right_data_set,0,axis = 0)

		#creates a maske that is only in the area where lines were previously found
		black_mask = np.zeros((frame_height, frame_width), dtype="uint8")

		for j in range(len(left_data_set)):
			try:
				x1, y1, x2, y2 = left_data_set[j]
				cv2.rectangle(black_mask, (x1 - int(1.25 * (x1 - x2)), y2 - int(1.25 * (y1 - y2))),(x2 + int(1.25 * (x1 - x2)), y1 + int(1.25 * (y1 - y2))), 255, -1)
			except:
				pass

		for j in range(len(right_data_set)):
			try:
				x1, y1, x2, y2 = right_data_set[j]
				cv2.rectangle(black_mask, (x1 - int(1.25*(x2-x1)), y1 - int(1.25*(y2-y1))) , (x2 + int(1.25*(x2-x1)), y2 + int(1.25*(y2-y1))), 255, -1)
			except:
				pass

		# if count isnt a factor of 10 it uses the peviously found mask that is only in the area where lines were peviously found
		if (count%10 != 0):
			result_frame = cv2.bitwise_and(frame, frame, mask=black_mask)
			gray_frame = cv2.cvtColor(result_frame, cv2.COLOR_BGR2GRAY)
			blurred = cv2.bilateralFilter(gray_frame, 6, 50, 50)
			edges = cv2.Canny(blurred, 30, 100)
			lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 60, maxLineGap=1)

			for i in range(len(lines)):
				x1, y1, x2, y2 = lines[i][0]
				if (y1 - y2 > 1 or y1 - y2 < -1) and (x2 - x1 > 1 or x2 - x1 < -1):
					# get rid of vertical lines to remove artifacts
					# get rid of horizontal lines to remove artifacts
					cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)

#show the image
		cv2.imshow('frame', frame)

#exit on escape key
		k = cv2.waitKey(30) & 0xff
		if k == 27:
			break

	count = count + 1