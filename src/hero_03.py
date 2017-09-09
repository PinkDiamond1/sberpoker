import sys
import json
import random

from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.card import Card

MULT = 1

MIN = 0
MAX = 999999999

POS_SB = 105
POS_BB = 104
POS_BU = 103
POS_CO = 102
POS_MD = 101
POS_EA = 100

class Hero03(BasePokerPlayer):

    random_percent = 0
    small_stack_bb = 10

    bb = 0
    game_info = []
    start_seats = []

    def __init__(self, random_percent=0, small_stack_bb=10):
        self.random_percent = random_percent
        self.small_stack_bb = small_stack_bb

    def declare_action(self, valid_actions, hole_card, round_state, bot_state=None):
        rnd = random.randint(1,101)
        c1 = Card.from_str(hole_card[0])
        c2 = Card.from_str(hole_card[1])

        own_stack, avg_stack = self.count_stacks(round_state)
        blinds = min(own_stack, avg_stack) / self.bb

        if round_state['street'] == 'preflop':
            pair = c1.rank == c2.rank
            suited = c1.suit == c2.suit

            if blinds < 14:
                return self.push_fold(valid_actions, round_state, blinds, c1, c2)

            is_kk_plus = pair and c1.rank > 12

            is_low_k = min(c1.rank, c2.rank) == 13
            is_hi_a = max(c1.rank, c2.rank) == 14
            is_ak = is_low_k and is_hi_a
            is_aks = is_ak and suited

            if is_kk_plus or is_aks:
                # print('MONSTER', c1, c2)
                return self.raise_or_call(valid_actions, MAX)
        return self.check_or_fold(valid_actions)

    def push_fold(self, valid_actions, round_state, blinds, c1, c2):
        low = min(c1.rank, c2.rank)
        hi = max(c1.rank, c2.rank)
        pair = c1.rank == c2.rank
        suited = c1.suit == c2.suit

        seat = self.get_seat(round_state)
        position = self.get_position_type(round_state, seat)

        raiser_seat = self.get_raiser_seat(round_state)
        if raiser_seat < 0:
            raiser_position = -1
        else:
            raiser_position = self.get_position_type(round_state, raiser_seat)

        pot = self.count_pot(round_state)
        pot_blinds = pot / self.bb

        medium = low >= 10 and hi >= 10
        big = low + hi >= 24
        monster = low + hi >= 26
        big_pair = pair and low >= 10

        push = False
        if raiser_position < 0:
            # AA-99
            if pair and low >= 9:
                push = True
            # 88-66
            elif pair and low >= 6:
                push = blinds <= 10 or position >= POS_MD
            # 55-22
            elif pair:
                push = blinds <= 8 or blinds <= 10 and position >= POS_MD or position >= POS_CO
            # AK, AQ
            elif hi == 14 and low >= 12:
                push = True
            # AJs, ATs
            elif suited and hi == 14 and low >= 10:
                push = blinds <= 8 or position >= POS_MD
            # A9s-A2s
            elif suited and hi == 14:
                push = blinds <= 5 or blinds <= 7 and position >= POS_MD or blinds <= 10 and position >= POS_CO or position >= POS_SB
            # AJo, ATo
            elif hi == 14 and low >= 10:
                push = blinds <= 7 or blinds <= 8 and position >= POS_MD or blinds <= 11 and position >= POS_CO or position >= POS_BU
            # A9o-A2o
            elif hi == 14:
                push = blinds <= 5 or blinds <= 7 and position >= POS_CO or blinds <= 9 and position >= POS_BU or position >= POS_SB
            # KQs-K9s, QJs-Q9s, JTs, J9s, T9s
            elif suited and low >= 9:
                push = blinds <= 8 or blinds <= 10 and position >= POS_MD or position >= POS_CO
            # K8s-K4s, Q8s, J8s, T8s, 98s
            elif suited and (low >= 8 or hi == 13 and low >= 4):
                push = blinds <= 5 or blinds <= 6 and position >= POS_MD or blinds <= 8 and position >= POS_CO or blinds <= 9 and position >= POS_BU or position >= POS_SB
            # KQo-KTo, QJo-QTo, JTo
            elif low >= 10:
                push = blinds <= 5 or blinds <= 8 and position >= POS_MD or blinds <= 10 and position >= POS_CO or position >= POS_SB
            # Q7s, Q6s
            elif suited and hi == 12 and low >= 6:
                push = blinds <= 4 or blinds <= 5 and position >= POS_MD or blinds <= 6 and position >= POS_CO or blinds <= 7 and position >= POS_BU or position >= POS_SB
            # 97s, 96s, 86s, 76s, 75s, 65s
            elif suited and ((low == 6 or low == 5) and (hi == 9 or hi == 8 or hi == 7) or low == 5 and (hi == 6 or hi == 7)):
                push = blinds <= 4 or blinds <= 5 and position >= POS_MD or blinds <= 6 and position >= POS_CO or blinds <= 7 and position >= POS_BU or position >= POS_SB
        else:
            if   blinds < 3:  push = True
            elif blinds < 5:  push = pair or medium
            elif blinds < 10: push = big_pair or big
            else:             push = monster

        if push:
            # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', blinds, first_in, position, c1, c2)
            # print('PUSH', blinds, c1, c2)
            return self.raise_or_call(valid_actions, MAX)
        return self.check_or_fold(valid_actions)

    def get_position_type(self, round_state, seat):
        pos_end = self.get_position_end(round_state, seat)

        if seat == round_state['small_blind_pos']:
            return POS_SB
        if seat == round_state['big_blind_pos']:
            return POS_BB
        if seat == round_state['dealer_btn']:
            if pos_end != 0:
                print(seat, pos_end)
                print(json.dumps(round_state, indent=2, sort_keys=True))
                raise RuntimeError('pos_end != 0')
            return POS_BU
        if pos_end == 0:
            print(seat, pos_end)
            print(json.dumps(round_state, indent=2, sort_keys=True))
            raise RuntimeError('pos_end == 0')
        if pos_end == 1:
            return POS_CO
        if pos_end < 5:
            return POS_MD
        return POS_EA

    def get_position_end(self, round_state, seat):
        count = 0
        i = 0
        while i < len(self.start_seats):
            s = self.start_seats[i]
            if s['stack'] > 0:
                count += 1
            i += 1
        return count - 1 - self.get_position(round_state, seat)

    def get_position(self, round_state, seat):
        position = 0
        found = False
        i = round_state['small_blind_pos']
        while i < len(self.start_seats):
            if i == seat:
                found = True
                break
            s = self.start_seats[i]
            if s['stack'] > 0:
                position += 1
            i += 1
        if not found:
            i = 0
            while i < round_state['small_blind_pos']:
                if i == seat:
                    found = True
                    break
                s = self.start_seats[i]
                if s['stack'] > 0:
                    position += 1
                i += 1
        if not found:
            raise RuntimeError('Position not found')
        return position

    def get_seat(self, round_state):
        i = 0
        while i < len(self.start_seats):
            seat = self.start_seats[i]
            if seat['uuid'] == self.uuid:
                return i
            i += 1
        raise RuntimeError('Seat not found')

    def get_raiser_seat(self, round_state):
        uuid = self.get_raiser_uuid(round_state)
        if uuid == '':
            return -1
        i = 0
        while i < len(self.start_seats):
            if self.start_seats[i]['uuid'] == uuid:
                return i
            i += 1
        raise RuntimeError('Raiser seat not found')

    def get_raiser_uuid(self, round_state):
        i = 0
        while i < len(round_state['action_histories']['preflop']):
            action = round_state['action_histories']['preflop'][i]
            if action['action'] == 'RAISE':
                return action['uuid']
            i += 1
        return ''

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
        while i < len(self.start_seats):
            seat = self.start_seats[i]
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
        self.start_seats = seats

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
