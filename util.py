from constants import *

# The following functions are useful for working with a grid.


# Returns -1 if p1 is not adjacent to p2, otherwise the relative position of p1 from p2.
def adjacency(p1, p2):
    if abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) != 1:
        return -1
    if p1[0] == p2[0] - 1: return NORTH
    if p1[1] == p2[1] - 1: return WEST
    if p1[0] == p2[0] + 1: return SOUTH
    if p1[1] == p2[1] + 1: return EAST


# Returns the coordinates of the adjacent cell at a given direction from p.
def near(p, direction):
    return p[0] + (direction == SOUTH) - (direction == NORTH), \
           p[1] + (direction == EAST) - (direction == WEST)
