import sys
import json
import random

from pypokerengine.players import BasePokerPlayer

class Randomer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    def declare_action(self, valid_actions, hole_card, round_state, bot_state=None):
        rnd = random.randint(1,101)
        if rnd < 50:
            return 'fold', 0
        elif rnd < 80 or valid_actions[2]['amount']['max'] <= 0:
            return 'call', valid_actions[1]['amount']
        else:
            action = valid_actions[2]
            mul = random.randint(1,10)
            amount = min(action['amount']['min'] * mul, action['amount']['max'])
            return 'raise', amount

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
