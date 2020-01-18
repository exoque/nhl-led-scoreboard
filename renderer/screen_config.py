from utils import get_file
import json
import os
import sys
import debug


class ScreenConfig:
    def __init__(self, filename_base, frame_time):
        json = self.__get_config(filename_base)
        self.team_logos_pos = json["team_logos"]
        self.frame_time = frame_time
        self.width = 64
        self.height = 32

    def read_json(self, filename):
        # Find and return a json file

        j = {}
        path = get_file(filename)
        if os.path.isfile(path):
            j = json.load(open(path))
        return j

    def __get_config(self, base_filename):
        # Look and return config.json file

        filename = "renderer/{}.json".format(base_filename)
        reference_config = self.read_json(filename)

        return reference_config

