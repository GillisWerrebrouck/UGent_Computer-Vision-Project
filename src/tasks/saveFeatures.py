import numpy as np
from glob import glob
from os.path import basename

from core.logger import get_root_logger
from core.extractFeatures import extract_features
from data.imageRepo import get_paintings_for_image, update_by_id
from data.serializer import serialize_keypoints, pickle_serialize

def save_features():
  logger = get_root_logger()
  filenames = glob('./datasets/images/dataset_pictures_msk/zaal_*/*.jpg')

  for path in filenames:
    filename = basename(path)
    paintings_in_image = get_paintings_for_image(filename)

    for painting in paintings_in_image:
      logger.info('Extracting features of image with id {}'.format(painting.get('_id')))
      features = extract_features(path, painting)

      update_by_id(painting.get('_id'), {
        '$set': {
          'keypoints': serialize_keypoints(features['orb']['keypoints'], features['orb']['descriptors']),
          'histograms': {
            'full_histogram': pickle_serialize(features['histograms']['full_histogram']),
            'block_histogram': pickle_serialize(features['histograms']['block_histogram'])
          },
          'good_features': pickle_serialize(features['good_features']),
          'sobel': pickle_serialize(features['sobel'])
        }
      })
