import cv2
from glob import glob
import numpy as np

from core.detection import detect_quadrilaters
from core.visualize import resize_image, show_image, draw_quadrilaterals_opencv
from data.imageRepo import get_paintings_for_image
from core.accuracyHelperFunctions import calculate_bounding_box_accuracy


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
    false_positives = 0
    false_negatives = 0
    paintings_found = 0
    average_accuracy = 0
    for q1 in result:
      area = 0
      for q2 in quadrilaterals: 
        q2 = np.reshape(q2, (4, 2)).astype(np.float32)
        for point in q2:
          point[0] = point[0]/width
          point[1] = point[1]/height
        accuracy = calculate_bounding_box_accuracy(q1.get('corners'), q2)
        if(area < accuracy):
          area = accuracy
      if(area <= 0.001):  # geen gevonden -> false positive
        false_negatives += 1
      else: # wel een gevonden, average accuracy verhogen
        paintings_found += 1
        average_accuracy += area

    # average accuracy delen door aantal gevonden + aantal false negatives uitrekenen
    # delen door 1 is nutteloos
    if(paintings_found > 1):
      average_accuracy /= paintings_found
    false_positives = len(quadrilaterals) - paintings_found

    print("false negatives: ", false_negatives)
    print("false positives: ", false_positives)
    print("average bounding box accuracy: ", average_accuracy)
    
    show_image("DOBRA DOBRA", image)
