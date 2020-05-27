import pyximport
pyximport.install(language_level='3')

import cv2
import PySimpleGUI as sg
from glob import glob
from os.path import basename, dirname

from core.logger import get_root_logger
from core.visualize import get_window, resize_image, draw_contour, draw_quadrilaterals, remove_quadrilateral_figures
from core.detection import detect_contours, pop_contour, pop_contour_with_id
from core.extractFeatures import extract_features
from core.shape import Point, Rect, detect_dragging_quadrilateral
from core.cornerHelpers import sort_corners, convert_corners_to_uniform_format
from data.imageRepo import create_image

logger = get_root_logger()


# size of the canvas (graph); tuple: (width, height)
graph_size = (600, 500)


def image_to_byte_string(image):
    """
    Convert an image to a byte string.
    This operation is very expensive in terms of performance therefore it should only be used when necessary.

    Parameters
    ----------
    - image -- The image to convert.

    Returns: A byte string of the given image.
    """

    # Use PPM encoding because PySimpleGUI doesn't support png encoding on macOS
    is_success, im_buf_arr = cv2.imencode(".ppm", image)
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

    # get minimal resize factor for best fit in canvas (graph)
    return min(graph_height/height, graph_width/width)


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


def show_next_image(graph, filenames, file_number):
    """
    Display the image in the canvas (graph) at position file_counter in filenames.

    Parameters
    ----------
    - graph -- The canvas element to display the image in.
    - filenames -- All filenames.
    - file_number -- The file to display.

    Returns: The detected contours in the image with its coordinates relative to the current image size.
    """

    if len(filenames) <= file_number:
        return None

    filepath = filenames[file_number]

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
    graph.change_coordinates(
        (-loc[0], graph_size[1]-loc[1]), (graph_size[0]-loc[0], -loc[1]))

    return (detected_contours, filepath, img.shape[:2], img)


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


def on_draw_event(point, graph, dragging_contour, current_dragging_contour, current_dragging_contour_id):
    """
    Function as part of the event loop (while True ...) to draw a contour.

    Parameters
    ----------
    - point -- The position of the cursor when the event was triggered.
    - graph -- The canvas element in which the click event occured.
    - dragging_contour -- Boolean value that indicates that drawing a contour is in progress.
    - current_dragging_contour -- The contour that is being drawn.
    - current_dragging_contour_id -- The id of the contour that is being drawn.

    Returns: The updated values for dragging_contour, current_dragging_contour and current_dragging_contour_id.
    """

    if dragging_contour == False:
        dragging_contour = True
        current_dragging_contour = Rect(point, point)

    if current_dragging_contour_id is not None:
        graph.DeleteFigure(current_dragging_contour_id)

    current_dragging_contour = Rect(current_dragging_contour.TLPoint, point)
    current_dragging_contour_id = draw_contour(
        graph, current_dragging_contour, color="red")

    return dragging_contour, current_dragging_contour, current_dragging_contour_id


def on_draw_done_event(point, graph, dragging_contour, current_dragging_contour, current_dragging_contour_id, visible_contours):
    """
    Function as part of the event loop (while True ...) that indicates the end of drawing a contour.

    Parameters
    ----------
    - point -- The position of the cursor when the event was triggered.
    - graph -- The canvas element in which the click event occured.
    - dragging_contour -- Boolean value that indicates that drawing a contour is in progress.
    - current_dragging_contour -- The contour that is being drawn.
    - current_dragging_contour_id -- The id of the contour that is being drawn.
    - visible_contours -- The visible contours on the canvas (graph). A drawn contour is added to the visible contours.

    Returns: The updated values for dragging_contour, current_dragging_contour, current_dragging_contour_id and visible_contours.
    """

    if current_dragging_contour_id is not None:
        graph.DeleteFigure(current_dragging_contour_id)

    if current_dragging_contour is not None:
        current_dragging_contour = Rect(
            current_dragging_contour.TLPoint, point)
        current_dragging_contour_id = draw_contour(
            graph, current_dragging_contour, color="red")

        visible_contours.append(
            [current_dragging_contour, current_dragging_contour_id])

    dragging_contour = False
    current_dragging_contour_id = None

    return dragging_contour, current_dragging_contour, current_dragging_contour_id, visible_contours


