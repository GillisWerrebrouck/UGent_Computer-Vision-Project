import cv2
from glob import glob
import numpy as np

from data.imageRepo import get_paintings_for_image


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


def run():

    filenames = glob(
        './src/data/datasets/images/dataset_pictures_msk/zaal_*/*.jpg')

    for filename in filenames:
        img = cv2.imread(filename)
        width, height = img.shape[:2]
        print(width, height)
        paintings_in_image = get_paintings_for_image(filename.split('/')[-1])
        for painting in paintings_in_image:
            print(filename)
            points = np.array(painting.get('corners'), np.float32)
            points = __reformatPoints(points, width, height)
            points.reshape((-1, 1, 2))
            x, y, w, h = cv2.boundingRect(points)
            rectPoints = __calculate_points_for_rect(x, y, w, h)

            transformMatrix = cv2.getPerspectiveTransform(
                np.float32(points), np.float32(rectPoints))

            img = cv2.warpPerspective(img, transformMatrix, (height, width))
            crop_img = img[y:y + h, x:x + w]

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            corners = cv2.goodFeaturesToTrack(gray, 25, 0.01, 10)
            corners = np.int0(corners)
            for i in corners:
                cx, cy = i.ravel()
                cv2.circle(img, (cx, cy), 10, 255, -1)

            img = cv2.polylines(img, [points], True,
                                (0, 255, 255), thickness=5)
            img = cv2.polylines(img, [rectPoints], True,
                                (255, 0, 255), thickness=5)

        cv2.imshow('image', crop_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
