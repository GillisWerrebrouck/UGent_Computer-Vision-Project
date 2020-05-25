# A point is a coordinate with an x and y value
class Point:
    x = None
    y = None

    def __init__(self, x, y):
        self.x = x
        self.y = y


# A quadrilateral is an object which has 4 points which are of type Point.
class Quadrilateral:
    TLPoint = None
    TRPoint = None
    BLPoint = None
    BRPoint = None

    def __init__(self, TL, TR, BL, BR):
        self.TLPoint = TL
        self.TRPoint = TR
        self.BLPoint = BL
        self.BRPoint = BR


# A quadrilateral figure is an object which has 4 point ids and 4 line ids
# these are the ids of the drawn figures in a canvas (graph).
class QuadrilateralFigure:
    TLPointId = None
    TRPointId = None
    BLPointId = None
    BRPointId = None
    TopLineId = None
    RightLineId = None
    BottomLineId = None
    LeftLineId = None

    def __init__(self, TL, TR, BL, BR, T, R, B, L):
        self.TLPointId = TL
        self.TRPointId = TR
        self.BLPointId = BL
        self.BRPointId = BR
        self.TopLineId = T
        self.RightLineId = R
        self.BottomLineId = B
        self.LeftLineId = L

    def get_all_ids(self):
        return [
            self.TLPointId, self.TRPointId, self.BLPointId, self.BRPointId,
            self.TopLineId, self.RightLineId, self.BottomLineId, self.LeftLineId,
        ]


# A rect is an object which inherits from Quadrilateral and for which the constructor only needs 2 point
# (top left and bottom right).
class Rect(Quadrilateral):
    def __init__(self, point1, point2):
        Quadrilateral.__init__(self, point1, Point(point2.x, point1.y), Point(point1.x, point2.y), point2)

    # Check if a point exists within this rectangle.
    def has_point(self, point):
        x1 = min(self.TLPoint.x, self.TRPoint.x)
        y1 = min(self.TLPoint.y, self.BLPoint.y)
        x2 = max(self.TLPoint.x, self.TRPoint.x)
        y2 = max(self.TLPoint.y, self.BLPoint.y)

        return x1 <= point.x <= x2 and y1 <= point.y <= y2


def detect_dragging_quadrilateral(point, quadrilaterals, quadrilateral_figures, point_size=15):
    """
    Detect if the current point is on one of the corner points of a quadrilateral within a range of point_size.

    Parameters
    ----------
    - point -- The coordinate of the point to check.
    - quadrilaterals -- All quadrilateral objects.
    - quadrilateral_figures -- All quadrilateral figure objects.
    - point_size -- The size of the corner points as drawn on the canvas (graph).

    Returns
    -------
    The quadrilateral object and quadrilateral figure object which is detected with the point and the corner
    point which the point is in range from. Or none if none is detected.
    """

    point_shift = point_size / 2

    for q, qf in zip(quadrilaterals, quadrilateral_figures):
        if q.TLPoint.x - point_shift <= point.x <= q.TLPoint.x + point_shift and q.TLPoint.y - point_shift <= point.y <= q.TLPoint.y + point_shift:
            return q, qf, q.TLPoint
        elif q.TRPoint.x - point_shift <= point.x <= q.TRPoint.x + point_shift and q.TRPoint.y - point_shift <= point.y <= q.TRPoint.y + point_shift:
            return q, qf, q.TRPoint
        elif q.BRPoint.x - point_shift <= point.x <= q.BRPoint.x + point_shift and q.BRPoint.y - point_shift <= point.y <= q.BRPoint.y + point_shift:
            return q, qf, q.BRPoint
        elif q.BLPoint.x - point_shift <= point.x <= q.BLPoint.x + point_shift and q.BLPoint.y - point_shift <= point.y <= q.BLPoint.y + point_shift:
            return q, qf, q.BLPoint

    return None, None, None
