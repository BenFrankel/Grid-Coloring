import pygame

# The following functions are to allow the main drawing grid to change its size to match the window dimensions.
# They take as arguments the screen object and main grid object to access their dimensions,
# and then return some info on how to display the grid.


# Returns the pixel sidelength of a tile.
def tile_size(screen, grid):
    return max(int(min(screen.get_width() / (grid.ncols+2), screen.get_height() / (grid.nrows+4)) - .5), 1)


# Returns the pixel width of a line.
def line_width(screen, grid):
    ts = tile_size(screen, grid)
    return max(int(ts / 32 + .5), 1)


# Returns the pixel width of the border.
def border_width(screen, grid):
    ts = tile_size(screen, grid)
    return max(int(ts / 15 + .5), 1)


# Returns a Rect object for the grid.
def grid_rect(screen, grid):
    ts = tile_size(screen, grid)
    lw = line_width(screen, grid)
    bw = border_width(screen, grid)

    width = (ts + lw) * grid.ncols - lw + 2*bw
    height = (ts + lw) * grid.nrows - lw + 2*bw
    top = ts // 2
    left = (screen.get_width() - width) // 2

    return pygame.Rect(left, top, width, height)