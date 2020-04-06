import cv2
import numpy as np
from core.visualize import show_image, resize_image
import os

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




resize_factor = 5

def onMouse(k, x, y, s, param):
    if k == cv2.EVENT_LBUTTONDOWN:
        param.append((x*resize_factor, y*resize_factor))


def detect_corners3(image):
  original = image

  (rows, cols) = image.shape[:2]
  minHeight = rows / 32.0
  minWidth = cols / 32.0

  imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
  imgray = cv2.dilate(imgray, kernel)
  imgray = cv2.erode(imgray, kernel)

  imgray = cv2.medianBlur(imgray, 21)
  ret, thresh = cv2.threshold(imgray, 127, 255, cv2.THRESH_BINARY)

  canny = cv2.Canny(thresh, threshold1=50, threshold2=150, apertureSize=3)

  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
  canny = cv2.dilate(canny, kernel)
  contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)





  mouseClicks = []
  selectedContours = []

  temp_show_img = resize_image(original, 1.0/resize_factor)


  cv2.namedWindow('Klik op schilderijen')
  cv2.setMouseCallback('Klik op schilderijen', onMouse, mouseClicks)
  cv2.imshow('Klik op schilderijen', temp_show_img)
  os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

  key = cv2.waitKey(10)
  while(key != 13):
      key = cv2.waitKey(10)
  cv2.destroyAllWindows()


  for contour in contours:
    for click in mouseClicks:
      x, y, w, h = cv2.boundingRect(contour)
      if(click[0] >= x and click[0] <= x+w and click[1] >= y and click[1] <= y+h):
        selectedContours.append(contour)
        break



  for c in selectedContours:
    x, y, w, h = cv2.boundingRect(c)

    if (w >= minWidth and h >= minHeight):
      original = cv2.rectangle(original, (x, y), (x+w, y+h), (0, 255, 0), 14)

  return original
