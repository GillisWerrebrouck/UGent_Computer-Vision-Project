import cv2
import os
import numpy as np
from core.logger import get_root_logger

logger = get_root_logger()


def __output_tuple_from_files(mtx_fn, dist_fn):
    """
    Read the calibration matrix and dist params from there files.

    Parameters
    ----------
    - mtx_fn -- File containing the matrix formatted by the nm.savetxt().
    - dist_fn -- File containing the dist formatted by the nm.savetxt().

    Returns
    -------
    A tuple of 2 np.array object containting the matrix and dist arrays in this order.
    """

    logger.info(
        "Returning output from file: {}, {} as tuple".format(mtx_fn, dist_fn))
    return np.loadtxt(mtx_fn, delimiter=','), np.loadtxt(dist_fn, delimiter=',')


def __check_file_existance(filename):
    """
    Check if a given file exists.

    Parameters
    ----------
    - filename -- file to be checked.

    Returns
    -------
    A boolean if the file exists.
    """

    if os.path.isfile(filename):
        logger.info("file: {} found".format(filename))
        return True
    else:
        logger.debug("file: {} not found".format(filename))
        return False


def __delete_file(filename):
    """
    Delete a given file.

    Parameters
    ----------
    - filename -- file to be deleted

    Returns
    -------
    Nothing
    """
    logger.debug("Removing file: {}".format(filename))
    os.remove(filename)


def __start_video_calibration(videoFN, cols, rows, skip, dim, objp, objpoints, imgpoints, matrix_filename, distortion_filename, start_video):
    """
    Calculate the calibration matrix and dist array for a given video and output these results to there speciefied files.

    Parameters
    ----------
    - videoFN -- filename of the video.
    - cols -- number of colums on the calibratrion paper.
    - rows -- number of rows on the calibratrion paper.
    - skip -- number of frames to skip when searching for the chessboard corners. (lower = more longer calculation time)
    - dim -- the dimention of the black squares in tht calibration paper in mm.
    - objp -- array containing the objectpoints.
    - objpoints -- array containing the objectpoints.
    - imgpoints -- array containing the imgpoints.
    - matrix_filename -- filename for the matix parameter
    - distortion_filename -- filename for the distortion parameter
    - start_video -- output a video for debuging.

    Returns
    -------
    Nothing
    """

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, dim, 0.001)

    cap = cv2.VideoCapture(videoFN)
    if not cap.isOpened():
        logger.warning("Videofile not found")
        return

    count = 0

    logger.info("Start analysing video")
    while cap.isOpened():

        success, frame = cap.read()

        if success:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(
                gray_frame, (cols, rows), None)

            if ret:
                count += 1
                objpoints.append(objp)

                corners2 = cv2.cornerSubPix(
                    gray_frame, corners, (11, 11), (-1, -1), criteria)

                imgpoints.append(corners2)
                if start_video:
                    cv2.drawChessboardCorners(
                        frame, (cols, rows), corners2, ret)
                    cv2.imshow('frame', frame)

        else:
            break

        for i in range(0, skip):
            cap.read()

    logger.info("Done Analysing video, got {} usable images".format(count))

    cap.release()
    logger.debug("Releasing video")

    logger.debug("Starting calibration calculations")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray_frame.shape[::-1], None, None)
    logger.info("Got matrix")

    logger.info("Got dist")

    logger.info("Writing matrix to {}".format(matrix_filename))
    np.savetxt(matrix_filename, mtx, delimiter=',')
    logger.info("Writing dist to {}".format(distortion_filename))
    np.savetxt(distortion_filename, dist, delimiter=',')


def undistort_frame(frame, params=None):
    """
    Given a frame, this function wil return the undistorted image.

    Parameters
    ----------
    - frame -- the frame to be processed
    - params -- the matrix and dist tuple

    Returns
    -------
    The undistorted image
    """

    h,  w = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
        params[0], params[1], (w, h), 0, (w, h))

    mapx, mapy = cv2.initUndistortRectifyMap(
        params[0], params[1], None, newcameramtx, (w, h), 5)
    dst = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)

    # crop the image
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]

    return dst


def get_calibration_matrix(video, fov, fps=60, quality=720, cols=6, rows=10, skip=60, dim=25, start_video=False):
    """
    Public function to calculate the calibration parameters for a given fideo. If the file for this video is present,
    the content will be returned. Otherwise the calculations wel be done.

    Parameters
    ----------
    - video -- filename of the video.
    - fov -- Field of view: M or W
    - fps -- the frames per second for the video.
    - quality -- the quality of the video.
    - cols -- number of colums on the calibratrion paper.
    - rows -- number of rows on the calibratrion paper.
    - skip -- number of frames to skip when searching for the chessboard corners. (lower = more longer calculation time)
    - dim -- the dimention of the black squares in tht calibration paper in mm.
    - start_video -- output a video for debuging.

    Returns
    -------
    A tuple of 2 np.array object containting the matrix and dist arrays in this order.
    """

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((rows * cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    # See if matrix allready exists
    matrix_filename = "calibrationMatrix{}{}{}.txt".format(
        quality, fps, fov)
    distortion_filename = "calibrationDistortion{}{}{}.txt".format(
        quality, fps, fov)

    logger.debug(matrix_filename)
    logger.debug(distortion_filename)

    mEx = __check_file_existance(matrix_filename)
    dEx = __check_file_existance(distortion_filename)

    logger.debug("mex: {}, dex: {}".format(mEx, dEx))

    if not mEx or not dEx:
        mEx and __delete_file(matrix_filename)
        dEx and __delete_file(distortion_filename)

        __start_video_calibration(video, cols, rows, skip, dim, objp, objpoints,
                                  imgpoints, matrix_filename, distortion_filename, start_video)

    logger.info(__output_tuple_from_files(matrix_filename, distortion_filename))
    return __output_tuple_from_files(matrix_filename, distortion_filename)



