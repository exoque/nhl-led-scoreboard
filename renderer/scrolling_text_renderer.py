import time
from math import ceil

from renderer.renderer import Renderer

import logging


class ScrollingTextRenderer(Renderer):
    def __init__(self, data, config, render_surface, scroll_speed=5):
        super().__init__(config, render_surface)
        logging.debug(data)
        self.data = data
        self.scroll_speed = scroll_speed
        self.x_pos = self._get_screen_width()
        self.frame_time = None

    def _do_render(self, image, draw, frame_time):
        scroll_distance = 0
        self._render_text(draw, self.data, self.x_pos, 10)

        length = self._get_text_length(None, self.data)
        if length + self.x_pos + self.scroll_speed < 0:
            self.x_pos = self._get_screen_width() + self.scroll_speed
        else:

            if self.frame_time is not None:
                logging.debug(time.time() - self.frame_time)

                time_delta = time.time() - self.frame_time
                logging.debug("time_delta: " + str(time_delta))
                scroll_distance = ceil(time_delta * self.scroll_speed)
                logging.debug("scroll_distance: " + str(scroll_distance))
                self.frame_time = time.time()
            else:
                self.frame_time = time.time()

            self.x_pos = self.x_pos - scroll_distance

            logging.debug("x_pos: " + str(self.x_pos))

        self._refresh_screen(image)

    def is_finished(self):
        return self.x_pos + self._get_text_length(None, self.data) + self.scroll_speed < 0

    def update_data(self, data):
        self.data = data
        self.x_pos = self._get_screen_width()


