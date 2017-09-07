from pypokerengine.api.game import setup_config, start_poker
from bot import *
from console import *
from fish import *
from honest import *
from manic import *
from randomer import *

config = setup_config(max_round=50, initial_stack=1500, small_blind_amount=15)
# config.register_player(name="Hero", algorithm=Console())
# config.register_player(name="Bot", algorithm=Bot())
# config.register_player(name="Fish", algorithm=Fish())
# config.register_player(name="Honest", algorithm=Honest())
config.register_player(name="Manic", algorithm=Manic())
config.register_player(name="Randomer", algorithm=Randomer())
# config.register_player(name="Randomer2", algorithm=Randomer())
# config.register_player(name="Randomer3", algorithm=Randomer())
# config.register_player(name="Randomer4", algorithm=Randomer())
# config.register_player(name="Randomer5", algorithm=Randomer())
# config.register_player(name="Randomer6", algorithm=Randomer())
# config.register_player(name="Randomer7", algorithm=Randomer())
# config.register_player(name="Randomer8", algorithm=Randomer())
# config.register_player(name="Randomer9", algorithm=Randomer())
game_result = start_poker(config, verbose=1)
print json.dumps(game_result["players"], indent=2, sort_keys=True)
