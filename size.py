import pygame


# Returns the pixel sidelength of a tile, given the window and grid dimensions.
def tile_size(screen, grid):
    return int(min(screen.get_width() / (grid.cols+2), screen.get_height() / (grid.rows+3)))


# Returns the pixel width of a line, given (the window and grid dimensions) or (the tile size).
def line_width(*args):
    if len(args) == 1:
        ts = args[0]
        return max(int(ts / 32 + .5), 1)
    elif len(args) == 2:
        screen = args[0]
        grid = args[1]
        ts = tile_size(screen, grid)
        return line_width(ts)


# Returns a Rect object for the grid, given the window and grid dimensions.
def grid_rect(screen, grid):
    ts = tile_size(screen, grid)

    width = ts * grid.cols
    height = ts * grid.rows
    top = ts/2
    left = (screen.get_width() - width)/2

    return pygame.Rect(left, top, width, height)