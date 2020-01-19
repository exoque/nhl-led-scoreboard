from datetime import datetime

from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics

from data.data_source_nhl import DataSourceNhl
from renderer.boxscore_renderer import BoxscoreRenderer
from renderer.game_day_renderer import GameDayRenderer
from renderer.renderer_config import RendererConfig
from renderer.scrolling_text_renderer import ScrollingTextRenderer
from utils import center_text
from calendar import month_abbr
from renderer.screen_config import ScreenConfig
from renderer.animation_renderer import AnimationRenderer
from renderer.team_logo_renderer import TeamLogoRenderer
from data.data_source import DataSource
import time
import debug


class MainRenderer:
    def __init__(self, render_surface, data):
        self.render_surface = render_surface
        self.animation_renderer = AnimationRenderer(self.render_surface)
        self.data = data
        self.frame_time = time.time()
        self.screen_config = ScreenConfig("64x32_config", self.frame_time)
        self.width = self.screen_config.width
        self.height = self.screen_config.height



        # Create a new data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Load the fonts
        self.font = ImageFont.truetype("fonts/score_large.otf", 16)
        self.font_mini = ImageFont.truetype("fonts/04B_24__.TTF", 8)

    def _get_renderer_config(self):
        return RendererConfig(self.screen_config, self.data.config)

    def render(self):
        # loop through the different state.
        #while True:

        #self.__render_test_boxscore()
        self.__render_test_game_day()
        #self.__render_test_scrolling_text()

        '''
        while True:
            self.data.get_current_date()
            self.data.refresh_fav_team_status()
            # Fav team game day
            if self.data.fav_team_game_today:
                debug.info('Game day State')
                self.__render_game()
            # Fav team off day
            else:
                debug.info('Off day State')
                self.__render_off_day()
'''

    def __render_test_boxscore(self):
        nhl_data_source = DataSourceNhl(self.data.config)
        #data = nhl_data_source.load_game_stats(2019020691)
        data = nhl_data_source.load_game_stats(2019020703)
        teams = nhl_data_source.load_teams()
        box_score_renderer = BoxscoreRenderer(data, teams, self._get_renderer_config(), self.render_surface)

        while True:
            self.frame_time = time.time()

            box_score_renderer.render(self.image, self.frame_time)
            #self.render_surface.render(self.image)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

            time.sleep(1)

    def __render_test_game_day(self):
        nhl_data_source = DataSourceNhl(self.data.config)
        data = nhl_data_source.load_day_schedule(datetime.today().strftime('%Y-%m-%d'))
        teams = nhl_data_source.load_teams()
        game_day_renderer = GameDayRenderer(data, teams, self._get_renderer_config(), self.render_surface)

        while True:
            self.frame_time = time.time()

            game_day_renderer.render(self.image, self.frame_time)
            # self.render_surface.render(self.image)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

            time.sleep(1)

    def __render_test_scrolling_text(self):
        scrolling_text_renderer = ScrollingTextRenderer("This is a really long text which doesn't fit on the screen so it has to be scrolled.", self._get_renderer_config(), self.render_surface)

        while True:
            self.frame_time = time.time()

            scrolling_text_renderer.render(self.image, self.frame_time)
            # self.render_surface.render(self.image)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

            time.sleep(1)

    def __draw_goal(self):
        debug.info('SCOOOOOOOORE, MAY DAY, MAY DAY, MAY DAY, MAY DAAAAAAAAY - Rick Jeanneret')
        self.animation_renderer.render("Assets/goal_light_animation.gif")

    def __draw_off_day(self):
        self.__draw_team_logo(self.image, 'away', self.data.fav_team_id)
        self.draw.multiline_text((28, 8), 'NO GAME\nTODAY', fill=(255, 255, 255), font=self.font_mini, align="center")
        self.render_surface.render(self.image)

    def __draw_team_logo(self, image, team_type, team_id):
        team_logo_pos = self.screen_config.team_logos_pos[str(team_id)][team_type]
        team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[team_id]['abbreviation']))
        image.paste(team_logo.convert("RGB"), (team_logo_pos["x"], team_logo_pos["y"]))
        team_logo.close()
