import cv2
from glob import glob
import numpy as np
from os.path import basename
from scipy import stats
from shapely.geometry import Polygon
from matplotlib import pyplot as plt

# from tasks.task01 import sort_corners
from core.visualize import show_image, resize_image

filenames = sorted(glob('./datasets/images/dataset_pictures_msk/zaal_1/*.jpg'))


def detect1(img):
    img = cv2.imread(file)

    height, width = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV);
    hsv[:,:,2] = 255;

    ORANGE_MIN = np.array([5, 50, 50],np.uint8)
    ORANGE_MAX = np.array([15, 255, 255],np.uint8)

    mask = cv2.inRange(hsv, ORANGE_MIN, ORANGE_MAX)

    # TODO: uitzetten indien je tweakt
    closed = mask

    # TODO: kan nog verder getweaked worden:
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # mask = cv2.erode(mask, kernel)

    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    # closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    result = cv2.bitwise_and(result, result, mask=mask)

    # contours, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # img = cv2.drawContours(img, contours, -1, (0, 0, 255), 10)

    # areas = []

    # for contour in contours:
    #     x, y, w, h = cv2.boundingRect(contour)
    #     areas.append(w * h)

    # minArea = max(areas) * 0.5

    # for contour in contours:
    #     arc_len = cv2.arcLength(contour, True)
    #     approx = cv2.approxPolyDP(contour, 0.1 * arc_len, True)

    #     x, y, w, h = cv2.boundingRect(contour)
    #     if (w * h > minArea):
    #         img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 10)

    cv2.imwrite('out/' + basename(file), result)
    # cv2.imwrite('out/' + basename(file), img)





for file in filenames:
    img = cv2.imread(file)
    detect1(img)

    # img = cv2.bilateralFilter(img, 5, 150, 150)
    # img = cv2.medianBlur(img, (11, 11))
    # img = resize_image(img, 0.2)
    # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV);

    # h, s, v = cv2.split(hsv)
    # mean = np.average(h)
    # std = np.std(h)
    # minimum = mean - std
    # maximum = mean + std
    # mask = (hsv[:,:,0] >= minimum & hsv[:,:,0] <= maximum)
    # hsv[(hsv[:,:,0] >= minimum) * (hsv[:,:,0] <= maximum)] = 255
    # hsv[] = 0
    # print(h)

    # print(s)
    # print(v)
    # avgSaturation = np.average(hsv)
    # avgSaturation = np.median(hsv[:,:,2]);
    # avgSaturation = 255;
    # where = hsv[hsv > avgSaturation]
    # hsv[hsv[:,:,2] > avgSaturation] = avgSaturation
    # hsv = np.where(hsv < avgSaturation, hsv, avgSaturation)
    # hsv[:,:,2] = avgSaturation;

    # ORANGE_MIN = np.array([5, 50, 50],np.uint8)
    # ORANGE_MAX = np.array([15, 255, 255],np.uint8)

    # mask = cv2.inRange(hsv, ORANGE_MIN, ORANGE_MAX)
    # _, result = cv2.threshold(result, 127, 255, cv2.THRESH_BINARY)

    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # closed = cv2.erode(mask, kernel)

    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    # closed = cv2.dilate(closed, kernel)

    # result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    # result = cv2.bitwise_and(result, result, mask=mask)

    # result = cv2.bilateralFilter(result, 5, 150, 150)

    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # result = cv2.erode(result, kernel)

    # gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    # mean = int(np.average(gray))
    # ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # edges = cv2.Canny(gray, 50, 100, apertureSize=3)
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    # closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    # closed = cv2.dilate(edges, kernel)
    # contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # img = cv2.drawContours(img, contours, -1, (0, 255, 0), 5)

    # for contour in contours:
    #     arc_len = cv2.arcLength(contour, True)
    #     approx = cv2.approxPolyDP(contour, 0.1 * arc_len, True)

    #     if len(approx) == 4:
    #         x, y, w, h = cv2.boundingRect(contour)
    #         img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 10)
    #     elif len(approx) == 5:
    #         cv2.drawContours(img, [contour], 0, (0, 255, 0), 5)

    print(file)
