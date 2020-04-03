import cv2
import sys
from data.connect import connect_mongodb_database
from core.visualize import show_image

mydb = connect_mongodb_database('localhost', 27017, 'computervision', 'devuser', 'devpwd')
print(mydb.list_collection_names())

# Python fucks with the current directory as it's not equal to this file's current directory.
# So be sure to start the script from the src-folder if you don't want this shit.
img = cv2.imread('rays.png')
show_image('Rays', img)
