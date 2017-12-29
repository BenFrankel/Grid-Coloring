import pygame

# The following functions are to allow the main drawing grid to change its size to match the window dimensions


# Returns the pixel sidelength of a tile
def tile_size(dim, grid):
    return max(int(min(dim[0] / (grid.ncols + 2), dim[1] / (grid.nrows + 4)) - .5), 1)


# Returns the pixel width of a line
def line_width(dim, grid):
    ts = tile_size(dim, grid)
    return max(int(ts / 32 + .5), 1)


# Returns the pixel width of the border
def border_width(dim, grid):
    ts = tile_size(dim, grid)
    return max(int(ts / 15 + .5), 1)


# Returns a Rect object for the grid TODO: Lower "top" in case of a short and fat grid
def grid_rect(dim, grid):
    ts = tile_size(dim, grid)
    lw = line_width(dim, grid)
    bw = border_width(dim, grid)

    width = (ts + lw) * grid.ncols - lw + 2 * bw
    height = (ts + lw) * grid.nrows - lw + 2 * bw
    top = (dim[1] - height - 2 * ts) // 2
    left = (dim[0] - width) // 2

    return pygame.Rect(left, top, width, height)


# Returns the pixel sidelength of a color square TODO: Reasonable size when tile_size is tiny
def splotch_size(dim, grid, num_colors):
    gr = grid_rect(dim, grid)
    cs = int(gr.width / grid.ncols * 0.8)
    if (dim[0] - cs / 2) / num_colors / cs <= 1.1:
        cs = int(cs * 0.8)
    return cs


# Returns the proportional size of the gap between color squares (proportional to color_size)
def splotch_gap(dim, grid, num_colors):
    cs = splotch_size(dim, grid, num_colors)
    return max(min(0.5, (dim[0] - cs/2) / num_colors / cs - 1), 0.1)


# Returns a Rect object for the color palette
def palette_rect(dim, grid, num_colors):
    cs = splotch_size(dim, grid, num_colors)
    gap = splotch_gap(dim, grid, num_colors)
    gr = grid_rect(dim, grid)

    width = cs * ((1 + gap) * num_colors - gap)
    height = cs
    top = (dim[1] + gr.bottom - height) // 2
    left = (dim[0] - width) // 2

    return pygame.Rect(left, top, width, height)
