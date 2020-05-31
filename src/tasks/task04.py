import pyximport
pyximport.install(language_level='3')

import cv2
import multiprocessing
import base64
import webview

from core.logger import get_root_logger
from core.video import VideoLoop
from core.visualize import resize_image, draw_quadrilaterals_opencv
from core.detection import detect_quadrilaterals
from core.hiddenMarkov import HiddenMarkov
from core.prediction import predict_room, prepare_prediction
from core.floorplan import Floorplan
from core.gracefullKiller import GracefulKiller

logger = get_root_logger()


def load_html(window, input_pipe):
    hm = HiddenMarkov(min_observations=5)
    fp = Floorplan('floorplan.svg', '')
    if fp is not None:
        html = fp.tostring()

    while input_pipe.readable:
        if html is not None:
            try:
                window.load_html(html.decode())
            except KeyError:
                exit(0)

        quadriliterals, frame, video_file = input_pipe.recv()
        chances = predict_room(frame, quadriliterals, 0.7)
        chances, room = hm.predict(chances)

        frame = draw_quadrilaterals_opencv(frame, quadriliterals, 4)
        ret, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode()
        html = fp.update_rooms(chances, room, jpg_as_text, video_file)


def show_floorplan(input_pipe):
    prepare_prediction()
    window = webview.create_window('Floorplan', html='Loading...', width=800, height=700, frameless=False)
    webview.start(load_html, (window, input_pipe))


def on_frame(output_pipe, frame, video_file):
    compression_factor = 0.2

    frame_copy = resize_image(frame, compression_factor)
    quadriliterals = detect_quadrilaterals(frame_copy)

    for quadriliteral in quadriliterals:
        for point in quadriliteral:
            point[0][0] *= 1/compression_factor
            point[0][1] *= 1/compression_factor

    if output_pipe.writable:
        output_pipe.send((quadriliterals, frame, video_file))
    else:
        exit(0)


def start_video_loop(frames_queue):
    video_loop = VideoLoop(buffer=frames_queue, nr_of_frames_to_skip=20, blur_threshold=10,
    video_file="./datasets/videos/smartphone/MSK_08.mp4")
    video_loop.start()


def start_detection(output_pipe, frames_queue):
    # wait for the first value to arrive
    frame, filename = frames_queue.get()
    on_frame(output_pipe, frame, filename)

    # then wait till the queue is empty
    while not frames_queue.empty():
        frame, filename = frames_queue.get()
        on_frame(output_pipe, frame, filename)


def run_task_04():
    multiprocessing.set_start_method('spawn')

    parent_pipe, child_pipe = multiprocessing.Pipe(duplex=False)
    manager = multiprocessing.Manager()
    frames_queue = manager.Queue(30)

    detection = multiprocessing.Process(target=start_detection, args=(child_pipe,frames_queue))
    videoloop = multiprocessing.Process(target=start_video_loop, args=(frames_queue,))
    floorplan_viewer = multiprocessing.Process(target=show_floorplan, args=(parent_pipe,))

    GracefulKiller([videoloop, detection, floorplan_viewer])
