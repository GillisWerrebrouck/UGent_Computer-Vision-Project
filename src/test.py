import pyximport
pyximport.install(language_level='3')

import cv2
import multiprocessing
import base64
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
from core.transitions import transitions

def load_html(window, input_pipe):
    hm = HiddenMarkov()
    fp = Floorplan('floorplan.svg', 'MSK_15.mp4')
    html = fp.tostring()

    while True:
        if html is not None:
            window.load_html(html.decode())

        quadriliterals, frame = input_pipe.recv()
        chances = predict_room(frame, quadriliterals)
        print('read data')

        chances, room = hm.predict(chances)

        ret, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode()
        html = fp.update_rooms(chances, room, jpg_as_text)


def show_floorplan(input_pipe):
    window = webview.create_window('Floorplan', html='Loading...', width=800, height=700, frameless=True)
    webview.start(load_html, (window, input_pipe))


def on_frame(output_pipe, frame):
    frame = resize_image(frame, 0.5)
    quadriliterals = detect_quadrilaterals(frame)
    frame = draw_quadrilaterals_opencv(frame, quadriliterals)
    output_pipe.send((quadriliterals, frame))


def start_detection(output_pipe):
    calibration_matrix = get_calibration_matrix(
        './datasets/videos/gopro/calibration_M.mp4',
        fov='M'
    )

    loop_through_video(
        './datasets/videos/gopro/MSK_15.mp4',
        partial(on_frame, output_pipe),
        nr_of_frames_to_skip=60,
        blur_threshold=10,
        calibration_matrix=calibration_matrix
    )


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')

    parent_pipe, child_pipe = multiprocessing.Pipe(duplex=False)

    detection = multiprocessing.Process(target=start_detection, args=(child_pipe,))
    floorplan_viewer = multiprocessing.Process(target=show_floorplan, args=(parent_pipe,))

    GracefulKiller([detection, floorplan_viewer])
