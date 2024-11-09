import datetime
import re
import time
from collections.abc import Iterable
#from collections import Iterable

from data.data_source import DataSource
from data.event import EventGoals, EventPlayer, Event, EventResult, EventAbout
from data.goal import Goal
from data.team import Team
from data.game import Game, GameTeam, GameTeamLeagueRecord, GameTeamShootoutInfo, GameTeamStats
from utils import convert_time
import logging


class DataSourceNhl(DataSource):

    def __init__(self, config):
        super().__init__(config)

    def load_teams(self):
        url = '{0}franchise'.format(self.stats_url)
        result = self._execute_request(url)
        teams = {}

        if result is None or 'data' not in result:
            return None

        for entry in result['data']:
            if entry['lastSeasonId'] is None:
                team = Team(entry['mostRecentTeamId'],
                        entry['fullName'],
                        entry['teamPlaceName'],
                        entry['teamAbbrev'],
                        'unknown',
                        'unknown')
                teams[entry['mostRecentTeamId']] = team

        return self.KEY_TEAMS, teams

    def load_game_info(self, key):
        url = '{0}score/{1}'.format(self.url, datetime.date.today().strftime('%Y-%m-%d'))
        result = self._execute_request(url)

        if result is None or 'games' not in result or len(result['games']) == 0:
            return self.KEY_GAME_INFO, None

        game = None
        games = result['games']
        for g in games:
            if g['id'] == key:
                game = g
                break

        game = self._build_game(game)
        self._update_time()
        return self.KEY_GAME_INFO, game

    def load_day_schedule(self, date):
        converted_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        url = '{0}score/{1}'.format(self.url, converted_date.strftime('%Y-%m-%d'))
        result = self._execute_request(url)

        if result is None or 'games' not in result or len(result['games']) == 0:
            return self.KEY_GAMES, None

        games = self._build_games(result['games'])
        self._update_time()
        return self.KEY_GAMES, games

    def load_game_stats(self, key):
        url = '{0}game/{1}/feed/live'.format(self.url, key)
        result = self._execute_request(url)

        if result is None or 'liveData' not in result or len(result['liveData']) == 0:
            return self.KEY_GAME_STATS, None

        live_data = result['liveData']
        plays = live_data['plays']
        all_plays = plays['allPlays']
        scoring_plays = plays['scoringPlays']
        current_play = plays['currentPlay']
        logging.debug(current_play)

        goals = []

        for scoring_play in scoring_plays:
            goals.append(self._build_goal(all_plays[scoring_play]))

        logging.debug(goals)
        self._update_time()
        return self.KEY_GAME_STATS, goals

    def load_game_stats_update(self, key, time_stamp):
        url = '{0}game/{1}/feed/live/diffPatch?site=en_nhl&startTimecode={2}'.format(self.url, key, time_stamp)
        result = self._execute_request(url)
        event_list = {}

        if 'gamePk' in result:
            meta_data = result['metaData']
            logging.debug(meta_data)
            time_stamp = meta_data['timeStamp']
            time.sleep(1)
            return self.load_game_stats_update(key, time_stamp)
        elif len(result) == 0:
            return self.KEY_GAME_STATS_UPDATE, (time_stamp, event_list)

        #for diff in result:
        time_stamp = self.parse_diff(result[0]['diff'], event_list)
        self._update_time()
        return self.KEY_GAME_STATS_UPDATE, (time_stamp, event_list)

    def parse_diff(self, diff, event_list):
        time_stamp = [res['value'] for res in diff if res['path'] == '/metaData/timeStamp'][0]
        logging.debug(time_stamp)
        goal_list = [re.findall(r'\d+', res['path']) for res in diff
                     if ('value' in res
                         and res['path'].startswith('/liveData/plays/allPlays/')
                         and (res['value'] == 'SHOT'
                              or res['value'] == 'FACEOFF'
                              or res['value'] == 'BLOCKED_SHOT'
                              or res['value'] == 'STOP'
                              or res['value'] == 'MISSED_SHOT'
                              or res['value'] == 'GOAL'
                              or res['value'] == 'PENALTY'
                              or res['value'] == 'HIT'
                              or res['value'] == 'TAKEAWAY'
                              or res['value'] == 'GIVEAWAY'))]
        for res in [re.findall(r'\d+', res['path']) for res in diff
                    if 'value' in res
                       and res['path'].startswith('/liveData/plays/allPlays/')
                       and (self._has_value(res, 'SHOT')
                            or self._has_value(res, 'FACEOFF')
                            or self._has_value(res, 'BLOCKED_SHOT')
                            or self._has_value(res, 'STOP')
                            or self._has_value(res, 'MISSED_SHOT')
                            or self._has_value(res, 'GOAL')
                            or self._has_value(res, 'PENALTY')
                            or self._has_value(res, 'HIT')
                            or self._has_value(res, 'TAKEAWAY')
                            or self._has_value(res, 'GIVEAWAY'))]:
            goal_list.append(res)
        for entry_key in goal_list:
            goal_items = [res for res in diff
                          if len(entry_key) > 0
                          and entry_key[0] in res['path']]

            if len(goal_items) == 0:
                continue

            e = Event(entry_key[0], None, EventResult(None, None, None, None, None), EventAbout(None, None, None, None),
                      None)

            for item in goal_items:
                if item['op'] == 'remove':
                    continue

                if item['path'].endswith('/about/periodTime'):
                    e.about.period_time = item['value']
                elif item['path'].endswith('/about/eventId'):
                    e.about.event_id = item['value']
                elif item['path'].endswith('/about/periodTimeRemaining'):
                    e.about.period_time_remaining = item['value']
                elif item['path'].endswith('/about/dateTime'):
                    e.about.date_time = item['value']
                elif item['path'].endswith('/result/description'):
                    e.result.description = item['value']
                elif item['path'].endswith('/result/event'):
                    e.result.event = item['value']
                elif item['path'].endswith('/result/eventCode'):
                    e.result.event_code = item['value']
                elif item['path'].endswith('/result/eventTypeId'):
                    e.result.event_type_id = item['value']
                elif '/players/0' in item['path']:
                    self.__init_player_if_new(e, 0)
                    self.__parse_player(e, item, 0)
                elif '/players/1' in item['path']:
                    self.__init_player_if_new(e, 1)
                    self.__parse_player(e, item, 1)
                elif '/players/2' in item['path']:
                    self.__init_player_if_new(e, 2)
                    self.__parse_player(e, item, 2)
                elif '/players/3' in item['path']:
                    self.__init_player_if_new(e, 3)
                    self.__parse_player(e, item, 3)
                elif item['path'].startswith('/liveData/plays/allPlays/') and self._get_trailing_number(
                        item['path']) is not None:
                    e.result = self._parse_result(item['value']['result'])
                    e.about = self._parse_about(item['value']['about'])
                    p_l = []
                    if 'players' in item['value']:
                        for i in item['value']['players']:
                            p_l.append(DataSourceNhl._parse_player(i))
                        e.players = p_l
                elif item['path'].endswith('/players'):
                    p_l = []
                    for i in item['value']:
                        p_l.append(DataSourceNhl._parse_player(i))
                    e.players = p_l

            event_list[entry_key[0]] = e
        for e in event_list: logging.debug(e)
        return time_stamp

    def __parse_player(self, e, item, index):
        if item['path'].endswith('fullName'):
            e.players[index].full_name = item['value']
        elif item['path'].endswith('id'):
            e.players[index].key = item['value']
        elif item['path'].endswith('link'):
            e.players[index].link = item['value']
        elif item['path'].endswith('playerType'):
            e.players[index].player_type = item['value']

    def _has_value(self, item, event_type):
        return len(item) > 0 \
               and 'value' in item \
               and isinstance(item['value'], Iterable) \
               and 'result' in item['value'] \
               and 'eventTypeId' in item['value']['result'] \
               and item['value']['result']['eventTypeId'] == event_type

    def _get_trailing_number(self, s):
        m = re.search(r'\d+$', s)
        return int(m.group()) if m else None

    def load_game_for_team(self, key, date):
        pass

    def load_team_schedule(self, key, from_date, to_date):
        pass

    @staticmethod
    def _build_goal(event):
        logging.debug(event)
        players = event['players']
        time = event['about']['periodTime']
        team = event['team']['id']
        kind = event['result']['secondaryType'] if 'secondaryType' in event['result'] else None
        strength = event['result']['strength']['code']
        scorer = None
        assist1 = None
        assist2 = None
        goalie = None

        for player in players:
            parsed_player = DataSourceNhl._parse_player(player)

            if parsed_player.player_type == 'Scorer':
                scorer = parsed_player
            elif parsed_player.player_type == 'Goalie':
                goalie = parsed_player
            elif parsed_player.player_type == 'Assist':
                if assist1 is None:
                    assist1 = parsed_player
                else:
                    assist2 = parsed_player

        return Goal(time, team, kind, strength, scorer, assist1, assist2, goalie, DataSourceNhl._build_result(event['about']['goals']))

    @staticmethod
    def _build_result(res):
        return EventGoals(res['home'], res['away'])

    def _build_games(self, games):
        game_list = []

        for game in games:
            game_list.append(self._build_game(game))

        return game_list

    def _build_game(self, game):
        period = None
        game_time = None

        if 'linescore' in game:
            linescore = game['linescore']
            period = self.__get_current_period(linescore)
            game_time = self.__get_current_period_time_remaining(linescore)
        elif 'periodDescriptor' in game:
            period = self.__get_period_text(str(game['periodDescriptor']['number']))
            if 'clock' in game:
                game_time = game['clock']['timeRemaining']

        home_team = game['homeTeam']
        away_team = game['awayTeam']
        h_team = self.__build_game_team(game, 'homeTeam')
        a_team = self.__build_game_team(game, 'awayTeam')

        return Game(game['id'],
                    period,
                    game_time,
                    int(home_team['id']),
                    int(home_team['score'] if 'score' in home_team else 0),
                    int(away_team['id']),
                    int(away_team['score'] if 'score' in away_team else 0),
                    self.__convert_game_state(game['gameState']),
                    game['startTimeUTC'],
                    convert_time(game['startTimeUTC']).strftime("%I:%M"),
                    h_team,
                    a_team)

    #See bottom of game_renderer for codes
    @staticmethod
    def __convert_game_state(state):
        if state == 'OFF':
            return 7
        elif state == 'PRE':
            return 1
        elif state == 'FUT':
            return 1
        elif state == 'LIVE':
            return 3
        elif state == 'FINAL':
            return 5
        else:
            return 0

    @staticmethod
    def __get_current_period_time_remaining(linescore):
        if linescore is None:
            return None

        time = linescore['currentPeriodTimeRemaining'] if 'currentPeriodTimeRemaining' in linescore else None
        return time

    @staticmethod
    def __get_current_period(linescore):
        if linescore is None:
            return None
        period = linescore['currentPeriodOrdinal'] if 'currentPeriodOrdinal' in linescore else DataSourceNhl.__get_period_text(linescore['currentPeriod']) if 'currentPeriod' in linescore else None
        return period

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

        team = GameTeam(int(game[team_type]['id']),
                        game[team_type]['abbrev'],
                        'unknown',
                        'unknown',
                        'unknown')
        return team

    @staticmethod
    def _parse_result(result):
        return EventResult(result['event'],
                           result['eventCode'],
                           result['eventTypeId'],
                           result['description'],
                           result['secondaryType'] if 'secondaryType' in result else None)

    @staticmethod
    def _parse_about(about):
        return EventAbout(about['period'],
                          about['periodType'],
                          about['periodTime'],
                          DataSourceNhl._parse_goals(about['goals']))

    @staticmethod
    def _parse_goals(goals):
        return EventGoals(goals['home'],
                          goals['away'])

    @staticmethod
    def _parse_player(player):
        return EventPlayer(player['player']['id'],
                           player['player']['fullName'],
                           player['player']['link'],
                           player['playerType'],
                           player['seasonTotal'] if 'seasonTotal' in player else None)

    def __init_player_if_new(self, e, index):
        if e.players is None:
            e.players = []

        if 0 <= index > len(e.players) - 1:
            e.players.append(EventPlayer(None, None, None, None, None))


