import PySimpleGUI as sg
from functools import partial

from core.visualize import get_window
from tasks.task01 import run_task_01
from tasks.task02 import run_task_02
from tasks.task03 import run_task_03, run_task_03_uniqueness
from tasks.saveFeatures import save_features
from tasks.room_calibration import run_room_calibration

# create a window with all tasks listed and set theme
sg.theme('DefaultNoMoreNagging')
layout = [
    [sg.Text('Choose a task', font=('Helvetica', 12, ''))],
    [sg.Button('Run task 1', font=('Helvetica', 10, ''))],
    [sg.Button('Run task 2 (dataset pictures)', font=('Helvetica', 10, ''))],
    [sg.Button('Run task 2 (test pictures)', font=('Helvetica', 10, ''))],
    [sg.Button('Run task 3 (uniqueness)', font=('Helvetica', 10, ''))],
    [sg.Button('Run task 3 (dataset pictures)', font=('Helvetica', 10, ''))],
    [sg.Button('Run task 3 (test pictures)', font=('Helvetica', 10, ''))],
    [sg.Button('Save features (no task)', font=('Helvetica', 10, ''))],
    [sg.Button('Calibrate rooms (no task)', font=('Helvetica', 10, ''))],
]
window = get_window('Tasks', layout)

switcher = {
  'Run task 1': run_task_01,
  'Run task 2 (dataset pictures)': partial(run_task_02, 'dataset_pictures_msk', True, True),
  'Run task 2 (test pictures)': partial(run_task_02, 'test_pictures_msk', True, True),
  'Run task 3 (uniqueness)': partial(run_task_03_uniqueness, True, True),
  'Run task 3 (dataset pictures)': partial(run_task_03, 'dataset_pictures_msk', True, True),
  'Run task 3 (test pictures)': partial(run_task_03, 'test_pictures_msk', True, True),
  'Save features (no task)': save_features,
  'Calibrate rooms (no task)': run_room_calibration
}

# event loop of the main window
while True:
  event, values = window.Read()

  task = switcher.get(event)
  if task is not None:
    window.close()
    task()
    break

  if event is None:
    break

window.close()
