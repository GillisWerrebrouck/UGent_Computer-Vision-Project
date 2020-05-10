import cv2
import numpy as np
from glob import glob
from os.path import basename

from core.logger import get_root_logger
from core.fileIO import createFolders, createFile, appendFile
from core.detection import detect_quadrilaterals, calculate_accuracy_metrics
from core.visualize import resize_image, show_image, draw_quadrilaterals_opencv
from data.imageRepo import get_paintings_for_image
from core.prediction import predict_room

logger = get_root_logger()


# TODO: add possibility to run detection on video frames
def run_task_02(dataset_folder='dataset_pictures_msk', show=True, save=True):
  if dataset_folder == 'dataset_pictures_msk' and save:
    filename = createFile('./results/task2/dataset_pictures_msk_detection')

  filenames = glob('./datasets/images/' + dataset_folder + '/zaal_*/*.jpg')

  false_negatives_sum = 0
  false_positives_sum = 0
  average_accuracy_sum = 0
  count = 0

  for f in filenames:
    original_image = cv2.imread(f, 1)
    original_image = resize_image(original_image, 0.2)
    image = original_image.copy()
    ground_truth_paintings = get_paintings_for_image(basename(f))
    detected_paintings = detect_quadrilaterals(image)

    (image, paintings_found, false_negatives, false_positives, average_accuracy) = calculate_accuracy_metrics(image, ground_truth_paintings, detected_paintings)

    if dataset_folder == 'dataset_pictures_msk':
      if save:
        appendFile(filename, f + '\n')

      log = "# of false negatives: {}".format(false_negatives)
      logger.info(log)
      if save:
        appendFile(filename, log + '\n')
    
      log = "# of false positives: {}".format(false_positives)
      logger.info(log)
      if save:
        appendFile(filename, log + '\n')
    
      log = "average bounding box accuracy: {}".format(average_accuracy)
      logger.info(log)
      if save:
        appendFile(filename, log + '\n\n')

      false_negatives_sum += false_negatives
      false_positives_sum += false_positives
      average_accuracy_sum += average_accuracy
      count += 1

    detection_image = draw_quadrilaterals_opencv(image, detected_paintings)

    if show:
      show_image(f, detection_image)

    if save:
      path = './results/task2/' + dataset_folder + '/' + basename(f)
      createFolders(path)
      cv2.imwrite(path, detection_image)

  if dataset_folder == 'dataset_pictures_msk':
    log = "SUMMARY"
    logger.info(log)
    if save:
      appendFile(filename, log + '\n')

    log = "total # of false negatives: {}".format(false_negatives_sum)
    logger.info(log)
    if save:
      appendFile(filename, log + '\n')

    log = "total # of false positives: {}".format(false_positives_sum)
    logger.info(log)
    if save:
      appendFile(filename, log + '\n')

    log = "average bounding box accuracy: {}".format(average_accuracy_sum/count)
    logger.info(log)
    if save:
      appendFile(filename, log)
