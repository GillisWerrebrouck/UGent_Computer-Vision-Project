import cv2
import sys
from data.connect import connect_mongodb_database
from core.visualize import show_image

mydb = connect_mongodb_database('localhost', 27017, 'computervision', 'devuser', 'devpwd')
if (mydb == None):
  exit(-1)
