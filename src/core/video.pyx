import cv2
import numpy as np
from glob import glob
from ntpath import basename
from queue import Queue
from multiprocessing import Process
from time import sleep

from core.cameraCalibration import undistort_frame, get_calibration_matrix
from core.detectBlurredImages import is_sharp_image
from core.logger import get_root_logger
from core.visualize import show_image, resize_image

cdef class VideoLoop:

    cdef object logger, calibration_matrix
    cdef int nr_of_frames_to_skip, blur_threshold
    cdef object on_frame
    cdef list videos
    cdef object buffer
    cdef int min_buffer_size

    def __init__(self, buffer, nr_of_frames_to_skip=30, blur_threshold=100, video=None):
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
        # self.on_frame = on_frame
        self.nr_of_frames_to_skip = nr_of_frames_to_skip
        self.blur_threshold = blur_threshold
        self.calibration_matrix = get_calibration_matrix(
            './datasets/videos/gopro/calibration_M.mp4',
            fov='M'
        )
        self.min_buffer_size = 10
        self.buffer = buffer

        if video is None:
            # first loop through the smartphone videos
            self.videos = sorted(glob('./datasets/videos/smartphone/*.mp4'))

            # then the gopro videos
            self.videos.append(sorted(glob('./datasets/videos/gopro/*.mp4')))
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

        try:
            # wait till the buffer is empty
            self.buffer.join()
        except:
            # we don't need the stupid EOFError
            pass

        self.logger.info('Video loop ended')


    cdef loop_through_video(self, video_file, calibration_matrix=None):
        self.logger.info('Starting loop for video {}'.format(video_file))
        cdef object cap = cv2.VideoCapture(video_file)

        if (cap.isOpened() == False):
            self.logger.error("Videofile {} not found".format(video_file))
            return

        cdef str filename = basename(video_file), filename_to_emit = None
        cdef int needsCalibration = calibration_matrix is not None

        cdef int success = False
        cdef object frame = None, frame_to_emit = None
        cdef int total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cdef int frame_counter = 0
        cdef int unsharp_counter = 0
        cdef int buffer_initialized = False

        while (cap.isOpened() and frame_counter <= total_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_counter)

            success, frame = cap.read()

            # if no frame was returned, stop processing the video
            if not success:
                self.logger.info('Video {} done'.format(video_file))
                break

            # we read a frame
            self.logger.debug('Read frame {}/{}'.format(frame_counter, total_frames))

            if needsCalibration:
                self.logger.debug('Calibrating frame')
                frame = undistort_frame(frame, params=calibration_matrix)

            if not is_sharp_image(frame, self.blur_threshold):
                self.logger.debug('Frame not sharp enough, skipping!')

                # Try the next frame (if not already 5 unsharp frames seen) when not sharp enough
                unsharp_counter += 1

                if unsharp_counter >= 5:
                    unsharp_counter = 0
                    frame_counter += self.nr_of_frames_to_skip
                else:
                    frame_counter += 1
            else:
                unsharp_counter = 0

            self.logger.debug('Emitting new frame')

            # if the frame is sharp, add it to the buffer
            if unsharp_counter == 0:
                try:
                    self.buffer.put((frame, filename))
                except BrokenPipeError:
                    exit(0)

            # only increment with the skip size when we had a good frame
            frame_counter += self.nr_of_frames_to_skip

        cap.release()

        # the buffer doesn't need to be cleared here, so we can begin processing
        # a new video while still having some leftovers in the buffer
