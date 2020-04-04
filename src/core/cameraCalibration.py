import cv2
import sys
import os
import numpy as np


nCols = 6
nRows = 10
skip = 10
dimension = 25  # - mm
criteria = (cv2.TERM_CRITERIA_EPS +
            cv2.TERM_CRITERIA_MAX_ITER, dimension, 0.001)


# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((nRows * nCols, 3), np.float32)
objp[:, :2] = np.mgrid[0:nCols, 0:nRows].T.reshape(-1, 2)

print(objp)

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.


def show(image):
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def determineUsability(frame, number):
    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(grayFrame, (nCols, nRows), None)

    if ret == True:
        print("found the chessboardCorners!")
        corners2 = cv2.cornerSubPix(
            grayFrame, corners, (11, 11), (-1, -1), criteria)
        cv2.drawChessboardCorners(frame, (nCols, nRows), corners2, ret)
        show(frame)


cap = cv2.VideoCapture(sys.argv[1])

if (cap.isOpened() == False):
    print("Error opening video stream or file")

aantal = 0
noTestImg = True

while (cap.isOpened()):
    ret, frame = cap.read()

    if ret == True:

        grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(
            grayFrame, (nCols, nRows), None)

        if ret == True:
            print("found the chessboardCorners!")
            aantal += 1
            if noTestImg and aantal == 10:
                testImg = grayFrame
                noTestImg = False
                print("Got test image")

            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(
                grayFrame, corners, (11, 11), (-1, -1), criteria)

            imgpoints.append(corners2)

            cv2.drawChessboardCorners(frame, (nCols, nRows), corners2, ret)

        cv2.imshow('frame', frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    else:
        break

    for i in range(0, skip):
        cap.read()

cap.release()

# print(aantal)
# print(testImg)

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, testImg.shape[::-1], None, None)


h,  w = testImg.shape[:2]
print("Image to undistort: ", testImg)
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

# undistort
mapx, mapy = cv2.initUndistortRectifyMap(
    mtx, dist, None, newcameramtx, (w, h), 5)
testImgDistorted = cv2.remap(testImg, mapx, mapy, cv2.INTER_LINEAR)

x, y, w, h = roi
print("ROI: ", x, y, w, h)
dst = testImgDistorted[y:y+h, x:x+w]
print(mtx)


resized = cv2.resize(dst, (testImg.shape[1], testImg.shape[0]))
show(np.hstack((testImg, resized)))

cv2.destroyAllWindows()
