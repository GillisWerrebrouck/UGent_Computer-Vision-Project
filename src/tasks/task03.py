import cv2
import numpy as np
from glob import glob
from os.path import basename
import re
import os

from core.logger import get_root_logger
from data.imageRepo import get_all_images
from core.fileIO import createFolders, createFile, appendFile
from core.detection import detect_quadrilaterals
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
    detected_paintings = detect_quadrilaterals(image)

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


def run_task_03_uniqueness(show=True, save=True):
  imagesFromDB = get_all_images({
    'filename': 1,
    'room': 1,
    'corners': 1
  })

  correct_matchings = 0
  total_matchings = 0
  average_probability = 0

  if save:
    filename = createFile('./results/task3/dataset_pictures_msk_uniqueness')
  
  dataset_folder = './datasets/images/dataset_pictures_msk'

  for imageFromDB in imagesFromDB:
    path = dataset_folder + '/zaal_' + imageFromDB['room'] + '/' + imageFromDB['filename']
    original_image = cv2.imread(path, 1)
    original_image = resize_image(original_image, 0.2)
    (height, width) = original_image.shape[:2]

    corners = imageFromDB.get('corners')
    for point in corners:
      point[0] = point[0]*width
      point[1] = point[1]*height

    detected_paintings = [np.asarray(corners).astype(np.int32)]

    if show:
      detected_image = draw_quadrilaterals_opencv(original_image, detected_paintings)
      show_image(imageFromDB['filename'], detected_image)

    probabilities = predict_room(original_image, detected_paintings, 0)

    total_matchings += 1
    if 0 == len(probabilities): continue

    max_probability = probabilities[0]
    
    if max_probability[0] is not None and max_probability[0][1] == imageFromDB['filename']:
      correct_matchings += 1
      average_probability += max_probability[0][0]

      log = "image: {}".format(imageFromDB['filename'])
      logger.info(log)
      if save:
        appendFile(filename, log + '\n')

      log = "probability: {}".format(max_probability[0][0])
      logger.info(log)
      if save:
        appendFile(filename, log + '\n\n')

  log = "SUMMARY"
  logger.info(log)
  if save:
    appendFile(filename, log + '\n')

  log = "total # of correct painting matchings: {}/{}".format(correct_matchings, total_matchings)
  logger.info(log)
  if save:
    appendFile(filename, log + '\n')

  log = "average probability: {}".format(average_probability/total_matchings)
  logger.info(log)
  if save:
    appendFile(filename, log)
