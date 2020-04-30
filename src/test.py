import cv2
from glob import glob

from core.visualize import show_image, resize_image

filenames = sorted(glob('./datasets/images/test_pictures_msk/*.jpg'))

for file in filenames:
    print(file)
    img = cv2.imread(file)
    # predict_room(img)
    # grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = cv2.bilateralFilter(img, 1, 10, 120)
    show_image('test', resize_image(img, 0.2))

