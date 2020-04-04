import cv2
import sys
import glob
from data.connect import connect_mongodb_database
from core.visualize import show_image, resize_image
from core.detection import detect_corners, detect_corners2, detect_corners3
from core.filter import apply_grayscale_for_painting_detection
from glob import glob

mydb = connect_mongodb_database('localhost', 27017, 'computervision', 'devuser', 'devpwd')
print(mydb.list_collection_names())

if (mydb == None):
  exit(-1)

# Difficult one: ../../data/images/dataset_pictures_msk/Zaal_A/20190323_111950.jpg
for filename in sorted(glob('../../data/images/dataset_pictures_msk/**/*.jpg')):
  img = cv2.imread(filename)
  img = detect_corners3(img)
  img = resize_image(img, 0.2)
  show_image('test', img)
