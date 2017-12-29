import size
import util
from const import *

import pygame


while True:
    gr = size.grid_rect(window.dim, window.main_grid)
    ts = size.tile_size(window.dim, window.main_grid)
    lw = size.line_width(window.dim, window.main_grid)
    bw = size.border_width(window.dim, window.main_grid)

    # for event in pygame.event.get():

        # elif event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_g:
        #         if event.mod & pygame.KMOD_CTRL:
        #             save_grid(window.main_grid)
        #
        #     elif event.key == pygame.K_l:
        #         if event.mod & pygame.KMOD_CTRL:
        #             window.main_grid = load_grid()
        #             visited = set()
        #             for i in range(window.main_grid.nrows):
        #                 for j in range(window.main_grid.ncols):
        #                     if window.main_grid.at(i, j).color != WHITE or window.main_grid.at(i, j).style != mark.DEFAULT:
        #                         visited.add((i, j))
        #
            # elif event.key == pygame.K_UP:
            #     grid = window.main_grid.grid
            #     if event.mod & pygame.KMOD_SHIFT:
            #         if window.main_grid.nrows > MIN_SIZE:
            #             window.main_grid.nrows -= 1
            #             window.main_grid.grid = grid[1:]
            #             for j in range(window.main_grid.ncols):
            #                 window.main_grid.disconnect((0, j), NORTH)
            #     elif window.main_grid.nrows < MAX_SIZE:
            #         window.main_grid.nrows += 1
            #         window.main_grid.grid = [[Tile() for j in range(window.main_grid.ncols)]] + grid
            #
            # elif event.key == pygame.K_DOWN:
            #     grid = window.main_grid.grid
            #     if event.mod & pygame.KMOD_SHIFT:
            #         if window.main_grid.nrows > MIN_SIZE:
            #             window.main_grid.nrows -= 1
            #             window.main_grid.grid = grid[:-1]
            #             for j in range(window.main_grid.ncols):
            #                 window.main_grid.disconnect((window.main_grid.nrows - 1, j), SOUTH)
            #     elif window.main_grid.nrows < MAX_SIZE:
            #         window.main_grid.nrows += 1
            #         window.main_grid.grid = grid + [[Tile() for j in range(window.main_grid.ncols)]]
            #
            # elif event.key == pygame.K_RIGHT:
            #     grid = window.main_grid.grid
            #     if event.mod & pygame.KMOD_SHIFT:
            #         if window.main_grid.ncols > MIN_SIZE:
            #             for i in range(window.main_grid.nrows):
            #                 grid[i].pop()
            #             window.main_grid.ncols -= 1
            #             window.main_grid.grid = grid
            #             for i in range(window.main_grid.nrows):
            #                 window.main_grid.disconnect((i, window.main_grid.ncols - 1), EAST)
            #     elif window.main_grid.ncols < MAX_SIZE:
            #         for i in range(window.main_grid.nrows):
            #             grid[i].append(Tile())
            #         window.main_grid.ncols += 1
            #         window.main_grid.grid = grid
            #
            # elif event.key == pygame.K_LEFT:
            #     grid = window.main_grid.grid
            #     if event.mod & pygame.KMOD_SHIFT:
            #         if window.main_grid.ncols > MIN_SIZE:
            #             for i in range(window.main_grid.nrows):
            #                 grid[i] = grid[i][1:]
            #             window.main_grid.ncols -= 1
            #             window.main_grid.grid = grid
            #     elif window.main_grid.ncols < MAX_SIZE:
            #         for i in range(window.main_grid.nrows):
            #             grid[i] = [Tile()] + grid[i]
            #         window.main_grid.ncols += 1
            #         window.main_grid.grid = grid
            #         for i in range(window.main_grid.nrows):
            #             window.main_grid.disconnect((i, 0), WEST)
