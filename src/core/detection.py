import cv2
import numpy as np
from core.filter import apply_grayscale_for_painting_detection
from core.visualize import show_image

def detect_corners(image):
  """
  Detect corners with the Shi–Tomasi corner detection algorithm.

  Parameters
  ----------
  - image -- The image to detect corners in.
  """
  grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  corners = cv2.goodFeaturesToTrack(grayscale, 20, 0.5, 100)
  corners = np.int0(corners)

  for i in corners:
    x, y = i.ravel()
    cv2.circle(image, (x,y), 20, (0, 0, 255), -1)

def detect_corners2(image):
  """
  Detect corners with the Harris corner detection algorithm.

  Parameters
  ----------
  - image -- The image to detect corners in.
  """
  original = image

  grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  dst = cv2.cornerHarris(grayscale, 15,15,0.1)
  #result is dilated for marking the corners, not important
  # dst = cv2.dilate(dst,None)

  kernel = np.ones((5,5), np.uint8)
  dst = cv2.dilate(dst, kernel, iterations=1)

  # Threshold for an optimal value, it may vary depending on the image.
  image[dst>0.001*dst.max()]=[0,0,255]

  grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  image = cv2.medianBlur(grayscale, 27)
  image = cv2.Canny(image, threshold1=50, threshold2=150, apertureSize=3)
  dst = cv2.dilate(dst, kernel, iterations=1)
  contours, hierarchy = cv2.findContours(image, mode = cv2.RETR_CCOMP, method = cv2.CHAIN_APPROX_SIMPLE)

  for c in contours:
    x, y, w, h = cv2.boundingRect(c)
    original = cv2.rectangle(original, (x, y), (x+w, y+h), (0, 255, 0), 14)
  image=original


def detect_corners3(image):
  original = image

  (rows, cols) = image.shape[:2]
  minHeight = rows / 32.0
  minWidth = cols / 32.0

  imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
  imgray = cv2.dilate(imgray, kernel, iterations=1)
  imgray = cv2.erode(imgray, kernel, iterations=2)

  imgray = cv2.medianBlur(imgray, 13)
  ret, thresh = cv2.threshold(imgray, 127, 255, cv2.THRESH_BINARY)

  canny = cv2.Canny(thresh, threshold1=50, threshold2=150, apertureSize=3)

  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
  canny = cv2.dilate(canny, kernel)
  contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  # original = cv2.drawContours(original, contours, -1, (0,255,0), 3)
  for c in contours:
    x, y, w, h = cv2.boundingRect(c)

    if (w >= minWidth and h >= minHeight):
      original = cv2.rectangle(original, (x, y), (x+w, y+h), (0, 255, 0), 14)

  return original
