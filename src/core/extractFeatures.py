import cv2
import sys
import numpy as np
from matplotlib import pyplot as plt

from data.serializer import serialize_keypoints, pickle_serialize
from data.imageRepo import get_paintings_for_image, update_by_id


def __reformatPoints(points, width, height):
    newPoints = []
    for point in points:
        newPoints.append([int(point[0] * height), int(point[1] * width)])
    return np.array(newPoints, np.int32)


def __calculate_points_for_rect(x, y, w, h):
    points = []
    points.append([x, y])
    points.append([x + w, y])
    points.append([x + w, y + h])
    points.append([x, y+h])
    return np.array(points, np.int32)

def __get_histogram(image):
    """
    Get histogram values from an image. Grayscale images will result in only one histogram array,
    color images will result in 3 histogram arrays.

    Parameters
    ----------
    - image -- Grayscale or color image to get histogram from.

    Returns
    -------
    - histograms -- Array with 1 (grayscale) or 3 (color) histogram(s).
    """

    colors = ('blue','green','red')
    histograms = np.empty([3], dtype=tuple)

    if(len(image.shape) == 3 and image.shape[2] == 3):
        max = 0
        min = sys.maxsize
        for i, color in enumerate(colors):
            histogram = cv2.calcHist([image], [i], None, [256], [0, 256])
            v = histogram

            # get min and max for min-max normalization over all channels
            if max < v.max():
                max = v.max()
            if min > v.min():
                min = v.min()

            histograms[i] = histogram

        # min-max normalization over all channels
        for i, color in enumerate(colors):
            v = histograms[i]
            histograms[i] = ((v - min) / (max - min))

        for i, color in enumerate(colors):
            histograms[i] = tuple([color, histograms[i]])

    elif(len(image.shape) == 2):
        histogram = cv2.calcHist([image], [0], None, [256], [0, 256])

        v = histogram
        histogram = (v - v.min()) / (v.max() - v.min())

        histograms[0] = ['gray', histogram]

    return histograms

def __get_NxN_histograms(image, N=4):
    """
    Get NxN histograms from an image divided in NxN blocks. This function uses __get_histogram.

    Parameters
    ----------
    - image -- Image to divide NxN blocks and calculate a histogram for each block.

    Returns
    -------
    - histograms -- Array with NxN histograms.
    - N -- NxN blocks to use to divide the image.
    """
    block_height = int(image.shape[0]/N)
    block_width = int(image.shape[1]/N)

    histograms = np.empty([N, N], dtype=object)

    for row in range(0, image.shape[0] - block_height + 1, block_height):
        for col in range(0, image.shape[1] - block_width + 1, block_width):
            block = image[row:row + block_height, col:col + block_width]

            row_num = int(row/block_height)
            col_num = int(col/block_width)
            histograms[row_num][col_num] = __get_histogram(block)

    return histograms

def __plot_histogram(histograms):
    """
    Plot one histogram generated from __get_histogram.

    Parameters
    ----------
    - histogram -- The histogram to plot.
    """

    plt.figure()
    plt.suptitle('Histogram')
    for histogram in histograms:
        plt.plot(histogram[1], color=histogram[0])
        plt.xlim([0,256])
    plt.show()

def __plot_NxN_histogram(histograms):
    """
    Plot one histogram generated from __get_histogram.

    Parameters
    ----------
    - histogram -- The histogram to plot.
    """

    fig, axs = plt.subplots(nrows=histograms.shape[0], ncols=histograms.shape[1], sharex='col', sharey='row', gridspec_kw={'hspace': .1, 'wspace': .1})
    fig.suptitle('Histograms of ' + str(histograms.shape[0]) + 'x' + str(histograms.shape[1]) + ' histograms')

    row_num = 0
    for row in axs:
        col_num = 0
        for col in row:
            for histogram in histograms[row_num][col_num]:
                if histogram is not None:
                    col.plot(histogram[1], color=histogram[0])
            col_num += 1
        row_num += 1

    for ax in axs.flat:
        ax.label_outer()

    plt.show()


def __cut_painting(image, corners):
  """
  Cut the painting from the given image.

  Parameters
  ----------
  - image -- A full color image to extract the painting from.
  - corners -- The corners of the painting.

  Returns
  -------
  The cut painting.
  """
  width, height = image.shape[:2]
  points = np.array(corners, np.float32)
  points = __reformatPoints(points, width, height)
  points.reshape((-1, 1, 2))
  x, y, w, h = cv2.boundingRect(points)
  rectPoints = __calculate_points_for_rect(x, y, w, h)

  transformMatrix = cv2.getPerspectiveTransform(
      np.float32(points), np.float32(rectPoints))

  img_warped = cv2.warpPerspective(image, transformMatrix, (height, width))
  return img_warped[y:y + h, x:x + w]


def __extract_orb(gray):
  """
  Extract ORB features from the given image.

  Parameters
  ----------
  - gray -- A grayscale image to extract ORB features from.

  Returns
  -------
  The ORB keypoints and descriptors.
  """
  orb = cv2.ORB_create()
  keypoints = orb.detect(gray, None)
  keypoints, des = orb.compute(gray, keypoints)

  return tuple([keypoints, des])


def extract_sobel(gray):
  """
  Extract sobel features from the given image.

  Parameters
  ----------
  - gray -- A grayscale image to extract sobel features from.

  Returns
  -------
  The sobel feature.
  """
  sobelX = cv2.Sobel(gray, cv2.CV_64F, 1, 0, 5)
  sobelY = cv2.Sobel(gray, cv2.CV_64F, 0, 1, 5)

  sobelX = cv2.convertScaleAbs(sobelX)
  sobelY = cv2.convertScaleAbs(sobelY)
  return cv2.addWeighted(sobelX, 0.5, sobelY, 0.5, 0)


def extract_features(path, dbPainting):
  """
  Extract fancy features from the given image.

  Parameters
  ----------
  - path -- The path to the image to extract features from.
  - dbPainting -- The painting in our database.

  Returns
  -------
  Object containing our very usefull features.
  """
  image = cv2.imread(path)
  painting = __cut_painting(image, dbPainting.get('corners'))
  painting_gray = cv2.cvtColor(painting, cv2.COLOR_BGR2GRAY)

  # Features with color image
  full_histogram = __get_histogram(painting)
  block_histogram =__get_NxN_histograms(painting)

  # Features with gray image
  keypoints, descriptors = __extract_orb(painting_gray)
  good_features = cv2.goodFeaturesToTrack(painting_gray, 25, 0.01, 2)

  return {
    'orb': {
      'keypoints': keypoints,
      'descriptors': descriptors
    },
    'histograms': {
      'full_histogram': full_histogram,
      'block_histogram': block_histogram
    },
    'good_features': good_features
  }
