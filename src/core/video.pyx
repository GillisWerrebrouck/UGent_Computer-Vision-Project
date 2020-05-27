import cv2
from ntpath import basename

from core.cameraCalibration import undistort_frame, get_calibration_matrix
from core.detectBlurredImages import is_sharp_image
from core.logger import get_root_logger

cdef class VideoLoop:

    cdef object logger, calibration_matrix
    cdef int nr_of_frames_to_skip, blur_threshold
    cdef object on_frame
    cdef list videos
    cdef object buffer
    cdef int min_buffer_size
    cdef str video_file

    def __init__(self, buffer, video_file, nr_of_frames_to_skip=30, blur_threshold=100):
        """
        Loop through all videos in the dataset.

        Parameters
        ----------
        - on_frame -- Function that will be called when a frame is fetched.
        - video_file -- Path to the video that needs to be processed.
        - nr_of_frames_to_skip -- The number of frames to skip before fetching a frame (default is 30).
        - blur_threshold -- Threshold of Laplacian before accepting a frame (default is 100).
        """
        self.logger = get_root_logger()
        self.nr_of_frames_to_skip = nr_of_frames_to_skip
        self.blur_threshold = blur_threshold
        self.buffer = buffer
        self.video_file = video_file
        self.calibration_matrix = get_calibration_matrix(
            './datasets/videos/gopro/calibration_M.mp4',
            fov='M'
        ) if "gopro" in self.video_file else None


    cpdef start(self):
        """
        Start the video loop. This function loops through the video given as parameter.
        If the video is completely processed, the loop waits till the buffer is empty
        before exiting.

        Returns
        -------
        Nothing
        """
        self.logger.info('Video loop started')
        self.loop_through_video()

        try:
            # wait till the buffer is empty
            self.buffer.join()
        except EOFError:
            # we don't need this error
            pass

        self.logger.info('Video loop ended')


    cdef loop_through_video(self):
        """
        Loop through this loop's video file, optionally use a calibration matrix per frame.
        This function fills the given buffer with frames until it's full, then it waits
        until the buffer has enough space to add new frames.

        Returns
        -------
        Nothing
        """
        self.logger.info('Starting loop for video {}'.format(self.video_file))
        cdef object cap = cv2.VideoCapture(self.video_file)

        if not cap.isOpened():
            self.logger.error("Videofile {} not found".format(self.video_file))
            return

        cdef str filename = basename(self.video_file), filename_to_emit = None
        cdef int needs_calibration = self.calibration_matrix is not None

        cdef int success = False
        cdef object frame = None, frame_to_emit = None
        cdef int total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cdef int frame_counter = 0
        cdef int unsharp_counter = 0
        cdef int buffer_initialized = False

        while cap.isOpened() and frame_counter <= total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_counter)

            success, frame = cap.read()

            # if no frame was returned, stop processing the video
            if not success:
                self.logger.info('Video {} done'.format(self.video_file))
                break

            # we read a frame
            self.logger.debug('Read frame {}/{}'.format(frame_counter, total_frames))

            if needs_calibration:
                self.logger.debug('Calibrating frame')
                frame = undistort_frame(frame, params=self.calibration_matrix)

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
