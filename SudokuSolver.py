import pytesseract
import cv2
import numpy as np
from PIL import Image
from PrivatePaths import *

def create_board(l, n):
    for i in range(0, len(l), n): 
        yield l[i:i + n]

def split(word):
    return list(word)

def image_preprocess(capImg):
    img = cv2.imread(capImg)

    grayImg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    grayImg = cv2.GaussianBlur(grayImg,(5,5),0)
    threshImg = cv2.adaptiveThreshold(grayImg,255,1,1,11,2)

    return grayImg, threshImg

def split_puzzle(puzzle):
    biggest = None
    maxArea = 0

    contours, hierarchy = cv2.findContours(puzzle, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

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
    gridSize = int((biggest[2][0][0] - biggest[0][0][0]) / 9)

    return x, y, gridSize

def ocr_puzzle(x, y, gridSize, puzzle):
    initialX = x
    initialY = y
    sudokuArray = []
    sudokuRow = []
    k = 0
    r = 0
    while r < 9:
        while k < 9:
            croppedImg = puzzle[y:y+gridSize, x:x+gridSize]
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
    return sudokuArray

def validate_board_entry(boardInput):
    print_formatted_board(boardInput)
    print("Confirm this board is correct (Y/N)")   
    if input().upper() == "Y" and find_next(boardInput) != (None, None):
        return True
    return False

def print_formatted_board(board):
    for i in range(len(board)):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - -")

        for j in range(len(board[0])):
            if j % 3 == 0 and j != 0:
                print("| ", end="")

            if j == 8:
                print(board[i][j])
            else:
                print(str(board[i][j]) + " ", end="")

def find_next(board):
    # Finds the next cell on the board which is available.  Empty cell is 0
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r,c
    return None, None # No empty spaces, board is filled

def is_valid(board, guess, row, col):
    # If the guess is valid return true
    # Check Rows
    rowValues = board[row]
    if guess in rowValues:
        return False

    # Check Columns
    colValues = []
    for i in range(9):
        colValues.append(board[i][col])
        if guess in colValues:
            return False

    # Check 3x3 square
    startingRow = (row // 3) * 3
    startingCol = (col // 3) * 3
    for r in range(startingRow, startingRow + 3): # Check just the 3 rows of the 3x3
        for c in range(startingCol, startingCol + 3):
            if board[r][c] == guess:
                return False
    return True

def solve_board(board):
    row, col = find_next(board)

    # If theres no next row, then the puzzle is complete
    if row is None:
        return True

    for guess in range(1,10):
        if is_valid(board, guess, row, col):
            board[row][col] = guess # Add guess to the board if it's valid
            if solve_board(board):
                return True
        board[row][col] = 0 # reset the guess if no result
    return False

if __name__ == '__main__':

    gray, thresh = image_preprocess(testImage)
    x, y, gridSize = split_puzzle(thresh)
    sudokuBoard = ocr_puzzle(x, y, gridSize, gray)

    if validate_board_entry(sudokuBoard):
        if solve_board(sudokuBoard) and sudokuBoard != False:
            print("\nSolved!\n")
            print_formatted_board(sudokuBoard)
        else:
            print("Unsolvable")
    else:
        print("Board entered is invalid")