import pygame
from pygame.locals import VIDEORESIZE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, KEYDOWN, KEYUP, QUIT
pygame.init()

NUM_ROWS = 8
NUM_COLS = 8


C_BLACK  = (0,   0,   0)
C_GRAY   = (120, 120, 120)
C_WHITE  = (255, 255, 255)
C_RED    = (200, 0,   0)
C_ORANGE = (240, 150, 0)
C_YELLOW = (220, 220, 0)
C_GREEN  = (0,   200, 0)
C_CYAN   = (0,   200, 200)
C_BLUE   = (0,   60,   220)
C_PURPLE = (160, 0,   200)

NORTH = 1
EAST  = 2
SOUTH = 4
WEST  = 8


# -1: not adjacent. 0: first north of second. 1: first east of second. 2: first south of second. 3: first west of second.
def adjacency(point1, point2):
    north = int(point1[0] == point2[0] - 1)
    east  = int(point1[1] == point2[1] + 1)
    south = int(point1[0] == point2[0] + 1)
    west  = int(point1[1] == point2[1] - 1)

    if north + east + south + west == 1:
        if north == 1: return NORTH
        if east  == 1: return EAST
        if south == 1: return SOUTH
        if west  == 1: return WEST

    return -1


# Returns coord of cell at direction from point.
def near(point, direction):
    return point[0] + (direction == SOUTH) - (direction == NORTH), point[1] + (direction == EAST) - (direction == WEST)


def tile_size(screen):
    return int(min(screen.get_width()/(main_grid.cols+2), screen.get_height()/(main_grid.rows+3)))


def line_width(tile_s):
    return max(int(tile_s/32+.5), 1)


def grid_rect(screen):
    ts = tile_size(screen)

    width = ts * main_grid.cols
    height = ts * main_grid.rows
    top = ts/2
    left = (screen.get_width() - width)/2

    return pygame.Rect(left, top, width, height)


def MARK_FLAT(surf, color, pos, connections, ts):
    lw = line_width(ts)
    tile_rect = pygame.Rect(pos[0]+lw-1, pos[1]+lw-1, ts-lw+1, ts-lw+1)
    pygame.draw.rect(surf, color, tile_rect)


def MARK_FILL(surf, color, pos, connections, ts):
    tile_rect = pygame.Rect(pos[0], pos[1], ts, ts)
    pygame.draw.rect(surf, color, tile_rect)
    lw = line_width(ts)

    # Boundary and shading.
    hori = pygame.Surface((tile_rect.width-lw, 2*lw), pygame.SRCALPHA)
    vert = pygame.Surface((2*lw, tile_rect.height-lw), pygame.SRCALPHA)
    if not connections & NORTH:
        pygame.draw.line(surf, C_BLACK, tile_rect.topleft, tile_rect.topright, lw)
        hori.fill((255, 255, 255, 70))
        surf.blit(hori, (tile_rect.left+lw, tile_rect.top+lw))
    if not connections & EAST:
        pygame.draw.line(surf, C_BLACK, tile_rect.topright, tile_rect.bottomright, lw)
        vert.fill((255, 255, 255, 70))
        surf.blit(vert, (tile_rect.right-2*lw, tile_rect.top+lw))
    if not connections & SOUTH:
        pygame.draw.line(surf, C_BLACK, tile_rect.bottomright, tile_rect.bottomleft, lw)
        hori.fill((0, 0, 0, 40))
        surf.blit(hori, (tile_rect.left+lw, tile_rect.bottom-2*lw))
    if not connections & WEST:
        pygame.draw.line(surf, C_BLACK, tile_rect.bottomleft, tile_rect.topleft, lw)
        vert.fill((0, 0, 0, 40))
        surf.blit(vert, (tile_rect.left+lw, tile_rect.top+lw))

    # Corner shading.
    corner = pygame.Surface((2*lw, 2*lw), pygame.SRCALPHA)
    if connections & NORTH and connections & EAST:
        corner.fill((255, 255, 255, 70))
        surf.blit(corner, (tile_rect.right-2*lw, tile_rect.top+lw))
    if connections & SOUTH and connections & EAST:
        corner.fill((0, 0, 0, 40))
        surf.blit(corner, (tile_rect.right-2*lw, tile_rect.bottom-2*lw))
    if connections & SOUTH and connections & WEST:
        corner.fill((0, 0, 0, 40))
        surf.blit(corner, (tile_rect.left+lw, tile_rect.bottom-2*lw))
    if connections & NORTH and connections & WEST:
        corner.fill((255, 255, 255, 70))
        surf.blit(corner, (tile_rect.left+lw, tile_rect.top+lw))


