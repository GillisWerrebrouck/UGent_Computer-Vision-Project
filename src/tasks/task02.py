import cv2
from glob import glob

from core.detection import detect_quadrilaters
from core.visualize import resize_image, show_image


def run_task_02():
  filenames = glob('./datasets/images/dataset_pictures_msk/zaal_*/*.jpg')

  for f in filenames:
    image = cv2.imread(f, 1)
    image = resize_image(image, 0.2)
    image = detect_quadrilaters(image)
    show_image("TEST", image)
