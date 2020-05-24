import pyximport
pyximport.install(language_level='3')

import cv2
from glob import glob
import re
import os
import pickle
import json

from core.logger import get_root_logger
from data.imageRepo import get_all_images, get_painting_count_by_room
from core.detection import detect_quadrilaterals
from core.visualize import resize_image
from core.prediction import predict_room

logger = get_root_logger()


def run_room_calibration():
  filenames = glob('./datasets/images/dataset_pictures_msk/zaal_*/*.jpg')

  probability_per_room = {} # key -> room, value -> count & average probability for the room

  for f in filenames:
    original_image = cv2.imread(f, 1)
    resized_image = resize_image(original_image, 0.2)
    image = resized_image.copy()
    detected_paintings = detect_quadrilaterals(image)

    probabilities = predict_room(resized_image, detected_paintings, 0.5)

    match = re.search('(z|Z)aal_(.+)$', os.path.dirname(f))
    room = match.group(2)

    if room not in probability_per_room:
      probability_per_room[room] = (0, 0)

    for painting_probabilities in probabilities:
      index = 0

      while index < len(painting_probabilities) and painting_probabilities[index][2] != room: index+=1

      probability = 0
      if index < len(painting_probabilities):
        probability = painting_probabilities[index][0]

      new_count = probability_per_room[room][0] + 1
      new_avg_probability = ((probability_per_room[room][0] * probability_per_room[room][1]) + probability) / new_count
      probability_per_room[room] = (new_count, new_avg_probability)
      
      logger.info("room: " + room + ", probability: " + str(probability))

  for room in probability_per_room:
    actual_number_of_paintings_in_room = get_painting_count_by_room(room)
    new_prob = probability_per_room[room][1] * probability_per_room[room][0] / actual_number_of_paintings_in_room
    if 1 < new_prob:
      new_prob = 1

    probability_per_room[room] = (actual_number_of_paintings_in_room, new_prob)

  with open('room_calibrations.pickle', 'wb') as handle:
    pickle.dump(probability_per_room, handle, protocol=pickle.HIGHEST_PROTOCOL)

  logger.info("Room calibrations: " + str(json.dumps(probability_per_room)))
