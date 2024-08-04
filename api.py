import requests
from functions import var_file, var_players, account_info_puuid, get_puuid, var_servers

servers = var_servers()

players = var_players()

for player in players.values():
    server = servers[player['sub_region']]['server']
    # print(server)
    region = servers[player['sub_region']]['region']
    # print(region)
    name = player['game_name']
    tag = player['tag_line']
    puuid = get_puuid(region=region, game_name=name, tag_line=tag)
    print(account_info_puuid(server=server, puuid=puuid))

"""


api_url = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/'

puuid = info.get('puuid')

api_url += puuid
api_url += '?api_key=' + api_key

#print(api_url)

resp = requests.get(api_url)
print(resp)
"""