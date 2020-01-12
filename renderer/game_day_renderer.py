from PIL import Image

from renderer.rotate_screen_render import RotateScreenRenderer

import debug


class GameDayRenderer(RotateScreenRenderer):
    def __init__(self, data, teams, screen_config, render_surface):
        super().__init__(data, screen_config, render_surface)
        self.teams = teams

    def _do_render(self, image, draw, frame_time):
        debug.log(self.current_item)

        data = self._get_item_to_display()

        time_text = "{} {}".format(data.time, data.period) if data.time is not None else data.game_time

        self._render_center_text(draw, time_text, 0)
        if data.time is not None:
            self._render_right_text(draw, data.away_score, 8)
            self._render_right_text(draw, data.home_score, 16)
        self._render_left_text(draw, self.teams[data.away_team_id].name, 8)
        self._render_left_text(draw, self.teams[data.home_team_id].name, 16)

        self.render_surface.render(image)

        # Refresh the Data image.
        image = Image.new('RGB', (self.screen_width, self.screen_height))
