import pygame
from pygame.locals import VIDEORESIZE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, KEYDOWN, KEYUP, QUIT
from constants import *
import marks
import size


pygame.init()


# TODO: At the moment there's no way to change the grid dimensions besides directly modifying the code.
NUM_ROWS = 8
NUM_COLS = 8


# Returns -1 if p1 is not adjacent to p2, otherwise the relative position of p1 from p2.
def adjacency(p1, p2):
    north = int(p1[0] == p2[0] - 1)
    east  = int(p1[1] == p2[1] + 1)
    south = int(p1[0] == p2[0] + 1)
    west  = int(p1[1] == p2[1] - 1)
    if north + east + south + west == 1:
        if north == 1: return NORTH
        if east  == 1: return EAST
        if south == 1: return SOUTH
        if west  == 1: return WEST
    return -1


# Returns the coordinates of the adjacent cell at a given direction from p.
def near(p, direction):
    return p[0] + (direction == SOUTH) - (direction == NORTH), \
           p[1] + (direction == EAST) - (direction == WEST)


class Tile:
    def __init__(self, color=WHITE, style=marks.FLAT, connections=0):
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
        self.style = marks.FLAT

    def draw(self, screen, pos, ts, lw):
        self.style(screen, self.color, pos, self.connections, ts, lw)

    def encode(self):
        style_c = '?'
        if self.style == marks.FLAT: style_c = 'O'
        elif self.style == marks.PATH: style_c = '+'
        elif self.style == marks.FILL: style_c = '#'

        color_c = chr(self.color[0]) + chr(self.color[1]) + chr(self.color[2])

        cnnct_c = chr(self.connections)

        return style_c + color_c + cnnct_c

    @staticmethod
    def decode(s):
        assert len(s) == 5

        style = marks.DEFAULT
        if s[0] == 'O': style = marks.FLAT
        elif s[0] == '+': style = marks.PATH
        elif s[0] == '#': style = marks.FILL

        color = (ord(s[1]), ord(s[2]), ord(s[3]))

        connections = ord(s[4])

        return Tile(color, style, connections)


class Grid:
    def __init__(self, nrows, ncols):
        self.nrows = nrows
        self.ncols = ncols
        self.grid = [[Tile() for i in range(ncols)] for j in range(nrows)]

    def at(self, *args):
        assert len(args) in (1, 2)

        if len(args) == 1:
            return self.grid[args[0][0]][args[0][1]]
        elif len(args) == 2:
            return self.grid[args[0]][args[1]]

    def set(self, p, tile):
        self.grid[p[0]][p[1]] = tile

    def put(self, p, color, style):
        self.grid[p[0]][p[1]].put(color, style)

    def connect(self, p, direction):
        if direction == -1: return
        self.grid[p[0]][p[1]].connect(direction)
        if direction & NORTH and p[0] > 0:
            self.grid[p[0] - 1][p[1]].connect(SOUTH)
        if direction & EAST and p[1] < self.ncols-1:
            self.grid[p[0]][p[1] + 1].connect(WEST)
        if direction & SOUTH and p[0] < self.nrows-1:
            self.grid[p[0] + 1][p[1]].connect(NORTH)
        if direction & WEST and p[1] > 0:
            self.grid[p[0]][p[1] - 1].connect(EAST)

    def disconnect(self, p, direction):
        self.grid[p[0]][p[1]].disconnect(direction)
        if direction & NORTH and p[0] > 0:
            self.grid[p[0] - 1][p[1]].disconnect(SOUTH)
        if direction & EAST and p[1] < self.ncols-1:
            self.grid[p[0]][p[1] + 1].disconnect(WEST)
        if direction & SOUTH and p[0] < self.nrows-1:
            self.grid[p[0] + 1][p[1]].disconnect(NORTH)
        if direction & WEST and p[1] > 0:
            self.grid[p[0]][p[1] - 1].disconnect(EAST)

    def erase(self, p):
        self.grid[p[0]][p[1]].erase()
        self.disconnect((p[0], p[1]), NORTH | EAST | SOUTH | WEST)

    def draw(self, surf, pos, ts, lw, bw):
        gr = pygame.Rect(pos[0], pos[1], (ts + lw) * self.ncols - lw + 2*bw, (ts + lw) * self.nrows - lw + 2*bw)

        for i in range(1, self.nrows):
            line = pygame.Surface((gr.width - 2*bw, lw))
            line.fill(L_GRAY)
            surf.blit(line, (gr.left + bw, gr.top + (ts+lw)*i + bw - lw))
        for i in range(1, self.ncols):
            line = pygame.Surface((lw, gr.height - 2*bw))
            line.fill(L_GRAY)
            surf.blit(line, (gr.left + (ts+lw)*i + bw - lw, gr.top + bw))

        for i in range(self.nrows):
            for j in range(self.ncols):
                self.at(i, j).draw(surf, (gr.left + (ts+lw)*j + bw - lw, gr.top + (ts+lw)*i + bw - lw), ts, lw)

        line = pygame.Surface((bw, gr.height))
        line.fill(BLACK)
        surf.blit(line, gr.topleft)
        surf.blit(line, (gr.right - bw, gr.top))
        line = pygame.Surface((gr.width, bw))
        line.fill(BLACK)
        surf.blit(line, gr.topleft)
        surf.blit(line, (gr.left, gr.bottom - bw))

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


