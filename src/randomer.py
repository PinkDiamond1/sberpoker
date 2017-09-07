import sys
import json
import random

from pypokerengine.players import BasePokerPlayer

MULT = 1

class Randomer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    def declare_action(self, valid_actions, hole_card, round_state):
        rnd = random.randint(1,101)
        if rnd < 34:
            action = valid_actions[0]
            return action['action'], action['amount']
        elif rnd < 67:
            action = valid_actions[1]
            return action['action'], action['amount']
        else:
            action = valid_actions[2]
            amount = min(action['amount']['min'] * MULT, action['amount']['max'])
            return action['action'], amount

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
