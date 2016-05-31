import pygame
from pygame.locals import VIDEORESIZE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, KEYDOWN, KEYUP, QUIT
from constants import *
import marks
import size


pygame.init()


NUM_ROWS = 8
NUM_COLS = 8
MAX_SIZE = 32
MIN_SIZE = 4


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
        if direction & WEST and p[1] > 0:
            self.grid[p[0]][p[1] - 1].connect(EAST)
        if direction & SOUTH and p[0] < self.nrows-1:
            self.grid[p[0] + 1][p[1]].connect(NORTH)
        if direction & EAST and p[1] < self.ncols-1:
            self.grid[p[0]][p[1] + 1].connect(WEST)

    def disconnect(self, p, direction):
        self.grid[p[0]][p[1]].disconnect(direction)
        if direction & NORTH and p[0] > 0:
            self.grid[p[0] - 1][p[1]].disconnect(SOUTH)
        if direction & WEST and p[1] > 0:
            self.grid[p[0]][p[1] - 1].disconnect(EAST)
        if direction & SOUTH and p[0] < self.nrows-1:
            self.grid[p[0] + 1][p[1]].disconnect(NORTH)
        if direction & EAST and p[1] < self.ncols-1:
            self.grid[p[0]][p[1] + 1].disconnect(WEST)

    def erase(self, p):
        self.grid[p[0]][p[1]].erase()
        self.disconnect((p[0], p[1]), NORTH | WEST | SOUTH | EAST)

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


def save_grid():
    f = open("grids/inf/latest.txt", 'w', encoding='utf-8')
    f.write(main_grid.encode())
    f.close()


def load_grid(name='latest'):
    f = open("grids/inf/" + name + ".txt", encoding='utf-8')
    global main_grid
    main_grid = Grid.decode(f.read())


def draw_colors(screen, colors, color_index):
    gr = size.grid_rect(screen, main_grid)
    cs = int(gr.width / main_grid.ncols * 0.8)
    gap = max(min(0.5, (screen.get_width() - cs/2)/len(colors)/cs - 1), 0.1)
    if gap == 0.1:
        cs = int(cs * 0.8)

    y = int((screen.get_height() + gr.bottom)/2 - cs/2)
    for i, c in enumerate(colors):
        x = int(screen.get_width()/2 - len(colors)*cs*(1+gap)/2 + cs*(1+gap)*i + cs*gap/2)
        if i == color_index:
            pygame.draw.rect(screen, c, pygame.Rect(x, y-cs/4, cs, cs))
        else:
            pygame.draw.rect(screen, c, pygame.Rect(x, y, cs, cs))


