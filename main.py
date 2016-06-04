import pygame
from pygame.locals import VIDEORESIZE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, KEYDOWN, KEYUP, QUIT
from grid import *
import tilemark
import displaysize
import gridutil
import draw


pygame.init()


def main():
    screen = pygame.display.set_mode((600, 400), pygame.RESIZABLE)
    pygame.display.set_caption("Grid Coloring")

    main_grid = Grid(NUM_ROWS, NUM_COLS)

    colors = [BLACK, RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE]
    color_index = 0

    BLOB = 0
    TREE = 1
    TRACE = 2
    connection_mode = TRACE

    style = tilemark.DEFAULT

    visited = set()
    previous = (-1, -1)

    while True:
        gr = displaysize.grid_rect(screen, main_grid)
        ts = displaysize.tile_size(screen, main_grid)
        lw = displaysize.line_width(screen, main_grid)
        bw = displaysize.border_width(screen, main_grid)
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
                            if colors[color_index] != main_grid.at(current).color or style != main_grid.at(current).style:
                                main_grid.erase(current)
                                visited.discard(current)

                            if connection_mode == TREE:
                                if current not in visited:
                                    adj = gridutil.adjacency(current, previous)
                                    main_grid.connect(previous, adj)

                            elif connection_mode == BLOB:
                                for direction in NORTH, WEST, SOUTH, EAST:
                                    if gridutil.near(current, direction) in visited:
                                        main_grid.connect(current, direction)

                            elif connection_mode == TRACE:
                                adj = gridutil.adjacency(current, previous)
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
                            if event.button == 3 or colors[color_index] != main_grid.at(current).color \
                                    or style != main_grid.at(current).style:
                                main_grid.erase(current)
                                visited.discard(current)
                            if event.button == 1:
                                visited.add(current)
                                previous = current
                                main_grid.put(current, colors[color_index], style)

            elif event.type == KEYDOWN:
                if event.unicode.isdigit() and not pygame.mouse.get_pressed()[0]:
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
                    style = tilemark.PATH

                elif event.key == pygame.K_o:
                    style = tilemark.FILL

                elif event.key == pygame.K_p:
                    style = tilemark.FLAT

                elif event.key == pygame.K_s:
                    if event.mod & pygame.KMOD_CTRL:
                        gr = displaysize.grid_rect(screen, main_grid)
                        grid_surf = pygame.Surface((gr.width, gr.height))
                        grid_surf.fill(WHITE)
                        draw.draw_grid(grid_surf,
                                       main_grid,
                                       (0, 0),
                                       displaysize.tile_size(screen, main_grid),
                                       displaysize.line_width(screen, main_grid),
                                       displaysize.border_width(screen, main_grid))
                        pygame.image.save(grid_surf, "grids/img/latest.png")

                elif event.key == pygame.K_g:
                    if event.mod & pygame.KMOD_CTRL:
                        save_grid(main_grid)

                elif event.key == pygame.K_l:
                    if event.mod & pygame.KMOD_CTRL:
                        main_grid = load_grid()
                        visited = set()
                        for i in range(main_grid.nrows):
                            for j in range(main_grid.ncols):
                                if main_grid.at(i, j).color != WHITE or main_grid.at(i, j).style != tilemark.DEFAULT:
                                    visited.add((i, j))

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

        draw.draw_grid(screen,
                       main_grid,
                       displaysize.grid_rect(screen, main_grid).topleft,
                       displaysize.tile_size(screen, main_grid),
                       displaysize.line_width(screen, main_grid),
                       displaysize.border_width(screen, main_grid))

        draw.draw_colors(screen,
                         main_grid,
                         displaysize.color_rect(screen, main_grid, colors).topleft,
                         displaysize.color_size(screen, main_grid, colors),
                         displaysize.color_gap(screen, main_grid, colors),
                         colors,
                         color_index)

        pygame.display.update()


if __name__ == '__main__':
    main()