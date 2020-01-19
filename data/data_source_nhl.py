import re
import time
from collections import Iterable

from data.data_source import DataSource
from data.event import EventGoals, EventPlayer, Event, EventResult, EventAbout
from data.goal import Goal
from data.team import Team
from data.game import Game, GameTeam, GameTeamLeagueRecord, GameTeamShootoutInfo, GameTeamStats
from utils import convert_time
import debug


class DataSourceNhl(DataSource):

    def load_teams(self):
        url = '{0}teams'.format(self.url)
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
        url = '{0}schedule?expand=schedule.linescore&teamId={1}'.format(self.url, key)
        result = self._execute_request(url)

        if len(result['dates']) == 0:
            return None

        dates = result['dates']
        game = self._build_game(dates[0]['games'][0])
        self._update_time()
        return game

    def load_day_schedule(self, date):
        url = '{0}schedule?expand=schedule.linescore&date={1}'.format(self.url, date)
        result = self._execute_request(url)

        if len(result['dates']) == 0:
            return None

        dates = result['dates']
        games = self._build_games(dates[0]['games'])
        self._update_time()
        return games

    def load_game_stats(self, key):
        url = '{0}game/{1}/feed/live'.format(self.url, key)
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
        self._update_time()
        return goals

    def load_game_stats_update(self, key, time_stamp):
        url = '{0}game/{1}/feed/live/diffPatch?site=en_nhl&startTimecode={2}'.format(self.url, key, time_stamp)
        result = self._execute_request(url)
        event_list = []

        if 'gamePk' in result:
            meta_data = result['metaData']
            debug.log(meta_data)
            time_stamp = meta_data['timeStamp']
            time.sleep(1)
            return self.load_game_stats_update(key, time_stamp)
        elif len(result) == 0:
            return time_stamp, event_list

        #for diff in result:
        time_stamp = self.parse_diff(result[0]['diff'], event_list)
        self._update_time()
        return time_stamp, event_list

    def parse_diff(self, diff, event_list):
        time_stamp = [res['value'] for res in diff if res['path'] == '/metaData/timeStamp'][0]
        debug.log(time_stamp)
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

            event_list.append(e)
        for e in event_list: debug.log(e)
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
        debug.log(event)
        players = event['players']
        time = event['about']['periodTime']
        team = event['team']['id']
        kind = event['result']['secondaryType']
        strength = event['result']['strength']['code']
        scorer = players[0]['player']['fullName']
        assist1 = players[1]['player']['fullName']
        assist2 = players[2]['player']['fullName']

        return Goal(time, team, kind, strength, scorer, assist1, assist2, DataSourceNhl._build_result(event['about']['goals']))

    @staticmethod
    def _build_result(res):
        return EventGoals(res['home'], res['away'])

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
                    int(home_team['team']['id']),
                    int(home_team['score']),
                    int(away_team['team']['id']),
                    int(away_team['score']),
                    int(game['status']['statusCode']),
                    game['gameDate'],
                    convert_time(game['gameDate']).strftime("%I:%M"),
                    h_team,
                    a_team)

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
                                      league_record['ot'] if 'ot' in league_record else 0)

        team = GameTeam(int(team['team']['id']),
                        team['team']['name'],
                        stats,
                        record,
                        shootout)
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
                           None)

    def __init_player_if_new(self, e, index):
        if e.players is None:
            e.players = []

        if 0 <= index > len(e.players) - 1:
            e.players.append(EventPlayer(None, None, None, None, None))


