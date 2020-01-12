import time

from PIL import ImageDraw, Image

import debug
from renderer.rotate_screen_render import RotateScreenRenderer


class BoxscoreRenderer(RotateScreenRenderer):
    def __init__(self, data, screen_config, render_surface):
        super().__init__(data, screen_config, render_surface)

    def _do_render(self, image, draw, frame_time):
        #self._render_left_text(draw, "Left text", 1)
        #self._render_center_text(draw, "Center text", 10)
        #self._render_right_text(draw, "Right text", 19)

        debug.log(self.current_item)

        goal_data = self._get_item_to_display()
        self._render_left_text(draw, "{} {} {}".format(goal_data.time, goal_data.team, goal_data.strength), 0)
        self._render_right_text(draw, "{}-{}".format(goal_data.result.away, goal_data.result.home), 0)
        self._render_left_text(draw, self._get_last_part(goal_data.scorer), 8)
        self._render_left_text(draw, self._get_last_part(goal_data.assist1), 16)
        self._render_left_text(draw, self._get_last_part(goal_data.assist2), 24)

        self.render_surface.render(image)

        # Refresh the Data image.
        image = Image.new('RGB', (self.screen_width, self.screen_height))