def on_drag_event(point, graph, dragging_quadrilateral, dragging_corner_point, all_quadrilaterals, all_quadrilateral_figures):
    """
    Function as part of the event loop (while True ...) to drag a contour.

    Parameters
    ----------
    - point -- The position of the cursor when the event was triggered.
    - graph -- The canvas element in which the click event occured.
    - dragging_quadrilateral -- Boolean value that indicates that dragging a contour is in progress.
    - dragging_corner_point -- The current corner point that is being dragged.
    - all_quadrilaterals -- A list with all qudrilateral objects on the canvas (graph).
    - all_quadrilateral_figures -- A list with all qudrilateral figure objects on the canvas (graph).

    Returns: The updated values for dragging_quadrilateral, all_quadrilaterals, all_quadrilateral_figures and dragging_corner_point.
    """

    if(dragging_quadrilateral == False):
        current_dragging_quadrilateral, current_dragging_quadrilateral_figure, dragging_corner_point = detect_dragging_quadrilateral(
            point, all_quadrilaterals, all_quadrilateral_figures)

        if current_dragging_quadrilateral is not None:
            dragging_quadrilateral = True

    if dragging_quadrilateral == True:
        dragging_corner_point.x = point.x
        dragging_corner_point.y = point.y
        remove_quadrilateral_figures(graph, all_quadrilateral_figures)
        all_quadrilateral_figures = draw_quadrilaterals(
            graph, all_quadrilaterals, color="red")

    return dragging_quadrilateral, all_quadrilaterals, all_quadrilateral_figures, dragging_corner_point


def on_drag_done_event(dragging_quadrilateral, current_dragging_quadrilateral, current_dragging_quadrilateral_figure, dragging_corner_point):
    """
    Function as part of the event loop (while True ...) that indicates the end of dragging a contour.

    Parameters
    ----------
    - dragging_quadrilateral -- Boolean value that indicates that dragging a contour is in progress.
    - current_dragging_quadrilateral -- The quadrilateral object that has been dragged.
    - current_dragging_quadrilateral_figure -- The quadrilateral figure object that has been dragged.
    - dragging_corner_point -- The current corner point that has been dragged.

    Returns: The updated values for dragging_quadrilateral, current_dragging_quadrilateral, current_dragging_quadrilateral_figure and dragging_corner_point.
    """

    if dragging_quadrilateral == True:
        dragging_quadrilateral = False
        current_dragging_quadrilateral = None
        current_dragging_quadrilateral_figure = None
        dragging_corner_point = None

    return dragging_quadrilateral, current_dragging_quadrilateral, current_dragging_quadrilateral_figure, dragging_corner_point


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


def set_button_color(window, btn_id, colors):
    """
    Set the color of the given button.

    Parameters
    ----------
    - window -- Reference to the window the button lives in.
    - btnId -- The name of the button to change.
    - color -- The color to set as the button's fore- and backgroundcolor, e.g. ('white', 'red').
    """

    if (btn_id is not None):
        btn = window.FindElement(btn_id)

        if (btn is not None):
            btn.Update(button_color=colors)


def toggle_active_button(window, current_active_btn, new_active_btn):
    """
    Change the currently active button.

    Parameters
    ----------
    - window -- Reference to the window the button lives in.
    - current_active_btn -- The name of the currently active button.
    - new_active_btn -- The name of the button that needs to become active.
    """

    set_button_color(window, current_active_btn, sg.DEFAULT_BUTTON_COLOR)
    set_button_color(window, new_active_btn, ('white', 'red'))


def get_room_from_file(filepath):
    """
    Parameters
    ----------
    - filepath -- The path to extract the room from.

    Returns
    -------
    The room this image is taken.
    """
    dirs = dirname(filepath).split('/')
    room = dirs[-1].split('_')[1]
    return room



