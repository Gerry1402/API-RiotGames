import os
import requests
import datetime
import re

def var_file(file):
    d={}
    with open(file, 'r') as enviroment:
        for line in enviroment:
            if line != '\n' and '=' in line:
                key, value = line.strip().split('=')
                d[key.strip()] = value.strip()
    return d

info = var_file('.env')

api_key = info.get('api_key')

def var_servers():
    
    d={}
    
    with open('regions.txt', 'r') as file:
        for line in file:
            
            if line == '\n':
                continue
            
            line = line.strip()

            if '=' not in line:
                continent = line.lower()

            else:
                country, server = line.strip().split('=')
                d[country.strip()] = {'server': server.strip(), 'region': continent}

    return d

def var_players():
    
    players = {}
    
    for file in os.listdir('players'):
        player = var_file('players/'+file)
        players[player['game_name']] = player
    
    return players

def account_info_puuid(server: str, puuid: str, api_key = api_key):
    
    url = f'https://{server}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}'
    
    resp = requests.get(url)
    
    return resp.json()

def get_puuid(region: str, game_name: str, tag_line: str, api_key = api_key):
    """_summary_

    Args:
        region (str): _description_
        game_name (str): _description_
        tag_line (str): _description_
        api_key (_type_, optional): _description_. Defaults to api_key.

    Returns:
        _type_: _description_
    """
    game_name = game_name.replace(' ', '%20')
    tag_line = tag_line.replace('#', '')
    url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?api_key={api_key}'
    resp = requests.get(url)
    
    return resp.json()['puuid']

def last_matches (region: str, puuid: str, start_time: str = None, end_time: str = None, queue: str = None, type: str = None, start: int = 0, count: int = 20, api_key = api_key):
    """Function to extarct the IDs of the last matches played. Identificate the account with the puuid and extract maximum the ID of the last 100 matches.

    Args:
        region (str): The region to execute this request on.
        puuid (str): The puuid.
        start_time (str): Epoch timestamp in seconds. The matchlist started storing timestamps on June 16th, 2021. Any matches played before won't be included. The correct format is 'yyyy/MM/dd HH:mm'.
        end_time (str): Epoch timestamp in seconds. The correct format is 'yyyy/MM/dd HH:mm'.
        queue (str): Filter the list of match ids by a specific queue id. This filter is mutually inclusive of the type filter meaning any match ids returned must match both the queue and type filters.
        type (str): Filter the list of match ids by the type of match. This filter is mutually inclusive of the queue filter meaning any match ids returned must match both the queue and type filters.
        start (int, optional): Defaults to 0. Start Index.
        count (int, optional): Defaults to 20. Valid values: 0 to 100. Number of match ids to return.
        api_key (_type_, optional): _description_. Defaults to api_key.

    Raises:
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_

    Returns:
        _type_: A json object describing all the details of the match.
    """
    start_seconds_riot = 1623801600 # Epoch time of 16th June 2021 (Ponit at when Riot started saving the information)
    start_time_riot = datetime.datetime(2021, 6, 16)
    to_add = []
    
    if start_time:
        pattern = re.compile(r"^(?:(?:19|20)\d{2})/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01]) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$", re.IGNORECASE)
        
        if pattern.match(start_time):
            year, month, day = [int(number) for number in start_time.split(' ')[0].split('/')]
            hour, minute = [int(number) for number in start_time.split(' ')[1].split(':')]
            date_specific = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
            difference_seconds = int((date_specific - start_time_riot).total_seconds())
            start_time_seconds = start_seconds_riot + difference_seconds
            to_add.append(f'startTime={start_time_seconds}')
        else:
            raise ValueError("The format of 'start_time' is not supported. The correct format is 'yyyy/MM/dd HH:mm'.")
    
    if end_time:
        pattern = re.compile(r"^(?:(?:19|20)\d{2})/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01]) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$", re.IGNORECASE)
        
        if pattern.match(end_time):
            year, month, day = [int(number) for number in end_time.split(' ')[0].split('/')]
            hour, minute = [int(number) for number in end_time.split(' ')[1].split(':')]
            date_specific = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
            difference_seconds = int((date_specific - start_time_riot).total_seconds())
            start_time_seconds = start_seconds_riot + difference_seconds
            to_add.append(f'endTime={end_time}')
        else:
            raise ValueError("The format of 'end_time' is not supported. The correct format is 'yyyy/MM/dd HH:mm'.")
    
    if queue:
        to_add.append(f'queue={queue}')
    
    if type:
        if type not in ['ranked', 'normal', 'tutorial', 'tourney']:
            raise ValueError("'type' can only be 'ranked', 'normal', 'tutorial', o 'tourney'.")
        to_add.append(f'type={type}')
    
    if start:
        if start < 0:
            raise ValueError("'start' cannot be negative.")
        to_add.append(f'start={start}')
    
    if count:
        if count < 1:
            raise ValueError("'count' cannot be less than 1.")
        to_add.append(f'count={count}')
    
    to_add.append(f'api_key={api_key}')

    url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?' + '&'.join(to_add)
    resp = requests.get(url)
    return resp.json()