main_grid = Grid(NUM_ROWS, NUM_COLS)


# TODO: save_grid and load_grid should allow saving grid objects (not as images) to load later and continue editing.
def save_grid():
    f = open("grids/inf/latest.txt", 'w', encoding='utf-8')
    f.write(main_grid.encode())
    f.close()


def load_grid(name='latest'):
    f = open("grids/inf/" + name + ".txt", encoding='utf-8')
    global main_grid
    main_grid = Grid.decode(f.read())


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

    colors = [BLACK, RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE]
    current_color = 0

    BLOB = 0
    TREE = 1
    TRACE = 2
    connection_mode = TRACE

    style = marks.DEFAULT

    visited = set()
    previous = (-1, -1)

    while True:
        gr = size.grid_rect(screen, main_grid)
        ts = size.tile_size(screen, main_grid)
        lw = size.line_width(screen, main_grid)
        bw = size.border_width(screen, main_grid)
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

            elif event.type == VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            elif event.type == MOUSEMOTION:
                if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
                    row = int((event.pos[1] - gr.top - bw)//(ts + lw))
                    col = int((event.pos[0] - gr.left - bw)//(ts + lw))
                    if 0 <= row < main_grid.nrows and 0 <= col < main_grid.ncols and (row, col) != previous:
                        current = (row, col)
                        if pygame.mouse.get_pressed()[0]:
                            if connection_mode == TREE:
                                if current not in visited:
                                    adj = adjacency(current, previous)
                                    main_grid.connect(previous, adj)
                            elif connection_mode == BLOB:
                                for direction in NORTH, EAST, SOUTH, WEST:
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
                    row = int((event.pos[1] - gr.top - bw)//(ts + lw))
                    col = int((event.pos[0] - gr.left - bw)//(ts + lw))
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
                    if 1 <= digit <= len(colors):
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
                        if event.mod & pygame.KMOD_SHIFT:
                            save_grid()
                        else:
                            gr = size.grid_rect(screen, main_grid)
                            grid_surf = pygame.Surface((gr.width, gr.height))
                            grid_surf.fill(WHITE)
                            main_grid.draw(grid_surf,
                                           (0, 0),
                                           size.tile_size(screen, main_grid),
                                           size.line_width(screen, main_grid),
                                           size.border_width(screen, main_grid))
                            pygame.image.save(grid_surf, "grids/img/latest.png")
                elif event.key == pygame.K_l:
                    load_grid()

        screen.fill(WHITE)

        main_grid.draw(screen,
                       size.grid_rect(screen, main_grid).topleft,
                       size.tile_size(screen, main_grid),
                       size.line_width(screen, main_grid),
                       size.border_width(screen, main_grid))

        draw_colors(screen, colors, current_color)

        pygame.display.update()


if __name__ == '__main__':
    main()