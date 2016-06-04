import pygame
from constants import *

# The following functions are the different marking styles.
# They take as arguments the surface being drawn onto, the tile's position, the tile's color,
# the tile's connections, the tile's size, and the line width.
# Then the functions draw their respective markings from these arguments.


# Plain color fill.
def FLAT(surf, pos, color, connections, ts, lw):
    tile_rect = pygame.Rect(pos[0] + lw, pos[1] + lw, ts, ts)
    pygame.draw.rect(surf, color, tile_rect)

DEFAULT = FLAT


# Color fill with borders and shading.
def FILL(surf, pos, color, connections, ts, lw):
    tr = pygame.Rect(pos[0] + lw, pos[1] + lw, ts, ts)
    pygame.draw.rect(surf, color, pygame.Rect(pos[0], pos[1], ts + 2*lw, ts + 2*lw))

    # Edge boundary and shading.
    sw = 2 * lw
    hori_shade = pygame.Surface((tr.width, sw), pygame.SRCALPHA)
    vert_shade = pygame.Surface((sw, tr.height), pygame.SRCALPHA)
    hori_border = pygame.Surface((tr.width + 2*lw, lw))
    hori_border.fill(BLACK)
    vert_border = pygame.Surface((lw, tr.height + 2*lw))
    vert_border.fill(BLACK)
    hori_cover = pygame.Surface((tr.width, lw), pygame.SRCALPHA)
    hori_cover.fill((*BLACK, 50))
    vert_cover = pygame.Surface((lw, tr.height), pygame.SRCALPHA)
    vert_cover.fill((*BLACK, 50))
    if connections & NORTH:
        surf.blit(hori_cover, (tr.left, tr.top - lw))
    else:
        hori_shade.fill((*WHITE, 70))
        surf.blit(hori_shade, tr.topleft)
        surf.blit(hori_border, (tr.left - lw, tr.top - lw))
    if connections & WEST:
        surf.blit(vert_cover, (tr.left - lw, tr.top))
    else:
        vert_shade.fill((*BLACK, 40))
        surf.blit(vert_shade, tr.topleft)
        surf.blit(vert_border, (tr.left - lw, tr.top - lw))
    if not connections & SOUTH:
        hori_shade.fill((*BLACK, 40))
        surf.blit(hori_shade, (tr.left, tr.bottom - sw))
        surf.blit(hori_border, (tr.left - lw, tr.bottom))
    if not connections & EAST:
        vert_shade.fill((*WHITE, 70))
        surf.blit(vert_shade, (tr.right - sw, tr.top))
        surf.blit(vert_border, (tr.right, tr.top - lw))

    # Corner boundary and shading.
    corner_shade = pygame.Surface((sw, sw), pygame.SRCALPHA)
    corner_border = pygame.Surface((lw, lw))
    corner_border.fill(BLACK)
    if connections & NORTH and connections & WEST:
        corner_shade.fill((*WHITE, 70))
        surf.blit(corner_shade, tr.topleft)
        surf.blit(corner_border, (tr.left - lw, tr.top - lw))
    if connections & WEST and connections & SOUTH:
        corner_shade.fill((*BLACK, 40))
        surf.blit(corner_shade, (tr.left, tr.bottom - sw))
        surf.blit(corner_border, (tr.left - lw, tr.bottom))
    if connections & SOUTH and connections & EAST:
        corner_shade.fill((*BLACK, 40))
        surf.blit(corner_shade, (tr.right - sw, tr.bottom - sw))
        surf.blit(corner_border, tr.bottomright)
    if connections & EAST and connections & NORTH:
        corner_shade.fill((*WHITE, 70))
        surf.blit(corner_shade, (tr.right - sw, tr.top))
        surf.blit(corner_border, (tr.right, tr.top - lw))


# Node + Edges type of mark.
def PATH(surf, pos, color, connections, ts, lw):
    tr = pygame.Rect(pos[0] + lw, pos[1] + lw, ts, ts)
    ds = int(ts / 7 + .5)
    ew = int(ts / 15 - .5)
    if ds % 2 != ew % 2:
        ew -= 1
    if ew <= 0:
        ew = 1
        ds += 1
    dot = pygame.Surface((ds, ds))
    dot.fill(color)
    surf.blit(dot, (tr.left + (ts - ds)//2 + 1, tr.top + (ts - ds)//2 + 1))
    if connections & NORTH:
        pygame.draw.line(surf, color, tr.center, tr.midtop, ew)
    if connections & WEST:
        pygame.draw.line(surf, color, tr.center, tr.midleft, ew)
    if connections & SOUTH:
        pygame.draw.line(surf, color, tr.center, tr.midbottom, ew)
    if connections & EAST:
        pygame.draw.line(surf, color, tr.center, tr.midright, ew)
