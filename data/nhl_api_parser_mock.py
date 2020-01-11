import requests
import datetime
import debug
from data.goal import Goal
from random import *
from utils import convert_time

NHL_API_URL = "http://statsapi.web.nhl.com/api/v1/"
NHL_API_URL_BASE = "http://statsapi.web.nhl.com"


# TEST_URL = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=2018-01-02&endDate=2018-01-02"

def get_teams():
    """
        Function to get a list of all the teams information
        The info for each team are store in multidimensional dictionary like so:
        {
            team ID{
                team name,
                location,
                abbreviation,
                conference name,
                division name
            }
        }
        This make it a lot simpler to call each info of a specific team as all info in the API are associated with a team ID
    """

    url = '{0}/teams'.format(NHL_API_URL)
    response = requests.get(url)
    results = response.json()
    teams = {}
    try:
        for team in results['teams']:
            info_dict = {'name': team['teamName'], 'location': team['locationName'],
                         'abbreviation': team['abbreviation'], 'conference': team['conference']['name'],
                         'division': team['division']['name']}
            teams[team['id']] = info_dict
        return teams
    except requests.exceptions.RequestException:
        print("Error encountered getting teams info, Can't reach the NHL API")


def fetch_live_stats(link):
    """ Function to get the live stats of the current game """
    url = '{0}{1}'.format(NHL_API_URL_BASE, link)
    response = requests.get(url)
    stuff = response.json()
    try:

        all_plays = stuff['liveData']['plays']['allPlays']
        scoring_plays_index = stuff['liveData']['plays']['scoringPlays']
        scoring_plays = []
        goals = []

        for scoring_play_index in scoring_plays_index:
            scoring_plays.append(all_plays[scoring_play_index])

        for scoring_play in scoring_plays:
            scorer = scoring_play['players'][0]['player']['fullName']
            assist1 = ''
            assist2 = ''
            if scoring_play['players'][1]['player'] == 'Assist':
                assist1 = scoring_play['players'][1]['player']['fullName']
                if scoring_play['players'][2]['player'] == 'Assist':
                    assist2 = scoring_play['players'][2]['player']['fullName']
            goals.append(Goal(scorer, assist1, assist2))

        current_period = int(stuff['liveData']['linescore']['currentPeriod'])
        home_sog = int(stuff['liveData']['linescore']['teams']['home']['shotsOnGoal'])
        away_sog = int(stuff['liveData']['linescore']['teams']['away']['shotsOnGoal'])
        home_powerplay = int(stuff['liveData']['linescore']['teams']['home']['powerPlay'])
        away_powerplay = int(stuff['liveData']['linescore']['teams']['away']['powerPlay'])
        try:
            time_remaining = stuff['liveData']['linescore']['currentPeriodTimeRemaining']
        except KeyError:
            time_remaining = "00:00"
        return current_period, home_sog, away_sog, home_powerplay, away_powerplay, time_remaining, goals
    except requests.exceptions.RequestException:
        print("Error encountered, Can't reach the NHL API")


def fetch_games():
    """
    Function to get a list of games

    request stats in json form from the schedule section of the NHL API URL
    create a list to store all the games
    loop through the games received and store the info in the created list:
        - for each games:
            - the ID of the game
            - the link to the complete stats of that game
            - the Home team
            - the Home team score
            - the Away team
            - the Away team score
            - game status

    finally return the list of games

    game_list = list of all the games and the number of games.
    url = the location where we can find the list of games.
    """
    game_list = []
    gameInfo = {"gameid": 1, "full_stats_link": '', "home_team_id": 5,
                        "home_score": randint(1, 100), "away_team_id": 8, "away_score": 0,
                        'game_status': 6, 'game_time': '10:00'}
    game_list.append(gameInfo)
    return game_list



def fetch_overview(team_id):
    """ Function to get the score of the game live depending on the chosen team.
    Inputs the team ID and returns the score found on web. """

    current_game_overview = {'period': '1', 'time': '10:00', 'home_team_id': 5, 'home_score': randint(1, 100),
                                 'away_team_id': 8, 'away_score': 0, 'game_status': 4,
                                 'game_time': '10:00'}

    return current_game_overview


def fetch_fav_team_schedule(team_id, current_date):
    """ Function to get the summary of a scheduled game. """
    current_game_schedule = {'home_team_id': team_id, 'away_team_id': 5, 'game_time': '10:00'}
    return current_game_schedule


def check_season():
    """ Function to check if in season. Returns True if in season, False in off season. """
    # Get current time
    now = datetime.datetime.now()
    if now.month in (7, 8):
        return False
    else:
        return True


def check_if_game(team_id, current_date):
    """ Function to check if there is a game now with chosen team. Returns True if game, False if NO game. """
    return 4