def MARK_PATH(surf, color, pos, connections, ts):
    tile_rect = pygame.Rect(pos[0], pos[1], ts, ts)
    dot_size = int(ts/7+.5)
    width = int(ts/15-.5)
    if dot_size % 2 != width % 2:
        width -= 1
    if width <= 0:
        width = 1
        dot_size += 1
    pygame.draw.rect(surf, color, pygame.Rect(pos[0] + (ts-dot_size)//2 + 1, pos[1] + (ts-dot_size)//2 + 1, dot_size, dot_size))
    if connections & NORTH:
        pygame.draw.line(surf, color, tile_rect.center, tile_rect.midtop, width)
    if connections & EAST:
        pygame.draw.line(surf, color, tile_rect.center, tile_rect.midright, width)
    if connections & SOUTH:
        pygame.draw.line(surf, color, tile_rect.center, tile_rect.midbottom, width)
    if connections & WEST:
        pygame.draw.line(surf, color, tile_rect.center, tile_rect.midleft, width)


class Tile:
    def __init__(self):
        self.color = C_WHITE
        self.style = MARK_FLAT
        self.connections = 0

    def put(self, color, style):
        self.color = color
        self.style = style

    def connect(self, direction):
        self.connections |= direction

    def disconnect(self, direction):
        self.connections &= ~direction

    def erase(self):
        self.color = C_WHITE
        self.style = MARK_FLAT

    def draw(self, screen, pos, ts):
        self.style(screen, self.color, pos, self.connections, ts)

    def encode(self):
        style_c = '?'
        if self.style == MARK_FLAT: style_c = 'O'
        elif self.style == MARK_PATH: style_c = '+'
        elif self.style == MARK_FILL: style_c = '#'
        color_c = chr(self.color[0]) + chr(self.color[1]) + chr(self.color[2])
        cnnct_c = chr(self.connections)
        return style_c + color_c + cnnct_c


class Grid():
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[Tile() for i in range(cols)] for j in range(rows)]

    def at(self, row, col):
        return self.grid[row][col]

    def put(self, place, color, style):
        self.grid[place[0]][place[1]].put(color, style)

    def connect(self, place, direction):
        if direction == -1: return
        self.grid[place[0]][place[1]].connect(direction)
        if direction & NORTH and place[0] > 0:
            self.grid[place[0]-1][place[1]].connect(SOUTH)
        if direction & EAST and place[1] < self.cols-1:
            self.grid[place[0]][place[1]+1].connect(WEST)
        if direction & SOUTH and place[0] < self.rows-1:
            self.grid[place[0]+1][place[1]].connect(NORTH)
        if direction & WEST and place[1] > 0:
            self.grid[place[0]][place[1]-1].connect(EAST)

    def disconnect(self, place, direction):
        self.grid[place[0]][place[1]].disconnect(direction)
        if direction & NORTH and place[0] > 0:
            self.grid[place[0]-1][place[1]].disconnect(SOUTH)
        if direction & EAST and place[1] < self.cols-1:
            self.grid[place[0]][place[1]+1].disconnect(WEST)
        if direction & SOUTH and place[0] < self.rows-1:
            self.grid[place[0]+1][place[1]].disconnect(NORTH)
        if direction & WEST and place[1] > 0:
            self.grid[place[0]][place[1]-1].disconnect(EAST)

    def erase(self, place):
        self.grid[place[0]][place[1]].erase()
        self.disconnect((place[0], place[1]), NORTH | EAST | SOUTH | WEST)

    def draw(self, surf, pos, ts):
        gr = pygame.Rect(pos[0], pos[1], ts*self.cols, ts*self.rows)

        for i in range(self.rows):
            for j in range(self.cols):
                self.at(i, j).draw(surf, (gr.left + ts*j, gr.top + ts*i), ts)

        line_width = max(int(ts/40 + .5), 1)
        for i in range(self.rows):
            line = pygame.Surface((gr.width, line_width), pygame.SRCALPHA)
            line.fill((0, 0, 0, 50))
            surf.blit(line, (gr.left, gr.top + ts*i))
        for i in range(self.cols):
            line = pygame.Surface((line_width, gr.height), pygame.SRCALPHA)
            line.fill((0, 0, 0, 50))
            surf.blit(line, (gr.left + ts*i, gr.top))

        pygame.draw.rect(surf, C_BLACK, pygame.Rect(gr.x, gr.y, gr.width+2, gr.height+2), max(int(ts/15 + .5), 1))
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
    gr = grid_rect(screen)
    clr_size = int(gr.width / main_grid.cols * 0.8)

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

    colors = [C_BLACK, C_RED, C_ORANGE, C_YELLOW, C_GREEN, C_CYAN, C_BLUE, C_PURPLE]
    current_color = 0

    BLOB = 0
    TREE = 1
    TRACE = 2
    connection_mode = TRACE

    style = MARK_FLAT

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
                    gr = grid_rect(screen)
                    ts = tile_size(screen)
                    row = int((event.pos[1] - gr.top)//ts)
                    col = int((event.pos[0] - gr.left)//ts)
                    if 0 <= row < main_grid.rows and 0 <= col < main_grid.cols and (row, col) != previous:
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
                    gr = grid_rect(screen)
                    ts = tile_size(screen)
                    row = int((event.pos[1] - gr.top)//ts)
                    col = int((event.pos[0] - gr.left)//ts)
                    if 0 <= row < main_grid.rows and 0 <= col < main_grid.cols:
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
                    style = MARK_PATH
                elif event.key == pygame.K_t:
                    style = MARK_FILL
                elif event.key == pygame.K_y:
                    style = MARK_FLAT
                elif event.key == pygame.K_s:
                    if event.mod & pygame.KMOD_CTRL:
                        gr = grid_rect(screen)
                        grid_surf = pygame.Surface((gr.width+2, gr.height+2))
                        grid_surf.fill(C_WHITE)
                        main_grid.draw(grid_surf, (0, 0), tile_size(screen))
                        pygame.image.save(grid_surf, "grids/img/latest.png")

        screen.fill(C_WHITE)
        main_grid.draw(screen, grid_rect(screen).topleft, tile_size(screen))
        draw_colors(screen, colors, current_color)

        pygame.display.update()


if __name__ == '__main__':
    main()