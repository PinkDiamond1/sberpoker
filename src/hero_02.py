import sys
import json
import random

from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.card import Card

MULT = 1

MIN = 0
MAX = 999999999

class Hero02(BasePokerPlayer):

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
        pair = c1.rank == c2.rank
        suited = c1.suit == c2.suit

        own_stack, avg_stack = self.count_stacks(round_state)
        blinds = min(own_stack, avg_stack) / self.bb

        if blinds < 14:
            return self.push_fold(valid_actions, round_state, blinds, c1, c2)

        is_kk_plus = pair and c1.rank > 12

        is_low_k = min(c1.rank, c2.rank) == 13
        is_hi_a = max(c1.rank, c2.rank) == 14
        is_ak = is_low_k and is_hi_a
        is_aks = is_ak and suited

        if is_kk_plus or is_aks:
            # print 'MONSTER', c1, c2
            return self.raise_or_call(valid_actions, MAX)
        return self.check_or_fold(valid_actions)

    def push_fold(self, valid_actions, round_state, blinds, c1, c2):
        low = min(c1.rank, c2.rank)
        hi = max(c1.rank, c2.rank)
        pair = c1.rank == c2.rank
        suited = c1.suit == c2.suit

        medium = low >= 10 and hi >= 10
        big = low + hi >= 24
        monster = low + hi >= 26
        big_pair = pair and low >= 10

        pot = self.count_pot(round_state)
        pot_blinds = pot / self.bb
        small_pot = pot_blinds < 3

        push = False

        if small_pot:
            if   blinds < 5:  push = True
            elif blinds < 10: push = pair or medium
            else:             push = pair or big
        else:
            if   blinds < 3:  push = True
            elif blinds < 5:  push = pair or medium
            elif blinds < 10: push = big_pair or big
            else:             push = monster

        if push:
            # print 'PUSH', blinds, c1, c2
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
        other_sum = 0
        other_num = 0

        i = 0
        while i < len(round_state['seats']):
            seat = round_state['seats'][i]
            if seat['uuid'] == self.uuid:
                own_stack = seat['stack']
            else:
                other_sum += seat['stack']
                other_num += 1
            i += 1

        if other_num > 0:
            avg_stack = other_sum / other_num
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
