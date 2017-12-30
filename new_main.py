from grid import Grid
from color import Palette
from style import style_packs#, compose
import size
from const import *

import hgf
import pygame


pygame.init()
pygame.mixer.quit()


class GridColoringApp(hgf.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid = None
        self.palette = None

    def on_load(self):
        self.palette = Palette(COLORS)
        self.register_load(self.palette)

        self.grid = Grid(8, 8)
        self.grid.color = self.palette.colors[self.palette.index]
        self.register_load(self.grid)

    def refresh_proportions(self):
        super().refresh_proportions()
        self.grid.size = size.grid_rect(self.size, self.grid).size
        self.grid._bw = size.border_width(self.size, self.grid)
        self.grid._lw = size.line_width(self.size, self.grid)
        self.grid._ts = size.tile_size(self.size, self.grid)

        self.palette.size = size.palette_rect(self.size, self.grid, len(self.palette.colors)).size
        self.palette._cs = size.splotch_size(self.size, self.grid, len(self.palette.colors))
        self.palette._gap = size.splotch_gap(self.size, self.grid, len(self.palette.colors))

    def refresh_layout(self):
        self.grid.pos = size.grid_rect(self.size, self.grid).topleft
        self.palette.pos = size.palette_rect(self.size, self.grid, len(self.palette.colors)).topleft

    def on_key_down(self, unicode, key, mod):
        if key == pygame.K_s:
            if mod & pygame.KMOD_CTRL:
                pygame.image.save(self.grid._display, "grids/img/latest.png")

    def handle_message(self, sender, message, **params):
        if message == Palette.MSG_CHANGED_COLOR:
            self.grid.color = params['color']
        else:
            super().handle_message(sender, message, **params)


launcher = hgf.AppManager('grid-coloring', GridColoringApp)
launcher.style_packs = style_packs
# launcher.compose_style = compose
launcher.load()
launcher.spawn_app().launch(fps=60, debug=True)
