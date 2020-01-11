from data.data_source import DataSource
from data.goal import Goal
from data.team import Team
from data.game import Game, GameTeam, GameTeamLeagueRecord, GameTeamShootoutInfo, GameTeamStats
from utils import convert_time
import debug


class DataSourceNhl(DataSource):
    NHL_API_URL = "http://statsapi.web.nhl.com/api/v1/"
    NHL_API_URL_BASE = "http://statsapi.web.nhl.com"

    def load_teams(self):
        url = '{0}/teams'.format(self.NHL_API_URL)
        result = self._execute_request(url)
        teams = {}

        for entry in result['teams']:
            team = Team(entry['id'],
                        entry['teamName'],
                        entry['teamName'],
                        entry['abbreviation'],
                        entry['conference']['name'],
                        entry['division']['name'])
            teams[entry['id']] = team
        return teams

    def load_game_info(self, key):
        url = '{0}schedule?expand=schedule.linescore&teamId={1}'.format(self.NHL_API_URL, key)
        result = self._execute_request(url)

        if len(result['dates']) == 0:
            return None

        dates = result['dates']
        game = self._build_game(dates[0]['games'][0])
        return game

    def load_day_schedule(self, date):
        url = '{0}schedule?date={1}'.format(self.NHL_API_URL, date)
        result = self._execute_request(url)

        if len(result['dates']) == 0:
            return None

        dates = result['dates']
        games = self._build_games(dates[0]['games'])
        return games

    def load_game_stats(self, key):
        url = '{0}{1}'.format(self.NHL_API_URL_BASE, '/api/v1/game/2019020691/feed/live')
        result = self._execute_request(url)
        live_data = result['liveData']
        plays = live_data['plays']
        all_plays = plays['allPlays']
        scoring_plays = plays['scoringPlays']
        current_play = plays['currentPlay']
        debug.log(current_play)

        goals = []

        for scoring_play in scoring_plays:
            goals.append(self._build_goal(all_plays[scoring_play]))

        debug.log(goals)

    def load_game_for_team(self, key, date):
        pass

    def load_team_schedule(self, key):
        pass

    @staticmethod
    def _build_goal(event):
        players = event['players']
        time = event['about']['periodTime']
        team = event['team']['id']
        kind = event['result']['secondaryType']
        strength = event['result']['strength']['code']
        scorer = players[0]['player']['fullName']
        assist1 = players[1]['player']['fullName']
        assist2 = players[2]['player']['fullName']

        return Goal(time, team, kind, strength, scorer, assist1, assist2)

    def _build_games(self, games):
        game_list = []

        for game in games:
            game_list.append(self._build_game(game))

        return game_list

    def _build_game(self, game):
        if 'linescore' in game:
            linescore = game['linescore']
        else:
            linescore = None

        home_team = game['teams']['home']
        away_team = game['teams']['away']
        h_team = self.__build_game_team(game, 'home')
        a_team = self.__build_game_team(game, 'away')

        return Game(game['gamePk'],
                    self.__get_current_period(linescore),
                    self.__get_current_period_time_remaining(linescore),
                    home_team['team']['id'],
                    home_team['score'],
                    away_team['team']['id'],
                    away_team['score'],
                    game['status']['statusCode'],
                    convert_time(game['gameDate']).strftime("%I:%M"),
                    h_team,
                    a_team)

    @staticmethod
    def __get_current_period_time_remaining(linescore):
        if linescore is None:
            return None

        return linescore['currentPeriodTimeRemaining'] if 'currentPeriodTimeRemaining' in linescore else None

    @staticmethod
    def __get_current_period(linescore):
        if linescore is None:
            return None

        return linescore['currentPeriodOrdinal'] if 'currentPeriodOrdinal' in linescore else DataSourceNhl.__get_period_text(linescore['currentPeriod']) if 'currentPeriod' in linescore else None

    @staticmethod
    def __get_period_text(period):
        if period == '1':
            return period + "st"
        elif period == '2':
            return period + "nd"
        elif period == '3':
            return period + "rd"
        else:
            return period

    @staticmethod
    def __build_game_team(game, team_type):
        if 'linescore' in game:
            linescore = game['linescore']
        else:
            linescore = None

        if linescore is not None and 'teams' in linescore:
            linescore_team = linescore['teams'][team_type]
        else:
            linescore_team = None

        team = game['teams'][team_type]
        league_record = team['leagueRecord']

        if linescore is not None:
            stats = GameTeamStats(linescore_team['goals'],
                                  linescore_team['shotsOnGoal'],
                                  linescore_team['goaliePulled'],
                                  linescore_team['numSkaters'],
                                  linescore_team['powerPlay'])

            shootout = GameTeamShootoutInfo(linescore['shootoutInfo'][team_type]['scores'],
                                            linescore['shootoutInfo'][team_type]['attempts'])
        else:
            stats = None
            shootout = None

        record = GameTeamLeagueRecord(league_record['wins'],
                                      league_record['losses'],
                                      league_record['ot'])

        team = GameTeam(team['team']['id'],
                        team['team']['name'],
                        stats,
                        record,
                        shootout)
        return team
