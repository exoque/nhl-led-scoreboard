from abc import abstractmethod

from renderer.renderer import Renderer
import debug
import time


class RotateScreenRenderer(Renderer):
    def __init__(self, data, screen_config, render_surface):
        super().__init__()
        self.screen_config = screen_config
        debug.log(data)
        self.data = data
        self.render_surface = render_surface

        self.display_time = 3
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

        return self.data[self.current_item]

    @staticmethod
    def _get_last_part(text):
        parts = text.split()
        return parts[len(parts) - 1]
