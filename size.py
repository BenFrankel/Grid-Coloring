import pygame

# The following functions are to allow the main drawing grid to change its size to match the window dimensions.


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


# Returns a Rect object for the grid. TODO: Lower "top" in case of a short and fat grid.
def grid_rect(screen, grid):
    ts = tile_size(screen, grid)
    lw = line_width(screen, grid)
    bw = border_width(screen, grid)

    width = (ts + lw) * grid.ncols - lw + 2*bw
    height = (ts + lw) * grid.nrows - lw + 2*bw
    top = (screen.get_height() - height - 2*ts) // 2
    left = (screen.get_width() - width) // 2

    return pygame.Rect(left, top, width, height)


# Returns the pixel sidelength of a color square. TODO: Reasonable size when tile_size is tiny.
def color_size(screen, grid, colors):
    gr = grid_rect(screen, grid)
    cs = int(gr.width / grid.ncols * 0.8)
    if (screen.get_width() - cs/2)/len(colors)/cs <= 1.1:
        cs = int(cs * 0.8)
    return cs


# Returns the proportional size of the gap between color squares (proportional to color_size).
def color_gap(screen, grid, colors):
    cs = color_size(screen, grid, colors)
    return max(min(0.5, (screen.get_width() - cs/2)/len(colors)/cs - 1), 0.1)


# Returns a Rect object for the color pallet.
def color_rect(screen, grid, colors):
    cs = color_size(screen, grid, colors)
    gap = color_gap(screen, grid, colors)
    gr = grid_rect(screen, grid)

    width = cs*(1+gap)*len(colors) - cs*gap
    height = cs
    top = (screen.get_height() + gr.bottom - height)//2
    left = (screen.get_width() - width)//2

    return pygame.Rect(left, top, width, height)
