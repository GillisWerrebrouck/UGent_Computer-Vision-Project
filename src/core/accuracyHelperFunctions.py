from shapely.geometry import Polygon

def calculate_bounding_box_accuracy(pointList1, pointList2):
    polygon = Polygon(pointList1)
    polygon2 = Polygon(pointList2)
    intersect = polygon.intersection(polygon2)
    union = polygon.area + polygon2.area - intersect.area
    return intersect.area / union
