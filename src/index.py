import cv2
import PySimpleGUI as sg
from functools import partial

from core.visualize import get_window
from tasks.task01 import run_task_01
from tasks.task02 import run_task_02
from core.detectKeypoints import run
from data.imageRepo import get_image_by_id
from data.serializeKeypoints import deserialize_keypoints

image = get_image_by_id('5e970960b5527c95502fd0e5')

tmp = image.get('keypoints')[0]
print(deserialize_keypoints(tmp))

# run()

# create a window with all tasks listed and set theme
# sg.theme('DefaultNoMoreNagging')
# layout = [
#     [sg.Text('Choose a task', font=('Helvetica', 12, ''))],
#     [sg.Button('Run task 1', font=('Helvetica', 10, ''))],
#     [sg.Button('Run task 2', font=('Helvetica', 10, ''))],
#     [sg.Button('Run task 3', font=('Helvetica', 10, ''))],
#     [sg.Button('Run task 4', font=('Helvetica', 10, ''))],
# ]
# window = get_window('Tasks', layout)

# switcher = {
#   'Run task 1': run_task_01,
#   'Run task 2': run_task_02,
# }

# # event loop of the main window
# while True:
#   event, values = window.Read()

#   task = switcher.get(event)
#   if task is not None:
#     window.close()
#     task()
#     break

#   if event == None:
#     break

# window.close()
