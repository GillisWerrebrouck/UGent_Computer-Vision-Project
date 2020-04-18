import cv2
import sys
import PySimpleGUI as sg
from logger import get_root_logger  # TODO fix back to core.logger

logger = get_root_logger()
threshHold = 100


def get_blurryness(img):
    return cv2.Laplacian(img, cv2.CV_64F).var()


cap = cv2.VideoCapture(sys.argv[1])
if (cap.isOpened() == False):
    logger.warning("Videofile not found")

while (cap.isOpened()):

    success, frame = cap.read()

    if success:
        grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurIndex = get_blurryness(grayFrame)

        if (blurIndex > threshHold):
            cv2.imshow('dst', grayFrame)

        cv2.waitKey(1)


cv2.destroyAllWindows()
