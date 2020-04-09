import cv2
import numpy as np
from core.visualize import show_image, resize_image
import os
import copy
import sys
from core.shape import Rect, Point

# TODO: consistentie naamgeving, soms capitalCasing, soms niet_capital_casing

resize_factor = 5

def detect_contours(image):
  (height, width) = image.shape[:2]
  minHeight = height / 32.0
  minWidth = width / 32.0

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

  # Te kleine contours wegfilteren
  filtered_contours = []
  for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    if (w >= minWidth and h >= minHeight):
      rectangle = Rect(Point(x, y), Point(x+w, y+h))
      filtered_contours.append(rectangle)

  return filtered_contours

def get_contour(contours, point):
  for c in contours:
    if(c.has_point(point)):
      copy = c
      contours.remove(c)
      return copy
  return None

def get_contour_with_id(contours, point):
  for c in contours:
    if(c[0].has_point(point)):
      copy = c
      contours.remove(c)
      return copy
  return None

def remove_contour(contours, point):
  for c in contours:
    if(c[0].has_point(point)):
      id = c[1]
      contours.remove(c)
      return id
  return None
