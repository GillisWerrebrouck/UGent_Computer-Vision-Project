import cv2
import numpy as np
import time

from core.logger import get_root_logger
from data.imageRepo import get_all_images
from core.visualize import show_image, resize_image
from core.detection import detect_quadrilaters
from core.extractFeatures import get_histogram, get_NxN_histograms, extract_orb
from core.cornerHelpers import sort_corners, convert_corners_to_uniform_format, cut_painting

logger = get_root_logger()
images = None


def __fetch_images(force=False):
    """
    Lazy load the images. Will only query the database once.
    You can force to query the database with the first parameter.
    This function removes the histograms from the tuples.

    Parameters
    ----------
    - force -- Force a database query.
    """
    # Yes Python, we're using the global variable
    global images

    if force or images is None:
        imagesFromDB = get_all_images({
            'histograms.full_histogram': 1,
            'histograms.block_histogram': 1,
            'keypoints': 1,
            'filename': 1,
            'room': 1,
            'corners': 1
        })

        images = []

        for image in imagesFromDB:
            image['histograms']['full_histogram'] = __convert_to_three_dims(image['histograms']['full_histogram'])
            image['histograms']['block_histogram'] = __convert_NxN_to_three_dims(image['histograms']['block_histogram'])

            images.append(image)


def __convert_to_three_dims(histogram):
    """
    Cut the colors ('blue', 'green' and 'red') from the given array.

    Parameters
    ----------
    - histogram -- The histogram to convert.

    Returns: The converted histogram.
    """
    result = []

    if histogram.dtype == np.object:
        for color, hist in histogram:
            result.append(hist)

    return np.array(result)


def __convert_NxN_to_three_dims(histogram):
    """
    Cut the colors ('blue', 'green' and 'red') from each block of the given array.

    Parameters
    ----------
    - histogram -- The NxN block histograms to convert.

    Returns: The converted histograms.
    """
    for row in range(0, len(histogram)):
        for col in range(0, len(histogram[row])):
            histogram[row][col] = __convert_to_three_dims(histogram[row][col])
    
    return histogram


def predict_room(original_image, quadrilaterals, threshold=0.5):
    """
    Predict the room of the given (full color!) image.

    Parameters
    ----------
    - original_image -- The image to predict.
    - quadrilaterals -- The detected paintings in the image.
    - threshold -- The probability threshold to reach before concidering it a valid match, matches with a probability below the threshold are ignored.

    Returns:
    --------
    An array of sorted arrays of probabilities in descending probability order, 
    each sorted array in the array represents all probablities for a quadrilateral/painting in the image.
    """

    t1 = time.time()

    # Yes Python, we're using the global variable
    global images
    __fetch_images()

    if not len(quadrilaterals):
        return []

    full_histogram_weight = 1
    block_histogram_weight = 8
    total_weight = full_histogram_weight + block_histogram_weight

    all_scores = []

    width, height = original_image.shape[:2]
    for quad in quadrilaterals:
        quad = quad.reshape(4,2)
        quad = sort_corners(convert_corners_to_uniform_format(quad, width, height))

        painting = cut_painting(original_image, quad)
        src_full_histogram = __convert_to_three_dims(get_histogram(painting))
        src_block_histogram = get_NxN_histograms(painting)
        src_block_histogram = __convert_NxN_to_three_dims(src_block_histogram)

        quad_scores = []

        for image in images:
            compare_full_histogram = image['histograms']['full_histogram']
            compare_block_histogram = image['histograms']['block_histogram']

            full_histogram_score = cv2.compareHist(src_full_histogram, compare_full_histogram, cv2.HISTCMP_CORREL)

            block_histogram_score = 0
            for row in range(0, len(src_block_histogram)):
                for col in range(0, len(src_block_histogram[row])):
                    block_histogram_score += cv2.compareHist(src_block_histogram[row][col], compare_block_histogram[row][col], cv2.HISTCMP_CORREL)
            block_histogram_score /= len(src_block_histogram)*len(src_block_histogram)
            
            combined_score = (full_histogram_score * full_histogram_weight + block_histogram_score * block_histogram_weight) / total_weight        
            if(threshold <= combined_score):   
                quad_scores.append(tuple([combined_score, image['filename'], image['room']]))

        # sort the array of probabilities in descending probability order
        quad_scores = sorted(quad_scores, key=lambda x: x[0], reverse=True)
        all_scores.append(quad_scores)
    
    t2 = time.time()
    logger.info("room prediction time: {}".format(t2-t1))

    return all_scores
