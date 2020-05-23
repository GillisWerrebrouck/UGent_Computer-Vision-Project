import cv2
import numpy as np
from glob import glob
from os.path import basename

from core.logger import get_root_logger
from core.extractFeatures import extract_features
from data.imageRepo import get_paintings_for_image, update_by_id
from data.serializer import pickle_serialize

def save_features():
    logger = get_root_logger()
    filenames = glob('./datasets/images/dataset_pictures_msk/zaal_*/*.jpg')
    total = len(filenames)
    count = 0

    for path in filenames:
        image = cv2.imread(path)
        filename = basename(path)
        count += 1
        paintings_in_image = get_paintings_for_image(filename)

        for painting in paintings_in_image:
            logger.info('Extracting features of image with id {}'.format(
                painting.get('_id')))
            full_histogram, block_histogram, LBP_histogram = extract_features(image, painting.get('corners'), False)

            update_by_id(painting.get('_id'), {
                '$set': {
                    'full_histogram': pickle_serialize(full_histogram),
                    'block_histogram': pickle_serialize(block_histogram),
                    'LBP_histogram': pickle_serialize(LBP_histogram)
                }
            })

        logger.info(f'{count}/{total} images processed')
