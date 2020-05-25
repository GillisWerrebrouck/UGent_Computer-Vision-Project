import cv2
import numpy as np


def convert_corners_to_uniform_format(corners, width, height):
    """
    Convert all given corners to a uniform interval [0, 1]. Now the corners
    represent a percentage of the width/height.

    Parameters
    ----------
    - corners -- The corners to convert.
    - width -- The width of the image containing the corners.
    - height -- The height of the image containing the corners.

    Returns
    -------
    The corners (in same order) but now all in the interval [0, 1].
    """

    uniform_corners = []

    for c in corners:
        uniform_corners.append([c[0]/height, c[1]/width])

    return uniform_corners


def sort_corners(corners):
    a, b, c, d = sorted(corners, key=lambda x: (x[1], x[0]))

    if a[0] > b[0]:
        tmp = b
        b = a
        a = tmp

    if c[0] < d[0]:
        tmp = c
        c = d
        d = tmp

    return [a, b, c, d]


def __calculate_points_for_rect(x, y, w, h):
    return np.array([
        [x, y],
        [x + w, y],
        [x + w, y + h],
        [x, y + h]
    ], np.int32)


def __reformatPoints(points, width, height):
    new_points = []
    for point in points:
        new_points.append([int(point[0] * height), int(point[1] * width)])
    return np.array(new_points, np.int32)


def cut_painting(original_image, corners):
    """
    Cut the painting from the given image.

    Parameters
    ----------
    - image -- A full color image to extract the painting from.
    - corners -- The corners of the painting.
    - uniform -- Boolean indicating whether the corners are uniform for the width or height.

    Returns
    -------
    The cut painting.
    """
    image = original_image.copy()
    width, height = image.shape[:2]
    points = np.array(corners, np.float32)
    points = __reformatPoints(points, width, height)
    points.reshape((-1, 1, 2))
    x, y, w, h = cv2.boundingRect(points)
    rect_points = __calculate_points_for_rect(x, y, w, h)

    transform_matrix = cv2.getPerspectiveTransform(
      np.float32(points), np.float32(rect_points))

    img_warped = cv2.warpPerspective(image, transform_matrix, (height, width))
    return img_warped[y:y + h, x:x + w]
