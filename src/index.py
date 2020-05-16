import cv2
import PySimpleGUI as sg
from functools import partial

from core.visualize import get_window
from tasks.task01 import run_task_01
from tasks.task02 import run_task_02
from tasks.task03 import run_task_03, run_task_03_uniqueness

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
]
window = get_window('Tasks', layout)

switcher = {
  'Run task 1': run_task_01,
  'Run task 2 (dataset pictures)': run_task_02,
  'Run task 2 (test pictures)': run_task_02,
  'Run task 3 (uniqueness)': run_task_03_uniqueness,
  'Run task 3 (dataset pictures)': run_task_03,
  'Run task 3 (test pictures)': run_task_03,
}

param_switcher = {
  'Run task 2 (dataset pictures)': ('dataset_pictures_msk', False, True),
  'Run task 2 (test pictures)': ('test_pictures_msk', False, True),
  'Run task 3 (uniqueness)': (False, True),
  'Run task 3 (dataset pictures)': ('dataset_pictures_msk', False, True),
  'Run task 3 (test pictures)': ('test_pictures_msk', False, True),
}

# event loop of the main window
while True:
  event, values = window.Read()

  task = switcher.get(event)
  params = param_switcher.get(event)
  if task is not None:
    window.close()
    if params is not None:
      task(*params)
    else:
      task()
    break

  if event == None:
    break

window.close()
