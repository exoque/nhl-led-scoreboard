import sys
from abc import ABC, abstractmethod
import time

import requests
import simplejson

import debug


class DataSource(ABC):
    def __init__(self, config):
        self.config = config
        self.url = config.url
        self.last_update_time = None

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
        return True if self.last_update_time is None else current_time - self.last_update_time > 10

    def _update_time(self):
        self.last_update_time = time.time()

    @staticmethod
    def _execute_request(url):
        try:
            debug.log(url)
            response = requests.get(url)
            data = response.json()
            debug.log(data)
            return data
        except requests.exceptions.RequestException:
            print("Error encountered getting teams info, Can't reach the NHL API.")
        except simplejson.errors.JSONDecodeError:
            print("Error parsing JSON.")
            sys.exit(1)
