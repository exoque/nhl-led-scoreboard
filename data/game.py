from enum import IntFlag, unique


@unique
class GameStateChange(IntFlag):
    NONE = 1,
    GAME_START = 2,
    GAME_END = 4,
    PERIOD_START = 8,
    PERIOD_END = 16,
    HOME_TEAM_SCORED = 32,
    AWAY_TEAM_SCORED = 64,
    SCORE_CHANGED = 96


class Game:

    def __init__(self, key, period, time, home_team_id, home_score, away_team_id, away_score, game_status, game_date, game_time, home_team, away_team):
        self.key = key
        self.period = period
        self.time = time
        self.home_team_id = home_team_id
        self.home_score = home_score
        self.away_team_id = away_team_id
        self.away_score = away_score
        self.game_status = game_status
        self.game_date = game_date
        self.game_time = game_time

        self.home_team = home_team
        self.away_team = away_team

        self.game_state = GameStateChange.NONE

    def update(self, game):
        game_state = GameStateChange.NONE

        if self.game_status != game.game_status:
            self.game_status = game.game_status

            # 3 => game started

            # Get the correct values
            if self.game_status == 1:
                game_state = game_state | GameStateChange.GAME_START
            elif self.game_status == 2 or (self.time != 'END' and game.time == 'END'):
                game_state = game_state | GameStateChange.PERIOD_END
            elif self.game_status == 3:
                game_state = game_state | GameStateChange.PERIOD_START
            elif self.game_status == 4:
                game_state = game_state | GameStateChange.GAME_END

        if self.game_status == 3 and (self.time != 'END' and game.time == 'END'):
            game_state = game_state | GameStateChange.PERIOD_END

        # score changed
        if self.home_score < game.home_score:
            self.home_score = game.home_score
            game_state = game_state | GameStateChange.HOME_TEAM_SCORED

        if self.away_score < game.away_score:
            self.away_score = game.away_score
            game_state = game_state | GameStateChange.AWAY_TEAM_SCORED

        self.game_state = game_state

        self.period = game.period
        self.time = game.time
        self.home_score = game.home_score
        self.away_score = game.away_score
        self.game_status = game.game_status
        self.game_time = game.game_time

        return game_state

    def __repr__(self):
        return "Game[{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]".format(self.key, self.period, self.time, self.home_team_id, self.home_score, self.away_team_id, self.away_score, self.game_status, self.game_date, self.game_time, self.home_team, self.away_team)


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
