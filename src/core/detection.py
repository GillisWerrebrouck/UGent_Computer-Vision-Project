import cv2
import numpy as np

from core.logger import get_root_logger
from core.visualize import show_image, resize_image
from core.shape import Point, Rect

logger = get_root_logger()


def detect_contours(image):
  """
  Detect (in a naive way) contours of images in an image.

  Parameters
  ----------
  - image --  The image to detect contours in.

  Returns: The detected contours.
  """

  logger.info('Starting naive contour detection')

  (height, width) = image.shape[:2]
  max_allowed_ratio = 10

  image = resize_image(image, 0.2)
  image = resize_image(image, 1/0.2)

  imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
  imgray = cv2.dilate(imgray, kernel)
  imgray = cv2.erode(imgray, kernel)

  imgray = cv2.medianBlur(imgray, 21)

  canny = cv2.Canny(imgray, threshold1=50, threshold2=80, apertureSize=3)

  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
  canny = cv2.dilate(canny, kernel)
  contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  logger.info('Detected {} contour(s)'.format(len(contours)))

  filtered_contours = []
  for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    if max(w/h, h/w) <= max_allowed_ratio:
      rectangle = Rect(Point(x, y), Point(x+w, y+h))
      filtered_contours.append(rectangle)

  logger.info('Detected {} contour(s) after filtering out contours with abnormal ratio'.format(len(filtered_contours)))

  return filtered_contours


def pop_contour(point, contours):
  """
  Detect the contour in which the point exists, if a contour around this point exists.
  If found, the contour is removed from the list and returned.

  Parameters
  ----------
  - point --  The coordinate of a point.
  - contours --  All contours from which to find a surrounding contour.

  Returns: The detected contour, if one exists.
  """

  for c in contours:
    if(c.has_point(point)):
      copy = c
      contours.remove(c)
      return copy
  return None


def pop_contour_with_id(point, contours):
  """
  Detect the contour in which the point exists, if a contour around this point exists.
  If found, the contour is removed from the list and returned.
  
  Parameters
  ----------
  - point --  The coordinate of a point.
  - contours --  All contours from which to find a surrounding contour. The contours are tupples; (Rect contour, figure id).

  Returns: The detected contour, if one exists.
  """

  for c in contours:
    if(c[0].has_point(point)):
      copy = c
      contours.remove(c)
      return copy
  return None

def detect_straight_lines(image):
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
  
  edges = cv2.Canny(gray, 50, 150, apertureSize=3) 
  
  lines = cv2.HoughLines(edges, 1, np.pi/180, 200)

  if lines is None:
    return image

  for line in lines:
    r,theta = line[0]
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*r
    y0 = b*r
    
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000*(a))

    cv2.line(image,(x1,y1), (x2,y2), (0,0,255),2) 

  return image
