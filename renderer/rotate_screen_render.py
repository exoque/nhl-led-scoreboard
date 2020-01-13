from abc import abstractmethod

from PIL import ImageColor

from renderer.renderer import Renderer
import debug
import time


class RotateScreenRenderer(Renderer):
    def __init__(self, data, screen_config, config, render_surface):
        super().__init__(config)
        self.screen_config = screen_config
        debug.log(data)
        self.data = data
        self.render_surface = render_surface

        self.display_time = 5
        self.start_time = None
        self.current_item = 0

    @abstractmethod
    def _do_render(self, image, draw, frame_time):
        pass

    def _get_item_to_display(self):
        if self.start_time is not None:
            debug.log(time.time() - self.start_time)
            if self.display_time <= time.time() - self.start_time:
                self.current_item = (self.current_item + 1) % len(self.data)
                self.start_time = time.time()
        else:
            self.start_time = time.time()

        debug.log(self.current_item)
        return self.data[self.current_item]

    def _draw_page_indicator(self, draw):
        color = ImageColor.getcolor('white', 'RGB')
        color_current_item = ImageColor.getcolor('red', 'RGB')
        num_items = len(self.data)
        length = num_items * 3
        small = length > 36

        if small:
            length = num_items * 2

        x = (self.screen_width - length) / 2
        y = 30
        size = 0 if small else 1

        for i in range(0, num_items):
            draw.rectangle([x, y, x + size, y + size], color if i != self.current_item else color_current_item)
            x = x + (size + 2)

    @staticmethod
    def _get_last_part(text):
        parts = text.split()
        return parts[len(parts) - 1]
