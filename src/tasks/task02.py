import cv2
import numpy as np
from glob import glob
from os.path import basename

from core.logger import get_root_logger
from core.detection import detect_quadrilaters
from core.visualize import resize_image, show_image, draw_quadrilaterals_opencv
from data.imageRepo import get_paintings_for_image
from core.accuracyHelperFunctions import calculate_bounding_box_accuracy
from core.prediction import predict_room

logger = get_root_logger()


def run_task_02():
  filenames = glob('./datasets/images/dataset_pictures_msk/zaal_*/*.jpg')

  false_negatives_sum = 0
  false_positives_sum = 0
  average_accuracy_sum = 0
  count = 0

  for f in filenames:
    original_image = cv2.imread(f, 1)
    original_image = resize_image(original_image, 0.2)
    image = original_image.copy()
    quadrilaterals = detect_quadrilaters(image)
    result = get_paintings_for_image(basename(f))

    (height, width) = image.shape[:2]
    false_positives = 0
    false_negatives = 0
    paintings_found = 0
    average_accuracy = 0
    for q1 in result:
      q1_corners = q1.get('corners')
      area = 0
      for point in q1_corners:
        point[0] = point[0]*width
        point[1] = point[1]*height
      
      for q2 in quadrilaterals:
        q2 = np.reshape(q2, (4, 2)).astype(np.float32)

        # draw ground truth quadrilaterals on image
        image = draw_quadrilaterals_opencv(image, [np.asarray(q1_corners).astype(np.int32)], (255, 0, 0))
        accuracy = calculate_bounding_box_accuracy(q1_corners, q2)
        if(area < accuracy):
          area = accuracy
      if(area <= 0.001):  # none found -> false positive
        false_negatives += 1
      else: # one found, increase average accuracy
        # TODO: check on duplicates, remove from result?
        paintings_found += 1
        average_accuracy += area

    # average accuracy dividing by amount found + calculating the amount of false nefatives 
    # division by 1 is not needed
    if paintings_found > 1:
      average_accuracy /= paintings_found
    if len(quadrilaterals) >= paintings_found:
      false_positives = len(quadrilaterals) - paintings_found

    # might give non correct result if a quadrilateral contains more than 1 painting!
    logger.info("# of false negatives: {}".format(false_negatives))
    logger.info("# of false positives: {}".format(false_positives))
    logger.info("average bounding box accuracy: {}".format(average_accuracy))

    false_negatives_sum += false_negatives
    false_positives_sum += false_positives
    average_accuracy_sum += average_accuracy
    count += 1

    predict_room(original_image, quadrilaterals)
    detection_image = draw_quadrilaterals_opencv(image, quadrilaterals)
    show_image(f, detection_image)
  
  logger.info("SUMMARY:")
  logger.info("total # of false negatives: {}".format(false_negatives_sum))
  logger.info("total # of false positives: {}".format(false_positives_sum))
  logger.info("average bounding box accuracy: {}".format(average_accuracy_sum/count))
