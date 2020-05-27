import cv2
import sys
import numpy as np
from matplotlib import pyplot as plt
from skimage.feature import local_binary_pattern

from core.cornerHelpers import cut_painting
from core.visualize import resize_image_to_width
from core.equalization import equalize


def get_histogram(image):
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

    colors = ('blue', 'green', 'red')
    histograms = np.empty([3], dtype=tuple)

    if len(image.shape) == 3 and image.shape[2] == 3:
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

    elif len(image.shape) == 2:
        histogram = cv2.calcHist([image], [0], None, [256], [0, 256])

        v = histogram
        histogram = (v - v.min()) / (v.max() - v.min())

        histograms[0] = ['gray', histogram]

    return histograms


def get_NxN_histograms(image, N=4):
    """
    Get NxN histograms from an image divided in NxN blocks. This function uses get_histogram.

    Parameters
    ----------
    - image -- Image to divide NxN blocks and calculate a histogram for each block.
    - N -- NxN blocks to use to divide the image.

    Returns
    -------
    Array with NxN histograms.
    """
    block_height = int(image.shape[0]/N)
    block_width = int(image.shape[1]/N)

    histograms = np.empty([N, N], dtype=object)

    for row in range(0, image.shape[0] - block_height + 1, block_height):
        for col in range(0, image.shape[1] - block_width + 1, block_width):
            block = image[row:row + block_height, col:col + block_width]

            row_num = int(row/block_height)
            col_num = int(col/block_width)
            histograms[row_num][col_num] = get_histogram(block)

    return histograms


def get_LBP_histogram(image):
    """
    Get LBP histogram from an image.

    Parameters
    ----------
    - image -- Color image to get histogram from.

    Returns
    -------
    - histograms -- Array with 1 histogram.
    """
    radius = 4
    no_points = 8 * radius
    eps = 1e-7

    image = resize_image_to_width(image, 500)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    lbp = local_binary_pattern(gray, no_points, radius, method='uniform')
    (hist, _) = np.histogram(lbp.ravel(), bins=np.arange(0, no_points + 3), range=(0, no_points + 2))
    hist = hist.astype("float")
    hist /= (hist.sum() + eps)

    return hist


def __plot_histogram(histograms):
    """
    Plot one histogram generated from get_histogram.

    Parameters
    ----------
    - histogram -- The histogram to plot.
    """

    plt.figure()
    plt.suptitle('Histogram')
    for histogram in histograms:
        plt.plot(histogram[1], color=histogram[0])
        plt.xlim([0, 256])
    plt.show()


def __plot_NxN_histogram(histograms):
    """
    Plot one histogram generated from get_histogram.

    Parameters
    ----------
    - histogram -- The histogram to plot.
    """

    fig, axs = plt.subplots(nrows=histograms.shape[0], ncols=histograms.shape[1],
                            sharex='col', sharey='row', gridspec_kw={'hspace': .1, 'wspace': .1})
    fig.suptitle('Histograms of ' +
                 str(histograms.shape[0]) + 'x' + str(histograms.shape[1]) + ' histograms')

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


def extract_features(image, corners, equalize_=False):
    """
    Extract fancy features from the given image.

    Parameters
    ----------
    - image -- The image to extract features from.
    - corners -- The corners of the painting in our database.
    - equalize_ -- Optional boolean to disable the equalization of the image's light intensity.

    Returns
    -------
    Object containing our very usefull features.
    """
    painting = cut_painting(image, corners)

    # Equalization
    if equalize_:
        painting = equalize(painting)

    # Extract the two types of histograms for the cut painting
    full_histogram = get_histogram(painting)
    block_histogram = get_NxN_histograms(painting)
    LBP_histogram = get_LBP_histogram(painting)

    return full_histogram, block_histogram, LBP_histogram
