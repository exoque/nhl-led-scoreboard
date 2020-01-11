

class Team:
    def __init__(self, key, name, location, abbreviation, conference, division):
        self.key = key
        self.name = name
        self.location = location
        self.abbreviation = abbreviation
        self.conference = conference
        self.division = division

    def __repr__(self):
        return "Team[{}, {}, {}, {}, {}, {}]".format(self.key, self.name, self.location, self.abbreviation, self.conference, self.division)