from datetime import datetime

from PIL import Image, ImageFont, ImageDraw

from data.data import Data
from data.data_source import DataSource
from data.data_source_nhl import DataSourceNhl
from renderer.boxscore_renderer import BoxscoreRenderer
from renderer.game_day_renderer import GameDayRenderer
from renderer.game_renderer import GameRenderer
from renderer.renderer_config import RendererConfig
from renderer.screen_controller import ScreenController
from renderer.scrolling_text_renderer import ScrollingTextRenderer
from renderer.screen_config import ScreenConfig
from renderer.animation_renderer import AnimationRenderer
import time
import logging
from utils import convert_time, parse_today


class MainRenderer:
    def __init__(self, render_surface, config):
        self.render_surface = render_surface
        self.animation_renderer = AnimationRenderer(self.render_surface)
        self.config = config
        self.frame_time = time.time()
        self.screen_config = ScreenConfig("64x32_config", self.frame_time)
        self.width = self.screen_config.width
        self.height = self.screen_config.height
        self.data_source = DataSourceNhl(self.config)
        self.renderers = []
        self.screen_controller = ScreenController(config, render_surface, self.data_source, Data(), self.renderers)
        self.data = {}

        self.image = None
        self.draw = None

        # Load the fonts
        self.font = ImageFont.truetype("fonts/score_large.otf", 16)
        self.font_mini = ImageFont.truetype("fonts/04B_24__.TTF", 8)

    def render(self):
        updated_data = self.data_source.load_teams()
        self.data[updated_data[0]] = updated_data[1]
        self.renderers.append(self.__init_game_renderer())
        self.screen_controller.run()
        return

        updated_data = self.data_source.load_teams()
        self.data[updated_data[0]] = updated_data[1]

        #self.renderers.append(self.__init_game_day_renderer())
        #self.renderers.append(self.__init_game_renderer())
        self.renderers.append(self.__init_boxscore_renderer())

        while True:
            self.frame_time = time.time()
            self.init_image()

            if self.data_source.must_update(self.frame_time):
                #data = self.data_source.load_day_schedule(datetime.today().strftime('%Y-%m-%d'))
                #updated_data = self.data_source.load_day_schedule(parse_today(self.config))
                data_config = {DataSource.KEY_GAMES: {}, DataSource.KEY_GAME_STATS_UPDATE: {}, DataSource.KEY_GAME_INFO: {}, DataSource.KEY_GAME_STATS: {}}
                if not self.config.debug:
                    data_config[DataSource.KEY_GAMES]['date'] = parse_today(self.config)
                    data_config[DataSource.KEY_GAME_STATS_UPDATE]['key'] = 2019020743
                    data_config[DataSource.KEY_GAME_STATS_UPDATE]['timestamp'] = '20200118_183400'
                    data_config[DataSource.KEY_GAME_INFO]['key'] = 2019020743
                    data_config[DataSource.KEY_GAME_STATS]['key'] = 2019020703
                else:
                    data_config[DataSource.KEY_GAMES]['date'] = '2020-01-11'
                    data_config[DataSource.KEY_GAME_STATS]['key'] = 2019020691
                    data_config[DataSource.KEY_GAME_STATS_UPDATE]['key'] = 2019020755
                    data_config[DataSource.KEY_GAME_STATS_UPDATE]['timestamp'] = '20200119_180703'
                    data_config[DataSource.KEY_GAME_INFO]['key'] = 2019020693

                self.data = self.data_source.update_data(data_config)

                #updated_data = self.data_source.load_day_schedule("2020-01-11")
                #self.data[updated_data[0]] = updated_data[1]
                #updated_data = self.data_source.load_game_stats_update(2019020743, '20200118_183400')
                #self.data[updated_data[0]] = updated_data[1]

            for renderer in self.renderers:
                renderer.update_data(self.data)
                renderer.render(self.image, self.frame_time)

            time.sleep(0.05)

    def __init_boxscore_renderer(self):
        teams = self.data[DataSource.KEY_TEAMS]
        return BoxscoreRenderer(teams, self._get_renderer_config(), self.render_surface)

    def __init_game_day_renderer(self):
        teams = self.data[DataSource.KEY_TEAMS]
        return GameDayRenderer(teams, self._get_renderer_config(), self.render_surface)

    def __init_game_renderer(self):
        teams = self.data[DataSource.KEY_TEAMS]
        return GameRenderer(teams, self._get_renderer_config(), self.render_surface)

    def __init_scrolling_text_renderer(self):
        return ScrollingTextRenderer("This is a really long text which doesn't fit on the screen so it has to be scrolled.",
                              self._get_renderer_config(), self.render_surface)

    def _get_renderer_config(self):
        return RendererConfig(self.screen_config, self.config)

    def __render_test_boxscore(self):
        nhl_data_source = DataSourceNhl(self.config)
        # data = nhl_data_source.load_game_stats(2019020691)
        data = nhl_data_source.load_game_stats(2019020703)[DataSource.KEY_GAME_STATS]
        teams = self.data[DataSource.KEY_TEAMS]
        box_score_renderer = BoxscoreRenderer(teams, self._get_renderer_config(), self.render_surface)
        box_score_renderer.update_data(data)

        while True:
            self.frame_time = time.time()

            box_score_renderer.render(self.image, self.frame_time)
            # self.render_surface.render(self.image)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

            time.sleep(1)

    def __render_test_game_day(self):
        nhl_data_source = DataSourceNhl(self.config)
        data = nhl_data_source.load_day_schedule(datetime.today().strftime('%Y-%m-%d'))[DataSource.KEY_GAMES]
        teams = self.data[DataSource.KEY_TEAMS]
        game_day_renderer = GameDayRenderer(teams, self._get_renderer_config(), self.render_surface)
        game_day_renderer.update_data(data)

        while True:
            self.frame_time = time.time()

            game_day_renderer.render(self.image, self.frame_time)
            # self.render_surface.render(self.image)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

            time.sleep(1)

    def __render_test_scrolling_text(self):
        scrolling_text_renderer = ScrollingTextRenderer(
            "This is a really long text which doesn't fit on the screen so it has to be scrolled.",
            self._get_renderer_config(), self.render_surface)

        while True:
            self.frame_time = time.time()

            scrolling_text_renderer.render(self.image, self.frame_time)
            # self.render_surface.render(self.image)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

            time.sleep(1)

    def __draw_goal(self):
        logging.info('SCOOOOOOOORE, MAY DAY, MAY DAY, MAY DAY, MAY DAAAAAAAAY - Rick Jeanneret')
        self.animation_renderer.render("Assets/goal_light_animation.gif")

    def __draw_off_day(self):
        self.__draw_team_logo(self.image, 'away', self.config.fav_team_ids[0])
        self.draw.multiline_text((28, 8), 'NO GAME\nTODAY', fill=(255, 255, 255), font=self.font_mini, align="center")
        self.render_surface.render(self.image)

    def __draw_team_logo(self, image, team_type, team_id):
        team_logo_pos = self.screen_config.team_logos_pos[str(team_id)][team_type]
        team_logo = Image.open('logos/{}.png'.format(self.config.get_teams_info[team_id]['abbreviation']))
        image.paste(team_logo.convert("RGB"), (team_logo_pos["x"], team_logo_pos["y"]))
        team_logo.close()

    def init_image(self):
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
