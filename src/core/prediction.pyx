import cv2
import numpy as np
import time

from core.logger import get_root_logger
from data.imageRepo import get_all_images
from core.visualize import show_image, resize_image
from core.detection import detect_quadrilaterals
from core.extractFeatures import get_histogram, get_NxN_histograms, extract_orb
from core.cornerHelpers import sort_corners, convert_corners_to_uniform_format, cut_painting
from core.transitions import transitions
from core.equalization import equalize

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


def FLD(image):
    global fld
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Create default Fast Line Detector class
    fld = cv2.ximgproc.createFastLineDetector(_length_threshold=10, _distance_threshold=6, _canny_th1=60, _canny_th2=60, _do_merge=False)
    # Get line vectors from the image
    lines = fld.detect(image)
    return lines


cdef sort_by_probability(x):
    return x[0]


cpdef list predict_room(original_image, quadrilaterals, threshold=0.5, possible_rooms=transitions['INKOM']):
    """
    Predict the room of the given (full color!) image.

    Parameters
    ----------
    - original_image -- The image to predict.
    - quadrilaterals -- The detected paintings in the image.
    - threshold -- The probability threshold to reach before considering if it is a valid match. Matches with a probability below this threshold are ignored.
    - possible_rooms -- The rooms that are possible at this stage of the prediction.

    Returns:
    --------
    An array of sorted arrays of probabilities in descending probability order,
    each sorted array in the array represents all probablities for a quadrilateral/painting in the image.
    """

    cpdef float t1 = time.time()

    # Yes Python, we're using the global variable
    global images
    __fetch_images()

    if not len(quadrilaterals):
        return []

    cpdef int full_histogram_weight = 1
    cpdef int block_histogram_weight = 8
    cpdef int total_weight = full_histogram_weight + block_histogram_weight

    cpdef list all_scores = []

    cpdef object quad = None, painting = None
    cpdef object src_full_histogram = None, src_block_histogram = None
    cpdef object compare_full_histogram = None, compare_block_histogram = None
    cpdef float full_histogram_score = 0, block_histogram_score = 0, combined_score = 0

    cpdef list quad_scores = None
    cpdef int width = original_image.shape[0]
    cpdef int height = original_image.shape[1]
    for quad in quadrilaterals:
        quad = quad.reshape(4,2)
        quad = sort_corners(convert_corners_to_uniform_format(quad, width, height))

        painting = equalize(cut_painting(original_image, quad))
        src_full_histogram = __convert_to_three_dims(get_histogram(painting))
        src_block_histogram = get_NxN_histograms(painting)
        src_block_histogram = __convert_NxN_to_three_dims(src_block_histogram)

        quad_scores = []

        # line1 = FLD(painting)
        # line1_img = np.zeros([painting.shape[0], painting.shape[1], 3], dtype=np.uint8)
        # fld = cv2.ximgproc.createFastLineDetector()
        # line1_img = fld.drawSegments(line1_img, line1)
        # show_image('test1', line1_img)

        for image in images:
            # skip images that are not possible!
            if image['room'] not in possible_rooms:
                continue

            compare_full_histogram = image['histograms']['full_histogram']
            compare_block_histogram = image['histograms']['block_histogram']

            # compare_painting = cv2.imread('.\\datasets\\images\\dataset_pictures_msk\\zaal_' + image['room'] +'\\' + image['filename'])
            # compare_painting = resize_image(compare_painting, 0.2)
            # compare_painting = cut_painting(compare_painting, image['corners'])

            # fld = cv2.ximgproc.createFastLineDetector()

            # compare_painting = cv2.resize(compare_painting, (painting.shape[1], int(painting.shape[1]/compare_painting.shape[1] * compare_painting.shape[0])), interpolation=cv2.INTER_AREA)
            # line2 = FLD(compare_painting)
            # line2_img = np.zeros([compare_painting.shape[0], compare_painting.shape[1], 3], dtype=np.uint8)

            # line2_img = fld.drawSegments(line2_img, line2)
            # show_image('test2', line2_img)


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
        quad_scores = sorted(quad_scores, key=sort_by_probability, reverse=True)
        all_scores.append(quad_scores)

    cpdef float t2 = time.time()
    logger.info("room prediction time: {}".format(t2-t1))

    return all_scores
