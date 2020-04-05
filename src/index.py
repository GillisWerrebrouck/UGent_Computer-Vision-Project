import cv2
import sys
import glob
from data.connect import connect_mongodb_database
from core.visualize import show_image, resize_image
from core.filter import apply_filters

mydb = connect_mongodb_database('localhost', 27017, 'computervision', 'devuser', 'devpwd')
print(mydb.list_collection_names())

if (mydb == None):
  exit(-1)

for filename in glob.glob('./dataset_pictures_msk/*/*.jpg'):
  img = cv2.imread(filename)
  img = resize_image(img, 0.2)
  img = apply_filters(img)
  show_image('test', img)
