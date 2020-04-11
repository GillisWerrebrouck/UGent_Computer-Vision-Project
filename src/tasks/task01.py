import cv2
import PySimpleGUI as sg
from glob import glob

from core.logger import get_root_logger
from core.visualize import get_window, resize_image, draw_contour, draw_quadrilaterals, remove_quadrilateral_figures
from core.detection import detect_contours, pop_contour, pop_contour_with_id
from core.shape import Point, Rect, Quadrilateral, detect_dragging_quadrilateral

logger = get_root_logger()


# size of the canvas (graph); tuple: (height, width)
graph_size = (800, 800)


def image_to_byte_string(image):
  """
  Convert an image to a byte string.
  This operation is very expensive in terms of performance therefore it should only be used when necessary.

  Parameters
  ----------
  - image -- The image to convert.

  Returns: A byte string of the given image.
  """

  is_success, im_buf_arr = cv2.imencode(".png", image)
  byte_im = im_buf_arr.tobytes()
  return byte_im


def get_image_resize_factor(image):
  """
  Calculates the resize factor for the image to fit in the canvas (graph).

  Parameters
  ----------
  - image -- The image to get the resize factor for.

  Returns: The resize factor for the given image in the canvas.
  """
  
  (height, width) = image.shape[:2]
  (graph_width, graph_height) = graph_size[:2]

  if height >= width:
    return graph_height/height
  
  if height < width:
    return graph_width/width


def get_image_location_in_graph(image):
  """
  Calculates the location of the image in the canvas (graph).
  The location is calculated so that the image is always positioned in the center in both x and y direction.

  Parameters
  ----------
  - image -- The image to get the location for.

  Returns: The location (tuple: (x, y)) for the given image to be positioned in the center of the canvas, based on the size of the image and the canvas.
  """
  
  (height, width) = image.shape[:2]
  (graph_width, graph_height) = graph_size[:2]

  if height == graph_height:
    return ((graph_width-width)/2, 0)
  
  if width == graph_width:
    return (0, (graph_height-height)/2)


def show_next_image(graph, filenames):
  """
  Display the next image in the canvas (graph).

  Parameters
  ----------
  - graph -- The canvas element to display the image in.
  - filenames -- Used as queue of filenames, the image to be displayed is removed from the queue.

  Returns: The detected contours in the image with its coordinates relative to the current image size.
  """
  
  if len(filenames) == 0:
    return
  
  filepath = filenames[0]
  filenames.remove(filenames[0])

  logger.info('Loading next image; {}'.format(filepath))

  img = cv2.imread(filepath)

  factor = get_image_resize_factor(img)
  img = resize_image(img, factor)

  detected_contours = detect_contours(img)
  graph.erase()

  loc = get_image_location_in_graph(img)

  # reset the coordinate system of the graph to display the image
  graph.change_coordinates((0, graph_size[1]), (graph_size[0], 0))
  byte_string = image_to_byte_string(img)
  graph.DrawImage(data=byte_string, location=loc)

  (graph_width, graph_height) = graph_size[:2]
  # change the coordinate system of the canvas (graph) to be according to the displayed (centered) image
  graph.change_coordinates((-loc[0], graph_size[1]-loc[1]), (graph_size[0]-loc[0], -loc[1]))

  return detected_contours


def on_add_contour_event(point, graph, visible_contours, invisible_contours):
  """
  Function as part of the event loop (while True ...) to add contours by clicking on the image.

  Parameters
  ----------
  - point -- The position of the cursor when the event was triggered.
  - graph -- The canvas element in which the click event occured.
  - visible_contours -- All visible rectangular contours (not quadrilateral).
  - invisible_contours -- All invisible rectangular contours.
  """

  logger.info('Add-contour-event triggered')
  
  contour = pop_contour(point, invisible_contours)
  if(contour is not None):
    id = draw_contour(graph, contour, color="red")
    visible_contours.append([contour, id])


