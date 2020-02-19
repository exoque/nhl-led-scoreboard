import time

from PIL import Image, ImageFont, ImageDraw

from data.data_source import DataSource
from data.game import GameStateChange
from renderer.animation_renderer import AnimationRenderer
from renderer.boxscore_renderer import BoxscoreRenderer
from renderer.game_renderer import GameRenderer
from renderer.screen_config import ScreenConfig
from utils import parse_today

import logging

from enum import unique, Enum


@unique
class RenderState(Enum):
    Game = 1,
    Goal_Light = 2,
    Goal_Scorer = 3,
    Goal_Result = 4,
    Goal_Reset = 5,
    Period_End = 6,
    Game_End = 7


class ScreenController:
    def __init__(self, config, render_surface, data_source, data, renderers):
        self.config = config
        self.render_surface = render_surface
        self.data_source = data_source
        self.data = data
        self.renderers = renderers
        self.frame_time = time.time()
        self.screen_config = ScreenConfig("64x32_config", self.frame_time)
        self.width = self.screen_config.width
        self.height = self.screen_config.height
        self.image = None
        self.draw = None
        self.config.data_needed = {}
        self.display_time = 5
        self.start_time = None
        self.current_game = None
        self.priority_game = None
        self.render_state = RenderState.Game
        self.state_start_time = time.time()

    def run(self):
        updated_data = self.data_source.load_teams()
        self.config.data_needed[updated_data[0]] = updated_data[1]
        self.config.data_needed = {DataSource.KEY_GAMES: {}, DataSource.KEY_GAME_STATS_UPDATE: {}, DataSource.KEY_GAME_INFO: {},
                       DataSource.KEY_GAME_STATS: {}}

        while True:
            self.frame_time = time.time()
            self.init_image()

            logging.info("Started frame with time '%d'.", self.frame_time)

            if self.data_source.must_update(self.frame_time):
                self.update_data()

            self.render()
            time.sleep(self.config.sleep_time)

    def update_data(self):
        today = parse_today(self.config)
        current_date = self.config.data_needed[DataSource.KEY_GAMES]['date'] if DataSource.KEY_GAMES in self.config.data_needed and 'date' in self.config.data_needed[DataSource.KEY_GAMES] else None
        if today != current_date:
            self.data.reset()
            self.config.data_needed[DataSource.KEY_GAMES]['date'] = today

        api_data = self.data_source.update_data(self.config.data_needed)

        for game in api_data[DataSource.KEY_GAMES]:
            if 2 < game.game_status < 7 or game.key not in self.data.games:
                self.config.data_needed[DataSource.KEY_GAME_INFO]['key'] = game.key

                updated_data = self.data_source.load_game_info(self.config.data_needed[DataSource.KEY_GAME_INFO]['key'])
                api_data[updated_data[0]] = updated_data[1]

                state_change = self.data.update_game(game.key, game, {})
                if GameStateChange.HOME_TEAM_SCORED in state_change \
                        or GameStateChange.AWAY_TEAM_SCORED in state_change \
                        or GameStateChange.PERIOD_END in state_change \
                        or GameStateChange.GAME_END in state_change:

                    logging.info("GameStateChange %d for game %s", state_change, game.key)
#
#
 #                   self.config.data_needed[DataSource.KEY_GAME_STATS_UPDATE]['key'] = game.key
 #                   updated_data = self.data_source.load_game_stats_update(self.config.data_needed[DataSource.KEY_GAME_STATS_UPDATE]['key'],
 #                                                              self.config.data_needed[DataSource.KEY_GAME_STATS_UPDATE]['timestamp'] if 'timestamp' in self.config.data_needed[DataSource.KEY_GAME_STATS_UPDATE] else 0)
#
#                    self.api_data[updated_data[0]] = updated_data[1]

                    self.config.data_needed[DataSource.KEY_GAME_STATS]['key'] = game.key
                    updated_data = self.data_source.load_game_stats(self.config.data_needed[DataSource.KEY_GAME_STATS]['key'])

                    logging.info(updated_data)
                    if len(updated_data) > 0:
                        logging.info(updated_data[1])
                        if len(updated_data[1]) > 0:
                            logging.info(updated_data[1][0])
                        else:
                            continue
                    else:
                        continue

                    self.priority_game = self.data.games[game.key]
                    self.data.update_events(game.key, [updated_data[1][0]])
                    self.render_state = RenderState.Goal_Light

    def render(self):
        if self.priority_game is not None:
            self.start_time = time.time()
        elif self.start_time is None or self.display_time <= time.time() - self.start_time:
            self.current_game = self.data.get_next_item_to_display()
            self.start_time = time.time()

        logging.info("current game: %d, priority game: %d", self.current_game.game.key if self.current_game is not None else 0, self.priority_game.game.key if self.priority_game is not None else 0)

        if self.render_state == RenderState.Goal_Light\
                or self.render_state == RenderState.Goal_Scorer\
                or self.render_state == RenderState.Goal_Result\
                or self.render_state == RenderState.Goal_Reset:
            self.render_goal()
        elif self.render_state == RenderState.Period_End:
            self.render_period_end()
        elif self.render_state == RenderState.Game_End:
            self.render_game_end()
        else:
            self.render_game()

    def render_game(self):
        renderer = self.renderers[GameRenderer.KEY_GAME_RENDERER]
        renderer.update_data(self.current_game)
        renderer.render(self.image, self.frame_time)

    def render_goal(self):

        logging.info("Rendering goal with state %s", self.render_state)

        if self.render_state == RenderState.Goal_Light:
            renderer = self.renderers[AnimationRenderer.KEY_ANIMATION_RENDERER]
            renderer.update_data(self.priority_game)
            renderer.render(self.image, self.frame_time)

            if self.__should_move_to_next_state():
                self.render_state = RenderState.Goal_Scorer
        elif self.render_state == RenderState.Goal_Scorer:
            renderer = self.renderers[BoxscoreRenderer.KEY_BOXSCORE_RENDERER]
            renderer.update_data(self.priority_game)
            renderer.render(self.image, self.frame_time)

            if self.__should_move_to_next_state():
                self.render_state = RenderState.Goal_Result
        elif self.render_state == RenderState.Goal_Result:
            renderer = self.renderers[GameRenderer.KEY_GAME_RENDERER]
            renderer.update_data(self.priority_game)
            renderer.render(self.image, self.frame_time)

            if self.__should_move_to_next_state():
                self.render_state = RenderState.Goal_Reset
        elif self.render_state == RenderState.Goal_Reset:
            self.priority_game = None
            self.start_time = time.time()
            self.render_state = RenderState.Game

    def render_period_end(self):
        # Show boxscore for period
        pass

    def render_game_end(self):
        # Show boxscore for game
        pass

    def __should_move_to_next_state(self):
        if time.time() - self.state_start_time > 5:
            self.state_start_time = time.time()
            return True

        return False

    def init_image(self):
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)


