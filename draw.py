import pygame
from constants import *


def draw_tile(surf, tile, pos, ts, lw):
    tile.style(surf, pos, tile.color, tile.connections, ts, lw)


def draw_grid(surf, grid, pos, ts, lw, bw):
    gr = pygame.Rect(pos[0], pos[1], (ts + lw) * grid.ncols - lw + 2*bw, (ts + lw) * grid.nrows - lw + 2*bw)

    # Draw edges.
    for i in range(1, grid.nrows):
        line = pygame.Surface((gr.width - 2*bw, lw))
        line.fill(L_GRAY)
        surf.blit(line, (gr.left + bw, gr.top + (ts+lw)*i + bw - lw))
    for i in range(1, grid.ncols):
        line = pygame.Surface((lw, gr.height - 2*bw))
        line.fill(L_GRAY)
        surf.blit(line, (gr.left + (ts+lw)*i + bw - lw, gr.top + bw))

    # Draw tiles.
    for i in range(grid.nrows):
        for j in range(grid.ncols):
            pos = (gr.left + (ts+lw)*j + bw - lw, gr.top + (ts+lw)*i + bw - lw)
            draw_tile(surf, grid.at(i, j), pos, ts, lw)

    # Draw boundary.
    line = pygame.Surface((bw, gr.height))
    line.fill(BLACK)
    surf.blit(line, gr.topleft)
    surf.blit(line, (gr.right - bw, gr.top))
    line = pygame.Surface((gr.width, bw))
    line.fill(BLACK)
    surf.blit(line, gr.topleft)
    surf.blit(line, (gr.left, gr.bottom - bw))


def draw_colors(screen, grid, pos, cs, gap, colors, color_index):
    for i, c in enumerate(colors):
        x = pos[0] + cs*(1+gap)*i
        if i == color_index:
            pygame.draw.rect(screen, c, pygame.Rect(x, pos[1] - cs*gap/2, cs, cs))
        else:
            pygame.draw.rect(screen, c, pygame.Rect(x, pos[1], cs, cs))
