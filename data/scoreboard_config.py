from utils import get_file
import json
import os


class ScoreboardConfig:
    def __init__(self, filename_base, args):
        json = self.__get_config(filename_base)
        # Misc config options
        self.end_of_day = json["end_of_day"]
        self.debug = json["debug"]
        self.image_output_file = json["image_output_file"]
        self.debug_output = json["debug_output"]
        self.update_rate = json["update_rate"]

        if not self.debug:
            self.url = json["url"]
            self.stats_url = json["stats_url"]
            self.sleep_time = 0.05
        else:
            self.url = json["debug_url"]
            self.stats_url = json["debug_stats_url"]
            self.sleep_time = 1

        # config options from arguments. If the argument was passed, use its value, else use the one from config file.
        if args.fav_team:
            self.fav_team_ids = self.set_fav_teams(args.fav_team)
        else:
            self.fav_team_ids = self.set_fav_teams(json['fav_team_ids'])

    def read_json(self, filename):
        # Find and return a json file

        j = {}
        path = get_file(filename)
        if os.path.isfile(path):
            j = json.load(open(path))
        return j

    def __get_config(self, base_filename):
        # Look and return config.json file

        filename = "{}.json".format(base_filename)
        reference_config = self.read_json(filename)

        return reference_config

    def set_fav_teams(self, values):
        return [int(v) for v in values.split(",")]
