class Game:
    def __init__(self, key, period, time, home_team_id, home_score, away_team_id, away_score, game_status, game_time, home_team, away_team):
        self.key = key
        self.period = period
        self.time = time
        self.home_team_id = home_team_id
        self.home_score = home_score
        self.away_team_id = away_team_id
        self.away_score = away_score
        self.game_status = game_status
        self.game_time = game_time

        self.home_team = home_team
        self.away_team = away_team

    def __repr__(self):
        return "Game[{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]".format(self.key, self.period, self.time, self.home_team_id, self.home_score, self.away_team_id, self.away_score, self.game_status, self.game_time, self.home_team, self.away_team)


class GameTeam:
    def __init__(self, key, name, stats, league_record, shootout_info):
        self.key = key
        self.name = name
        self.stats = stats
        self.league_record = league_record
        self.shootout_info = shootout_info

    def __repr__(self):
        return "{}, {}, {}, {}, {}".format(self.key, self.name, self.stats, self.league_record, self.shootout_info)


class GameTeamStats:
    def __init__(self, goals, shots_on_goal, goalie_pulled, num_skaters, power_play):
        self.goals = goals
        self.shots_on_goal = shots_on_goal
        self.goalie_pulled = goalie_pulled
        self.num_skaters = num_skaters
        self.power_play = power_play

    def __repr__(self):
        return "{}, {}, {}, {}, {}".format(self.goals, self.shots_on_goal, self.goalie_pulled, self.num_skaters, self.power_play)


class GameTeamLeagueRecord:
    def __init__(self, wins, losses, ot):
        self.wins = wins
        self.losses = losses
        self.ot = ot

    def __repr__(self):
        return "{}, {}, {}".format(self.wins, self.losses, self.ot)


class GameTeamShootoutInfo:
    def __init__(self, scores, attempts):
        self.scores = scores
        self.attempts = attempts

    def __repr__(self):
        return "{}, {}".format(self.scores, self.attempts)
