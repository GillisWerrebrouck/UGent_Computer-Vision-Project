import cv2
import sys
import glob
from data.connect import connect_mongodb_database
from core.visualize import show_image, resize_image
from core.detection import detect_corners, detect_corners2
from core.filter import apply_filters

mydb = connect_mongodb_database('localhost', 27017, 'computervision', 'devuser', 'devpwd')
print(mydb.list_collection_names())

# Python fucks with the current directory as it's not equal to this file's current directory.
# So be sure to start the script from the src-folder if you don't want this shit.
# show_image('Rays', img)

for filename in glob.glob('./dataset_pictures_msk/*/*.jpg'):
  img = cv2.imread(filename)
  img = apply_filters(img)
  # detect_corners(img)
  # detect_corners2(img)
  img = resize_image(img, 0.2)
  show_image('test', img)
