from datetime import datetime, timedelta
import logging
#import data.nhl_api_parser_mock as nhlparser
import data.nhl_api_parser as nhlparser


class DataOld:
    def __init__(self, config):

        self.idex = 0
        # Save the parsed config
        self.config = config

        # Flag to determine when to refresh data
        self.needs_refresh = True

        # Flag to determine when it's a new day
        self.new_day = False

        # get favorite team's id
        self.fav_team_id = self.config.fav_team_ida[0]

        # Parse today's date and see if we should use today or yesterday
        self.get_current_date()

        # Fetch the teams info
        self.get_teams_info = nhlparser.get_teams()

        # Fetch the games for today
        self.refresh_games = nhlparser.fetch_games()

        # Look if favorite team play today
        self.refresh_fav_team_status()



    def __parse_today(self):
        today = datetime.today()
        end_of_day = datetime.strptime(self.config.end_of_day, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
        if end_of_day > datetime.now():
            today -= timedelta(days=1)

        return today.year, today.month, today.day

    def set_date(self):
        return datetime(self.year, self.month, self.day)

    def get_current_date(self):
        self.year, self.month, self.day = self.__parse_today()
        logging.info("{}-{}-{}".format(self.year, self.month, self.day))

    def refresh_overview(self):
        self.overview = nhlparser.fetch_overview(self.fav_team_id)
        self.needs_refresh = False

    def get_schedule(self):
        self.schedule = nhlparser.fetch_fav_team_schedule(self.fav_team_id, self.get_date())

    def refresh_fav_team_status(self):
        self.fav_team_game_today = nhlparser.check_if_game(self.fav_team_id, self.get_date())

    def get_date(self):
        return "{}-{}-{}".format(self.year, self.month, self.day)

    def check_fav_team_next_game(self):
        pass