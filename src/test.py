from pypokerengine.api.game import setup_config, start_poker
from bot import *
from console import *
from fish import *
from honest import *
from manic import *
from randomer import *

STACK = 1500
GAMES = 100

players = [
    ['Bot     ', Bot(), 0],
    ['Randomer', Randomer(), 0]
]

for g in range(GAMES):
    config = setup_config(max_round=50, initial_stack=STACK, small_blind_amount=15)

    i = 0
    while i < len(players):
        config.register_player(name=players[i][0], algorithm=players[i][1])
        i += 1

    game_result = start_poker(config, verbose=0)
    print json.dumps(game_result['players'], indent=2, sort_keys=True)

    i = 0
    while i < len(game_result['players']):
        players[i][2] += game_result['players'][i]['stack'] - STACK
        i += 1

i = 0
while i < len(players):
    config.register_player(name=players[i][0], algorithm=players[i][1])
    print players[i][0], players[i][2] / GAMES
    i += 1
