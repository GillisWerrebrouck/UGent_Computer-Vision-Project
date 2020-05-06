import cv2
import numpy as np

from data.imageRepo import get_all_images
from core.visualize import show_image, resize_image
from core.detection import detect_quadrilaters
from core.extractFeatures import get_histogram, get_NxN_histograms, extract_orb
from core.cornerHelpers import sort_corners, convert_corners_to_uniform_format, cut_painting

images = None


def __fetch_images(force=False):
    """
    Lazy load the images. Will only query the database once.
    You can force to query the database with the first parameter.
    This function removes the histograms from the tuples.

    Parameters
    ----------
    - force -- Force a database query.

    Returns
    -------
    Nothing
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

    Returns
    -------
    The converted histogram.
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

    Returns
    -------
    The converted histograms.
    """
    for row in range(0, len(histogram)):
        for col in range(0, len(histogram[row])):
            histogram[row][col] = __convert_to_three_dims(histogram[row][col])
    
    return histogram


def predict_room(original_image, quadrilaterals):
    """
    Predict the room of the given (full color!) image.

    Parameters
    ----------
    - original_image -- The image to predict.
    - quadrilaterals -- The detected paintings in the image.

    Returns
    -------
    The room of this image.
    """
    # Yes Python, we're using the global variable
    global images
    __fetch_images()

    if not len(quadrilaterals):
        return None

    width, height = original_image.shape[:2]
    for quad in quadrilaterals:
        quad = quad.reshape(4,2)
        quad = sort_corners(convert_corners_to_uniform_format(quad, width, height))

        painting = cut_painting(original_image, quad)
        show_image('test', painting)
        src_histogram = __convert_to_three_dims(get_histogram(painting))
        src_block_histogram = get_NxN_histograms(painting)
        src_block_histogram = __convert_NxN_to_three_dims(src_block_histogram)

        scores = []
        for image in images:
            compare_to = image['histograms']['full_histogram']

            score = cv2.compareHist(src_histogram, compare_to, cv2.HISTCMP_CORREL)
            scores.append(tuple([score, image['filename'], image['room']]))

        # get the highest matching score
        max_score = max(scores, key=lambda t: t[0])
        probability = max_score[0] * 100
        print('Probability: ', probability, '%')
        print('Probably image: ', max_score[1])
        print('Probably room: ', max_score[2])



        scores = []
        for image in images:
            compare_block_histogram = image['histograms']['block_histogram']

            score = 0
            for row in range(0, len(src_block_histogram)):
                for col in range(0, len(src_block_histogram[row])):
                    score += cv2.compareHist(src_block_histogram[row][col], compare_block_histogram[row][col], cv2.HISTCMP_CORREL)
            
            scores.append(tuple([score, image['filename'], image['room']]))

        # get the highest matching score
        max_score = max(scores, key=lambda t: t[0])
        probability = max_score[0] / (len(src_block_histogram)*len(src_block_histogram)) * 100
        print('Probability: ', probability, '%')
        print('Probably image: ', max_score[1])
        print('Probably room: ', max_score[2])
