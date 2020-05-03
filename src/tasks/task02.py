import cv2
import numpy as np
from glob import glob
from os.path import basename

from core.detection import detect_quadrilaters
from core.visualize import resize_image, show_image, draw_quadrilaterals_opencv
from data.imageRepo import get_paintings_for_image
from core.accuracyHelperFunctions import calculate_bounding_box_accuracy


def run_task_02():
  filenames = glob('./datasets/images/dataset_pictures_msk/zaal_*/*.jpg')

  false_negatives_sum = 0
  false_positives_sum = 0
  average_accuracy_sum = 0
  count = 0

  for f in filenames:
    image = cv2.imread(f, 1)
    image = resize_image(image, 0.2)
    quadrilaterals = detect_quadrilaters(image)
    image = draw_quadrilaterals_opencv(image, quadrilaterals)
    result = get_paintings_for_image(basename(f)) 
    # todo: maybe just fetch the corners
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
      if(area <= 0.001):  # none found -> false positive
        false_negatives += 1
      else: # one found, increase average accuracy
        # TODO: check on duplicates, remove from result?
        paintings_found += 1
        average_accuracy += area
        if area == 0:
          false_positives += 1

    # average accuracy dividing by amount found + calculating the amount of false nefatives 
    # division by 1 is not needed
    if paintings_found > 1:
      average_accuracy /= paintings_found
    if len(quadrilaterals) >= paintings_found:
      false_positives = len(quadrilaterals) - paintings_found

    # might give non correct result if a quadrilateral contains more than 1 painting!
    print("# of false negatives: ", false_negatives)
    print("# of false positives: ", false_positives)
    print("average bounding box accuracy: ", average_accuracy)

    false_negatives_sum += false_negatives
    false_positives_sum += false_positives
    average_accuracy_sum += average_accuracy
    count += 1

    show_image(f, image)

  print("SUMMARY:")
  print("total # of false negatives: ", false_negatives_sum)
  print("total # of false positives: ", false_positives_sum)
  print("average bounding box accuracy: ", average_accuracy_sum/count)
