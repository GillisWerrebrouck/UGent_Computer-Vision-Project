import cv2
from glob import glob

from core.extractFeatures import __get_histogram, __get_NxN_histograms, __plot_histogram, __plot_NxN_histogram
from core.visualize import resize_image, show_image

filenames = glob('./datasets/images/dataset_pictures_msk/zaal_*/*.jpg')
for f in filenames:
    image = cv2.imread(f, 1)
    image = resize_image(image, 0.2)
    show_image(f, image)

    hist = __get_histogram(image)
    __plot_histogram(hist)
    NxNHist = __get_NxN_histograms(image)
    __plot_NxN_histogram(NxNHist)
