import pygame
from pygame.locals import VIDEORESIZE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, KEYDOWN, KEYUP, QUIT
from constants import *
import marks
import size


pygame.init()


NUM_ROWS = 8
NUM_COLS = 8


# Returns -1 if p1 is not adjacent to p2, otherwise the relative position of p1 from p2.
def adjacency(p1, p2):
    north = int(p1[0] == p2[0] - 1)
    east  = int(p1[1] == p2[1] + 1)
    south = int(p1[0] == p2[0] + 1)
    west  = int(p1[1] == p2[1] - 1)
    if north + east + south + west == 1:
        if north == 1: return Direction.NORTH
        if east  == 1: return Direction.EAST
        if south == 1: return Direction.SOUTH
        if west  == 1: return Direction.WEST
    return -1


# Returns the coordinate of the adjacent cell at direction dir from p.
def near(p, dir):
    return p[0] + (dir == Direction.SOUTH) - (dir == Direction.NORTH),\
           p[1] + (dir == Direction.EAST) - (dir == Direction.WEST)


class Tile:
    def __init__(self):
        self.color = Color.WHITE
        self.style = marks.FLAT
        self.connections = 0

    def put(self, color, style):
        self.color = color
        self.style = style

    def connect(self, direction):
        self.connections |= direction

    def disconnect(self, direction):
        self.connections &= ~direction

    def erase(self):
        self.color = Color.WHITE
        self.style = marks.FLAT

    def draw(self, screen, pos, ts):
        self.style(screen, self.color, pos, self.connections, ts)

    def encode(self):
        style_c = '?'
        if self.style == marks.FLAT: style_c = 'O'
        elif self.style == marks.PATH: style_c = '+'
        elif self.style == marks.FILL: style_c = '#'
        color_c = chr(self.color[0]) + chr(self.color[1]) + chr(self.color[2])
        cnnct_c = chr(self.connections)
        return style_c + color_c + cnnct_c


class Grid():
    def __init__(self, nrows, ncols):
        self.nrows = nrows
        self.ncols = ncols
        self.grid = [[Tile() for i in range(ncols)] for j in range(nrows)]

    def at(self, row, col):
        return self.grid[row][col]

    def put(self, p, color, style):
        self.grid[p[0]][p[1]].put(color, style)

    def connect(self, p, dir):
        if dir == -1: return
        self.grid[p[0]][p[1]].connect(dir)
        if dir & Direction.NORTH and p[0] > 0:
            self.grid[p[0] - 1][p[1]].connect(Direction.SOUTH)
        if dir & Direction.EAST and p[1] < self.ncols-1:
            self.grid[p[0]][p[1] + 1].connect(Direction.WEST)
        if dir & Direction.SOUTH and p[0] < self.nrows-1:
            self.grid[p[0] + 1][p[1]].connect(Direction.NORTH)
        if dir & Direction.WEST and p[1] > 0:
            self.grid[p[0]][p[1] - 1].connect(Direction.EAST)

    def disconnect(self, p, dir):
        self.grid[p[0]][p[1]].disconnect(dir)
        if dir & Direction.NORTH and p[0] > 0:
            self.grid[p[0] - 1][p[1]].disconnect(Direction.SOUTH)
        if dir & Direction.EAST and p[1] < self.ncols-1:
            self.grid[p[0]][p[1] + 1].disconnect(Direction.WEST)
        if dir & Direction.SOUTH and p[0] < self.nrows-1:
            self.grid[p[0] + 1][p[1]].disconnect(Direction.NORTH)
        if dir & Direction.WEST and p[1] > 0:
            self.grid[p[0]][p[1] - 1].disconnect(Direction.EAST)

    def erase(self, p):
        self.grid[p[0]][p[1]].erase()
        self.disconnect((p[0], p[1]), Direction.NORTH | Direction.EAST | Direction.SOUTH | Direction.WEST)

    def draw(self, surf, pos, ts):
        gr = pygame.Rect(pos[0], pos[1], ts * self.ncols, ts * self.nrows)

        for i in range(self.nrows):
            for j in range(self.ncols):
                self.at(i, j).draw(surf, (gr.left + ts*j, gr.top + ts*i), ts)

        line_width = max(int(ts/40 + .5), 1)
        for i in range(self.nrows):
            line = pygame.Surface((gr.width, line_width), pygame.SRCALPHA)
            line.fill((0, 0, 0, 50))
            surf.blit(line, (gr.left, gr.top + ts*i))
        for i in range(self.ncols):
            line = pygame.Surface((line_width, gr.height), pygame.SRCALPHA)
            line.fill((0, 0, 0, 50))
            surf.blit(line, (gr.left + ts*i, gr.top))

        pygame.draw.rect(surf, Color.BLACK, pygame.Rect(gr.x, gr.y, gr.width+2, gr.height+2), max(int(ts/15 + .5), 1))
