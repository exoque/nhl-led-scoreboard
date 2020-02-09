import time

from PIL import Image, ImageFont, ImageDraw

from data.data_source import DataSource
from data.game import GameStateChange
from renderer.screen_config import ScreenConfig
from utils import parse_today


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
        self.api_data = {}
        self.display_time = 5
        self.start_time = None
        self.current_game = None

    def run(self):
        updated_data = self.data_source.load_teams()
        self.config.data_needed[updated_data[0]] = updated_data[1]
        self.config.data_needed = {DataSource.KEY_GAMES: {}, DataSource.KEY_GAME_STATS_UPDATE: {}, DataSource.KEY_GAME_INFO: {},
                       DataSource.KEY_GAME_STATS: {}}
        self.config.data_needed[DataSource.KEY_GAMES]['date'] = parse_today(self.config)

        while True:
            self.frame_time = time.time()
            self.init_image()

            if self.data_source.must_update(self.frame_time):
                self.update_data()

            self.render()
            time.sleep(1)

    def update_data(self):
        self.api_data = self.data_source.update_data(self.config.data_needed)

        for game in self.api_data[DataSource.KEY_GAMES]:
            if 1 < game.game_status < 7 or game.key not in self.data.games:
                self.config.data_needed[DataSource.KEY_GAME_INFO]['key'] = game.key

                updated_data = self.data_source.load_game_info(self.config.data_needed[DataSource.KEY_GAME_INFO]['key'])
                self.api_data[updated_data[0]] = updated_data[1]

                state_change = self.data.update_game(game.key, game, {})
                if GameStateChange.HOME_TEAM_SCORED in state_change \
                        or GameStateChange.AWAY_TEAM_SCORED in state_change \
                        or GameStateChange.PERIOD_END in state_change \
                        or GameStateChange.GAME_END in state_change:

                    self.config.data_needed[DataSource.KEY_GAME_STATS_UPDATE]['key'] = game.key
                    updated_data = self.data_source.load_game_stats_update(self.config.data_needed[DataSource.KEY_GAME_STATS_UPDATE]['key'],
                                                               self.config.data_needed[DataSource.KEY_GAME_STATS_UPDATE]['timestamp'])

                    self.api_data[updated_data[0]] = updated_data[1]

    def render(self):
        if self.start_time is None or self.display_time <= time.time() - self.start_time:
            self.current_game = self.data.get_next_item_to_display()
            self.start_time = time.time()

        for renderer in self.renderers:
            renderer.update_data(self.current_game)
            renderer.render(self.image, self.frame_time)

    def init_image(self):
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)


