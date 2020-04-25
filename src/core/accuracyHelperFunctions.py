from shapely.geometry import Polygon

# polygon = Polygon([[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]])
# polygon2 = Polygon([(2, 2), (6, 2), (6, 6), (2, 6), (2, 2)])

# x = polygon.intersection(polygon2)
# print(x)

def calculate_bounding_box_accuracy(pointList1, pointList2):
    print("pointlist1: ", pointList1)
    print("pointlist2: ", pointList2)
    polygon = Polygon(pointList1)
    polygon2 = Polygon(pointList2)
    intersect = polygon.intersection(polygon2)
    union = polygon.area + polygon2.area - intersect.area
    return intersect.area / union
