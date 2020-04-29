import cv2
import numpy as np

from data.imageRepo import get_all_images
from core.visualize import show_image, resize_image
from core.detection import detect_quadrilaters
from core.extractFeatures import get_histogram
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
            'filename': 1,
            'room': 1
        })

        images = []

        for image in imagesFromDB:
            image['histograms']['full_histogram'] = __convert_to_three_dims(image['histograms']['full_histogram'])
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

    for color, hist in histogram:
        result.append(hist)

    return np.array(result)


def predict_room(image):
    """
    Predict the room of the given (full color!) image.

    Parameters
    ----------
    - image -- The image to predict.

    Returns
    -------
    The room of this image.
    """
    # Yes Python, we're using the global variable
    global images
    __fetch_images()

    quadriliterals = detect_quadrilaters(image)

    if not len(quadriliterals):
        return None

    width, height = image.shape[:2]
    for quad in quadriliterals:
        quad = sort_corners(convert_corners_to_uniform_format(quad, width, height))
        painting = cut_painting(image, quad)

        src_histogram = __convert_to_three_dims(get_histogram(painting))

        scores = []
        for image in images:
            compare_to = image['histograms']['full_histogram']

            score = cv2.compareHist(src_histogram, compare_to, cv2.HISTCMP_CORREL)
            scores.append(tuple([score, image['filename'], image['room']]))

        # get the highest matching score
        max_score = max(scores, key=lambda t: t[0])
        print('Probably image: ', max_score[1])
        print('Probably room: ', max_score[2])

