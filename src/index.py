import cv2
import PySimpleGUI as sg
from functools import partial

from data.connect import connect_mongodb_database
from core.visualize import get_window
from tasks.task01 import run_task_01


# create database connection
db_connection = connect_mongodb_database('localhost', 27017, 'computervision', 'devuser', 'devpwd')
print(db_connection.list_collection_names())

if (db_connection == None):
  exit(-1)


# create a window with all tasks listed and set theme
sg.theme('DefaultNoMoreNagging')
layout = [
    [sg.Text('Choose a task', font=('Helvetica', 12, ''))],
    [sg.Button('Run task 1', font=('Helvetica', 10, ''))],
    [sg.Button('Run task 2', font=('Helvetica', 10, ''))],
    [sg.Button('Run task 3', font=('Helvetica', 10, ''))],
    [sg.Button('Run task 4', font=('Helvetica', 10, ''))],
]
window = get_window('Tasks', layout)

switcher = {
  'Run task 1': partial(run_task_01, db_connection),
}

# event loop of the main window
while True:
  event, values = window.Read()

  task = switcher.get(event)
  if task is not None:
    window.close()
    task()
    break

  if event == None:
    break

window.close()
