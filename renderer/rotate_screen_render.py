from abc import abstractmethod

from PIL import ImageColor

from renderer.renderer import Renderer
import debug
import time


class RotateScreenRenderer(Renderer):
    def __init__(self, data, config, render_surface):
        super().__init__(config, render_surface)
        debug.log(data)
        self.data = data

        self.display_time = 5
        self.start_time = None
        self.current_item = 0
        self.last_item = -1

    @abstractmethod
    def _do_render(self, image, draw, frame_time):
        pass

    def _get_item_to_display(self):
        if self.start_time is not None:
            debug.log(time.time() - self.start_time)
            self.last_item = self.current_item

            if self.display_time <= time.time() - self.start_time:
                self.last_item = self.current_item
                self.current_item = (self.current_item + 1) % len(self.data)
                self.start_time = time.time()
                self.text_y_pos = 0
        else:
            self.start_time = time.time()

        debug.log(self.current_item)
        debug.log("last item: {}".format(self.last_item))
        return self.data[self.current_item]

    def _item_has_changed(self):
        return self.current_item != self.last_item

    def _draw_page_indicator(self, draw):
        color = ImageColor.getcolor('white', 'RGB')
        color_current_item = ImageColor.getcolor('red', 'RGB')
        num_items = len(self.data)
        length = num_items * 3
        small = length > self._get_screen_width() * float(0.6)

        if small:
            length = num_items * 2

        x = (self._get_screen_width() - length) / 2
        y = self._get_screen_height() - 2
        size = 0 if small else 1

        for i in range(0, num_items):
            draw.rectangle([x, y, x + size, y + size], color if i != self.current_item else color_current_item)
            x = x + (size + 2)

    @staticmethod
    def _get_last_part(text):
        parts = text.split()
        return parts[len(parts) - 1]

