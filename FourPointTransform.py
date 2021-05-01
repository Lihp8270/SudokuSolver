import cv2
import numpy as np

def order_coordinates(coords):
    box = np.zeros((4,2), dtype="float32")

    s = np.sum(coords, axis = 1, dtype="float32")
    box[0] = coords[np.argmin(s)]
    box[2] = coords[np.argmax(s)]

    diff = np.diff(coords, axis = 1)
    box[1] = coords[np.argmin(diff)]
    box[3] = coords[np.argmax(diff)]

    return box

# Coordinates to be supplied clockwise from top left (x1)
def transform(image, coords):
    topLeft = coords[0][0]
    topRight = coords[1][0]
    bottomRight = coords[2][0]
    bottomLeft = coords[3][0]

    pts = "[("+str(topLeft[0])+","+str(topLeft[1])+"),("+str(topRight[0])+","+str(topRight[1])+"),("+str(bottomRight[0])+","+str(bottomRight[1])+"),("+str(bottomLeft[0])+","+str(bottomLeft[1])+")]"

    points = np.array(eval(pts),dtype="float32")
    box = order_coordinates(points)
    (tl, tr, br, bl) = box
   
    # Find max width Euclidean Distance
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # Find max height Euclidean Distance
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [10,10],
        [maxWidth - 1,10],
        [maxWidth -1, maxHeight - 1],
        [10, maxHeight -1]], dtype="float32")
    
    trans = cv2.getPerspectiveTransform(points, dst)
    straightImage = cv2.warpPerspective(image, trans, (maxWidth+25, maxHeight+25))
    straightImage = cv2.flip(straightImage, 1)

    return straightImage