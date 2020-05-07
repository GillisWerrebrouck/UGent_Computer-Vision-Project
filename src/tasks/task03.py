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
def run_task_03(dataset_folder='dataset_pictures_msk', show=True, save=True):
  if save:
    filename = createFile('./results/task3/' + dataset_folder + '_prediction')

  filenames = glob('./datasets/images/' + dataset_folder + '/zaal_*/*.jpg')

  correct_image_predictions = 0
  correct_room_predictions = 0
  total_predictions = 0

  for f in filenames:
    original_image = cv2.imread(f, 1)
    original_image = resize_image(original_image, 0.2)
    image = original_image.copy()
    detected_paintings = detect_quadrilaters(image)

    probabilities = predict_room(original_image, detected_paintings)

    match = re.search('(z|Z)aal_(.+)$', os.path.dirname(f))
    room = match.group(2)
    image_filename =  os.path.basename(f)

    for painting_probabilities in probabilities:
      total_predictions += 1

      # ignore if no probabilities for a detected painting (possibly no match above given threshold)
      if 0 == len(painting_probabilities): continue

      max_probability = painting_probabilities[0]

      # only sure about the correctness of the predicted image with the dataset_pictures_msk set
      if dataset_folder == 'dataset_pictures_msk':
        if image_filename == max_probability[1]:
          correct_image_predictions += 1

      # always sure about the correctness of the predicted room due to the folder structure
      if room == max_probability[2]:
        correct_room_predictions += 1

      if save:
        appendFile(filename, f + '\n')

      log = "probability: {}".format(max_probability[0])
      logger.info(log)
      if save:
        appendFile(filename, log + '\n')

      log = "predicted image: {}".format(max_probability[1])
      logger.info(log)
      if save:
        appendFile(filename, log + '\n')

      log = "actual image: {}".format(image_filename)
      logger.info(log)
      if save:
        appendFile(filename, log + '\n')

      log = "predicted room: {}".format(max_probability[2])
      logger.info(log)
      if save:
        appendFile(filename, log + '\n')

      log = "correct room: {}".format(room)
      logger.info(log)
      if save:
        appendFile(filename, log + '\n\n')

    detection_image = draw_quadrilaterals_opencv(image, detected_paintings)

    if show:
      show_image(f, detection_image)
  
  log = "SUMMARY"
  logger.info(log)
  if save:
    appendFile(filename, log + '\n')

  if dataset_folder == 'dataset_pictures_msk':
    log = "total # of correct painting predictions: {}/{}".format(correct_image_predictions, total_predictions)
    logger.info(log)
    if save:
      appendFile(filename, log + '\n')

  log = "total # of correct room predictions: {}/{}".format(correct_room_predictions, total_predictions)
  logger.info(log)
  if save:
    appendFile(filename, log)