def main():
    screen = pygame.display.set_mode((600, 400), pygame.RESIZABLE)
    pygame.display.set_caption("Grid Coloring")

    colors = [BLACK, RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE]
    color_index = 0

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
                if pygame.mouse.get_pressed()[0] ^ pygame.mouse.get_pressed()[2]:
                    row = int((event.pos[1] - gr.top - bw)//(ts + lw))
                    col = int((event.pos[0] - gr.left - bw)//(ts + lw))
                    if 0 <= row < main_grid.nrows and 0 <= col < main_grid.ncols and (row, col) != previous:
                        current = (row, col)
                        if pygame.mouse.get_pressed()[0]:
                            if (colors[color_index], style) != (main_grid.at(current).color, main_grid.at(current).style):
                                main_grid.erase(current)
                                visited.discard(current)
                            if connection_mode == TREE:
                                if current not in visited:
                                    adj = adjacency(current, previous)
                                    main_grid.connect(previous, adj)
                            elif connection_mode == BLOB:
                                for direction in NORTH, WEST, SOUTH, EAST:
                                    if near(current, direction) in visited:
                                        main_grid.connect(current, direction)
                            elif connection_mode == TRACE:
                                adj = adjacency(current, previous)
                                main_grid.connect(previous, adj)
                            main_grid.put(current, colors[color_index], style)
                            visited.add(current)
                        else:
                            main_grid.erase(current)
                            visited.discard(current)
                        previous = current

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    color_index += 1
                    color_index %= len(colors)
                elif event.button == 5:
                    color_index -= 1
                    color_index %= len(colors)
                elif event.button == 1 or event.button == 3:
                    if pygame.mouse.get_pressed()[0] and pygame.mouse.get_pressed()[2]:
                        previous = (-1, -1)
                    else:
                        row = int((event.pos[1] - gr.top - bw)//(ts + lw))
                        col = int((event.pos[0] - gr.left - bw)//(ts + lw))
                        if 0 <= row < main_grid.nrows and 0 <= col < main_grid.ncols:
                            current = (row, col)
                            if event.button == 1:
                                if (colors[color_index], style) != (main_grid.at(current).color, main_grid.at(current).style):
                                    main_grid.erase(current)
                                    visited.discard(current)
                                visited.add(current)
                                previous = current
                                main_grid.put(current, colors[color_index], style)
                            elif event.button == 3:
                                main_grid.erase(current)
                                visited.discard(current)

            elif event.type == KEYDOWN:
                if event.unicode.isdigit():
                    digit = int(event.unicode)
                    if 1 <= digit <= len(colors):
                        color_index = digit - 1
                elif event.key == pygame.K_q:
                    connection_mode = TREE
                elif event.key == pygame.K_w:
                    connection_mode = BLOB
                elif event.key == pygame.K_e:
                    connection_mode = TRACE
                elif event.key == pygame.K_i:
                    style = marks.PATH
                elif event.key == pygame.K_o:
                    style = marks.FILL
                elif event.key == pygame.K_p:
                    style = marks.FLAT
                elif event.key == pygame.K_s:
                    if event.mod & pygame.KMOD_CTRL:
                        gr = size.grid_rect(screen, main_grid)
                        grid_surf = pygame.Surface((gr.width, gr.height))
                        grid_surf.fill(WHITE)
                        main_grid.draw(grid_surf,
                                       (0, 0),
                                       size.tile_size(screen, main_grid),
                                       size.line_width(screen, main_grid),
                                       size.border_width(screen, main_grid))
                        pygame.image.save(grid_surf, "grids/img/latest.png")
                elif event.key == pygame.K_g:
                    if event.mod & pygame.KMOD_CTRL:
                        save_grid()
                elif event.key == pygame.K_l:
                    if event.mod & pygame.KMOD_CTRL:
                        load_grid()
                elif event.key == pygame.K_UP:
                    grid = main_grid.grid
                    if event.mod & pygame.KMOD_SHIFT:
                        if main_grid.nrows > MIN_SIZE:
                            main_grid.nrows -= 1
                            main_grid.grid = grid[1:]
                            for j in range(main_grid.ncols):
                                main_grid.disconnect((0, j), NORTH)
                    elif main_grid.nrows < MAX_SIZE:
                        main_grid.nrows += 1
                        main_grid.grid = [[Tile() for j in range(main_grid.ncols)]] + grid
                elif event.key == pygame.K_DOWN:
                    grid = main_grid.grid
                    if event.mod & pygame.KMOD_SHIFT:
                        if main_grid.nrows > MIN_SIZE:
                            main_grid.nrows -= 1
                            main_grid.grid = grid[:-1]
                            for j in range(main_grid.ncols):
                                main_grid.disconnect((main_grid.nrows - 1, j), SOUTH)
                    elif main_grid.nrows < MAX_SIZE:
                        main_grid.nrows += 1
                        main_grid.grid = grid + [[Tile() for j in range(main_grid.ncols)]]
                elif event.key == pygame.K_RIGHT:
                    grid = main_grid.grid
                    if event.mod & pygame.KMOD_SHIFT:
                        if main_grid.ncols > MIN_SIZE:
                            for i in range(main_grid.nrows):
                                grid[i].pop()
                            main_grid.ncols -= 1
                            main_grid.grid = grid
                            for i in range(main_grid.nrows):
                                main_grid.disconnect((i, main_grid.ncols - 1), EAST)
                    elif main_grid.ncols < MAX_SIZE:
                        for i in range(main_grid.nrows):
                            grid[i].append(Tile())
                        main_grid.ncols += 1
                        main_grid.grid = grid
                elif event.key == pygame.K_LEFT:
                    grid = main_grid.grid
                    if event.mod & pygame.KMOD_SHIFT:
                        if main_grid.ncols > MIN_SIZE:
                            for i in range(main_grid.nrows):
                                grid[i] = grid[i][1:]
                            main_grid.ncols -= 1
                            main_grid.grid = grid
                    elif main_grid.ncols < MAX_SIZE:
                        for i in range(main_grid.nrows):
                            grid[i] = [Tile()] + grid[i]
                        main_grid.ncols += 1
                        main_grid.grid = grid
                        for i in range(main_grid.nrows):
                            main_grid.disconnect((i, 0), WEST)

        screen.fill(WHITE)

        main_grid.draw(screen,
                       size.grid_rect(screen, main_grid).topleft,
                       size.tile_size(screen, main_grid),
                       size.line_width(screen, main_grid),
                       size.border_width(screen, main_grid))

        draw_colors(screen, colors, color_index)

        pygame.display.update()


if __name__ == '__main__':
    main()