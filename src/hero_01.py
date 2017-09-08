import sys
import json
import random

from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.card import Card

MULT = 1

MIN = 0
MAX = 999999999

class Hero01(BasePokerPlayer):

    random_percent = 0
    small_stack_bb = 10

    bb = 0
    game_info = []

    def __init__(self, random_percent=0, small_stack_bb=10):
        self.random_percent = random_percent
        self.small_stack_bb = small_stack_bb

    def declare_action(self, valid_actions, hole_card, round_state, bot_state=None):
        rnd = random.randint(1,101)

        c1 = Card.from_str(hole_card[0])
        c2 = Card.from_str(hole_card[1])
        big = c1.rank + c2.rank >= 24
        monster = c1.rank + c2.rank >= 26
        pair = c1.rank == c2.rank
        big_pair = pair and c1.rank >= 12

        if big or pair or rnd < self.random_percent:
            pot = self.count_pot(round_state)
            small_pot = pot < self.bb * self.small_stack_bb

            if small_pot or monster or big_pair:
                return self.raise_or_call(valid_actions, MAX)
        return self.check_or_fold(valid_actions)

    def raise_or_call(self, valid_actions, val):
        if valid_actions[2]['amount']['max'] < 0:
            return 'call', valid_actions[1]['amount']
        elif valid_actions[2]['amount']['max'] < val:
            return 'raise', valid_actions[2]['amount']['max']
        elif val < valid_actions[2]['amount']['min']:
            return 'raise', valid_actions[2]['amount']['min']
        return 'raise', val

    def check_or_fold(self, valid_actions):
        if valid_actions[1]['amount'] > 0:
            return 'fold', 0
        return 'call', 0

    def count_stacks(self, round_state):
        own_stack = 0
        other_stacks = 0
        other_sum = 0

        i = 0
        while i < len(round_state['seats']):
            seat = round_state['seats'][i]
            if seat['uuid'] == self.uuid:
                own_stack = seat['stack']
            else:
                other_stacks += seat['stack']
                other_sum += 1
            i += 1

        if other_stacks > 0:
            avg_stack = other_sum / other_stacks
        else:
            avg_stack = 0

        return own_stack, avg_stack

    def count_pot(self, round_state):
        total = round_state['pot']['main']['amount']
        i = 0
        while i < len(round_state['pot']['side']):
            total += round_state['pot']['side'][i]['amount']
            i += 1
        return total

    def receive_game_start_message(self, game_info):
        self.game_info = game_info
        self.bb = self.game_info['rule']['small_blind_amount'] * 2

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
