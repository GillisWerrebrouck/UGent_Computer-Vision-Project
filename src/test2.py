import cv2
from glob import glob
from matplotlib import pyplot as plt

from core.detection import detect_quadrilaterals
from core.cornerHelpers import cut_painting, sort_corners, convert_corners_to_uniform_format
from core.visualize import show_image, resize_image, draw_quadrilaterals_opencv

filenames = sorted(glob('./datasets/images/dataset_pictures_msk/zaal_*/*.jpg'))

for path in filenames:
    original = cv2.imread(path)

    resized_image = resize_image(original, 0.2)
    width, height = resized_image.shape[:2]
    image = resized_image.copy()

    quadriliterals = detect_quadrilaterals(image)

    if not len(quadriliterals):
        continue

    for quad in quadriliterals:
        quad = quad.reshape(4, 2)
        quad = sort_corners(convert_corners_to_uniform_format(quad, width, height))

        painting = cut_painting(resized_image, quad)

        # Initiate ORB detector
        orb = cv2.ORB_create()

        # find the keypoints with ORB
        kp = orb.detect(painting, None)

        # compute the descriptors with ORB
        kp, des = orb.compute(painting, kp)

        # draw only keypoints location,not size and orientation
        img2 = cv2.drawKeypoints(painting, kp, None, color=(0, 255, 0), flags=0)
        plt.imshow(img2)
        plt.show()