def on_remove_contour_event(point, graph, visible_contours, invisible_contours):
  """
  Function as part of the event loop (while True ...) to remove contours (make invisible) by clicking on the image.
  The contour in which has been clicked is removed.

  Parameters
  ----------
  - point -- The position of the cursor when the event was triggered.
  - graph -- The canvas element in which the click event occured.
  - visible_contours -- All visible rectangular contours (not quadrilateral).
  - invisible_contours -- All invisible rectangular contours.
  """

  logger.info('Remove-contour-event triggered')

  contour = pop_contour_with_id(point, visible_contours)
  if(contour is not None):
    invisible_contours.append(contour[0])
    id = contour[1]
    graph.DeleteFigure(id)


def on_convert_contours_event(graph, visible_contours, invisible_contours, all_quadrilaterals, all_quadrilateral_figures):
  """
  Function as part of the event loop (while True ...) to convert contours from rectangular contours to quadrilateral objects.
  All visible contours become quadrilateral figures and the original contours are made invisible.

  Parameters
  ----------
  - graph -- The canvas element in which the click event occured.
  - visible_contours -- All visible rectangular contours (not quadrilateral).
  - invisible_contours -- All invisible rectangular contours.
  - all_quadrilaterals -- All quadrilateral contours objects.
  - all_quadrilateral_figures -- All quadrilateral figure objects.

  Returns: The converted and drawn quadrilateral figure objects.
  """

  logger.info('Convert-contours-event triggered')

  for c in visible_contours:
    all_quadrilaterals.append(c[0])
    graph.DeleteFigure(c[1])
    invisible_contours.append(c[0])
  visible_contours = []
  remove_quadrilateral_figures(graph, all_quadrilateral_figures)
  return draw_quadrilaterals(graph, all_quadrilaterals, color="red")


