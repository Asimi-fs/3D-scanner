# ECE 5725
# Michael Xiao (mfx2) and Thomas Scavella (tbs47)
# 3D scanner software
import cv2
import numpy as np
import math
from picamera import PiCamera
from time import sleep
import RPi.GPIO as GPIO
import time
import os
from gpiozero import LED
from gpiozero import PWMLED
from gpiozero import Button
import smtplib
import serial

# # pins of the stepper motor
# out1 = 13
# out2 = 16
# out3 = 5
# out4 = 12
# 
# # additional GPIO pins
# button = Button(23)
# led = PWMLED(18)

# placeholder variable to track status of stepper motor
i=0

# # GPIO setup
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(out1,GPIO.OUT)
# GPIO.setup(out2,GPIO.OUT)
# GPIO.setup(out3,GPIO.OUT)
# GPIO.setup(out4,GPIO.OUT)
ser = serial.Serial('/dev/ttyS0', 9600)

#vertex class
class vertex:
	def __init__(self, x,y,z):
		self.x = x
		self.y = y
		self.z = z

	def write(self):
		return "v " + str(self.x) + " " + str(self.y) + " " +str(self.z)
		#return  str(self.x) + "," + str(self.y) + "," +str(self.z)
#face class
class face:
	def __init__(self, v1,v2,v3):
		self.v1 = v1
		self.v2 = v2
		self.v3 = v3

	def write(self):
		return "f " + str(self.v1) + " " + str(self.v2) + " " +str(self.v3)

# transforms cylindrical coordinates into rectangular coordinates
def getVertex(pCoord):
	#pass
	H = pCoord.x
	t = pCoord.y
	d = pCoord.z
	x = d*math.cos(t)
	y = d*math.sin(t)
	z = H
	return vertex(int(x),int(y),int(z))

def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect

def step(step):
    while(ser.writable() is not True):
        sleep(0.1)
        print("sleep")
    if(step < 10):
        RXbuff = "R00{}"
    elif(step >= 10 and step < 100):
        RXbuff = "R0{}"
    else:
        RXbuff = "R{}"
    b = 0x00
    RXbuff = RXbuff.format(step)
    print(RXbuff)
    b = str.encode(RXbuff)
    sleep(0.1)
    ser.write(b)
    
def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped

while (1):
	# angular resolution
	numItt = 20

	# angle
	theta = 0
	thetaInc = 360.0/numItt

	# motor position
	motorPos = 0
	motorPosI = 400.0/numItt

	#data
	meshPoints = []
	lineLenth = []

	# while loop for system


	# wait for start button

	# turn on status light

	while(theta < 360):
		#will loop this
		camera = PiCamera()
		camera.start_preview()
		sleep(1)
		camera.capture('lineDetection.jpg')
		camera.close()
		img = cv2.imread('lineDetection.jpg')

		#---------- Preview the picture ----------------
		cv2.imshow("perspective", img)
		cv2.waitKey(0)

		#get perspective
# 		tlp = (375.0,275.0)
# 		trp = (1090.0,420.0)
# 		brp = (1090.0,915.0)
# 		blp = (375.0,1060.0)
# 		pts = np.array([tlp,trp,brp,blp])
# 		img = four_point_transform(img, pts)

		#---------- Preview the PERSPECTIVE picture ----------------
		cv2.imshow("perspective", img)
		cv2.waitKey(0)


		# filter
		lowerb = np.array([0, 0, 20])
		upperb = np.array([255, 255, 255])
		#1200,1600
		red_line = cv2.inRange(img, lowerb, upperb)
		##red_line = cv2.resize(red_line, (60,80), interpolation = cv2.INTER_AREA)


		#---------- Preview the filtered picture ----------------
		cv2.imshow("perspective", red_line)
		cv2.waitKey(0)
		#print red_line.shape


		h,w = np.shape(red_line)
		backG = np.zeros((h, w))

		#print backG

		bottomR = 0

		r = 0
		for cIndex in np.argmax(red_line, axis=1):
			if red_line[r,cIndex] != 0:
				backG[r,cIndex] = 1
				bottomR = r
			r += 1

		#---------- Preview the processed picture ----------------
		cv2.imshow("perspective", backG)
		cv2.waitKey(0)


		tempV = []
		r = 0
		centerC = 420.0 #center column
		for cIndex in np.argmax(backG,axis=1):
			if(backG[r,cIndex] == 1):
				#intvi = 0
				H = r-bottomR
				dist = cIndex - centerC
				coord = vertex(H,np.radians(theta),dist)
				tempV.append(coord)
			r += 1

		# vertical resolution
		intv = 20
		intv = len(tempV)/intv

		if(len(tempV) != 0 and intv != 0):
			V = []
			V.append(tempV[0])

			for ind in range(1,len(tempV)-2):
				if(ind % intv == 0):
					V.append(tempV[ind])

			V.append(tempV[(len(tempV)-1)])
			meshPoints.append(V)
			print(str(len(V)))
			lineLenth.append(-1*len(V))

		theta += thetaInc
		ser.reset_output_buffer()
		sleep(0.5)
		ser.write(b'R001')
		sleep(0.01)
		theta = theta + 1
		time.sleep(0.3)


	# for row in meshPoints:
	# 	for coord in row:
	# 		print getVertex(coord).write()

	print(lineLenth)
	shortest = len(meshPoints[np.argmax(lineLenth)])

	for line in meshPoints:
		while(len(line) > shortest):
			line.pop(len(line)-2)


	points = []
	faces = []
	firstRow = []
	prevRow = []
	for index in range(1,len(meshPoints[0])+1):

		points.append(getVertex(meshPoints[0][index-1]))
		firstRow.append(index)

	prevRow = firstRow
	for col in range(0,len(meshPoints)):
		if col != 0:
			indexS = prevRow[-1]
			currentRow = []
			for point in range(0,len(meshPoints[col])-1):
				tl = indexS + point + 1
				bl = tl + 1
				tr = prevRow[point]
				br = prevRow[point + 1]

				f1 = face(tl,tr,bl)
				f2 = face(bl,tr,br)
				faces.append(f1)
				faces.append(f2)

				points.append(getVertex(meshPoints[col][point]))
				currentRow.append(tl)
				if(point == len(meshPoints[col])-2):
					points.append(getVertex(meshPoints[col][point+1]))
					currentRow.append(bl)

				if col == (len(meshPoints)-1):
					tr = tl
					br = bl
					tl = firstRow[point]
					bl = firstRow[point+1]
					f1 = face(tl,tr,bl)
					f2 = face(bl,tr,br)
					faces.append(f1)
					faces.append(f2)
			prevRow = currentRow

	#---------- debugging prints ----------------
	# for point in points:
	# 	print(point.write())
	# for face in faces:
	# 	print(face.write())

	# writing the file
	filetowrite='3d.obj'
	with open(filetowrite, 'w') as file:
		for point in points:
			file.write(point.write() + "\n")
		for f in faces:
			file.write(f.write() + "\n")
		file.close()

	# turn status light off

	# TODO: send data online
	# TODO: clear variables

GPIO.cleanup()
