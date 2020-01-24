import time

from data.data_source import DataSource
from renderer.renderer import Renderer
from renderer.scrolling_text_renderer import ScrollingTextRenderer


class GameRenderer(Renderer):
    def __init__(self, config, render_surface):
        super().__init__(config, render_surface)
        self.scrolling_renderer = ScrollingTextRenderer(self.data, self.config, self.render_surface, 10)
        self.current_item = -1

    def _do_render(self, image, draw, frame_time):
        event_list = self.data[DataSource.KEY_GAME_STATS_UPDATE][1]

        if len(event_list) == 0 or self.is_finished():
            return

        if self.scrolling_renderer.is_finished():
            self.current_item = self.current_item + 1

            if self.current_item >= len(self.data):
                return

            event = event_list[self.current_item]
            self.scrolling_renderer.update_data(event.result.description)
        elif self.current_item == -1:
            self.current_item = 0
            event = event_list[self.current_item]
            self.scrolling_renderer.update_data(event.result.description)

        self.scrolling_renderer.render(image, frame_time)
        time.sleep(1)

    def is_finished(self):
        return self.current_item >= len(self.data)
