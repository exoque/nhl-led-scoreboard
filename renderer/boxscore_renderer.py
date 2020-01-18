import time

from PIL import ImageDraw, Image

import debug
from renderer.rotate_screen_render import RotateScreenRenderer


class BoxscoreRenderer(RotateScreenRenderer):
    def __init__(self, data, teams, config, render_surface):
        super().__init__(data, config, render_surface)
        self.teams = teams

    def _do_render(self, image, draw, frame_time):
        goal_data = self._get_item_to_display()

        if not self._item_has_changed():
            return

        self._render_left_text(draw, "{} {} {}".format(goal_data.time, self.teams[goal_data.team].abbreviation, goal_data.strength), self.text_y_pos)
        self._render_right_text(draw, "{}-{}".format(goal_data.result.away, goal_data.result.home), self.text_y_pos)
        self._render_left_text(draw, self._get_last_part(goal_data.scorer), self._move_to_next_line())
        self._render_left_text(draw, self._get_last_part(goal_data.assist1), self._move_to_next_line())
        self._render_left_text(draw, self._get_last_part(goal_data.assist2), self._move_to_next_line())

        self._refresh_screen(image)