def run_task_01(db_connection):
  """
  Run task 1.
  Open a window and display the first image.

  Parameters
  ----------
  - db_connection -- The database connection to use for database queries.
  """

  logger.info('Task 1 started')

  # variables to drag a rectangle contour
  dragging_contour = False
  current_dragging_contour = None
  current_dragging_contour_id = None

  # variables to drag a quadrilateral by dragging its points
  dragging_quadrilateral = False
  current_dragging_quadrilateral = None
  current_dragging_quadrilateral_figure = None
  dragging_corner_point = None
  all_quadrilaterals = []
  all_quadrilateral_figures = []
  
  # the current selected action
  current_action = "add"

  # read all filenames
  filenames = glob('./data/dataset_pictures_msk/zaal_*/*.jpg')

  # the layout of the window
  layout = [
    [sg.Text('Add, remove and modify contours in the displayed images by using the provided actions.', font=('Helvetica', 12, ''))], 
    [
      sg.Button('Add', font=('Helvetica', 10, '')), 
      sg.Button('Remove', font=('Helvetica', 10, '')), 
      sg.Button('Drag', font=('Helvetica', 10, '')), 
      sg.Button('Convert', font=('Helvetica', 10, '')), 
      sg.Button('Clear canvas', font=('Helvetica', 10, '')), 
      sg.Button('Save to database', font=('Helvetica', 10, '')), 
      sg.Button('Next image', font=('Helvetica', 10, ''))
    ],
    [sg.Frame('Image',[[
      sg.Graph(
        canvas_size=graph_size,
        graph_bottom_left=(0, graph_size[1]),
        graph_top_right=(graph_size[0], 0),
        key="graph",
        pad=None,
        enable_events=True,
        drag_submits=True,
      )
    ]])]
  ]

  # close the window if no filenames could be found
  if len(filenames) != 0:
    window = get_window("Task 1", layout)
    graph = window.Element("graph")
  else:
    return

  visible_contours = []
  old_filenames = filenames.copy()
  # display the first image
  invisible_contours = show_next_image(graph, filenames)

  logger.info('Starting event loop of task 1')

  # the event loop
  while True:
      event, values = window.Read()
      if values is not None:
          point = Point(values["graph"][0], values["graph"][1])

      # button click events
      if event == "Add":
        current_action = "add"
      if event == "Remove":
        current_action = "remove"
      if event == "Drag":
        current_action = "drag"
      if event == "Convert":
        all_quadrilateral_figures = on_convert_contours_event(graph, visible_contours, invisible_contours, all_quadrilaterals, all_quadrilateral_figures)
        visible_contours = []
      if event == "Clear canvas":
        graph.erase()
        temp_old_filenames = old_filenames.copy()
        show_next_image(graph, old_filenames)
        old_filenames = temp_old_filenames

        all_quadrilaterals = []
        all_quadrilateral_figures = []

        for contour in visible_contours:
          invisible_contours.append(contour[0])
        visible_contours = []
      
      if event == "Save to database":
        for quadrilateral in all_quadrilaterals:
          x1 = quadrilateral.TLPoint.x
          y1 = quadrilateral.TLPoint.y
          x2 = quadrilateral.TRPoint.x
          y2 = quadrilateral.TRPoint.y
          x3 = quadrilateral.BRPoint.x
          y3 = quadrilateral.BRPoint.y
          x4 = quadrilateral.BLPoint.x
          y4 = quadrilateral.BLPoint.y

          print("[SAVE TO DATABASE] P(" + str(x1) + ", " + str(y1) + ") - P(" + str(x2) + ", " + str(y2) + ") - P(" + str(x3) + ", " + str(y3) + ") - P(" + str(x4) + ", " + str(y4) + ")")
          # TODO: call a funcion, preferably a function in the data folder in the connect.py file, to save an image with its points, keypoints and feature vector (histogram, etc.) to the db

      if event == "Next image":
        if len(filenames) == 0:
          window.close()
          return
        
        visible_contours = []
        old_filenames = filenames.copy()
        invisible_contours = show_next_image(graph, filenames)
        all_quadrilaterals = []
        all_quadrilateral_figures = []
      
      # the canvas (graph) events
      if event == "graph":
        if current_action == "add":
          on_add_contour_event(point, graph, visible_contours, invisible_contours)
        
        if current_action == "remove":
          on_remove_contour_event(point, graph, visible_contours, invisible_contours)
        
        if current_action == "drag":
          if(dragging_contour == False and dragging_quadrilateral == False):
            current_dragging_quadrilateral, current_dragging_quadrilateral_figure, dragging_corner_point = detect_dragging_quadrilateral(point, all_quadrilaterals, all_quadrilateral_figures)
            
            if current_dragging_quadrilateral is not None:
              dragging_quadrilateral = True

          if dragging_quadrilateral == False:
            if dragging_contour == False:
              dragging_contour = True
              current_dragging_contour = Rect(point, point)
            
            if current_dragging_contour_id is not None:
              graph.DeleteFigure(current_dragging_contour_id)
            
            current_dragging_contour = Rect(current_dragging_contour.TLPoint, point)
            current_dragging_contour_id = draw_contour(graph, current_dragging_contour, color="red")
          
          elif dragging_quadrilateral == True:
            dragging_corner_point.x = point.x
            dragging_corner_point.y = point.y
            remove_quadrilateral_figures(graph, all_quadrilateral_figures)
            all_quadrilateral_figures = draw_quadrilaterals(graph, all_quadrilaterals, color="red")

      if event == "graph+UP":
        if current_action == "drag":
          if dragging_quadrilateral == False:
            if current_dragging_contour_id is not None:
              graph.DeleteFigure(current_dragging_contour_id)

            if current_dragging_contour is not None:
              current_dragging_contour = Rect(current_dragging_contour.TLPoint, point)
              current_dragging_contour_id = draw_contour(graph, current_dragging_contour, color="red")

              visible_contours.append([current_dragging_contour, current_dragging_contour_id])

            dragging_contour = False
            start_of_drag = None
            current_dragging_contour_id = None

          elif dragging_quadrilateral == True:
            dragging_quadrilateral = False
            current_dragging_quadrilateral = None
            current_dragging_quadrilateral_figure = None
            dragging_corner_point = None
                  
      if event == None:
        break

  window.close()
