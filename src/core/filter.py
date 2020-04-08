import cv2
import numpy as np
import math

def apply_filters(image):
  """
  ...
  Parameters
  ----------
  - image -- The image to apply filters to.
  """

  original = image
  grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  kernel = np.ones((5,5), np.uint8)
  image = cv2.dilate(grayscale, kernel, iterations=1)

  # image = cv2.GaussianBlur(src=image, ksize=(17, 17), sigmaX=0)
  image = cv2.medianBlur(image, 27)

  image = cv2.Canny(image, threshold1=25, threshold2=80, apertureSize=3)
  image = cv2.dilate(image, kernel, iterations=1)

  # image = cv2.bitwise_not(image)

  contours, hierarchy = cv2.findContours(image, mode = cv2.RETR_EXTERNAL, method = cv2.CHAIN_APPROX_SIMPLE)
  print("Number of Contours found = " + str(len(contours)))
  
  ## original = cv2.drawContours(original, contours, -1, (255, 255, 0), 3)

  i=0
  ## blank_image = np.zeros((image.shape[0],image.shape[1],3), np.uint8)
  for c in contours:
    if(hierarchy[0,i,3] == -1):
      x, y, w, h = cv2.boundingRect(c)
      original = cv2.rectangle(original, (x, y), (x+w, y+h), (0, 255, 0), 14)
    i += 1

  
  return original