import cv2
from glob import glob

from data.imageRepo import get_all_images
from core.prediction import predict_room

filenames = sorted(glob('./datasets/images/test_pictures_msk/*.jpg'))

for file in filenames:
    print(file)
    img = cv2.imread(file)
    predict_room(img)
