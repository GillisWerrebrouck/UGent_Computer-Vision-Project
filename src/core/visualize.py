import cv2
import numpy as np
import PySimpleGUI as sg
from core.logger import get_root_logger
from core.shape import Point, Rect, Quadrilateral, QuadrilateralFigure

logger = get_root_logger()


def get_window(title, layout):
  """
  Create a PySimpleGUI window with a title and layout.

  Parameters
  ----------
  - title -- The title for the window (will appear in the title bar of the window).
  - layout -- All elements of the window.

  Returns: The created window object.
  """

  logger.info('Creating a window with title: {}'.format(title))

  window = sg.Window(title, layout)
  window.Finalize()
  return window


def draw_contour(graph, contour, width=2, color="red"):
  """
  Draw the given rectangular contour on the canvas (graph).

  Parameters
  ----------
  - graph -- The canvas to draw a contour on.
  - contour -- The contour to draw (object of type Rect).

  Returns: The id of the drawn object.
  """

  (x1, y1) = contour.TLPoint.x, contour.TLPoint.y
  (x2, y2) = contour.BRPoint.x, contour.BRPoint.y
  id = graph.DrawRectangle((x1, y1), (x2, y2), fill_color=None, line_color=color, line_width=width)

  return id


def draw_quadrilaterals(graph, quadrilaterals, point_size=15, width=2, color="red"):
  """
  Draw the given quadrilaterals on the canvas (graph).

  Parameters
  ----------
  - graph -- The canvas to draw figures on.
  - quadrilaterals -- The quadrilateral objects to draw.
  - point_size -- The size of corner points of each quadrilateral.
  - color -- The color of the lines and points of the quadrilaterals.

  Returns: A collection of quadrilateral objects which contain the ids of the lines and corner points that have been drawn.
  """

  quadrilateralFigures = []
  point_shift = point_size/2

  for q in quadrilaterals:
    TopLineId = graph.DrawLine((q.TLPoint.x, q.TLPoint.y), (q.TRPoint.x, q.TRPoint.y), color=color, width=width)
    RightLineId = graph.DrawLine((q.TRPoint.x, q.TRPoint.y), (q.BRPoint.x, q.BRPoint.y), color=color, width=width)
    BottomLineId = graph.DrawLine((q.BRPoint.x, q.BRPoint.y), (q.BLPoint.x, q.BLPoint.y), color=color, width=width)
    LeftLineId = graph.DrawLine((q.BLPoint.x, q.BLPoint.y), (q.TLPoint.x, q.TLPoint.y), color=color, width=width)

    TLPointId = graph.DrawRectangle((q.TLPoint.x - point_shift, q.TLPoint.y - point_shift), (q.TLPoint.x + point_shift, q.TLPoint.y + point_shift), fill_color=color, line_color=None, line_width=None)
    TRPointId = graph.DrawRectangle((q.TRPoint.x - point_shift, q.TRPoint.y - point_shift), (q.TRPoint.x + point_shift, q.TRPoint.y + point_shift), fill_color=color, line_color=None, line_width=None)
    BLPointId = graph.DrawRectangle((q.BLPoint.x - point_shift, q.BLPoint.y - point_shift), (q.BLPoint.x + point_shift, q.BLPoint.y + point_shift), fill_color=color, line_color=None, line_width=None)
    BRPointId = graph.DrawRectangle((q.BRPoint.x - point_shift, q.BRPoint.y - point_shift), (q.BRPoint.x + point_shift, q.BRPoint.y + point_shift), fill_color=color, line_color=None, line_width=None)

    quadrilateralFigures.append(QuadrilateralFigure(TLPointId, TRPointId, BRPointId, BLPointId, TopLineId, RightLineId, BottomLineId, LeftLineId))
  
  return quadrilateralFigures


def remove_quadrilateral_figures(graph, quadrilateral_figures):
  """
  Remove the given quadrilateral figures from the canvas (graph).

  Parameters
  ----------
  - graph -- The canvas to remove figures from.
  - quadrilateral_figures -- The quadrilateral figure objects.
  """

  for quadrilateral_figure in quadrilateral_figures:
    for id in quadrilateral_figure.get_all_ids():
      graph.DeleteFigure(id)


def show_image(title, image):
  """
  Show the given image in a named cv2 window.

  Parameters
  ----------
  - title -- The title of the window.
  - image -- The image to show.
  """

  logger.info('Showing image {} of size {}'.format(title, image.shape[:2]))

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

  Returns: The resized image.
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

  logger.info('Showing DoG filter of size {}'.format(dog.shape[:2]))

  copy = np.array(dog)
  minVal, maxVal = cv2.minMaxLoc(copy)[:2]
  maxVal = max(abs(minVal), maxVal)
  copy /= (maxVal * 2)
  copy += 0.5
  show_image('DoG', copy)

def draw_quadrilaterals_opencv(image, quadrilaterals):
  for q in quadrilaterals:
    cv2.drawContours(image, [q], -1, (0, 0, 255), 2)
  return image