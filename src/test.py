from pypokerengine.api.game import setup_config, start_poker
from console import *
from hero import *
from hero_01 import *
from fish import *
from honest import *
from manic import *
from randomer import *

STACK = 1500
GAMES = 100

players = [
    ['Hero     1', Hero(), 0],
    ['Hero01   2', Hero01(), 0],
    ['Hero     3', Hero(), 0],
    ['Hero01   4', Hero01(), 0],
    ['Hero     5', Hero(), 0],
    ['Hero01   6', Hero01(), 0],
    ['Hero     7', Hero(), 0],
    ['Hero01   8', Hero01(), 0],

    # ['Hero2    ', Hero(), 0],
    # ['Hero3    ', Hero(), 0],
    # ['Hero4    ', Hero(), 0],
    # ['Hero5    ', Hero(), 0],
    # ['Hero6    ', Hero(), 0],
    # ['Hero7    ', Hero(), 0],
    # ['Hero8    ', Hero(), 0],
    # ['Hero9    ', Hero(), 0],

    # ['Randomer1', Randomer(), 0],
    # ['Randomer2', Randomer(), 0],
    # ['Randomer3', Randomer(), 0],
    # ['Randomer4', Randomer(), 0],
    # ['Randomer5', Randomer(), 0],
    # ['Randomer6', Randomer(), 0],
    # ['Randomer7', Randomer(), 0],
    # ['Randomer8', Randomer(), 0],
]

for g in range(GAMES):
    print g

    config = setup_config(max_round=50, initial_stack=STACK, small_blind_amount=15)

    i = 0
    while i < len(players):
        config.register_player(name=players[i][0], algorithm=players[i][1])
        i += 1

    game_result = start_poker(config, verbose=0)
    # print json.dumps(game_result['players'], indent=2, sort_keys=True)

    i = 0
    while i < len(game_result['players']):
        players[i][2] += game_result['players'][i]['stack'] - STACK
        i += 1

i = 0
while i < len(players):
    config.register_player(name=players[i][0], algorithm=players[i][1])
    print players[i][0], players[i][2] / GAMES
    i += 1
