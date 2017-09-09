from pypokerengine.api.game import setup_config, start_poker
from console import *
from hero_01 import *
from hero_02 import *
from hero_03 import *
from hero_04 import *
from fish import *
from honest import *
from manic import *
from randomer import *

STACK = 1500
GAMES = 100

players = [
    ['Hero04   ', Hero04(), 0, 0],
    # ['Hero03   ', Hero03(), 0, 0],
    # ['Hero02   ', Hero02(), 0, 0],
    # ['Hero01   ', Hero01(), 0, 0],
    # ['Hero04   ', Hero04(), 0, 0],
    # ['Hero03   ', Hero03(), 0, 0],
    # ['Hero02   ', Hero02(), 0, 0],
    # ['Hero01   ', Hero01(), 0, 0],

    ['Randomer1', Randomer(), 0, 0],
    ['Randomer2', Randomer(), 0, 0],
    ['Randomer3', Randomer(), 0, 0],
    ['Randomer4', Randomer(), 0, 0],
    ['Randomer5', Randomer(), 0, 0],
    ['Randomer6', Randomer(), 0, 0],
    ['Randomer7', Randomer(), 0, 0],
    ['Randomer8', Randomer(), 0, 0],
]

for g in range(GAMES):
    print(g)

    config = setup_config(max_round=50, initial_stack=STACK, small_blind_amount=15)

    i = 0
    while i < len(players):
        config.register_player(name=players[i][0], algorithm=players[i][1])
        i += 1

    game_result = start_poker(config, verbose=0)
    # print(json.dumps(game_result['players'], indent=2, sort_keys=True))

    i = 0
    while i < len(game_result['players']):
        chips = game_result['players'][i]['stack']
        players[i][2] += chips - STACK
        if chips >= STACK:
            players[i][3] += 1
        i += 1

i = 0
while i < len(players):
    config.register_player(name=players[i][0], algorithm=players[i][1])
    print(players[i][0], players[i][2] / GAMES, players[i][3] * 100 / GAMES)
    i += 1
