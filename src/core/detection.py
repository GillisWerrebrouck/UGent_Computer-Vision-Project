import cv2
import numpy as np
from core.visualize import show_image, resize_image
import os
import copy
import sys

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

def add_contours_to_image(contours, image):
  for c in contours:
    x, y, w, h = cv2.boundingRect(c)
    image = cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 14)
  return image

# zegt of het punt in de contour ligt. positieve waarde is binnen, negatieve is buiten. grootte is de afstand
# dit is een naïve methode en controleert enkel horizontal afstand bij verticale lijnen 
# methode van opencv werkt niet correct: https://docs.opencv.org/3.4/d3/dc0/group__imgproc__shape.html#ga1a539e8db2135af2566103705d7a5722
def pointContourTest(contour, point):
  x, y, w, h = cv2.boundingRect(contour)
  X, Y = point
  dist = abs(x - X)
  dist = min(dist, abs(y - Y))
  dist = min(dist, abs((x + w) - X))
  dist = min(dist, abs((y + h) - Y))
  if(not (point[0] >= x and point[0] <= x + w and point[1] >= y and point[1] <= y + h)):
    dist = dist * -1
  return dist


def detect_corners3(image):
  original = copy.deepcopy(image)

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

  # te kleine contours wegfilteren
  temp_contours = []
  for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    if (w >= minWidth and h >= minHeight):
      temp_contours.append(contour)
  contours = temp_contours

  mouseClicks = []
  selectedContours = []

  temp_img = copy.deepcopy(image)
  temp_img = resize_image(temp_img, 1.0/resize_factor)


  cv2.namedWindow('Klik op schilderijen om de randen te detecteren')
  cv2.setMouseCallback('Klik op schilderijen om de randen te detecteren', onMouse, mouseClicks)
  cv2.imshow('Klik op schilderijen om de randen te detecteren', temp_img)
  os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

  key = cv2.waitKey(10)
  while(key != 13):
      key = cv2.waitKey(10)
  cv2.destroyAllWindows()

  # selecteren welke contouren we willen behouden
  for contour in contours:
    for click in mouseClicks:
      x, y, w, h = cv2.boundingRect(contour)
      if(pointContourTest(contour, click) >= 0):
        selectedContours.append(contour)
        break

  mouseClicks = []
  temp_img = copy.deepcopy(image)
  # Kijk bij welke contour een klik het dichtste ligt en verwijder deze
  if(len(selectedContours) > 0):
    add_contours_to_image(selectedContours, temp_img)
    temp_img = resize_image(temp_img, 1.0/resize_factor)
    cv2.namedWindow('Klik zo dicht mogelijk bij de randen van de te verwijderen contouren')
    cv2.setMouseCallback('Klik zo dicht mogelijk bij de randen van de te verwijderen contouren', onMouse, mouseClicks)
    cv2.imshow('Klik zo dicht mogelijk bij de randen van de te verwijderen contouren', temp_img)
    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

    key = cv2.waitKey(10)
    while(key != 13):
        key = cv2.waitKey(10)
    cv2.destroyAllWindows()


    removeIndices = []
    for click in mouseClicks:
      # we willen de kortste afstand vinden, dus moeten we op een groot genoege waarde starten
      dist = sys.maxsize
      index = -1
      for i in range(len(selectedContours)):
        if(abs(pointContourTest(selectedContours[i], click)) < dist):
          dist = abs(abs(pointContourTest(selectedContours[i], click)))
          index = i
      removeIndices.append(index)
    removeIndices = list(dict.fromkeys(removeIndices))
    # van groot naar klein, zodat we geen andere verwijder indexen aanpassen
    removeIndices.sort(reverse = True) 
    for i in range(len(removeIndices)):
      selectedContours.pop(removeIndices[i])




  add_contours_to_image(selectedContours, original)
  return original
