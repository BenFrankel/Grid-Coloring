import pickle

import mark
from const import *


class Tile:
    def __init__(self, color=WHITE, style=mark.FLAT, connections=0):
        self.color = color
        self.style = style
        self.connections = connections

    def put(self, color, style):
        self.color = color
        self.style = style

    def connect(self, direction):
        self.connections |= direction

    def disconnect(self, direction):
        self.connections &= ~direction

    def erase(self):
        self.color = WHITE
        self.style = mark.FLAT


class Grid:
    def __init__(self, nrows, ncols):
        self.nrows = nrows
        self.ncols = ncols
        self.grid = [[Tile() for i in range(ncols)] for j in range(nrows)]

    def at(self, *args):
        if len(args) == 1:
            return self.grid[args[0][0]][args[0][1]]
        elif len(args) == 2:
            return self.grid[args[0]][args[1]]

    def set(self, p, tile):
        self.grid[p[0]][p[1]] = tile

    def put(self, p, color, style):
        self.grid[p[0]][p[1]].put(color, style)

    def connect(self, p, direction):
        if not 1 <= direction <= 15:
            return

        self.at(p).connect(direction)

        if direction & NORTH and p[0] > 0:
            self.grid[p[0] - 1][p[1]].connect(SOUTH)
        if direction & WEST and p[1] > 0:
            self.grid[p[0]][p[1] - 1].connect(EAST)
        if direction & SOUTH and p[0] < self.nrows-1:
            self.grid[p[0] + 1][p[1]].connect(NORTH)
        if direction & EAST and p[1] < self.ncols-1:
            self.grid[p[0]][p[1] + 1].connect(WEST)

    def disconnect(self, p, direction):
        self.at(p).disconnect(direction)

        if direction & NORTH and p[0] > 0:
            self.grid[p[0] - 1][p[1]].disconnect(SOUTH)
        if direction & WEST and p[1] > 0:
            self.grid[p[0]][p[1] - 1].disconnect(EAST)
        if direction & SOUTH and p[0] < self.nrows-1:
            self.grid[p[0] + 1][p[1]].disconnect(NORTH)
        if direction & EAST and p[1] < self.ncols-1:
            self.grid[p[0]][p[1] + 1].disconnect(WEST)

    def erase(self, p):
        self.at(p).erase()
        self.disconnect(p, NORTH | WEST | SOUTH | EAST)


def save_grid(grid):
    with open("grids/inf/latest.txt", 'wb') as f:
        pickle.dump(grid, f)
        f.close()


def load_grid(name='latest'):
    with open("grids/inf/" + name + ".txt", 'rb') as f:
        return pickle.load(f)
