from const import *

import pygame


def splotch_bg(size, color):
    surf = pygame.Surface(size)
    surf.fill(color)
    return surf


# Flat fill markings
def flat_mark(color, connections, ts, lw):
    side = ts + 2 * lw
    surf = pygame.Surface((side, side))
    pygame.draw.rect(surf, color, pygame.Rect(lw, lw, ts, ts))
    return surf


# Tetris-like fill markings with shading
def fill_mark(color, connections, ts, lw):
    side = ts + 2 * lw
    surf = pygame.Surface((side, side))
    tr = pygame.Rect(lw, lw, ts, ts)
    pygame.draw.rect(surf, color, pygame.Rect(0, 0, side, side))

    # Edge boundary and shading
    sw = 2 * lw
    hori_shade = pygame.Surface((ts, sw), pygame.SRCALPHA)
    vert_shade = pygame.Surface((sw, ts), pygame.SRCALPHA)
    hori_border = pygame.Surface((side, lw))
    hori_border.fill(BLACK)
    vert_border = pygame.Surface((lw, side))
    vert_border.fill(BLACK)
    hori_cover = pygame.Surface((ts, lw), pygame.SRCALPHA)
    hori_cover.fill((*BLACK, 50))
    vert_cover = pygame.Surface((lw, ts), pygame.SRCALPHA)
    vert_cover.fill((*BLACK, 50))
    if connections & NORTH:
        surf.blit(hori_cover, (lw, 0))
    else:
        hori_shade.fill((*WHITE, 70))
        surf.blit(hori_shade, (0, 0))
        surf.blit(hori_border, (0, 0))
    if connections & WEST:
        surf.blit(vert_cover, (0, 0))
    else:
        vert_shade.fill((*BLACK, 40))
        surf.blit(vert_shade, (0, 0))
        surf.blit(vert_border, (0, 0))
    if not connections & SOUTH:
        hori_shade.fill((*BLACK, 40))
        surf.blit(hori_shade, (lw, tr.bottom - sw))
        surf.blit(hori_border, (0, tr.bottom))
    if not connections & EAST:
        vert_shade.fill((*WHITE, 70))
        surf.blit(vert_shade, (tr.right - sw, tr.top))
        surf.blit(vert_border, (tr.right, 0))

    # Corner boundary and shading
    corner_shade = pygame.Surface((sw, sw), pygame.SRCALPHA)
    corner_border = pygame.Surface((lw, lw))
    corner_border.fill(BLACK)
    if connections & NORTH and connections & WEST:
        corner_shade.fill((*WHITE, 70))
        surf.blit(corner_shade, (0, 0))
        surf.blit(corner_border, (0, 0))
    if connections & WEST and connections & SOUTH:
        corner_shade.fill((*BLACK, 40))
        surf.blit(corner_shade, (lw, tr.bottom - sw))
        surf.blit(corner_border, (0, tr.bottom))
    if connections & SOUTH and connections & EAST:
        corner_shade.fill((*BLACK, 40))
        surf.blit(corner_shade, (tr.right - sw, tr.bottom - sw))
        surf.blit(corner_border, tr.bottomright)
    if connections & EAST and connections & NORTH:
        corner_shade.fill((*WHITE, 70))
        surf.blit(corner_shade, (tr.right - sw, lw))
        surf.blit(corner_border, (tr.right, 0))

    return surf


# Ball and stick (graph-like markings)
def path_mark(color, connections, ts, lw):
    side = ts + 2 * lw
    surf = pygame.Surface((side, side))
    tr = pygame.Rect(lw, lw, ts, ts)
    ds = int(ts / 7 + .5)
    ew = int(ts / 15 - .5)
    if ds % 2 != ew % 2:
        ew -= 1
    if ew <= 0:
        ew = 1
        ds += 1
    dot = pygame.Surface((ds, ds))
    dot.fill(color)
    surf.blit(dot, (lw + (ts - ds) // 2 + 1,  lw + (ts - ds) // 2 + 1))
    if connections & NORTH:
        pygame.draw.line(surf, color, tr.center, tr.midtop, ew)
    if connections & WEST:
        pygame.draw.line(surf, color, tr.center, tr.midleft, ew)
    if connections & SOUTH:
        pygame.draw.line(surf, color, tr.center, tr.midbottom, ew)
    if connections & EAST:
        pygame.draw.line(surf, color, tr.center, tr.midright, ew)

    return surf


def grid_bg(size, nrows, ncols, bw, lw, ts):
    surf = pygame.Surface(size)

    # Draw edges
    # Horizontal
    for i in range(1, nrows):
        line = pygame.Surface((size[0] - 2 * bw, lw))
        line.fill(LGREY)
        surf.blit(line, (bw, (ts + lw) * i + bw - lw))
    # Vertical
    for i in range(1, ncols):
        line = pygame.Surface((lw, size[1] - 2 * bw))
        line.fill(LGREY)
        surf.blit(line, ((ts + lw) * i + bw - lw, bw))

    # Draw boundary
    # Horizontal
    line = pygame.Surface((size[0], bw))
    line.fill(BLACK)
    surf.blit(line, (0, 0))
    surf.blit(line, (0, size[1] - bw))
    # Vertical
    line = pygame.Surface((bw, size[1]))
    line.fill(BLACK)
    surf.blit(line, (0, 0))
    surf.blit(line, (size[0] - bw, 0))

    return surf


def unknown_bg(size):
    surf = pygame.Surface(size)
    surf.fill((255, 0, 0))
    return surf


default_style_pack = {
    'default': {
        'default': {
            'background': unknown_bg,
        },
    },

    'splotch': {
        'default': {
            'background': splotch_bg,
        },
    },

    'grid': {
        'default': {
            'background': grid_bg,
            'marks': (flat_mark, fill_mark, path_mark),
        },
    },
}

style_packs = {
    'default': default_style_pack,
}
