import cv2

def show_image(title, image):
  """
  Show the given image in a named window.

  Parameters
  ----------
  - title -- The title of the window.
  - image -- The image to show.
  """
  cv2.imshow(title, image)
  cv2.waitKey()
  cv2.destroyAllWindows()

def resize_image(image, scale):
  """
  Resize the image with a given scale.

  Parameters
  ----------
  - image -- The image to resize.
  - scale -- The scale value between 0 and 1.
  """
  width = int(image.shape[1] * scale)
  height = int(image.shape[0] * scale)
  dimensions = (width, height)
  return cv2.resize(image, dimensions, interpolation=cv2.INTER_AREA)

def show_dog(dog):
  """
  Visualize a DoG filter.

  Parameters
  ----------
  - dog -- The DoG to visualize.
  """
  copy = np.array(dog)
  minVal, maxVal = cv2.minMaxLoc(copy)[:2]
  maxVal = max(abs(minVal), maxVal)
  copy /= (maxVal * 2)
  copy += 0.5
  show_image('Dog', copy)
