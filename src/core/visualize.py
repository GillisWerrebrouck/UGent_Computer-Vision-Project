import cv2
import PySimpleGUI as sg
from core.logger import get_root_logger
from core.shape import Quadrilateral, Point, QuadrilateralFigure

logger = get_root_logger()

def get_window(title, layout):
  window = sg.Window(title, layout)
  window.Finalize()
  return window

def draw_contour(graph, contour):
  (x1, y1) = contour.TLPoint.x, contour.TLPoint.y
  (x2, y2) = contour.BRPoint.x, contour.BRPoint.y
  id = graph.DrawRectangle((x1, y1), (x2, y2), line_color="red")
  
  return id

def draw_quadrilaterals(graph, quadrilaterals):
    quadrilateralFigures = []
    point_size = 10
    point_shift = point_size/2
    for q in quadrilaterals:
        TopLineId = graph.DrawLine((q.TLPoint.x, q.TLPoint.y), (q.TRPoint.x, q.TRPoint.y), color="green", width=1)
        RightLineId = graph.DrawLine((q.TRPoint.x, q.TRPoint.y), (q.BRPoint.x, q.BRPoint.y), color="green", width=1)
        BottomLineId = graph.DrawLine((q.BRPoint.x, q.BRPoint.y), (q.BLPoint.x, q.BLPoint.y), color="green", width=1)
        LeftLineId = graph.DrawLine((q.BLPoint.x, q.BLPoint.y), (q.TLPoint.x, q.TLPoint.y), color="green", width=1)

        TLPointId = graph.DrawRectangle((q.TLPoint.x - point_shift, q.TLPoint.y - point_shift), (q.TLPoint.x + point_shift, q.TLPoint.y + point_shift), fill_color="green", line_color=None, line_width=None)
        TRPointId = graph.DrawRectangle((q.TRPoint.x - point_shift, q.TRPoint.y - point_shift), (q.TRPoint.x + point_shift, q.TRPoint.y + point_shift), fill_color="green", line_color=None, line_width=None)
        BLPointId = graph.DrawRectangle((q.BLPoint.x - point_shift, q.BLPoint.y - point_shift), (q.BLPoint.x + point_shift, q.BLPoint.y + point_shift), fill_color="green", line_color=None, line_width=None)
        BRPointId = graph.DrawRectangle((q.BRPoint.x - point_shift, q.BRPoint.y - point_shift), (q.BRPoint.x + point_shift, q.BRPoint.y + point_shift), fill_color="green", line_color=None, line_width=None)

        quadrilateralFigures.append(QuadrilateralFigure(TLPointId, TRPointId, BRPointId, BLPointId, TopLineId, RightLineId, BottomLineId, LeftLineId))
    
    return quadrilateralFigures

def remove_quadrilateral_figure(graph, quadrilateral_figure):
    if quadrilateral_figure is not None:
        graph.DeleteFigure(quadrilateral_figure.TLPointId)
        graph.DeleteFigure(quadrilateral_figure.TRPointId)
        graph.DeleteFigure(quadrilateral_figure.BLPointId)
        graph.DeleteFigure(quadrilateral_figure.BRPointId)
        graph.DeleteFigure(quadrilateral_figure.TopLineId)
        graph.DeleteFigure(quadrilateral_figure.RightLineId)
        graph.DeleteFigure(quadrilateral_figure.BottomLineId)
        graph.DeleteFigure(quadrilateral_figure.LeftLineId)


def show_image(title, image):
  """
  Show the given image in a named window.

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
