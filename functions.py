import os
import requests

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
    game_name = game_name.replace(' ', '%20')
    tag_line = tag_line.replace('#', '')
    url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?api_key={api_key}'
    resp = requests.get(url)
    return resp.json()['puuid']