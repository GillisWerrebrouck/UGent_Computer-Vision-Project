import cv2
from glob import glob

from core.detection import detect_quadrilaters
from core.visualize import resize_image, show_image, draw_quadrilaterals_opencv
from data.imageRepo import get_paintings_for_image


def run_task_02():
  filenames = glob('./datasets/images/dataset_pictures_msk/zaal_*/*.jpg')

  for f in filenames:
    image = cv2.imread(f, 1)
    image = resize_image(image, 0.2)
    quadrilaterals = detect_quadrilaters(image)
    image = draw_quadrilaterals_opencv(image, quadrilaterals)
    result = get_paintings_for_image(f.split('/')[-1])
    print('found: ' , str(len(quadrilaterals)) , ' - from: ' , str(result.count()))
    # show_image("SMEH", image)
