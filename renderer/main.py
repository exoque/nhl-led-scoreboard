from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics

from data.data_source_nhl import DataSourceNhl
from renderer.boxscore_renderer import BoxscoreRenderer
from renderer.game_day_renderer import GameDayRenderer
from renderer.scrolling_text_renderer import ScrollingTextRenderer
from utils import center_text
from calendar import month_abbr
from renderer.screen_config import screenConfig
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
        self.screen_config = screenConfig("64x32_config", self.frame_time)
        self.width = 64
        self.height = 32



        # Create a new data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Load the fonts
        self.font = ImageFont.truetype("fonts/score_large.otf", 16)
        self.font_mini = ImageFont.truetype("fonts/04B_24__.TTF", 8)

    def render(self):
        # loop through the different state.
        #while True:

        #self.__render_test_boxscore()
        #self.__render_test_game_day()
        self.__render_test_scrolling_text()

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
        box_score_renderer = BoxscoreRenderer(data, teams, self.screen_config, self.data.config, self.render_surface)

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
        data = nhl_data_source.load_day_schedule("2020-01-14")
        teams = nhl_data_source.load_teams()
        game_day_renderer = GameDayRenderer(data, teams, self.screen_config, self.data.config, self.render_surface)

        while True:
            self.frame_time = time.time()

            game_day_renderer.render(self.image, self.frame_time)
            # self.render_surface.render(self.image)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

            time.sleep(1)

    def __render_test_scrolling_text(self):
        scrolling_text_renderer = ScrollingTextRenderer("This is a really long text which doesn't fit on the screen so it has to be scrolled.", self.screen_config, self.data.config, self.render_surface)

        while True:
            self.frame_time = time.time()

            scrolling_text_renderer.render(self.image, self.frame_time)
            # self.render_surface.render(self.image)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

            time.sleep(1)

    def __render_game(self):

        if self.data.fav_team_game_today == 1:
            debug.info('Scheduled State')
            self.__draw_pregame()
            time.sleep(1800)
        elif self.data.fav_team_game_today == 2:
            debug.info('Pre-Game State')
            self.__draw_pregame()
            time.sleep(60)
        elif (self.data.fav_team_game_today == 3) or (self.data.fav_team_game_today == 4):
            debug.info('Live State')
            # Draw the current game
            self.__draw_game()
        elif (self.data.fav_team_game_today == 5) or (self.data.fav_team_game_today == 6) or (self.data.fav_team_game_today == 7):
            debug.info('Final State')
            self.__draw_post_game()
            #sleep an hour
            time.sleep(3600)
        debug.info('ping render_game')

    def __render_off_day(self):

        debug.info('ping_day_off')
        self.__draw_off_day()
        time.sleep(21600) #sleep 6 hours

    def __draw_pregame(self):

        if self.data.get_schedule() != 0:

            overview = self.data.schedule

            # Save when the game start
            game_time = overview['game_time']

            self.__draw_status_text('TODAY', game_time, 'VS')
            self.__draw_team_logos(self.image, overview['home_team_id'], overview['away_team_id'])
            self.render_surface.render(self.image)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
        else:
            #(Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            #self.canvas = self.matrix.SwapOnVSync(self.canvas)
            #self.image.save('/home/ch/Pictures/nhl-scoreboard.png', "PNG")
            self.render_surface.render(self.image)
            time.sleep(60)  # sleep for 1 min
            # Refresh canvas
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

    def __draw_game(self):
        self.data.refresh_overview()
        overview = self.data.overview
        home_score = overview['home_score']
        away_score = overview['away_score']

        while True:

            # Refresh the data
            if self.data.needs_refresh:
                debug.info('Refresh game overview')
                self.data.refresh_overview()
                self.data.needs_refresh = False

            if self.data.overview != 0:
                overview = self.data.overview

                # Use This code if you want the goal animation to run only for your fav team's goal
                # if self.data.fav_team_id == overview['home_team_id']:
                #     if overview['home_score'] > home_score:
                #         self._draw_goal()
                # else:
                #     if overview['away_score'] > away_score:
                #         self._draw_goal()

                # Use this code if you want the goal animation to run for both team's goal.
                # Run the goal animation if there is a goal.
                if overview['home_score'] > home_score or overview['away_score'] > away_score:
                    self.__draw_goal()

                # Prepare the data
                score = '{}-{}'.format(overview['away_score'], overview['home_score'])
                period = overview['period']
                time_period = overview['time']

                self.__draw_status_text(period, time_period, score)
                self.__draw_team_logos(self.image, overview['home_team_id'], overview['away_team_id'])
                self.render_surface.render(self.image)

                # Refresh the Data image.
                self.image = Image.new('RGB', (self.width, self.height))
                self.draw = ImageDraw.Draw(self.image)

                # Check if the game is over
                if overview['game_status'] == 6 or overview['game_status'] == 7:
                    debug.info('GAME OVER')
                    break

                # Save the scores.
                away_score = overview['away_score']
                home_score = overview['home_score']

                self.data.needs_refresh = True
                time.sleep(10)
            else:
                # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
                self.draw.line((0, 0) + (self.width, 0), fill=128)
                #self.canvas = self.matrix.SwapOnVSync(self.canvas)
                #self.image.save('/home/ch/Pictures/nhl-scoreboard.png', "PNG")
                self.render_surface.render(self.image)
                #time.sleep(60)  # sleep for 1 min

    def __draw_post_game(self):
        self.data.refresh_overview()
        if self.data.overview != 0:
            overview = self.data.overview

            # Prepare the data
            game_date = '{} {}'.format(month_abbr[self.data.month], self.data.day)
            score = '{}-{}'.format(overview['away_score'], overview['home_score'])
            period = overview['period']

            # Only show the period if the game ended in Overtime "OT" or Shootouts "SO"
            if period == "OT" or period == "SO":
                time_period = period
            else:
                time_period = overview['time']

            self.__draw_status_text(game_date, time_period, score)
            self.__draw_team_logos(self.image, overview['home_team_id'], overview['away_team_id'])
            self.render_surface.render(self.image)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

        else:
            # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.render_surface.render(self.image)
            time.sleep(60)  # sleep for 1 min

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

    def __draw_team_logos(self, image, home_team_id, away_team_id):
        self.__draw_team_logo(image, 'home', home_team_id)
        self.__draw_team_logo(image, 'away', away_team_id)

    def __draw_status_text(self, first_line, second_line, third_line):
        # Set the position of the information on screen.
        first_position = center_text(self.font_mini.getsize(first_line)[0], 32)
        second_position = center_text(self.font_mini.getsize(second_line)[0], 32)
        third_position = center_text(self.font.getsize(third_line)[0], 32)

        # Draw the text on the Data image.
        self.draw.multiline_text((first_position, 1), first_line, fill=(255, 255, 255), font=self.font_mini, align="center")
        self.draw.multiline_text((second_position, 8), second_line, fill=(255, 255, 255), font=self.font_mini, align="center")
        self.draw.multiline_text((third_position, 15), third_line, fill=(255, 255, 255), font=self.font, align="center")
