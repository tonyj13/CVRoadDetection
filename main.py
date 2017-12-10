import cv2
import numpy as np
from matplotlib import pyplot as plt
import sys
import time






#cap = cv2.VideoCapture('edited_road_vid.wmv') #open up the video
cap = cv2.VideoCapture('norway_edited2.mp4') #open up the video



if (cap.isOpened() == False): #check to see if the video opened
	sys.exit("Unable to open video")




frame_width = int(cap.get(3)) #get the frame width
frame_height=int(cap.get(4)) #get the frame height
mask = np.zeros((frame_height,frame_width),dtype = "uint8") #make a mask of nothing but 0's to remove the stuff we dont care about
count = 0 #keep track of the frames for mod math

cv2.rectangle(mask,(0,int(12*frame_height/20)),(frame_width,frame_height-50),(255,255,255),-1) #make a rectangle on the mask of the stuff we care about
#it has to be in RGB since converting all the frame to greyscale and then masking it will take more time than masking and then converting



#screecode because Im a garbage human
while(cap.isOpened()):
#this keeps the loop running while there is video. I havent tested it because the video I've been using is corrupted and a pain but it works for like the first 100 seconds

	ret, frame = cap.read()
#get the frame


	if (count%10 ==  0): #scans every 10th frame to update blackmask


		result_frame = cv2.bitwise_and(frame,frame,mask=mask) #add the mask for the dumb rectangle
		gray_frame = cv2.cvtColor(result_frame, cv2.COLOR_BGR2GRAY) #convert to grayscale
		blurred = cv2.bilateralFilter(gray_frame,6,50,50) #blur out the lines so only the long strong lines show
		edges = cv2.Canny(blurred,30,100) #use canny edge to detect the edges

		lines = cv2.HoughLinesP(edges,1,np.pi/180,60,maxLineGap=1) #find line segments using probablisiic Hough transform (more effecient apparently)

		#this divides the data into left and half planes
		left_data_set = np.array([0,0,0,0])
		right_data_set = np.array([0,0,0,0])

		for i in range(len(lines)):
			x1, y1, x2, y2 = lines[i][0]
			if (y1 - y2 > 1 or y1 - y2 < -1) and (x2 - x1 > 1 or x2 - x1 < -1): #gets rid of purely horizontal and vertical lines to remove artifacts
			#get rid of vertical lines to remove artifacts
			#get rid of horizontal lines to remove artifacts
				cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 5) #draws the lines on the frame for this pass

				if (x2 < frame_width/2): #points on left half of screen
					left_data_set = np.vstack((left_data_set,lines[i][0]))


				if (x2> frame_width/2): #points on right
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

		if (count%10 != 0): #if count isnt a factor of 10 it uses the peviously found mask that is only in the area where lines were peviously found

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


#I should probably put in a graceful exit but nah