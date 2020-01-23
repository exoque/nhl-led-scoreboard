from abc import abstractmethod

from PIL import ImageColor

from renderer.renderer import Renderer
import logging
import time


class RotateScreenRenderer(Renderer):
    def __init__(self, config, render_surface):
        super().__init__(config, render_surface)

        self.display_time = 5
        self.start_time = None
        self.current_item = 0
        self.last_item = -1

    @abstractmethod
    def _do_render(self, image, draw, frame_time):
        pass

    def _get_item_to_display(self):
        if self.data is None or len(self.data) == 0:
            return None

        if self.start_time is not None:
            logging.debug(time.time() - self.start_time)
            self.last_item = self.current_item

            if self.display_time <= time.time() - self.start_time:
                self.last_item = self.current_item
                self.current_item = (self.current_item + 1) % len(self.data)
                self.start_time = time.time()
                self.text_y_pos = 0
        else:
            self.start_time = time.time()

        logging.debug(self.current_item)
        logging.debug("last item: {}".format(self.last_item))
        return self.data[self.current_item]

    def _item_has_changed(self):
        return self.current_item != self.last_item

    #FIXME: correct implementation
    def _draw_page_indicator_scaled(self, draw):
        color = ImageColor.getcolor('white', 'RGB')
        color_current_item = ImageColor.getcolor('red', 'RGB')
        num_items = len(self.data)
        item_width = self._get_screen_width() / 64
        length = num_items * item_width * 1.5
        small = length > self._get_screen_width() * float(0.6)

        if small:
            length = num_items * item_width

        x = (self._get_screen_width() - length) / 2
        y = self._get_screen_height() - item_width

        size = item_width - 1 if small else item_width

        for i in range(0, num_items):
            draw.rectangle([x, y, x + size, y + size], color if i != self.current_item else color_current_item)
            x = x + (size + item_width)

    def _draw_page_indicator(self, draw):
        if self.data is None or len(self.data) == 0:
            return

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

