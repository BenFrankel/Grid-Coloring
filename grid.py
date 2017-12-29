import mark
from const import *

import hgf
import pygame

import pickle


class Tile(hgf.SimpleWidget):
    def __init__(self, color=None, mark=None, connections=0, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.mark = mark
        self.connections = connections
        self._ts = None
        self._lw = None

    def refresh_background(self):
        self.background = self.mark(self.color, self.connections, self._ts, self._lw)

    @hgf.double_buffer
    class color:
        def on_transition(self):
            self.refresh_background_flag = True

    @hgf.double_buffer
    class style:
        def on_transition(self):
            self.refresh_background_flag = True

    @hgf.double_buffer
    class connections:
        def on_transition(self):
            self.refresh_background_flag = True

    def put(self, color, style):
        self.color = color
        self.mark = style

    def connect(self, direction):
        self.connections |= direction

    def disconnect(self, direction):
        self.connections &= ~direction

    def erase(self):
        self.color = WHITE
        # self.mark = mark.FLAT


class Grid(hgf.SimpleWidget):
    BLOB = 0
    TREE = 1
    TRACE = 2

    def __init__(self, nrows, ncols, **kwargs):
        super().__init__(**kwargs)
        self.type = 'grid'
        self._bg_factory = None

        self.nrows = nrows
        self.ncols = ncols

        self.connection_mode = Grid.TRACE
        self._marks = None
        self.mark = 0

        self._visited = set()
        self._previous = (-1, -1)
        self.color = None

        self._bw = None
        self._lw = None
        self._ts = None

        self.grid = None

    def on_load(self):
        self.grid = [[Tile(WHITE) for _ in range(self.ncols)] for _ in range(self.nrows)]
        self.register_load(*[tile for row in self.grid for tile in row])

    def load_style(self):
        self._bg_factory = self.style_get('background')
        self._marks = self.style_get('marks')
        for row in self.grid:
            for tile in row:
                if tile.mark is None:
                    tile.mark = self._marks[self.mark]

    def refresh_proportions(self):
        super().refresh_proportions()
        side = self._ts + 2 * self._lw
        for row in self.grid:
            for tile in row:
                tile._ts = self._ts
                tile._lw = self._lw
                tile.size = side, side

    def refresh_layout(self):
        super().refresh_layout()
        for i, row in enumerate(self.grid):
            for j, tile in enumerate(row):
                tile.pos = ((self._ts + self._lw) * j + self._bw - self._lw,
                            (self._ts + self._lw) * i + self._bw - self._lw)

    def refresh_background(self):
        self.background = self._bg_factory(
            self.size,
            self.nrows,
            self.ncols,
            self._bw,
            self._lw,
            self._ts
        )

    def on_mouse_down(self, pos, button, hovered):
        if pygame.mouse.get_pressed()[0] and pygame.mouse.get_pressed()[2]:
            self._previous = (-1, -1)
            return
        if button == 1 or button == 3:
            row = int((pos[1] - self._bw) // (self._ts + self._lw))
            col = int((pos[0] - self._bw) // (self._ts + self._lw))
            if 0 <= row < self.nrows and 0 <= col < self.ncols:
                current = (row, col)
                if button == 3 \
                        or self.color != self.at(current).color \
                        or self._marks[self.mark] != self.at(current).style:
                    self.erase(current)
                    self._visited.discard(current)
                if button == 1:
                    self._visited.add(current)
                    self._previous = current
                    self.put(current, self.color, self._marks[self.mark])

    def on_key_down(self, unicode, key, mod):
        if key == pygame.K_q:
            self.connection_mode = Grid.TREE
        elif key == pygame.K_w:
            self.connection_mode = Grid.BLOB
        elif key == pygame.K_e:
            self.connection_mode = Grid.TRACE
        elif key == pygame.K_i:
            self.mark = self._marks['path']
        elif key == pygame.K_o:
            self.mark = self._marks['fill']
        elif key == pygame.K_p:
            self.mark = self._marks['flat']

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
        if direction & SOUTH and p[0] < self.nrows - 1:
            self.grid[p[0] + 1][p[1]].connect(NORTH)
        if direction & EAST and p[1] < self.ncols - 1:
            self.grid[p[0]][p[1] + 1].connect(WEST)

    def disconnect(self, p, direction):
        self.at(p).disconnect(direction)

        if direction & NORTH and p[0] > 0:
            self.grid[p[0] - 1][p[1]].disconnect(SOUTH)
        if direction & WEST and p[1] > 0:
            self.grid[p[0]][p[1] - 1].disconnect(EAST)
        if direction & SOUTH and p[0] < self.nrows - 1:
            self.grid[p[0] + 1][p[1]].disconnect(NORTH)
        if direction & EAST and p[1] < self.ncols - 1:
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