def run_task_01():
    """
    Run task 1.
    Open a window and display the first image.
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

    # the previous event (used for active buttons)
    previous_event = "Add"

    # read all filenames
    filenames = glob('./datasets/images/dataset_pictures_msk/zaal_*/*.jpg')

    # the layout of the window
    layout = [
        [sg.Text('Add, remove and modify contours in the displayed images by using the provided actions.', font=(
            'Helvetica', 12, ''))],
        [
            sg.Button('Add', font=('Helvetica', 10, '')),
            sg.Button('Remove', font=('Helvetica', 10, '')),
            sg.Button('Draw', font=('Helvetica', 10, '')),
            sg.Button('Drag', font=('Helvetica', 10, '')),
            sg.Button('Convert', font=('Helvetica', 10, '')),
            sg.Button('Clear canvas', font=('Helvetica', 10, '')),
            sg.Button('Save to database', font=('Helvetica', 10, '')),
            sg.Button('Next image', font=('Helvetica', 10, '')),
            sg.StatusBar('---/---', key='file_counter',
                         font=('Helvetica', 12, '')),
        ],
        [sg.Frame('Image', [[
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
    file_counter = 0
    # display the first image
    invisible_contours, filepath, img_shape, img = show_next_image(
        graph, filenames, file_counter)
    room = get_room_from_file(filepath)

    window.FindElement("file_counter").Update(
        value=(str(file_counter+1) + "/" + str(len(filenames))))

    logger.info('Starting event loop of task 1')

    # show to the user the active button ('Add' on start)
    toggle_active_button(window, previous_event, 'Add')

    # the event loop
    while True:
        event, values = window.Read()
        if values is not None:
            point = Point(values["graph"][0], values["graph"][1])

        if (event is not None and event in ('Add', 'Remove', 'Draw', 'Drag')):
            toggle_active_button(window, previous_event, event)
            previous_event = event

        # button click events
        if event == "Add":
            current_action = "add"
        if event == "Remove":
            current_action = "remove"
        if event == "Draw":
            current_action = "draw"
        if event == "Drag":
            current_action = "drag"
        if event == "Convert":
            all_quadrilateral_figures = on_convert_contours_event(
                graph, visible_contours, invisible_contours, all_quadrilaterals, all_quadrilateral_figures)
            visible_contours = []
        if event == "Clear canvas":
            graph.erase()
            invisible_contours, filepath, img_shape, img = show_next_image(
                graph, filenames, file_counter)
            room = get_room_from_file(filepath)
            all_quadrilaterals = []
            all_quadrilateral_figures = []

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

                # sort the corners on y-coordinate, then on x: order will be TL, TR, BL, BR
                # and map to a percentage in the painting
                uniform_corners = convert_corners_to_uniform_format([
                    [x1, y1],
                    [x2, y2],
                    [x3, y3],
                    [x4, y4],
                ], img_shape[0], img_shape[1])
                uniform_corners = sort_corners(uniform_corners)

                full_histogram, block_histogram, LBP_histogram = extract_features(img, uniform_corners, False)

                image = {
                    'filename': basename(filepath),
                    'corners': uniform_corners,
                    'room': room,
                    'full_histogram': full_histogram,
                    'block_histogram': block_histogram,
                    'LBP_histogram': LBP_histogram
                }

                create_image(image)

        if event in ("Next image", "Save to database"):
            if len(filenames) == 0:
                window.close()
                return

            visible_contours = []
            file_counter += 1
            invisible_contours, filepath, img_shape, img = show_next_image(
                graph, filenames, file_counter)
            room = get_room_from_file(filepath)
            if invisible_contours is None:
                break

            window.FindElement("file_counter").Update(
                value=(str(file_counter+1) + "/" + str(len(filenames))))

            # make add again the current action
            toggle_active_button(window, previous_event, 'Add')
            previous_event = 'Add'
            current_action = 'add'

            all_quadrilaterals = []
            all_quadrilateral_figures = []

        # the canvas (graph) events
        if event == "graph":
            if current_action == "add":
                on_add_contour_event(
                    point, graph, visible_contours, invisible_contours)

            if current_action == "remove":
                on_remove_contour_event(
                    point, graph, visible_contours, invisible_contours)

            if current_action == "draw":
                dragging_contour, current_dragging_contour, current_dragging_contour_id = on_draw_event(
                    point, graph, dragging_contour, current_dragging_contour, current_dragging_contour_id)

            if current_action == "drag":
                dragging_quadrilateral, all_quadrilaterals, all_quadrilateral_figures, dragging_corner_point = on_drag_event(
                    point, graph, dragging_quadrilateral, dragging_corner_point, all_quadrilaterals, all_quadrilateral_figures)

        if event == "graph+UP" and current_action == "draw":
            dragging_contour, current_dragging_contour, current_dragging_contour_id, visible_contours = on_draw_done_event(
                point, graph, dragging_contour, current_dragging_contour, current_dragging_contour_id, visible_contours)

        if event == "graph+UP" and current_action == "drag":
            dragging_quadrilateral, current_dragging_quadrilateral, current_dragging_quadrilateral_figure, dragging_corner_point = on_drag_done_event(
                dragging_quadrilateral, current_dragging_quadrilateral, current_dragging_quadrilateral_figure, dragging_corner_point)

        if event == None:
            break

    window.close()
