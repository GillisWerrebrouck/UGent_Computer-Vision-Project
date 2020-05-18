import cv2
import numpy as np

from core.cameraCalibration import undistort_frame
from core.detectBlurredImages import is_sharp_image
from core.logger import get_root_logger
from core.visualize import show_image, resize_image

logger = get_root_logger()

# TODO: docs!
cpdef loop_through_video(
    video_file,
    on_frame,
    nr_of_frames_to_skip=10,
    difference_threshold=10,
    blur_threshold=100,
    calibration_matrix=None
):
    logger.info('Starting loop for video {}'.format(video_file))
    cdef object cap = cv2.VideoCapture(video_file)

    if (cap.isOpened() == False):
        raise Exception("Videofile {} not found".format(video_file))

    cdef int needsCalibration = calibration_matrix is not None

    cdef int framesRead = 0
    cdef object previousFrame = None

    cdef int success = False
    cdef object frame = None

    while (cap.isOpened()):
        success, frame = cap.read()

        # if no frame was returned, go to the next one
        if not success:
            logger.info('Video {} done'.format(video_file))
            cap.release()
            break

        # we read a frame
        framesRead += 1
        if framesRead % 10 == 0:
            logger.info('Frame {}'.format(framesRead))

        if framesRead % nr_of_frames_to_skip is not 0:
            continue

        if needsCalibration:
            frame = undistort_frame(frame, params=calibration_matrix)

        if not is_sharp_image(frame, blur_threshold):
            continue

        # TODO: search a fancy way to determine if it's worth to show the frame
        # if previousFrame is not None:
        #     difference = np.average(abs(cv2.subtract(previousFrame, frame)))
        # else:
        #     difference = difference_threshold

        # print("Difference", np.average(difference))
        # if difference >= difference_threshold:
        #     previousFrame = frame

        on_frame(frame)

        framesRead = 0
