import pyximport
pyximport.install(language_level='3')

import cv2
import multiprocessing
import base64
import webview
from functools import partial

from core.video import VideoLoop
from core.visualize import show_image, resize_image, draw_quadrilaterals_opencv
from core.detection import detect_quadrilaterals
from core.hiddenMarkov import HiddenMarkov
from core.prediction import predict_room, prepare_prediction
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

        quadriliterals, frame, video_file = input_pipe.recv()
        chances = predict_room(frame, quadriliterals)
        print('read data')

        chances, room = hm.predict(chances)

        ret, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode()
        html = fp.update_rooms(chances, room, jpg_as_text, video_file)


def show_floorplan(input_pipe):
    window = webview.create_window('Floorplan', html='Loading...', width=800, height=700, frameless=True)
    webview.start(load_html, (window, input_pipe))


def on_frame(output_pipe, frame, video_file):
    frame = resize_image(frame, 0.5)
    quadriliterals = detect_quadrilaterals(frame)
    frame = draw_quadrilaterals_opencv(frame, quadriliterals)
    output_pipe.send((quadriliterals, frame, video_file))


def start_detection(output_pipe):
    prepare_prediction()
    video_loop = VideoLoop(on_frame=partial(on_frame, output_pipe), nr_of_frames_to_skip=1000, blur_threshold=10)
    video_loop.start()


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')

    parent_pipe, child_pipe = multiprocessing.Pipe(duplex=False)

    detection = multiprocessing.Process(target=start_detection, args=(child_pipe,))
    floorplan_viewer = multiprocessing.Process(target=show_floorplan, args=(parent_pipe,))

    GracefulKiller([detection, floorplan_viewer])
