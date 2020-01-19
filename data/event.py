class Event:
    def __init__(self, key, players, result, about, team):
        self.key = key
        self.players = players
        self.result = result
        self.about = about
        self.team = team

    def __repr__(self):
        return "Event[{}, {}, {}, {}, {}]".format(self.key, self.result, self.players, self.about, self.team)


class EventPlayer:
    def __init__(self, key, full_name, link, player_type, season_total):
        self.key = key
        self.full_name = full_name
        self.link = link
        self.player_type = player_type
        self.season_total = season_total

    def __repr__(self):
        return "EventPlayer[{}, {}, {}, {}, {}]".format(self.key, self.full_name, self.link, self.player_type, self.season_total)


class EventGoals:
    def __init__(self, home, away):
        self.home = home
        self.away = away

    def __repr__(self):
        return "EventGoals[{}, {}]".format(self.home, self.away)


class EventResult:
    def __init__(self, event, event_code, event_type_id, description, secondary_type):
        self.event = event
        self.event_code = event_code
        self.event_type_id = event_type_id
        self.description = description
        self.secondary_type = secondary_type

    def __repr__(self):
        return "EventResult[{}, {}, {}, {}, {}]".format(self.event, self.event_code, self.event_type_id, self.description, self.secondary_type)


class EventAbout:
    def __init__(self, period, period_type, period_time, goals):
        self.period = period
        self.period_type = period_type
        self.period_time = period_time
        self.goals = goals

    def __repr__(self):
        return "EventAbout[{}, {}, {}, {}]".format(self.period, self.period_type, self.period_time, self.goals,)
