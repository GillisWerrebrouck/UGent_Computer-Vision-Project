import cv2
import numpy as np
from glob import glob
from ntpath import basename

from core.cameraCalibration import undistort_frame, get_calibration_matrix
from core.detectBlurredImages import is_sharp_image
from core.logger import get_root_logger
from core.visualize import show_image, resize_image

cdef class VideoLoop:

    cdef object logger, calibration_matrix
    cdef int nr_of_frames_to_skip, blur_threshold
    cdef object on_frame
    cdef list videos

    def __init__(self, on_frame, nr_of_frames_to_skip=30, blur_threshold=100, video=None):
        """
        Loop through all videos in the dataset.

        Parameters
        ----------
        - on_frame -- Function that will be called when a frame is fetched.
        - nr_of_frames_to_skip -- The number of frames to skip before fetching a frame (default is 30).
        - blur_threshold -- Threshold of Laplacian before accepting a frame (default is 100).
        - video -- Optional path when only one videos needs to be processed.
        """
        self.logger = get_root_logger()
        self.on_frame = on_frame
        self.nr_of_frames_to_skip = nr_of_frames_to_skip
        self.blur_threshold = blur_threshold
        self.calibration_matrix = get_calibration_matrix(
            './datasets/videos/gopro/calibration_M.mp4',
            fov='M'
        )

        if video is None:
            # first loop through the smartphone videos
            self.videos = sorted(glob('./datasets/videos/smartphone/*.mp4'))

            # then the gopro videos
            self.videos.append(sorted(glob('/datasets/videos/gopro/*.mp4')))
        else:
            self.videos = [video]

    cpdef start(self):
        self.logger.info('Video loop started')
        cdef int index = 0
        cdef str video_file = None
        cdef object calibration_matrix = None
        cdef int total_nr_videos = len(self.videos)

        while index < total_nr_videos:
            video_file = self.videos[index]
            calibration_matrix = self.calibration_matrix if "gopro" in video_file else None
            self.loop_through_video(video_file, calibration_matrix)
            index += 1

        self.logger.info('Video loop ended')


    cdef loop_through_video(self, video_file, calibration_matrix=None):
        self.logger.info('Starting loop for video {}'.format(video_file))
        cdef object cap = cv2.VideoCapture(video_file)

        if (cap.isOpened() == False):
            self.logger.error("Videofile {} not found".format(video_file))
            return

        cdef str filename = basename(video_file)
        cdef int needsCalibration = calibration_matrix is not None

        cdef int success = False
        cdef object frame = None
        cdef int total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cdef int frame_counter = 0

        while (cap.isOpened() and frame_counter <= total_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_counter)

            success, frame = cap.read()

            # if no frame was returned, stop processing the video
            if not success:
                self.logger.info('Video {} done'.format(video_file))
                break

            # we read a frame
            self.logger.info('Read frame {}/{}'.format(frame_counter, total_frames))
            frame_counter += self.nr_of_frames_to_skip

            if needsCalibration:
                self.logger.info('Calibrating frame')
                frame = undistort_frame(frame, params=calibration_matrix)

            self.logger.info('Checking if frame is sharp')
            if not is_sharp_image(frame, self.blur_threshold):
                self.logger.info('Frame not sharp enough, skipping!')
                continue

            self.logger.info('Emitting new frame')
            self.on_frame(frame, filename)

        cap.release()
