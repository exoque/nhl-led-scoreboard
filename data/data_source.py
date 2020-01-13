from abc import ABC, abstractmethod
import requests
import debug


class DataSource(ABC):
    def __init__(self, config):
        self.config = config
        self.url = config.url

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

    @staticmethod
    def _execute_request(url):
        try:
            debug.log(url)
            response = requests.get(url)
            data = response.json()
            debug.log(data)
            return data
        except requests.exceptions.RequestException:
            print("Error encountered getting teams info, Can't reach the NHL API")