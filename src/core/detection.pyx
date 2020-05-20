import cv2
import numpy as np
from shapely.geometry import Polygon
import time
from queue import Queue

from core.logger import get_root_logger
from core.visualize import show_image, resize_image, draw_quadrilaterals_opencv
from core.shape import Point, Rect
from core.cornerHelpers import sort_corners
from core.accuracyHelperFunctions import calculate_bounding_box_accuracy

logger = get_root_logger()

def detect_contours(image):
    """
    Detect (in a naive way) contours of images in an image.

    Parameters
    ----------
    - image --  The image to detect contours in.

    Returns: The detected contours.
    """

    logger.info('Starting naive contour detection')

    (height, width) = image.shape[:2]
    max_allowed_ratio = 10

    image = resize_image(image, 0.2)
    image = resize_image(image, 1/0.2)

    imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
    imgray = cv2.dilate(imgray, kernel)
    imgray = cv2.erode(imgray, kernel)

    imgray = cv2.medianBlur(imgray, 21)

    canny = cv2.Canny(imgray, threshold1=50, threshold2=80, apertureSize=3)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    canny = cv2.dilate(canny, kernel)
    contours, hierarchy = cv2.findContours(
        canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    logger.info('Detected {} contour(s)'.format(len(contours)))

    filtered_contours = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if max(w/h, h/w) <= max_allowed_ratio:
            rectangle = Rect(Point(x, y), Point(x+w, y+h))
            filtered_contours.append(rectangle)

    logger.info('Detected {} contour(s) after filtering out contours with abnormal ratio'.format(
        len(filtered_contours)))

    return filtered_contours


def pop_contour(point, contours):
    """
    Detect the contour in which the point exists, if a contour around this point exists.
    If found, the contour is removed from the list and returned.

    Parameters
    ----------
    - point --  The coordinate of a point.
    - contours --  All contours from which to find a surrounding contour.

    Returns: The detected contour, if one exists.
    """

    for c in contours:
        if(c.has_point(point)):
            copy = c
            contours.remove(c)
            return copy
    return None


def pop_contour_with_id(point, contours):
    """
    Detect the contour in which the point exists, if a contour around this point exists.
    If found, the contour is removed from the list and returned.

    Parameters
    ----------
    - point --  The coordinate of a point.
    - contours --  All contours from which to find a surrounding contour. The contours are tupples; (Rect contour, figure id).

    Returns: The detected contour, if one exists.
    """

    for c in contours:
        if(c[0].has_point(point)):
            copy = c
            contours.remove(c)
            return copy
    return None


cdef __flooding(object image, object mask, int step, int y):
    # consider 4 nearest neighbours (those that share an edge)
    cdef int floodFlags = 4
    floodFlags |= cv2.FLOODFILL_MASK_ONLY  # do not change the image
    floodFlags |= (255 << 8)  # fill the mask with color 255

    cdef int img_h = image.shape[0]
    cdef int img_w = image.shape[1]
    cdef int channels = image.shape[2]
    cdef float img_area = img_h * img_w

    cdef int num, x
    cdef float w, h, current_size, largest_segment_size = 0
    cdef object largest_mask = None, im, rect

    for x in range(0, image.shape[1], step):
        num, im, mask, rect = cv2.floodFill(
            image, mask, (x, y), (255, 0, 0), (8,)*3, (8,)*3, floodFlags)
        x, y, w, h = rect
        current_size = w*h

        if current_size > largest_segment_size:
            largest_segment_size = current_size
            largest_mask = mask
        if largest_segment_size == img_area:
            break

    return (largest_mask, largest_segment_size)


cpdef detect_quadrilaterals(object original_image):
    """
    Detect painings in an image.

    Parameters
    ----------
    - original_image -- The image to detect paintings in.

    Returns: The detected paintings as polygons.
    """

    cdef float t1 = time.time()

    cdef object image = cv2.pyrMeanShiftFiltering(original_image, 12, 18, maxLevel=4)
    cdef int h = image.shape[0]
    cdef int w = image.shape[1]
    cdef int channels = image.shape[2]

    # use flooding to find mask
    cdef int largest_segment_size = 0
    cdef object largest_mask = None
    cdef int step = 200

    cdef object flooding_result = None
    cdef object mask = np.zeros((h+2, w+2), np.uint8)
    cdef int size = 0

    for y in range(0, image.shape[0], step):
        mask, size = __flooding(image, mask, step, y)

        if largest_segment_size < size:
            largest_segment_size = size
            largest_mask = mask
        if size == h*w:
            break

    mask = largest_mask

    cdef object kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    mask = cv2.bitwise_not(mask)
    mask = cv2.erode(mask, kernel, 1)
    mask = cv2.medianBlur(mask, 9)

    # Calculate OTSU threshold to use as threshold for Canny detection
    cdef int ret = 0
    cdef object threshold = None, edge = None, closed = None
    cdef object contours = None, hierarchy = None

    cdef object grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, threshold = cv2.threshold(grayscale, 0, 255, cv2.THRESH_OTSU)
    edges = cv2.Canny(mask, ret/2, ret, apertureSize=3)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # find contours in mask
    contours, hierarchy = cv2.findContours(
        closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cdef list quadrilaterals = []

    cdef int height = image.shape[0]
    cdef int width = image.shape[1]
    cdef object polygonImage = Polygon([(0, 0), (width, 0), (width, height), (0, height), (0, 0)])

    cdef int arc_len = 0
    cdef object approx = None, polygon = None
    for contour in contours:
        arc_len = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.1 * arc_len, True)

        if (len(approx) == 4):
            polygon = Polygon(np.reshape(approx, (4, 2)))
            if(polygon.is_valid and polygon.area/polygonImage.area > 0.005):
                quadrilaterals.append(approx)

    cdef float t2 = time.time()
    logger.info("painting detection time: {}".format(t2-t1))

    return quadrilaterals


def calculate_accuracy_metrics(image, ground_truth_paintings, detected_paintings):
  (height, width) = image.shape[:2]

  false_negatives = 0
  false_positives = 0
  paintings_found = 0
  average_accuracy = 0

  for q1 in ground_truth_paintings:
    q1_corners = q1.get('corners')
    area = 0
    for point in q1_corners:
      point[0] = point[0]*width
      point[1] = point[1]*height

    for q2 in detected_paintings:
      q2 = np.reshape(q2, (4, 2)).astype(np.float32)

      # draw ground truth quadrilaterals on image
      image = draw_quadrilaterals_opencv(image, [np.asarray(q1_corners).astype(np.int32)], (255, 0, 0))
      accuracy = calculate_bounding_box_accuracy(q1_corners, q2)
      if(area < accuracy):
        area = accuracy
    if(area <= 0.001):  # none found -> false positive
      false_negatives += 1
    else: # one found, increase average accuracy
      # TODO: check on duplicates, remove from result
      paintings_found += 1
      average_accuracy += area

  # average accuracy dividing by amount found + calculating the amount of false nefatives
  # division by 1 is not needed
  if paintings_found > 1:
    average_accuracy /= paintings_found
  if len(detected_paintings) >= paintings_found:
    false_positives = len(detected_paintings) - paintings_found

  return (image, paintings_found, false_negatives, false_positives, average_accuracy)
