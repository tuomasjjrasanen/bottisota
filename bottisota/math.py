import math

def heading(point0, point1):
    x0, y0 = point0
    x1, y1 = point1
    return round(math.degrees(math.atan2(y1 - y0, x1 - x0))) % 360

def distance(point0, point1):
    x0, y0 = point0
    x1, y1 = point1
    return math.hypot(x1 - x0, y1 - y0)
