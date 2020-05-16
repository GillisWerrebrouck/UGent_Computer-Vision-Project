import pyximport
pyximport.install(language_level='3')

import cv2
import numpy as np
from glob import glob
from ntpath import basename

from core.detection import detect_quadrilaterals
from core.cornerHelpers import cut_painting, convert_corners_to_uniform_format, sort_corners
from core.visualize import show_image, resize_image
from data.imageRepo import get_paintings_for_image, get_all_images

filenames = glob('./datasets/images/dataset_pictures_msk/zaal_1/*.jpg')

def FLD(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Create default Fast Line Detector class
    fld = cv2.ximgproc.createFastLineDetector(_length_threshold=10, _distance_threshold=6, _canny_th1=60, _canny_th2=60, _do_merge=False)
    # Get line vectors from the image
    lines = fld.detect(image)
    return lines

def compare_segments(size1, lines1, size2, lines2, max_ratio=1.1):
    height1, width1 = size1
    height2, width2 = size2

    ratio1 = width1/height1
    ratio2 = width2/height2

    if max(ratio1/ratio2, ratio2/ratio1) > max_ratio:
        print('ratio broken')
        return -1

    dx = width1/width2
    dy = height1/height2

    line_image1 = np.zeros((height1, width1, 3))
    line_image2 = np.zeros((height1, width1, 3))

    lines1 = np.reshape(lines1, (lines1.shape[0], 4))
    lines2 = np.reshape(lines2, (lines2.shape[0], 4))

    for x1, y1, x2, y2 in lines1:
        line_image1 = cv2.line(line_image1, (x1, y1), (x2, y2), (0, 0, 255))

    for x1, y1, x2, y2 in lines2:
        line_image2 = cv2.line(line_image2, (int(x1 * dx), int(y1 * dy)), (int(x2 * dx),int(y2 * dy)), (0, 0, 255))

    diff = line_image2 - line_image1
    pixels_lines1 = np.count_nonzero(line_image1 == 255)
    pixels_lines2 = np.count_nonzero(line_image2 == 255)
    pixels_diff = np.count_nonzero(diff == 255)

    non_match_percentage = pixels_diff / (pixels_lines1 + pixels_lines2)
    return 1 - non_match_percentage


images_in_db = get_all_images({ 'corners': 1, 'room': 1, 'filename': 1 })

for path in filenames:
    image = cv2.imread(path)
    image = resize_image(image, 0.2)
    width, height = image.shape[:2]

    lines_in_image, image_with_lines = FLD(image)

    quadrilaterals = detect_quadrilaterals(image)

    for quad in quadrilaterals:
        quad = sort_corners(convert_corners_to_uniform_format(np.reshape(quad, (4, 2)), width, height))
        painting = cut_painting(image, quad)
        lines_in_painting, painting_with_lines = FLD(painting)

        show_image('test', resize_image(painting, 0.5))
        for image_in_db in images_in_db:
            room = image_in_db['room']
            if room != '1':
                continue

            filename = image_in_db['filename']
            img = cv2.imread(f'./datasets/images/dataset_pictures_msk/zaal_{room}/{filename}')
            img = resize_image(img, 0.2)
            painting_in_db = cut_painting(img, image_in_db['corners'])

            show_image('test', painting_in_db)
            lines_in_painting_db, painting_with_lines_db = FLD(painting_in_db)

            compare_segments(painting_in_db.shape[:2], lines_in_painting_db, painting.shape[:2], lines_in_painting)

