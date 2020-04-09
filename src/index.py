import cv2
import PySimpleGUI as sg
import sys
import glob

from data.connect import connect_mongodb_database
from core.visualize import get_window, show_image, resize_image, draw_contour, draw_quadrilaterals, remove_quadrilateral_figure
from core.detection import detect_contours, get_contour, get_contour_with_id, remove_contour
from core.shape import Quadrilateral, Point, Rect, corner_of_quadrilateral
from glob import glob

# mydb = connect_mongodb_database('localhost', 27017, 'computervision', 'devuser', 'devpwd')
# print(mydb.list_collection_names())

# if (mydb == None):
#   exit(-1)



current_action = ""

layout = [
    [sg.Text('Some text on Row 1')],
    [sg.Button('Add')],
    [sg.Button('Remove')],
    [sg.Button('Drag')],
    [sg.Button('Convert')],
    [
        sg.Graph(
            canvas_size=(1000, 800),
            graph_bottom_left=(0, 800),
            graph_top_right=(1000, 0),
            key="graph",
            enable_events=True,
            drag_submits=True,
        )
    ]
]

window = get_window("Assignment 1", layout)
graph = window.Element("graph")

img = cv2.imread('./dataset_pictures_msk/Zaal_1/IMG_20190323_111749.jpg')

img = resize_image(img, 1000/img.shape[1])
invisible_contours = detect_contours(img)

is_success, im_buf_arr = cv2.imencode(".png", img)
byte_im = im_buf_arr.tobytes()

graph.DrawImage(data=byte_im, location=(0,0))

visible_contours = []

dragging = False
dragged_contour = None
dragged_rect_id = None

dragging_quadrilateral = False
current_dragging_quadrilateral = None
current_dragging_quadrilateral_figure = None
dragging_corner_point = None
quadrilateralFigures = []
quadrilaterals = []

def add_contour_event(point):
    contour = get_contour(invisible_contours, point)
    if(contour is not None):
        id = draw_contour(graph, contour)
        visible_contours.append([contour, id])

def remove_contour_event(point):
    contour = get_contour_with_id(visible_contours, point)
    if(contour is not None):
        invisible_contours.append(contour[0])
        id = contour[1]
        graph.DeleteFigure(id)

# def convert_contours_event():
#     for c in visible_contours:
#         quadrilaterals.append(c[0])
#         graph.DeleteFigure(c[1])

#     quadrilateralFigures = draw_quadrilaterals(graph, quadrilaterals)

while True:
    event, values = window.Read()
    if values is not None:
        point = Point(values["graph"][0], values["graph"][1])

    if event == "Add":
        current_action = "add"
    if event == "Remove":
        current_action = "remove"
    if event == "Drag":
        current_action = "drag"
    if event == "Convert":
        # convert_contours_event()
        for c in visible_contours:
            quadrilaterals.append(c[0])
            graph.DeleteFigure(c[1])

        quadrilateralFigures = draw_quadrilaterals(graph, quadrilaterals)
    if event == "graph":
        if(dragging_quadrilateral == False):
            current_dragging_quadrilateral, current_dragging_quadrilateral_figure, dragging_corner_point = corner_of_quadrilateral(point, quadrilaterals, quadrilateralFigures)
            if current_dragging_quadrilateral is not None:
                dragging_quadrilateral = True

        if current_action == "remove":
            remove_contour_event(point)
        
        if current_action == "add":
            add_contour_event(point)
        
        if current_action == "drag":
            if dragging_quadrilateral == False:
                if dragging == False:
                    dragging = True
                    dragged_contour = Rect(point, point)
                
                if dragged_rect_id is not None:
                    graph.DeleteFigure(dragged_rect_id)
                
                dragged_contour = Rect(dragged_contour.TLPoint, point)
                dragged_rect_id = draw_contour(graph, dragged_contour)
            elif dragging_quadrilateral == True:
                # DELETE BY ID
                remove_quadrilateral_figure(graph, current_dragging_quadrilateral_figure)
                        
                dragging_corner_point.x = point.x
                dragging_corner_point.y = point.y

                # DRAW QUADRILATERAL
                quadrilateral_figure = draw_quadrilaterals(graph, [current_dragging_quadrilateral])
                current_dragging_quadrilateral_figure = quadrilateral_figure[0]

    if event == "graph+UP":
        if current_action == "drag":
            if dragging_quadrilateral == False:
                if dragged_rect_id is not None:
                    graph.DeleteFigure(dragged_rect_id)
                dragged_contour = Rect(dragged_contour.TLPoint, point)
                dragged_rect_id = draw_contour(graph, dragged_contour)

                visible_contours.append([dragged_contour, dragged_rect_id])

                dragging = False
                start_of_drag = None
                dragged_rect_id = None

            elif dragging_quadrilateral == True:
                dragging_quadrilateral = False
                current_dragging_quadrilateral = None
                current_dragging_quadrilateral_figure = None
                dragging_corner_point = None
                
    if event == None:
        break

window.close()

# for filename in glob('./dataset_pictures_msk/zaal_*/*.jpg'):
