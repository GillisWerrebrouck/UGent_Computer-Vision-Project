import cv2
import PySimpleGUI as sg

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
    [sg.Text('Choose a task')],
    [sg.Button('Task 1')],
]
window = get_window('Tasks', layout)


# event loop of the main window
while True:
  event, values = window.Read()

  if event == 'Task 1':
    window.close()
    run_task_01(db_connection)

  if event == None:
    break

window.close()
