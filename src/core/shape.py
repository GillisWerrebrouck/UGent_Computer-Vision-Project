class Point:
    x = None
    y = None

    def __init__(self, x, y):
        self.x = x
        self.y = y

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

class Rect(Quadrilateral):
    def __init__(self, point1, point2):
        Quadrilateral.__init__(self, point1, Point(point2.x, point1.y), Point(point1.x, point2.y), point2)
    
    def has_point(self, point):
        x1 = min(self.TLPoint.x, self.TRPoint.x)
        y1 = min(self.TLPoint.y, self.BLPoint.y)
        x2 = max(self.TLPoint.x, self.TRPoint.x)
        y2 = max(self.TLPoint.y, self.BLPoint.y)

        if(x1 <= point.x <= x2 and y1 <= point.y <= y2):
            return True
        return False

def corner_of_quadrilateral(point, quadrilaterals, quadrilateralFigures):
    point_size = 10
    point_shift = point_size/2
    
    for q, qf in zip(quadrilaterals, quadrilateralFigures):
        if q.TLPoint.x-point_shift <= point.x <= q.TLPoint.x+point_shift and q.TLPoint.y-point_shift <= point.y <= q.TLPoint.y+point_shift:
            return q, qf, q.TLPoint
        if q.TRPoint.x-point_shift <= point.x <= q.TRPoint.x+point_shift and q.TRPoint.y-point_shift <= point.y <= q.TRPoint.y+point_shift:
            return q, qf, q.TRPoint
        if q.BRPoint.x-point_shift <= point.x <= q.BRPoint.x+point_shift and q.BRPoint.y-point_shift <= point.y <= q.BRPoint.y+point_shift:
            return q, qf, q.BRPoint
        if q.BLPoint.x-point_shift <= point.x <= q.BLPoint.x+point_shift and q.BLPoint.y-point_shift <= point.y <= q.BLPoint.y+point_shift:
            return q, qf, q.BLPoint
    
    return None, None, None
