import hgf
import pygame


class Splotch(hgf.FlatComponent):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self.type = 'splotch'
        self._bg_factory = None

        self.color = color

    def load_style(self):
        self._bg_factory = self.style_get('background')

    def refresh_background(self):
        self.background = self._bg_factory(
            self.size,
            self.color
        )


class Palette(hgf.LayeredComponent):
    MSG_CHANGED_COLOR = 'palette-changed-color'

    def __init__(self, colors, **kwargs):
        super().__init__(**kwargs)
        self._splotches = None
        self.index = 0
        self.colors = colors

        self._cs = None
        self._gap = None

    def on_load(self):
        self._splotches = [Splotch(color) for color in self.colors]
        self.register_load(*self._splotches)

    @hgf.double_buffer
    class index:
        def on_transition(self):
            self.send_message(Palette.MSG_CHANGED_COLOR, color=self.colors[self.index])
            self.refresh_layout_flag = True

    def refresh_layout(self):
        super().refresh_layout()
        x = 0
        for splotch in self._splotches:
            splotch.pos = x, 0
            x += self._cs * (1 + self._gap)
        self._splotches[self.index].y -= self._cs * self._gap / 2
        for splotch in self._splotches:
            splotch.on_x_transition()
            splotch.on_y_transition()

    def refresh_proportions(self):
        super().refresh_proportions()
        for splotch in self._splotches:
            splotch.size = self._cs, self._cs

    def on_mouse_down(self, pos, button, hovered):
        if button == 4:
            self.index += 1
            self.index %= len(self.colors)
        elif button == 5:
            self.index -= 1
            self.index %= len(self.colors)

    def on_key_down(self, unicode, key, mod):
        if unicode.isdigit() and not pygame.mouse.get_pressed()[0]:
            digit = int(unicode)
            if 1 <= digit <= len(self.colors):
                self.index = digit - 1
