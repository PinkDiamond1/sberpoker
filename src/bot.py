import sys
import json
import random

from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.card import Card

MULT = 1

MIN = 0
MAX = 999999999

class Bot(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        rnd = random.randint(1,101)

        c1 = Card.from_str(hole_card[0])
        c2 = Card.from_str(hole_card[1])
        big = c1.rank + c2.rank >= 23
        monster = c1.rank + c2.rank >= 26
        pair = c1.rank == c2.rank
        bigPair = c1.rank >= 10

        if big or pair:
            pot = self.countPot(round_state)
            smallPot = pot < 500

            if smallPot or monster or bigPair:
                # print c1, c2
                return self.raiseOrCall(valid_actions, MAX)
        return 'fold', 0

    def raiseOrCall(self, valid_actions, val):
        if valid_actions[2]['amount']['max'] < 0:
            return 'call', valid_actions[1]['amount']
        elif valid_actions[2]['amount']['max'] < val:
            return 'raise', valid_actions[2]['amount']['max']
        elif val < valid_actions[2]['amount']['min']:
            return 'raise', valid_actions[2]['amount']['min']
        else:
            return 'raise', val

    def countPot(self, round_state):
        total = round_state['pot']['main']['amount']
        i = 0
        while i < len(round_state['pot']['side']):
            total += round_state['pot']['side'][i]['amount']
            i += 1
        return total

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
