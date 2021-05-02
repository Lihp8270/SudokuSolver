import pytesseract
import cv2
import numpy as np
from PIL import Image
from PrivatePaths import *
from FourPointTransform import transform

def capture_image():
    cap = cv2.VideoCapture(0)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Display the resulting frame
        cv2.imshow('Press C to continue',frame)
        if cv2.waitKey(1) & 0xFF == ord('c'):
            img = frame
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
    return img

def create_board(l, n):
    for i in range(0, len(l), n): 
        yield l[i:i + n]

def split(word):
    return list(word)

def image_preprocess(capImg):
    img = capImg

    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC) # Resize to increase DPI
    
    kernel = np.ones((1, 1), np.uint8)
    grayImg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    grayImg = cv2.dilate(grayImg, kernel, iterations=1)
    grayImg = cv2.erode(grayImg, kernel, iterations=1)

    blurImg = cv2.GaussianBlur(grayImg,(5,5),0)
    
    threshImg = cv2.adaptiveThreshold(blurImg,255,1,1,11,2)

    return blurImg, threshImg

def find_puzzle(image):
    biggest = None
    maxArea = 0

    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for i in contours:
        area = cv2.contourArea(i)
        if area > 100:
                peri = cv2.arcLength(i,True)
                approx = cv2.approxPolyDP(i,0.02*peri,True)
                if area > maxArea and len(approx)==4:
                        biggest = approx
                        maxArea = area
    return biggest

def ocr_puzzle(img, gridSizeX, gridSizeY):
    x = 0
    y = 0
    sudokuArray = []
    sudokuRow = []
    k = 0
    r = 0
    cnt = 0

    while r < 9:
        while k < 9:
            croppedImg = img[y:y+gridSizeY, x:x+gridSizeX]
            '''
            cnt += 1
            cv2.imshow(str(cnt),croppedImg)
            cv2.waitKey(0)
            cv2.destroyWindow(str(cnt))
            '''
            ocr = pytesseract.image_to_string(croppedImg, config="-c tessedit_char_whitelist=0123456789 --psm 10")
            # print(ocr)
            if len(split(ocr)) == 1:
                ocr = 0
            else:
                ocr = int(split(ocr)[0])
            sudokuRow.append(ocr)
            k += 1
            x += gridSizeX

        k = 0
        x = 0
        y += gridSizeY
        r += 1

    sudokuArray = list(create_board(sudokuRow,9))
    return sudokuArray

def get_gridsize(image):
    dimensions = np.shape(image)
    height = dimensions[0]
    width = dimensions[1]
    print(width)

    gridSizeX = width/9
    gridSizeY = height/9

    return gridSizeX, gridSizeY

def get_puzzle():
    initCap = capture_image()
    grayImg, threshImg = image_preprocess(initCap)
    puzzleArray = find_puzzle(threshImg)
    straightPuzzle = transform(grayImg, puzzleArray)

    gridSizeX, gridSizeY = get_gridsize(straightPuzzle)
    gridSizeX = int(gridSizeX)
    gridSizeY = int(gridSizeY)

    sudokuBoard = ocr_puzzle(straightPuzzle, gridSizeX, gridSizeY)

    return sudokuBoard

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
    
    sudokuBoard = get_puzzle()

    if validate_board_entry(sudokuBoard):
        if solve_board(sudokuBoard) and sudokuBoard != False:
            print("\nSolved!\n")
            print_formatted_board(sudokuBoard)
        else:
            print("Unsolvable")
    else:
        print("Board entered is invalid")