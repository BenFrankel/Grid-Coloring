"""
Some useful functions for working with a grid
"""

from const import *


# The relative position of p1 from p2 (or -1 if they are not adjacent)
def adjacency(p1, p2):
    if abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) != 1:
        return -1
    if p1[0] == p2[0] - 1: return NORTH
    if p1[1] == p2[1] - 1: return WEST
    if p1[0] == p2[0] + 1: return SOUTH
    if p1[1] == p2[1] + 1: return EAST


# The coordinates of the cell adjacent to p at a given direction
def near(p, direction):
    return (p[0] + (direction == SOUTH) - (direction == NORTH),
            p[1] + (direction == EAST) - (direction == WEST))
