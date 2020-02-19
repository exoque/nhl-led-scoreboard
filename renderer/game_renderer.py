import logging
import time
from calendar import month_abbr
from datetime import datetime

from PIL import Image

from data.data_source import DataSource
from renderer.renderer import Renderer
from renderer.scrolling_text_renderer import ScrollingTextRenderer
from utils import convert_time


class GameRenderer(Renderer):
    KEY_GAME_RENDERER = 'game_renderer'

    def __init__(self, teams, config, render_surface):
        super().__init__(config, render_surface)
        self.scrolling_renderer = ScrollingTextRenderer(self.data, self.config, self.render_surface, scroll_speed=10, text_y_pos_init=26)
        self.current_item = -1
        self.teams = teams

    def _do_render(self, image, draw, frame_time):

        game_info = self.data.game

        #self.__draw_team_logos(image, game_info.home_team_id, game_info.away_team_id)

        #score = self.format_score(game_info)
        #period = game_info.period

        #self.__draw_status_text(draw, period, score, "")

        self._render_graphical_version(game_info, image, draw)

        self._refresh_screen(image)
        return

        event_list = self.data[DataSource.KEY_GAME_STATS_UPDATE][1]

        if len(event_list) == 0 or self.is_finished():
            self._refresh_screen(image)
            return

        if self.scrolling_renderer.is_finished():
            self.current_item = self.current_item + 1

            if self.current_item >= len(self.data[DataSource.KEY_GAME_STATS_UPDATE][1]):
                return

            event = event_list[self.current_item]
            self.scrolling_renderer.update_data(event.result.description)
        elif self.current_item == -1:
            self.current_item = 0
            event = event_list[self.current_item]
            self.scrolling_renderer.update_data(event.result.description)

        self.scrolling_renderer.render(image, frame_time)

    def is_finished(self):
        return self.current_item >= -1 #len(self.data[DataSource.KEY_GAME_STATS_UPDATE][1])

    def __draw_team_logo(self, image, team_type, team_id):
        if not str(team_id) in self.config.screen_config.team_logos_pos:
            logging.warning("No logo configuration for team id %d found.", team_id)
            return

        team_logo_pos = self.config.screen_config.team_logos_pos[str(team_id)][team_type]
        team_logo = Image.open('logos/{}.png'.format(self.teams[team_id].abbreviation))
        y_pos = team_logo_pos["y"] if self.is_finished() else team_logo_pos["y"] - 6
        image.paste(team_logo.convert("RGB"), (team_logo_pos["x"], y_pos))

    def __draw_team_logos(self, image, home_team_id, away_team_id):
        self.__draw_team_logo(image, 'home', home_team_id)
        self.__draw_team_logo(image, 'away', away_team_id)

    def __draw_status_text(self, draw, first_line, second_line, third_line):
        self._render_center_text(draw, first_line, 0)
        self._render_center_text(draw, second_line, self._move_to_next_line())
        self._render_center_text(draw, third_line, self._move_to_next_line()-1, self.font)

    # FIXME copied from GameDayRenderer
    @staticmethod
    def format_score(data):
        return '{}-{}'.format(data.away_score, data.home_score)

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
    def __format_game_date(game_date):
        return '{} {}'.format(month_abbr[game_date.month], game_date.day)

    def __get_date_string(self, game_date):
        return "TODAY" if game_date == datetime.today().date() else self.__format_game_date(game_date)

    @staticmethod
    def __is_pregame(data):
        return data.game_status == 1 or data.game_status == 2

    @staticmethod
    def __is_live_game(data):
        return data.game_status == 3 or data.game_status == 4

    @staticmethod
    def __is_off_day(data):
        return data is None