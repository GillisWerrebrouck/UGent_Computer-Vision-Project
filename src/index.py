import cv2
import sys
import glob
from data.connect import connect_mongodb_database
from core.visualize import show_image
from core.detection import detect_paintings

mydb = connect_mongodb_database('localhost', 27017, 'computervision', 'devuser', 'devpwd')
print(mydb.list_collection_names())

if (mydb == None):
  exit(-1)

for filename in glob.glob('./dataset_pictures_msk/*/*.jpg'):
  image = cv2.imread(filename)
  image = detect_paintings(image)
  show_image('test', image)
