import cv2
import multiprocessing
import webview
from functools import partial

from core.video import loop_through_video
from core.cameraCalibration import get_calibration_matrix
from core.visualize import show_image, resize_image, draw_quadrilaterals_opencv
from core.detection import detect_quadrilaterals
from core.hiddenMarkov import HiddenMarkov
from core.prediction import predict_room
from core.floorplan import Floorplan
from core.gracefullKiller import GracefulKiller

hm = HiddenMarkov()

def on_kill(processes):
    for process in processes:
        process.kill()
        process.join()


def load_html(window, input_pipe):
    while True:
        html = input_pipe.recv()

        if html is not None:
            window.load_html(html.decode())


def show_floorplan(input_pipe):
    window = webview.create_window('Floorplan', html='Loading...')
    webview.start(load_html, (window, input_pipe))


def on_frame(fp, frame):
    frame = resize_image(frame, 0.5)
    quadriliterals = detect_quadrilaterals(frame)
    chances = predict_room(frame, quadriliterals)
    chances, room = hm.predict(chances)
    fp.update_rooms(chances, room)
    frame = draw_quadrilaterals_opencv(frame, quadriliterals)
    cv2.imshow('Frame', frame)
    cv2.waitKey(1)


def start_detection(output_pipe):
    fp = Floorplan(output_pipe, 'floorplan.svg', 'MSK_13.mp4')

    calibration_matrix = get_calibration_matrix(
        './datasets/videos/gopro/calibration_M.mp4',
        fov='M'
    )

    loop_through_video(
        './datasets/videos/gopro/MSK_13.mp4',
        partial(on_frame, fp),
        nr_of_frames_to_skip=60,
        blur_threshold=20,
        calibration_matrix=calibration_matrix
    )


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')

    parent_pipe, child_pipe = multiprocessing.Pipe(duplex=False)

    detection = multiprocessing.Process(target=start_detection, args=(child_pipe,))
    floorplan_viewer = multiprocessing.Process(target=show_floorplan, args=(parent_pipe,))

    detection.start()
    floorplan_viewer.start()

    GracefulKiller(partial(on_kill, [detection, floorplan_viewer]))
