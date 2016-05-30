import pygame
import size
from constants import Direction, Color


# Plain color fill.
def FLAT(surf, color, pos, connections, ts):
    lw = size.line_width(ts)
    tile_rect = pygame.Rect(pos[0]+lw-1, pos[1]+lw-1, ts-lw+1, ts-lw+1)
    pygame.draw.rect(surf, color, tile_rect)
DEFAULT = FLAT


# Color fill with borders.
def FILL(surf, color, pos, connections, ts):
    tile_rect = pygame.Rect(pos[0], pos[1], ts, ts)
    pygame.draw.rect(surf, color, tile_rect)
    lw = size.line_width(ts)

    # Boundary and shading.
    hori = pygame.Surface((tile_rect.width-lw, 2*lw), pygame.SRCALPHA)
    vert = pygame.Surface((2*lw, tile_rect.height-lw), pygame.SRCALPHA)
    if not connections & Direction.NORTH:
        pygame.draw.line(surf, Color.BLACK, tile_rect.topleft, tile_rect.topright, lw)
        hori.fill((255, 255, 255, 70))
        surf.blit(hori, (tile_rect.left+lw, tile_rect.top+lw))
    if not connections & Direction.EAST:
        pygame.draw.line(surf, Color.BLACK, tile_rect.topright, tile_rect.bottomright, lw)
        vert.fill((255, 255, 255, 70))
        surf.blit(vert, (tile_rect.right-2*lw, tile_rect.top+lw))
    if not connections & Direction.SOUTH:
        pygame.draw.line(surf, Color.BLACK, tile_rect.bottomright, tile_rect.bottomleft, lw)
        hori.fill((0, 0, 0, 40))
        surf.blit(hori, (tile_rect.left+lw, tile_rect.bottom-2*lw))
    if not connections & Direction.WEST:
        pygame.draw.line(surf, Color.BLACK, tile_rect.bottomleft, tile_rect.topleft, lw)
        vert.fill((0, 0, 0, 40))
        surf.blit(vert, (tile_rect.left+lw, tile_rect.top+lw))

    # Corner shading.
    corner = pygame.Surface((2*lw, 2*lw), pygame.SRCALPHA)
    if connections & Direction.NORTH and connections & Direction.EAST:
        corner.fill((255, 255, 255, 70))
        surf.blit(corner, (tile_rect.right-2*lw, tile_rect.top+lw))
    if connections & Direction.SOUTH and connections & Direction.EAST:
        corner.fill((0, 0, 0, 40))
        surf.blit(corner, (tile_rect.right-2*lw, tile_rect.bottom-2*lw))
    if connections & Direction.SOUTH and connections & Direction.WEST:
        corner.fill((0, 0, 0, 40))
        surf.blit(corner, (tile_rect.left+lw, tile_rect.bottom-2*lw))
    if connections & Direction.NORTH and connections & Direction.WEST:
        corner.fill((255, 255, 255, 70))
        surf.blit(corner, (tile_rect.left+lw, tile_rect.top+lw))


# Node + Edges type of mark.
def PATH(surf, color, pos, connections, ts):
    tile_rect = pygame.Rect(pos[0], pos[1], ts, ts)
    dot_size = int(ts/7+.5)
    width = int(ts/15-.5)
    if dot_size % 2 != width % 2:
        width -= 1
    if width <= 0:
        width = 1
        dot_size += 1
    pygame.draw.rect(surf, color, pygame.Rect(pos[0] + (ts-dot_size)//2 + 1, pos[1] + (ts-dot_size)//2 + 1, dot_size, dot_size))
    if connections & Direction.NORTH:
        pygame.draw.line(surf, color, tile_rect.center, tile_rect.midtop, width)
    if connections & Direction.EAST:
        pygame.draw.line(surf, color, tile_rect.center, tile_rect.midright, width)
    if connections & Direction.SOUTH:
        pygame.draw.line(surf, color, tile_rect.center, tile_rect.midbottom, width)
    if connections & Direction.WEST:
        pygame.draw.line(surf, color, tile_rect.center, tile_rect.midleft, width)