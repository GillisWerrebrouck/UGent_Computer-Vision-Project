import cv2

from core.video import loop_through_video
from core.cameraCalibration import get_calibration_matrix
from core.visualize import show_image, resize_image, draw_quadrilaterals_opencv
from core.detection import detect_quadrilaterals

def yihaa(frame):
    print('Got frame')
    frame = resize_image(frame, 0.5)
    quadriliterals = detect_quadrilaterals(frame)
    draw_quadrilaterals_opencv(frame, quadriliterals)
    cv2.imshow('Frame', frame)
    cv2.waitKey(100)

calibration_matrix = get_calibration_matrix(
    './datasets/videos/gopro/calibration_M.mp4',
    fov='M'
)

loop_through_video(
    './datasets/videos/gopro/MSK_13.mp4',
    yihaa,
    # nr_of_frames_to_skip=30,
    blur_threshold=20,
    calibration_matrix=calibration_matrix
)
