import util
from const import *

import hgf
import pygame

import pickle


class Tile(hgf.FlatComponent):
    def __init__(self, color=WHITE, mark=None, connections=0, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.mark = mark
        self.connections = connections
        self._ts = None
        self._lw = None

    def refresh_background(self):
        self.background = self.mark(
            self.color,
            self.connections,
            self._ts,
            self._lw,
        )

    @hgf.double_buffer
    class color:
        def on_transition(self):
            self.refresh_background_flag = True

    @hgf.double_buffer
    class mark:
        def on_transition(self):
            self.refresh_background_flag = True

    @hgf.double_buffer
    class connections:
        def on_transition(self):
            self.refresh_background_flag = True

    @property
    def is_empty(self):
        return self.color == WHITE

    def put(self, color, mark):
        self.color = color
        self.mark = mark

    def connect(self, direction):
        self.connections |= direction

    def disconnect(self, direction):
        self.connections &= ~direction

    def erase(self):
        self.color = WHITE


class Grid(hgf.LayeredComponent):
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
        self.mark = None

        self._visited = set()
        self._previous = (-1, -1)
        self.color = None

        self._bw = None
        self._lw = None
        self._ts = None

        self.grid = None

    def on_load(self):
        self.grid = [[Tile() for _ in range(self.ncols)] for _ in range(self.nrows)]
        self.register_load(*[tile for row in self.grid for tile in row])

    def load_style(self):
        self._bg_factory = self.style_get('background')
        self._marks = self.style_get('marks')
        if self.mark is None:
            self.mark = self._marks[1]
        for row in self.grid:
            for tile in row:
                tile.mark = self._marks[0]

    def refresh_proportions(self):
        super().refresh_proportions()
        side = self._ts + 2 * self._lw
        for row in self.grid:
            for tile in row:
                tile._ts = self._ts
                tile._lw = self._lw
                tile.size = side, side

                # TODO: All of this is boilerplate. It should not be necessary in later versions of hgf.
                tile.on_w_transition()
                tile.on_h_transition()
                tile.refresh_background_flag = True

    def refresh_layout(self):
        super().refresh_layout()
        for i, row in enumerate(self.grid):
            for j, tile in enumerate(row):
                tile.pos = ((self._ts + self._lw) * j + self._bw - self._lw,
                            (self._ts + self._lw) * i + self._bw - self._lw)

                # TODO: All of this is boilerplate. It should not be necessary in later versions of hgf.
                tile.on_x_transition()
                tile.on_y_transition()

    def refresh_background(self):
        self.background = self._bg_factory(
            self.size,
            self.nrows,
            self.ncols,
            self._bw,
            self._lw,
            self._ts,
        )

    def on_mouse_down(self, pos, button, hovered):
        if pygame.mouse.get_pressed()[0] == pygame.mouse.get_pressed()[2]:
            self._previous = (-1, -1)
            return
        if button != 1 and button != 3:
            return
        row = int((pos[1] - self._bw) // (self._ts + self._lw))
        col = int((pos[0] - self._bw) // (self._ts + self._lw))
        if not (0 <= row < self.nrows and 0 <= col < self.ncols):
            return
        current = (row, col)
        if pygame.key.get_mods() & pygame.KMOD_SHIFT and self.at(current).color != WHITE:
            if button == 3:
                for p in flood_set(self, current):
                    self.erase(p)
                    self._visited.discard(p)
            else:
                for p in flood_set(self, current):
                    self._visited.add(p)
                    self.put(p, self.color, self.mark)
        else:
            if button == 3 \
                    or self.color != self.at(current).color \
                    or self.mark != self.at(current).mark:
                self.erase(current)
                self._visited.discard(current)
            if button == 1:
                self._visited.add(current)
                self.put(current, self.color, self.mark)
                self._previous = current

    def on_mouse_motion(self, start, end, buttons, start_hovered, end_hovered):
        if buttons[0] == buttons[2]:
            return
        row = int((end[1] - self._bw) // (self._ts + self._lw))
        col = int((end[0] - self._bw) // (self._ts + self._lw))
        if not (0 <= row < self.nrows and 0 <= col < self.ncols) or (row, col) == self._previous:
            return
        current = row, col
        if buttons[0]:
            if self.color != self.at(current).color \
                    or self.mark != self.at(current).mark:
                self.erase(current)
                self._visited.discard(current)

            if self.connection_mode == Grid.TREE:
                if current not in self._visited:
                    adj = util.adjacency(current, self._previous)
                    self.connect(self._previous, adj)

            elif self.connection_mode == Grid.BLOB:
                for direction in NORTH, WEST, SOUTH, EAST:
                    if util.step(current, direction) in self._visited:
                        self.connect(current, direction)

            elif self.connection_mode == Grid.TRACE:
                self.connect(self._previous, util.adjacency(current, self._previous))

            self.put(current, self.color, self.mark)
            self._visited.add(current)
        else:
            self.erase(current)
            self._visited.discard(current)
        self._previous = current

    def insert_row(self, index):
        if self.nrows >= MAX_SIZE:
            raise ValueError('Grid may not have more than {} rows'.format(MAX_SIZE))
        self.nrows += 1
        row = [Tile() for _ in range(self.ncols)]
        self.register_load(*row)
        self.grid.insert(index, row)
        self.parent.refresh_proportions_flag = True
        self.parent.refresh_layout_flag = True
        # TODO: Disconnect

    def pop_row(self, index):
        if self.nrows <= MIN_SIZE:
            raise ValueError('Grid may not have fewer than {} rows'.format(MIN_SIZE))
        self.nrows -= 1
        self.unregister(*self.grid.pop(index))
        self.parent.refresh_proportions_flag = True
        self.parent.refresh_layout_flag = True

    def insert_col(self, index):
        if self.nrows >= MAX_SIZE:
            raise ValueError('Grid may not have more than {} columns'.format(MAX_SIZE))
        self.ncols += 1
        col = [Tile() for _ in range(self.nrows)]
        self.register_load(*col)
        for row, tile in zip(self.grid, col):
            row.insert(index, tile)
        self.parent.refresh_proportions_flag = True
        self.parent.refresh_layout_flag = True

    def pop_col(self, index):
        if self.ncols <= MIN_SIZE:
            raise ValueError('Grid may not have fewer than {} columns'.format(MIN_SIZE))
        self.ncols -= 1
        for row in self.grid:
            self.unregister(row.pop(index))
        self.parent.refresh_proportions_flag = True
        self.parent.refresh_layout_flag = True

    def on_key_down(self, unicode, key, mod):
        if key == pygame.K_q:
            self.connection_mode = Grid.TREE
        elif key == pygame.K_w:
            self.connection_mode = Grid.BLOB
        elif key == pygame.K_e:
            self.connection_mode = Grid.TRACE
        elif key == pygame.K_i:
            self.mark = self._marks[0]
        elif key == pygame.K_o:
            self.mark = self._marks[1]
        elif key == pygame.K_p:
            self.mark = self._marks[2]

        elif key == pygame.K_UP:
            if mod & pygame.KMOD_SHIFT:
                self.pop_row(0)
            else:
                self.insert_row(0)
        elif key == pygame.K_DOWN:
            if mod & pygame.KMOD_SHIFT:
                self.pop_row(-1)
            else:
                self.insert_row(-1)
        elif key == pygame.K_RIGHT:
            if mod & pygame.KMOD_SHIFT:
                self.pop_col(-1)
            else:
                self.insert_col(-1)
        elif key == pygame.K_LEFT:
            if mod & pygame.KMOD_SHIFT:
                self.pop_col(0)
            else:
                self.insert_col(0)

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
        self.at(p).mark = self._marks[0]
        self.disconnect(p, NORTH | WEST | SOUTH | EAST)


def flood_set(grid, p):
    queue = [p]
    visited = set()
    while queue:
        q = queue.pop()
        visited.add(q)
        for direction in (NORTH, WEST, SOUTH, EAST):
            adj = util.step(q, direction)
            if grid.at(q).connections & direction and adj not in visited:
                queue.append(adj)
    return visited


def save_grid(grid, name='latest'):
    with open('grids/inf/' + name, 'wb') as f:
        grid_data = [[(tile.color, tile.mark, tile.connections) for tile in row] for row in grid.grid]
        pickle.dump((grid._visited, grid.nrows, grid.ncols, grid_data), f)
        f.close()


def load_grid(grid, name='latest'):
    with open('grids/inf/' + name, 'rb') as f:
        grid._visited, grid.nrows, grid.ncols, grid_data = pickle.load(f)

        grid.unregister(*[tile for row in grid.grid for tile in row])
        grid.grid = [[Tile(*tile_data) for tile_data in row] for row in grid_data]
        grid.register_load(*[tile for row in grid.grid for tile in row])

        grid.parent.refresh_proportions_flag = True
        grid.parent.refresh_layout_flag = True
