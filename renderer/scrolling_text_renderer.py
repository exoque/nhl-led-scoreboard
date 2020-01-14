from renderer.renderer import Renderer

import debug


class ScrollingTextRenderer(Renderer):
    def __init__(self, data, screen_config, config, render_surface):
        super().__init__(config, render_surface)
        self.screen_config = screen_config
        debug.log(data)
        self.data = data
        self.scroll_speed = 5
        self.x_pos = self.screen_width

    def _do_render(self, image, draw, frame_time):
        self._render_text(draw, self.data, self.x_pos, 10)

        length = self._get_text_length(None, self.data)
        if length + self.x_pos < 0:
            self.x_pos = self.screen_width + self.scroll_speed
        else:
            self.x_pos = self.x_pos - self.scroll_speed

        self._refresh_screen(image)
