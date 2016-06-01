import mark
from constants import *


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

    def encode(self):
        style = '?'
        if self.style == mark.FLAT: style = 'O'
        elif self.style == mark.PATH: style = '+'
        elif self.style == mark.FILL: style = '#'

        color = str(self.color[0]) + ',' + str(self.color[1]) + ',' + str(self.color[2])

        connections = str(self.connections)

        return style + ';' + color + ';' + connections

    @staticmethod
    def decode(s):
        style_s, color_s, connections_s = s.split(';')
        style = mark.DEFAULT
        if style_s == 'O': style = mark.FLAT
        elif style_s == '+': style = mark.PATH
        elif style_s == '#': style = mark.FILL

        color = [int(x) for x in color_s.split(',')]

        connections = int(connections_s)

        return Tile(color, style, connections)


class Grid:
    def __init__(self, nrows, ncols):
        self.nrows = nrows
        self.ncols = ncols
        self.grid = [[Tile() for i in range(ncols)] for j in range(nrows)]

    def at(self, *args):
        assert 1 <= len(args) <= 2

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
        if not 1 <= direction <= 15:
            return

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

    def encode(self):
        encoded = str(self.nrows) + ',' + str(self.ncols)
        for row in self.grid:
            for tile in row:
                encoded += '\n' + tile.encode()
        return encoded

    @staticmethod
    def decode(s):
        lines = s.splitlines()
        nrows, ncols = lines[0].split(',')
        nrows = int(nrows)
        ncols = int(ncols)

        decoded = Grid(nrows, ncols)
        for i in range(nrows):
            for j in range(ncols):
                decoded.set((i, j), Tile.decode(lines[ncols*i + j + 1]))
        return decoded


def save_grid(grid):
    f = open("grids/inf/latest.txt", 'w')
    f.write(grid.encode())
    f.close()


def load_grid(name='latest'):
    f = open("grids/inf/" + name + ".txt")
    return Grid.decode(f.read())
