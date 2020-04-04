import cv2
import sys
import os
import numpy as np
from logger import get_root_logger

logger = get_root_logger()


def __output_tuple_from_files(mtxFN, distFN):
    logger.info(
        "Returning output form file: {}, {} as tuple".format(mtxFN, distFN))
    return (np.loadtxt(mtxFN, delimiter=','), np.loadtxt(distFN, delimiter=','))


def __check_file_existance(filename):
    if os.path.isfile(filename):
        logger.info("file: {} found".format(filename))
        return True
    else:
        logger.debug("file: {} not found".format(filename))
        return False


def __delete_file(fn):
    logger.debug("Removing file: {}".format(fn))
    os.remove(fn)


def __start_video_calibration(videoFN, cols, rows, skip, dim, objp, objpoints, imgpoints, matrixFilename, distortionFilename, startVideo):

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, dim, 0.001)

    cap = cv2.VideoCapture(videoFN)
    if (cap.isOpened() == False):
        logger.warning("Videofile not found")
    aantal = 0

    logger.info("Start analysing video")
    while (cap.isOpened()):

        success, frame = cap.read()

        if success:

            grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(
                grayFrame, (cols, rows), None)

            if ret == True:
                aantal += 1
                objpoints.append(objp)

                corners2 = cv2.cornerSubPix(
                    grayFrame, corners, (11, 11), (-1, -1), criteria)

                imgpoints.append(corners2)
                if startVideo:
                    cv2.drawChessboardCorners(
                        frame, (cols, rows), corners2, ret)
                    cv2.imshow('frame', frame)

        else:
            break

        for i in range(0, skip):
            cap.read()

    logger.info("Done Analysing video, got {} usable images".format(aantal))

    cap.release()
    logger.debug("Releasing video")

    logger.debug("Starting calibration calculations")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, grayFrame.shape[::-1], None, None)
    logger.info("Got matrix")

    h, w = grayFrame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
        mtx, dist, (w, h), 1, (w, h))
    logger.info("Got dist")

    logger.info("Writing matrix to {}".format(matrixFilename))
    np.savetxt(matrixFilename, mtx, delimiter=',')
    logger.info("Writing dist to {}".format(distortionFilename))
    np.savetxt(distortionFilename, dist, delimiter=',')


def get_calibration_matrix(video, fps=60, quality=720, cols=6, rows=10, skip=60, dim=25, startVideo=False):

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((rows * cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    # See if matrix allready exists
    matrixFilename = "calibrationMatrix{}{}.txt".format(quality, fps)
    distortionFilename = "calibrationDistortion{}{}.txt".format(quality, fps)

    logger.debug(matrixFilename)
    logger.debug(distortionFilename)

    mEx = __check_file_existance(matrixFilename)
    dEx = __check_file_existance(distortionFilename)

    logger.debug("mex: {}, dex: {}".format(mEx, dEx))

    if (not mEx or not dEx):
        mEx and __delete_file(matrixFilename)
        dEx and __delete_file(distortionFilename)

        __start_video_calibration(video, cols, rows, skip, dim, objp, objpoints,
                                  imgpoints, matrixFilename, distortionFilename, startVideo)

    logger.info(__output_tuple_from_files(matrixFilename, distortionFilename))
    return __output_tuple_from_files(matrixFilename, distortionFilename)


get_calibration_matrix(
    "/Users/pieter-janphilips/Desktop/telin.ugent.be/dvhamme/computervisie_2020/videos/gopro/calibration_M.mp4")
