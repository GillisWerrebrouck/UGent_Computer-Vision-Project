import cv2
import numpy as np
from glob import glob
from os.path import basename
import re
import os

from core.logger import get_root_logger
from core.fileIO import createFolders, createFile, appendFile
from core.detection import detect_quadrilaters
from core.visualize import resize_image, show_image, draw_quadrilaterals_opencv
from core.prediction import predict_room

logger = get_root_logger()


# TODO: add possibility to run prediction on video frames
def run_task_03(dataset_folder='dataset_pictures_msk', show=True):
  if dataset_folder == 'dataset_pictures_msk':
    filename = createFile('./results/task2/dataset_pictures_msk_prediction')

  filenames = glob('./datasets/images/' + dataset_folder + '/zaal_*/*.jpg')

  for f in filenames:
    original_image = cv2.imread(f, 1)
    original_image = resize_image(original_image, 0.2)
    image = original_image.copy()
    detected_paintings = detect_quadrilaters(image)

    probabilities = predict_room(original_image, detected_paintings)

    match = re.search(r'zaal_(.+)', os.path.dirname(f))
    room = match.group(1)

    for painting_probabilities in probabilities:
      # ignore if no probabilities for a detected painting (possibly no match above given threshold)
      if 0 == len(painting_probabilities): continue

      max_probability = painting_probabilities[0]

      appendFile(filename, f + '\n')

      log = "probability: {}".format(max_probability[0])
      logger.info(log)
      appendFile(filename, log + '\n')

      log = "probably image: {}".format(max_probability[1])
      logger.info(log)
      appendFile(filename, log + '\n')

      log = "probably room: {}".format(max_probability[2])
      logger.info(log)
      appendFile(filename, log + '\n')
      log = "correct room: {}".format(room)
      logger.info(log)
      appendFile(filename, log + '\n\n')

    detection_image = draw_quadrilaterals_opencv(image, detected_paintings)

    if show:
      show_image(f, detection_image)
