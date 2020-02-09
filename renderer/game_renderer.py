import logging
import time

from PIL import Image

from data.data_source import DataSource
from renderer.renderer import Renderer
from renderer.scrolling_text_renderer import ScrollingTextRenderer


class GameRenderer(Renderer):
    def __init__(self, teams, config, render_surface):
        super().__init__(config, render_surface)
        self.scrolling_renderer = ScrollingTextRenderer(self.data, self.config, self.render_surface, scroll_speed=10, text_y_pos_init=26)
        self.current_item = -1
        self.teams = teams

    def _do_render(self, image, draw, frame_time):

        game_info = self.data.game

        self.__draw_team_logos(image, game_info.home_team_id, game_info.away_team_id)

        score = self.format_score(game_info)
        period = game_info.period

        self.__draw_status_text(draw, period, score, "")

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
        time.sleep(1)

    def is_finished(self):
        return self.current_item >= len(self.data[DataSource.KEY_GAME_STATS_UPDATE][1])

    def __draw_team_logo(self, image, team_type, team_id):
        if not str(team_id) in self.config.screen_config.team_logos_pos:
            logging.warning("No logo configuration for team id %d found.", team_id)
            return

        team_logo_pos = self.config.screen_config.team_logos_pos[str(team_id)][team_type]
        team_logo = Image.open('logos/{}.png'.format(self.teams[team_id].abbreviation))
        image.paste(team_logo.convert("RGB"), (team_logo_pos["x"], team_logo_pos["y"] - 6))
        team_logo.close()

    def __draw_team_logos(self, image, home_team_id, away_team_id):
        self.__draw_team_logo(image, 'home', home_team_id)
        self.__draw_team_logo(image, 'away', away_team_id)

    def __draw_status_text(self, draw, first_line, second_line, third_line):
        self._render_center_text(draw, first_line, 0)
        self._render_center_text(draw, second_line, self._move_to_next_line(), self.font)
        self._render_center_text(draw, third_line, self._move_to_next_line()-1, self.font)

    # FIXME copied from GameDayRenderer
    @staticmethod
    def format_score(data):
        return '{}-{}'.format(data.away_score, data.home_score)