main_grid = Grid(NUM_ROWS, NUM_COLS)


def save_grid():
    encoded = ''
    for row in main_grid.grid:
        for tile in row:
            encoded += tile
        encoded += '\n'


def load_grid(name):
    pass


def draw_colors(screen, colors, current_color):
    gr = size.grid_rect(screen, main_grid)
    clr_size = int(gr.width / main_grid.ncols * 0.8)

    y = int((screen.get_height() + gr.bottom)/2 - clr_size/2)
    for i, c in enumerate(colors):
        x = int(screen.get_width()/2 - len(colors)*clr_size*0.75 + clr_size*1.5*i + clr_size/4)
        if i == current_color:
            pygame.draw.rect(screen, c, pygame.Rect(x, y-clr_size/4, clr_size, clr_size))
        else:
            pygame.draw.rect(screen, c, pygame.Rect(x, y, clr_size, clr_size))


def main():
    screen = pygame.display.set_mode((600, 400), pygame.RESIZABLE)
    pygame.display.set_caption("Grid Coloring")

    colors = [Color.BLACK, Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN, Color.CYAN, Color.BLUE, Color.PURPLE]
    current_color = 0

    BLOB = 0
    TREE = 1
    TRACE = 2
    connection_mode = TRACE

    style = marks.DEFAULT

    visited = set()
    previous = (-1, -1)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

            elif event.type == VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            elif event.type == MOUSEMOTION:
                if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
                    gr = size.grid_rect(screen, main_grid)
                    ts = size.tile_size(screen, main_grid)
                    row = int((event.pos[1] - gr.top)//ts)
                    col = int((event.pos[0] - gr.left)//ts)
                    if 0 <= row < main_grid.nrows and 0 <= col < main_grid.ncols and (row, col) != previous:
                        current = (row, col)
                        if pygame.mouse.get_pressed()[0]:
                            if connection_mode == TREE:
                                if current not in visited:
                                    adj = adjacency(current, previous)
                                    main_grid.connect(previous, adj)
                            elif connection_mode == BLOB:
                                for direction in Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST:
                                    if near(current, direction) in visited:
                                        main_grid.connect(current, direction)
                            elif connection_mode == TRACE:
                                adj = adjacency(current, previous)
                                main_grid.connect(previous, adj)
                            main_grid.put(current, colors[current_color], style)
                            visited.add(current)
                        else:
                            main_grid.erase(current)
                            if current in visited:
                                visited.remove(current)
                        previous = current

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    current_color += 1
                    current_color %= len(colors)
                elif event.button == 5:
                    current_color -= 1
                    current_color %= len(colors)
                else:
                    gr = size.grid_rect(screen, main_grid)
                    ts = size.tile_size(screen, main_grid)
                    row = int((event.pos[1] - gr.top)//ts)
                    col = int((event.pos[0] - gr.left)//ts)
                    if 0 <= row < main_grid.nrows and 0 <= col < main_grid.ncols:
                        current = (row, col)
                        if event.button == 1:
                            visited.add(current)
                            previous = current
                            main_grid.put(current, colors[current_color], style)
                        elif event.button == 3:
                            main_grid.erase(current)
                            if current in visited:
                                visited.remove(current)

            elif event.type == KEYDOWN:
                if event.unicode.isdigit():
                    digit = int(event.unicode)
                    if digit <= len(colors):
                        current_color = digit - 1
                elif event.key == pygame.K_q:
                    connection_mode = TREE
                elif event.key == pygame.K_w:
                    connection_mode = BLOB
                elif event.key == pygame.K_e:
                    connection_mode = TRACE
                elif event.key == pygame.K_r:
                    style = marks.PATH
                elif event.key == pygame.K_t:
                    style = marks.FILL
                elif event.key == pygame.K_y:
                    style = marks.FLAT
                elif event.key == pygame.K_s:
                    if event.mod & pygame.KMOD_CTRL:
                        gr = size.grid_rect(screen)
                        grid_surf = pygame.Surface((gr.width+2, gr.height+2))
                        grid_surf.fill(Color.WHITE)
                        main_grid.draw(grid_surf, (0, 0), size.tile_size(screen, main_grid))
                        pygame.image.save(grid_surf, "grids/img/latest.png")

        screen.fill(Color.WHITE)
        main_grid.draw(screen, size.grid_rect(screen, main_grid).topleft, size.tile_size(screen, main_grid))
        draw_colors(screen, colors, current_color)

        pygame.display.update()


if __name__ == '__main__':
    main()