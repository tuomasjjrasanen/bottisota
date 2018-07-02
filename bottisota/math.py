import math
import random

import bottisota.constants

def direction_f(point0, point1):
    x0, y0 = point0
    x1, y1 = point1
    return math.degrees(math.atan2(y1 - y0, x1 - x0)) % 360

def direction(point0, point1):
    return round(direction_f(point0, point1))

def distance_f(point0, point1):
    x0, y0 = point0
    x1, y1 = point1
    return math.hypot(x1 - x0, y1 - y0)

def distance(point0, point1):
    return round(distance_f(point0, point1))

def minmaxloc(loc):
    x, y = loc

    return (
        min(bottisota.constants.ARENA_X_MAX, max(bottisota.constants.ARENA_X_MIN, x)),
        min(bottisota.constants.ARENA_Y_MAX, max(bottisota.constants.ARENA_Y_MIN, y)),
    )

def travel(x, y, direction, distance):
    xd = math.cos(math.radians(direction)) * distance
    yd = math.sin(math.radians(direction)) * distance

    return minmaxloc((x + xd, y + yd))

def randloc():
    x = random.randint(0, bottisota.ARENA_WIDTH - 1)
    y = random.randint(0, bottisota.ARENA_HEIGHT - 1)

    return x, y
