import cv2
import numpy as np
from core.visualize import show_image, resize_image
import os
import copy
import sys
import core.selectinwindow as window

# TODO: consistentie naamgeving, soms capitalCasing, soms niet_capital_casing

resize_factor = 5

def onMouse(k, x, y, s, param):
    if k == cv2.EVENT_LBUTTONDOWN:
        param.append((x*resize_factor, y*resize_factor))

def add_contours_to_image(contours, image):
  # de contours zijn van de vorm list(tuple(x, y, w, h))
  for c in contours:
    (x, y, w, h) = c
    image = cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 14)
  return image

def show_contours(title, image, clicks, contours):
  temp_img = copy.deepcopy(image)
  add_contours_to_image(contours, temp_img)
  temp_img = resize_image(temp_img, 1.0/resize_factor)
  cv2.namedWindow(title)
  cv2.setMouseCallback(title, onMouse, clicks)
  cv2.imshow(title, temp_img)
  os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

# Zegt of het punt in de contour ligt. positieve waarde is binnen, negatieve is buiten. grootte is de afstand
# Dit is een naïve methode en controleert enkel horizontal afstand bij verticale lijnen 
# Methode van opencv werkt niet correct: https://docs.opencv.org/3.4/d3/dc0/group__imgproc__shape.html#ga1a539e8db2135af2566103705d7a5722
def pointContourTest(contour, point):
  (x, y, w, h) = contour
  X, Y = point
  dist = abs(x - X)
  dist = min(dist, abs(y - Y))
  dist = min(dist, abs((x + w) - X))
  dist = min(dist, abs((y + h) - Y))
  if(not (point[0] >= x and point[0] <= x + w and point[1] >= y and point[1] <= y + h)):
    dist = dist * -1
  return dist


def detect_corners3(image):
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

  # Te kleine contours wegfilteren
  temp_contours = []
  for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    if (w >= minWidth and h >= minHeight):
      temp_contours.append(contour)
  contours = temp_contours

  mouseClicks = []
  # Bij selected contours wordt overgegaan naar rectangles vanwege makkelijker gebruik. Deze selectedContours zijn van de vorm list(tuple(x, y, w, h))
  selectedContours = []
  show_contours('Klik op schilderijen om de randen te detecteren, enter om door te gaan', image, mouseClicks, selectedContours)

  previous_amount_of_clicks = len(mouseClicks)
  key = cv2.waitKey(10)
  while(key != 13):
      key = cv2.waitKey(10)
      if(len(mouseClicks) > previous_amount_of_clicks):
        selectedContours = []
        previous_amount_of_clicks = len(mouseClicks)
        # Selecteren welke contouren we willen behouden
        for contour in contours:
          #TODO: hier zijn performantie mogelijkheden misschien mogelijk, dezelfde mouseClicks worden per klik allemaal opnieuw overlopen, als dit aangepast wordt moet wel opgelet worden op duplicate contours!
          for click in mouseClicks:
            x, y, w, h = cv2.boundingRect(contour)
            if(pointContourTest((x, y, w, h), click) >= 0):
              selectedContours.append((x, y, w, h))
              break
        show_contours('Klik op schilderijen om de randen te detecteren, enter om door te gaan', image, mouseClicks, selectedContours)
        



  # Kijk bij welke contour een klik het dichtste ligt en verwijder deze
  if(len(selectedContours) > 0):
    mouseClicks = []

    cv2.destroyAllWindows()
    show_contours('Klik zo dicht mogelijk bij de randen van de te verwijderen contouren, enter om door te gaan', image, mouseClicks, selectedContours)

    key = cv2.waitKey(10)
    while(key != 13):
        key = cv2.waitKey(10)
        if(len(mouseClicks) > 0):
          dist = sys.maxsize
          index = -1 
          for i in range(len(selectedContours)):
            if(abs(pointContourTest(selectedContours[i], mouseClicks[0])) < dist):
              dist = abs(pointContourTest(selectedContours[i], mouseClicks[0]))
              index = i
          selectedContours.pop(index)
          mouseClicks = []
          show_contours('Klik zo dicht mogelijk bij de randen van de te verwijderen contouren, enter om door te gaan', image, mouseClicks, selectedContours)
  




  # Nieuwe vierkanten bijtekenen
  mouseClicks = []
  cv2.destroyAllWindows()
  #TODO: willen we eender welke overeenstaande hoeken toestaan?
  show_contours('Klik op de linker bovenhoek en de rechter onderhoek van een schilderij om een nieuwe contour te tekenen, enter om door te gaan', image, mouseClicks, selectedContours)

  key = cv2.waitKey(10)
  while(key != 13):
    key = cv2.waitKey(10)
    if(len(mouseClicks) == 2):
      # Naief: eerste click is linksboven, tweede rechtsonder
      (x1, y1) = mouseClicks[0]
      (x2, y2) = mouseClicks[1]
      selectedContours.append((x1, y1, abs(x1 - x2), abs(y1 - y2)))
      mouseClicks = []
      show_contours('Klik op de linker bovenhoek en de rechter onderhoek van een schilderij om een nieuwe contour te tekenen, enter om door te gaan', image, mouseClicks, selectedContours)



  # TODO: contour initieel tonen
  # TODO: resultaat terug geven bij dubbelklik
  # TODO: alle contouren oplossing vinden
  # Contouren verfijnen
  cv2.destroyAllWindows()
  # Set recursion limit
  sys.setrecursionlimit(10 ** 9)
  # Define the drag object
  quadrilateral = window.dragRect 
  wName = "click to edit contour or enter to approve"
  temp_img = copy.deepcopy(image)
  temp_img = resize_image(temp_img, 1.0/resize_factor)
  window.init(quadrilateral, temp_img, selectedContours, wName, temp_img.shape[1], temp_img.shape[0], resize_factor)

  cv2.namedWindow(quadrilateral.wname)
  cv2.setMouseCallback(quadrilateral.wname, window.dragrect, quadrilateral)

  # keep looping until rectangle finalized
  key = cv2.waitKey(10)
  while (key != 13):
      # display the image
      cv2.imshow(wName, quadrilateral.image)
      key = cv2.waitKey(1)

  print("Dragged quadrilateral coordinates")
  print(str(quadrilateral.outQuad.LUPoint.printit()) + ',' + str(quadrilateral.outQuad.RUPoint.printit()) + ',' + str(quadrilateral.outQuad.LBPoint.printit()) + ',' + str(quadrilateral.outQuad.RBPoint.printit()))


  cv2.destroyAllWindows()
  add_contours_to_image(selectedContours, image)
  return image
