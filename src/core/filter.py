import cv2
import numpy as np
import math
from core.visualize import resize_image

def apply_filters(image):
  """
  ...

  Parameters
  ----------
  - image -- The image to apply filters to.
  """
  original = image.copy()
  kernel = np.ones((3,3), np.uint8)

  image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  image = cv2.dilate(image, kernel, iterations=1)
  image = cv2.medianBlur(image, 11)
  image = cv2.dilate(image, kernel, iterations=3)
  image = resize_image(image, 0.04)
  image = resize_image(image, 1/0.04)

  image = cv2.Canny(image, threshold1=60, threshold2=80, apertureSize=3)
  image = cv2.dilate(image, kernel, iterations=1)
  
  contours, hierarchy = cv2.findContours(image, mode = cv2.RETR_EXTERNAL, method = cv2.CHAIN_APPROX_NONE)
  print("Number of Contours found = " + str(len(contours)))
  
  # original = cv2.drawContours(original, contours, -1, (255, 255, 0), 3, hierarchy=hierarchy, maxLevel=2)

  area = image.shape[0]*image.shape[1]
  i=0
  count=0
  for c in contours:
    x, y, w, h = cv2.boundingRect(c)
    aspect_ratio = w/h
    allowed_aspect_ratio = 8
    if(hierarchy[0,i,3] == -1 and 1/allowed_aspect_ratio <= aspect_ratio and aspect_ratio <= allowed_aspect_ratio):
      count += 1
      original = cv2.rectangle(original, (x, y), (x+w, y+h), (0, 255, 0), 4)
    i += 1
  print(count)

  return original
