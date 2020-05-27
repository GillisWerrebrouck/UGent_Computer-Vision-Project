from shapely.geometry import Polygon


def calculate_bounding_box_accuracy(point_list1, point_list2):
    polygon = Polygon(point_list1)
    polygon2 = Polygon(point_list2)
    intersect = polygon.intersection(polygon2)
    union = polygon.area + polygon2.area - intersect.area
    return intersect.area / union
