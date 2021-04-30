import pytesseract
import cv2
import numpy as np
from PIL import Image
from PrivatePaths import *
from SudokuSolver import print_formatted_board
from FourPointTransform import transform

def create_board(l, n):
    for i in range(0, len(l), n): 
        yield l[i:i + n]

def split(word):
    return list(word)

# Image pre-process function
# Inputs required -- Captured image
# Output -- Threshold Image
img = cv2.imread(testImage)
grayImg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#cv2.imshow('first gray', grayImg)
#cv2.waitKey(0)
blurImg = cv2.GaussianBlur(grayImg,(5,5),0)
#cv2.imshow('second gray', grayImg)
#cv2.waitKey(0)
threshImg = cv2.adaptiveThreshold(blurImg,255,1,1,11,2)
#cv2.imshow('threshold image', threshImg)
#cv2.waitKey(0)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
readyCont = cv2.morphologyEx(threshImg, cv2.MORPH_OPEN, kernel)
#cv2.imshow('ready for Contours', readyCont)
#cv2.waitKey(0)

# Split puzzle function
# Inputs required -- Threshold Image
# Output -- x, y, gridsize
biggest = None
maxArea = 0
contours, hierarchy = cv2.findContours(readyCont, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for i in contours:
    area = cv2.contourArea(i)
    if area > 100:
            peri = cv2.arcLength(i,True)
            approx = cv2.approxPolyDP(i,0.02*peri,True)
            if area > maxArea and len(approx)==4:
                    biggest = approx
                    maxArea = area

x = biggest[0][0][0]
y = biggest[0][0][1]
x2 = biggest[2][0][0]
y2 = biggest[2][0][1]

startPoint = (x, y)
endPoint = (x2, y2)
colour = (0,0,255)

#detectTest = cv2.rectangle(img, startPoint, endPoint, colour, 5)
#cv2.imshow('Detect Test', detectTest)
#cv2.waitKey(0)
print(biggest)
#print(biggest[0][0])
#print(biggest[1][0])
#print(biggest[2][0])
#print(biggest[3][0])
gridSize = int((biggest[2][0][0] - biggest[0][0][0]) / 9)
straightImage = transform(img,biggest)
cv2.imshow('Straightened Image',straightImage)
cv2.waitKey(0)
'''
# OCR function
# Variables required -- x, y, gridsize, image
# Output -- sudokuArray
initialX = x
initialY = y
sudokuArray = []
sudokuRow = []
k = 0
r = 0
while r < 9:
    while k < 9:
        croppedImg = blurImg[y:y+gridSize, x:x+gridSize]
        #cv2.imshow("Cropped Image", croppedImg)
        #cv2.waitKey(0)
        ocr = pytesseract.image_to_string(croppedImg, config="-c tessedit_char_whitelist=0123456789 --psm 10")
        if len(split(ocr)) == 1:
            ocr = 0
        else:
            ocr = int(split(ocr)[0])
        sudokuRow.append(ocr)
        k += 1
        x += gridSize
    k = 0
    x = initialX
    y += gridSize
    r += 1

sudokuArray = list(create_board(sudokuRow,9))
print_formatted_board(sudokuArray)
'''