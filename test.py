from pypokerengine.api.game import setup_config, start_poker
from fish import *
from manic import *

config = setup_config(max_round=1, initial_stack=100, small_blind_amount=5)
config.register_player(name="p1", algorithm=Fish())
config.register_player(name="p2", algorithm=Manic())
game_result = start_poker(config, verbose=1)
print json.dumps(game_result["players"], indent=2, sort_keys=True)
