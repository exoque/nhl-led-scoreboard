from datetime import datetime
from calendar import month_abbr

from PIL import Image

from data.data_source import DataSource
from renderer.rotate_screen_render import RotateScreenRenderer
from utils import parse_today, convert_time

import logging


class GameDayRenderer(RotateScreenRenderer):
    def __init__(self, teams, config, render_surface):
        super().__init__(config, render_surface)
        self.teams = teams

    def update_data(self, data):
        super().update_data(data[DataSource.KEY_GAMES])

    def _do_render(self, image, draw, frame_time):
        logging.debug(self.current_item)

        data = self._get_item_to_display()

        if not self._item_has_changed():
            return
        else:
            logging.debug('rendering')

        if False:
            self._render_text_version(data, draw)
        else:
            self._render_graphical_version(data, image, draw)

        self._draw_page_indicator(draw)

        self._refresh_screen(image)

    def _render_text_version(self, data, draw):
        if self.__is_off_day(data):
            self._render_center_text(draw, "No Game today", self._get_screen_height() / 2)
            return

        if data.game_status < 7:
            time_text = "{} {}".format(data.time, data.period) if data.time is not None else data.game_time
        else:
            time_text = data.time
        self._render_center_text(draw, time_text, self.text_y_pos)
        self._render_left_text(draw, self.teams[data.away_team_id].name, self._move_to_next_line())
        if data.time is not None:
            self._render_right_text(draw, data.away_score, self.text_y_pos)
        self._render_left_text(draw, self.teams[data.home_team_id].name, self._move_to_next_line())
        if data.time is not None:
            self._render_right_text(draw, data.home_score, self.text_y_pos)

    def _render_graphical_version(self, data, image, draw):

        if self.__is_off_day(data):
            self.__draw_team_logo(image, 'away', self.config.app_config.fav_team_id[0])
            self._render_text(draw, 'NO GAME\nTODAY', 28, 8)
            return

        game_date = convert_time(data.game_date)
        logging.debug(game_date)
        logging.debug(data.game_status)

        if self.__is_pregame(data):
            self.__draw_status_text(draw, self.__get_date_string(game_date), data.game_time, 'VS')
        elif self.__is_live_game(data):
            score = self.format_score(data)
            period = data.period
            time_period = data.time

            self.__draw_status_text(draw, period, time_period, score)
        else:
            game_date = self.__format_game_date(game_date)
            score = self.format_score(data)
            period = data.period

            # Only show the period if the game ended in Overtime "OT" or Shootouts "SO"
            if period == "OT" or period == "SO":
                time_period = period
            else:
                time_period = data.time

            self.__draw_status_text(draw, game_date, time_period, score)

        self.__draw_team_logos(image, data.home_team_id, data.away_team_id)

    @staticmethod
    def format_score(data):
        return '{}-{}'.format(data.away_score, data.home_score)

    @staticmethod
    def __format_game_date(game_date):
        return '{} {}'.format(month_abbr[game_date.month], game_date.day)

    def __get_date_string(self, game_date):
        return "TODAY" if game_date == datetime.today().date() else self.__format_game_date(game_date)

    def __draw_team_logo(self, image, team_type, team_id):
        if not str(team_id) in self.config.screen_config.team_logos_pos:
            logging.warning("No logo configuration for team id %d found.", team_id)
            return

        team_logo_pos = self.config.screen_config.team_logos_pos[str(team_id)][team_type]
        team_logo = Image.open('logos/{}.png'.format(self.teams[team_id].abbreviation))
        image.paste(team_logo.convert("RGB"), (team_logo_pos["x"], team_logo_pos["y"]))

    def __draw_team_logos(self, image, home_team_id, away_team_id):
        self.__draw_team_logo(image, 'home', home_team_id)
        self.__draw_team_logo(image, 'away', away_team_id)

    def __draw_status_text(self, draw, first_line, second_line, third_line):
        self._render_center_text(draw, first_line, 0)
        self._render_center_text(draw, second_line, self._move_to_next_line())
        self._render_center_text(draw, third_line, self._move_to_next_line()-1, self.font)

    @staticmethod
    def __is_pregame(data):
        return data.game_status == 1 or data.game_status == 2

    @staticmethod
    def __is_live_game(data):
        return data.game_status == 3 or data.game_status == 4

    @staticmethod
    def __is_off_day(data):
        return data is None

