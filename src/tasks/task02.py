import cv2
from glob import glob
import numpy as np

from core.detection import detect_quadrilaters
from core.visualize import resize_image, show_image, draw_quadrilaterals_opencv
from data.imageRepo import get_paintings_for_image
from core.accuracyHelperFunctions import calculate_intersection


def run_task_02():
  filenames = glob('./datasets/images/dataset_pictures_msk/zaal_*/*.jpg')

  for f in filenames:
    image = cv2.imread(f, 1)
    image = resize_image(image, 0.2)
    quadrilaterals = detect_quadrilaters(image)
    image = draw_quadrilaterals_opencv(image, quadrilaterals)
    result = get_paintings_for_image(f.split('/')[-1])
    print('found: ' , str(len(quadrilaterals)) , ' - from: ' , str(result.count()))
    (height, width) = image.shape[:2]
    print(height, width)
    for q1 in result:
      for q2 in quadrilaterals: 
        print('q2 original: ', q2)
        q2 = np.reshape(q2, (2, 3))
        print('q2 flatted: ', q2)
        # for point in q2:
        #   point[0] = float(point[0])/width
        #   point[1] = float(point[1])/height
        print('q2 calculated: ', q2)
        intersection = calculate_intersection(q1.get('corners'), q2)
        
    # break
    show_image("SMEH", image)
