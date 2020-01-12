from calendar import month_abbr

from PIL import Image

from renderer.rotate_screen_render import RotateScreenRenderer
from utils import center_text, parse_today

import debug


class GameDayRenderer(RotateScreenRenderer):
    def __init__(self, data, teams, screen_config, config, render_surface):
        super().__init__(data, screen_config, config, render_surface)
        self.teams = teams

    def _do_render(self, image, draw, frame_time):
        debug.log(self.current_item)

        data = self._get_item_to_display()

        if False:
            self._render_text_version(data, draw)
        else:
            self._render_graphical_version(data, image, draw)

        self.render_surface.render(image)

        # Refresh the Data image.
        image = Image.new('RGB', (self.screen_width, self.screen_height))

    def _render_text_version(self, data, draw):
        if data.game_status < 7:
            time_text = "{} {}".format(data.time, data.period) if data.time is not None else data.game_time
        else:
            time_text = data.time
        self._render_center_text(draw, time_text, 0)
        self._render_left_text(draw, self.teams[data.away_team_id].name, 8)
        self._render_left_text(draw, self.teams[data.home_team_id].name, 16)
        if data.time is not None:
            self._render_right_text(draw, data.away_score, 8)
            self._render_right_text(draw, data.home_score, 16)

    def _render_graphical_version(self, data, image, draw):
        _, month, day = parse_today(self.config)

        game_date = '{} {}'.format(month_abbr[month], day)
        score = '{}-{}'.format(data.away_score, data.home_score)
        period = data.period

        # Only show the period if the game ended in Overtime "OT" or Shootouts "SO"
        if period == "OT" or period == "SO":
            time_period = period
        else:
            time_period = data.time

        self.__draw_status_text(draw, game_date, time_period, score)
        self.__draw_team_logos(image, data.home_team_id, data.away_team_id)

    def __draw_team_logo(self, image, team_type, team_id):
        team_logo_pos = self.screen_config.team_logos_pos[str(team_id)][team_type]
        team_logo = Image.open('logos/{}.png'.format(self.teams[team_id].abbreviation))
        image.paste(team_logo.convert("RGB"), (team_logo_pos["x"], team_logo_pos["y"]))
        team_logo.close()

    def __draw_team_logos(self, image, home_team_id, away_team_id):
        self.__draw_team_logo(image, 'home', home_team_id)
        self.__draw_team_logo(image, 'away', away_team_id)

    def __draw_status_text(self, draw, first_line, second_line, third_line):
        self._render_center_text(draw, first_line, 1)
        self._render_center_text(draw, second_line, 8)
        self._render_center_text(draw, third_line, 15, self.font)

