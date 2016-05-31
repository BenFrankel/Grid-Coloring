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
        style_c = '?'
        if self.style == mark.FLAT: style_c = 'O'
        elif self.style == mark.PATH: style_c = '+'
        elif self.style == mark.FILL: style_c = '#'

        color_c = chr(self.color[0]) + chr(self.color[1]) + chr(self.color[2])

        cnnct_c = chr(self.connections)

        return style_c + color_c + cnnct_c

    @staticmethod
    def decode(s):
        assert len(s) == 5

        style = mark.DEFAULT
        if s[0] == 'O': style = mark.FLAT
        elif s[0] == '+': style = mark.PATH
        elif s[0] == '#': style = mark.FILL

        color = (ord(s[1]), ord(s[2]), ord(s[3]))

        connections = ord(s[4])

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
        encoded = chr(self.nrows) + chr(self.ncols)
        for row in self.grid:
            for tile in row:
                encoded += tile.encode()
        return encoded

    @staticmethod
    def decode(s):
        assert len(s) >= 2

        nrows = ord(s[0])
        ncols = ord(s[1])

        assert len(s) == 2 + 5*nrows*ncols

        decoded = Grid(nrows, ncols)
        for i in range(nrows):
            for j in range(ncols):
                tile_pos = 2 + 5*ncols*i + 5*j
                decoded.set((i, j), Tile.decode(s[tile_pos:tile_pos + 5]))
        return decoded


def save_grid(grid):
    f = open("grids/inf/latest.txt", 'w', encoding='utf-8')
    f.write(grid.encode())
    f.close()


def load_grid(name='latest'):
    f = open("grids/inf/" + name + ".txt", encoding='utf-8')
    return Grid.decode(f.read())
