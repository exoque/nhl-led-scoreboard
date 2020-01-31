import sys
from abc import ABC, abstractmethod
import time

import requests
import simplejson

import logging


class DataSource(ABC):
    KEY_TEAMS = 'teams'
    KEY_GAME_INFO = 'game_info'
    KEY_GAMES = 'games'
    KEY_GAME_STATS = 'game_stats'
    KEY_GAME_STATS_UPDATE = 'game_stats_update'

    def __init__(self, config):
        self.config = config
        self.url = config.url
        self.last_update_time = None
        self.data = {}

    def update_data(self, data_needed):

        if self.KEY_TEAMS in data_needed:
            updated_data = self.load_teams()
            self.data[updated_data[0]] = updated_data[1]
        if self.KEY_GAMES in data_needed:
            updated_data = self.load_day_schedule(data_needed[self.KEY_GAMES]['date'])
            self.data[updated_data[0]] = updated_data[1]
        if self.KEY_GAME_INFO in data_needed:
            updated_data = self.load_game_info(data_needed[self.KEY_GAME_INFO]['key'])
            self.data[updated_data[0]] = updated_data[1]
        if self.KEY_GAME_STATS in data_needed:
            updated_data = self.load_game_stats(data_needed[self.KEY_GAME_STATS]['key'])
            self.data[updated_data[0]] = updated_data[1]
        if self.KEY_GAME_STATS_UPDATE in data_needed:
            updated_data = self.load_game_stats_update(data_needed[self.KEY_GAME_STATS_UPDATE]['key'], data_needed[self.KEY_GAME_STATS_UPDATE]['timestamp'])
            self.data[updated_data[0]] = updated_data[1]

        return self.data

    @abstractmethod
    def load_teams(self):
        pass

    @abstractmethod
    def load_game_info(self, key):
        pass

    @abstractmethod
    def load_team_schedule(self, key, from_date, to_date):
        pass

    @abstractmethod
    def load_day_schedule(self, date):
        pass

    @abstractmethod
    def load_game_for_team(self, key, date):
        pass

    @abstractmethod
    def load_game_stats(self, key):
        pass

    @abstractmethod
    def load_game_stats_update(self, key, time_stamp):
        pass

    def must_update(self, current_time):
        return True if self.last_update_time is None else current_time - self.last_update_time > 60

    def _update_time(self):
        self.last_update_time = time.time()

    @staticmethod
    def _execute_request(url):
        try:
            logging.debug(url)
            response = requests.get(url)
            data = response.json()
            logging.debug(data)
            return data
        except requests.exceptions.RequestException:
            logging.error("Error encountered getting teams info, Can't reach the NHL API.")
        except simplejson.errors.JSONDecodeError:
            logging.error("Error parsing JSON.")
            sys.exit(1)
