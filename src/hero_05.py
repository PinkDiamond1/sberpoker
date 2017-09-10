import sys
import json
import random

from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.card import Card

MULT = 1

MIN = 0
MAX = 99999999

POS_SB = 105
POS_BB = 104
POS_BU = 103
POS_CO = 102
POS_MD = 101
POS_EA = 100

class Hero05(BasePokerPlayer):

    insanity = 1.0

    bb = 0
    game_info = []
    start_seats = []

    did_raise_preflop = False
    did_raise_turn = False
    short = False
    mid = False
    bluff = False

    def __init__(self, insanity=1.0):
        self.insanity = insanity

    def declare_action(self, valid_actions, hole_card, round_state, bot_state=None):
        rnd = random.randint(1,101)
        c1 = Card.from_str(hole_card[0])
        c2 = Card.from_str(hole_card[1])

        own_stack, avg_stack = self.count_starting_stacks(round_state)
        blinds = min(own_stack, avg_stack) / self.bb

        # push/fold
        if round_state['street'] == 'preflop' and blinds < self.ins(14):
            return self.push_fold(valid_actions, round_state, blinds, c1, c2)

        # short stack
        if self.short or round_state['street'] == 'preflop' and blinds < self.ins(31):
            return self.play_short_stack(valid_actions, round_state, c1, c2)

        # mid stack
        if self.mid or round_state['street'] == 'preflop':# and blinds < self.ins(51):
            return self.play_mid_stack(valid_actions, round_state, c1, c2)

        # monster
        if round_state['street'] == 'preflop':
            return self.play_monster(valid_actions, c1, c2)
        return self.check_or_fold(valid_actions)

    def ins(self, val):
        return val * self.insanity

    def play_mid_stack(self, valid_actions, round_state, c1, c2):
        self.mid = True

        low = min(c1.rank, c2.rank)
        hi = max(c1.rank, c2.rank)
        pair = c1.rank == c2.rank
        suited = c1.suit == c1.suit

        ccards = self.get_community_cards(round_state)
        own_stack, avg_stack = self.count_current_stacks(round_state)
        pot = self.count_pot(round_state)

        if round_state['street'] == 'preflop':
            pos, rpos, lrpos = self.get_positions_types(round_state)
            rcount = self.count_preflop_raisers(round_state)

            bet_size = 0
            if rcount == 0:
                if pos >= POS_CO:
                    # AA-77, AK-AT, A9s, KQ
                    bet = pair and low >= 7 or hi == 14 and (low >= 10 or suited and low == 9) or hi == 13 and low == 12
                elif pos >= POS_MD:
                    # AA-88, AK-AJ, ATs
                    bet = pair and low >= 8 or hi == 14 and (low >= 11 or suited and low == 10)
                else:
                    # AA-TT, AK, AQ, AJs
                    bet = pair and low >= 10 or hi == 14 and (low >= 12 or suited and low == 11)
                if bet:
                    bet_size = self.calc_bet_size_mid_stack_preflop(round_state)
            elif self.did_raise_preflop:
                if pos >= POS_CO:
                    # AA-JJ, AK
                    all_in = pair and low >= 11 or hi == 14 and low == 13
                elif pos >= POS_MD:
                    # AA-QQ, AK
                    all_in = pair and low >= 12 or hi == 14 and low == 13
                else:
                    # AA-QQ
                    all_in = pair and low >= 12
                if all_in:
                    bet_size = MAX
            elif rcount == 1:
                if rpos >= POS_CO:
                    # AA-88, AK-AT, A9s
                    bet = pair and low >= 8 or hi == 14 and (low >= 10 or suited and low == 9)
                elif rpos >= POS_MD:
                    # AA-99, AK-AJ, ATs
                    bet = pair and low >= 9 or hi == 14 and (low >= 11 or suited and low == 10)
                else:
                    # AA-QQ
                    bet = pair and low >= 12
                if bet:
                    bet_size = self.calc_bet_size_mid_stack_preflop(round_state)
            else:
                all_in = pair and low >= 13
                if all_in:
                    bet_size = MAX
            # TODO Steal/resteal

            if bet_size > 0:
                if bet_size * 3 > own_stack:
                    bet_size = MAX
                self.did_raise_preflop = True
                return self.raise_or_call(valid_actions, bet_size)
        elif round_state['street'] == 'flop':
            pcount = self.count_players(round_state)
            rcount = self.count_flop_raisers(round_state)

            monster = self.has_monster(c1, c2, ccards)
            over = self.has_over_pair(c1, c2, ccards)
            top = self.has_top_pair(c1, c2, ccards)
            monster_draw = self.has_monster_draw(c1, c2, ccards)
            oesd = self.has_oesd(c1, c2, ccards)
            fd = self.has_flush_draw(c1, c2, ccards)
            dgs = self.has_double_gutshot(c1, c2, ccards)

            has_good = monster or over or monster_draw
            has = has_good or top or oesd or fd or dgs

            # More than one opponent or draw board
            if pcount > 2 or self.is_dangerous_board(round_state, c1, c2, ccards):
                bet = has_good or has and rcount == 0
            # Safe flop
            else:
                bet = has_good or rcount == 0
            if bet:
                bet_size = pot * 2 / 3
                if bet_size * 2 > own_stack:
                    bet_size = MAX
                return self.raise_or_call(valid_actions, bet_size)
        elif round_state['street'] == 'turn':
            rcount = self.count_flop_raisers(round_state)

            monster = self.has_monster(c1, c2, ccards)
            over = self.has_over_pair(c1, c2, ccards)
            top = self.has_top_pair(c1, c2, ccards)
            monster_draw = self.has_monster_draw(c1, c2, ccards)

            has_good = monster or over or monster_draw
            has = has_good or top

            if has_good or has and rcount == 0:
                bet_size = pot * 2 / 3
                if bet_size * 2 > own_stack:
                    bet_size = MAX
                self.did_raise_turn = True
                return self.raise_or_call(valid_actions, bet_size)
        elif round_state['street'] == 'river':
            monster = self.has_monster(c1, c2, ccards)
            over = self.has_over_pair(c1, c2, ccards)
            top = self.has_top_pair(c1, c2, ccards)

            has_good = monster or over or top and self.did_raise_turn
            has = has_good or top

            if has_good or has and rcount == 0:
                bet_size = pot * 2 / 3
                if bet_size * 2 > own_stack:
                    bet_size = MAX
                return self.raise_or_call(valid_actions, bet_size)
            elif has:
                return self.call(valid_actions)
        return self.check_or_fold(valid_actions)

    def calc_bet_size_mid_stack_preflop(self, round_state):
        calls = 0
        i = len(round_state['action_histories']['preflop']) - 1
        while i >= 0:
            action = round_state['action_histories']['preflop'][i]
            if action['action'] == 'CALL':
                calls += 1
            elif action['action'] == 'RAISE' or action['action'] == 'BIGBLIND':
                return action['amount'] * (4 + calls)
            i -= 1
        raise RuntimeError('Initial bet not found')

    def play_short_stack(self, valid_actions, round_state, c1, c2):
        self.short = True

        low = min(c1.rank, c2.rank)
        hi = max(c1.rank, c2.rank)
        pair = c1.rank == c2.rank

        ccards = self.get_community_cards(round_state)

        if round_state['street'] == 'preflop':
            own_stack, avg_stack = self.count_starting_stacks(round_state)
            pos, rpos, lrpos = self.get_positions_types(round_state)
            rcount = self.count_preflop_raisers(round_state)

            if rcount == 0:
                if pos >= POS_CO:
                    # AA-77, AK-AT, KQ
                    bet = pair and low >= 7 or hi == 14 and low >= 10 or hi == 13 and low == 12
                elif pos == POS_MD:
                    # AA-99, AK, AQ
                    bet = pair and low >= 9 or hi == 14 and low >= 12
                else: # POS_EA
                    # AA-JJ, AK
                    bet = pair and low >= 11 or hi == 14 and low == 13
                if bet:
                    bet_size_blinds = self.calc_bet_size_short_stack_preflop(round_state)
                    bet_size = bet_size_blinds * self.bb
                    if bet_size * 3 > own_stack:
                        bet_size = MAX
                    self.did_raise_preflop = True
                    return self.raise_or_call(valid_actions, bet_size)
            else:
                if rcount == 1:
                    # resteal
                    if rpos >= POS_CO and pos >= POS_SB:
                        all_in = pair and low >= 8 or hi == 14 and low >= 11
                    # reraise
                    else:
                        # AA-JJ, AK
                        all_in = pair and low >= 11 or hi == 14 and low == 13
                elif self.did_raise_preflop:
                    # on resteal
                    if rcount == 2 and pos >= POS_CO and lrpos >= POS_SB:
                        # AA-99, AK-AJ
                        all_in = pair and low >= 9 or hi == 14 and low >= 11
                    else:
                        # AA-TT, AK
                        all_in = pair and low >= 10 or hi == 14 and low == 13
                else:
                    # AA, KK
                    all_in = pair and low >= 13
                if all_in:
                    return self.raise_or_call(valid_actions, MAX)
        elif round_state['street'] == 'flop':
            own_stack, avg_stack = self.count_current_stacks(round_state)
            pot = self.count_pot(round_state)
            rcount = self.count_flop_raisers(round_state)
            pcount = self.count_players(round_state)

            bet_size = 0
            # TODO need stronger hand if did not do a preflop raise
            if self.has_something(c1, c2, ccards):
                if rcount == 0:
                    bet_size = pot * 2 / 3
                else:
                    bet_size = MAX
            elif pot >= own_stack * 2:
                bet_size = MAX
            elif not self.bluff and self.did_raise_preflop and rcount == 0 and pcount == 2:
                self.bluff = True
                bet_size = pot * 2 / 3

            if bet_size > 0:
                if bet_size * 2 > own_stack:
                    bet_size = MAX
                return self.raise_or_call(valid_actions, bet_size)
        elif round_state['street'] == 'turn':
            if self.has_something(c1, c2, ccards):
                return self.raise_or_call(valid_actions, MAX)
        return self.check_or_fold(valid_actions)

    def has_something(self, c1, c2, ccards):
        mid = self.has_mid_pair(c1, c2, ccards)
        top = self.has_top_pair(c1, c2, ccards)
        over = self.has_over_pair(c1, c2, ccards)
        oesd = self.has_oesd(c1, c2, ccards)
        dgs = self.has_double_gutshot(c1, c2, ccards)
        fd = self.has_flush_draw(c1, c2, ccards)
        two = self.has_two_pairs(c1, c2, ccards)
        three = self.has_set(c1, c2, ccards)
        has = mid or top or over or oesd or dgs or fd or two or three
        # if has:
        #     cs = []
        #     for c in ccards:
        #         cs.append((c.rank, c.suit))
        #     print((c1.rank, c1.suit), (c2.rank, c2.suit), cs)
        #     print({ 'mid': mid, 'top': top, 'over': over, 'oesd': oesd, 'fd': fd, 'two': two, 'three': three })
        return has

    def has_mid_pair(self, c1, c2, ccards):
        if c1.rank != c2.rank:
            return False
        bigger = 0
        for c in ccards:
            if c1.rank <= c.rank:
                bigger += 1
        return bigger == 1

    def has_top_pair(self, c1, c2, ccards):
        max_rank = 0
        for c in ccards:
            if c.rank > max_rank:
                max_rank = c.rank
        return c1.rank == max_rank or c2.rank == max_rank

    def has_over_pair(self, c1, c2, ccards):
        if c1.rank != c2.rank:
            return False
        for c in ccards:
            if c1.rank <= c.rank:
                return False
        return True

    def has_oesd(self, c1, c2, ccards):
        # TODO Do not count A at both sides
        return self.has_straight(c1, c2, ccards, 4)

    def has_double_gutshot(self, c1, c2, ccards):
        # TODO Implement
        return False

    def has_straight(self, c1, c2, ccards, num=5):
        ranks = [c1.rank, c2.rank]
        for c in ccards:
            ranks.append(c.rank)
        ranks = list(set(ranks))
        ranks.sort()
        last = 0
        count = 0
        for r in ranks:
            if last > 0:
                if r == last + 1:
                    last = r
                    count += 1
                    if count >= 4:
                        return True
                else:
                    last = 0
                    count = 0
            else:
                last = r
                count = 1
        return False

    def has_flush_draw(self, c1, c2, ccards):
        return self.has_flush(c1, c2, ccards, 4)

    def has_flush(self, c1, c2, ccards, num=5):
        suits = { 2: 0 , 4: 0, 8: 0, 16: 0 }
        suits[c1.suit] += 1
        suits[c2.suit] += 1
        for c in ccards:
            suits[c.suit] += 1
        for s in suits:
            if suits[s] >= num:
                return True
        return False

    def has_monster_draw(self, c1, c2, ccards):
        fd = self.has_flush_draw(c1, c2, ccards)
        oesd = self.has_oesd(c1, c2, ccards)
        dgs = self.has_double_gutshot(c1, c2, ccards)
        return fd and (oesd or dgs)

    def has_monster(self, c1, c2, ccards):
        two = self.has_two_pairs(c1, c2, ccards)
        three = self.has_set(c1, c2, ccards)
        flush = self.has_flush(c1, c2, ccards)
        straight = self.has_straight(c1, c2, ccards)
        return two or three or flush or straight

    def has_two_pairs(self, c1, c2, ccards):
        ranks = { 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0 }
        ranks[c1.rank] += 1
        ranks[c2.rank] += 1
        for c in ccards:
            ranks[c.rank] += 1
        pairs = 0
        for r in ranks:
            if ranks[r] >= 2:
                pairs += 1
        return pairs > 1

    def has_set(self, c1, c2, ccards):
        ranks = { 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0 }
        ranks[c1.rank] += 1
        ranks[c2.rank] += 1
        for c in ccards:
            ranks[c.rank] += 1
        for r in ranks:
            if ranks[r] >= 3:
                return True
        return False

    def is_dangerous_board(self, round_state, c1, c2, ccards):
        # TODO Implement
        return False

    def get_community_cards(self, round_state):
        cards = []
        i = 0
        while i < len(round_state['community_card']):
            c = Card.from_str(round_state['community_card'][i])
            cards.append(c)
            i += 1
        return cards

    def calc_bet_size_short_stack_preflop(self, round_state):
        blinds = 4
        i = 0
        while i < len(round_state['action_histories']['preflop']):
            action = round_state['action_histories']['preflop'][i]
            if action['action'] == 'CALL':
                blinds += 1
            i += 1
        return blinds

    def play_monster(self, valid_actions, c1, c2):
        pair = c1.rank == c2.rank
        suited = c1.suit == c2.suit
        is_kk_plus = pair and c1.rank > 12
        is_low_k = min(c1.rank, c2.rank) == 13
        is_hi_a = max(c1.rank, c2.rank) == 14
        is_ak = is_low_k and is_hi_a
        is_aks = is_ak and suited

        if is_kk_plus:# or is_aks:
            # print('MONSTER', c1, c2)
            return self.raise_or_call(valid_actions, MAX)
        return self.check_or_fold(valid_actions)

    def push_fold(self, valid_actions, round_state, blinds, c1, c2):
        self.short = True

        low = min(c1.rank, c2.rank)
        hi = max(c1.rank, c2.rank)
        pair = c1.rank == c2.rank
        suited = c1.suit == c2.suit

        pos, rpos, lrpos = self.get_positions_types(round_state)

        pot = self.count_pot(round_state)
        pot_blinds = pot / self.bb

        medium = low >= 10 and hi >= 10
        big = low + hi >= 24
        monster = low + hi >= 26
        big_pair = pair and low >= 10

        push = False
        if rpos < 0:
            # AA-99
            if pair and low >= 9:
                push = True
            # 88-66
            elif pair and low >= 6:
                push = self.is_push(pos, blinds, { POS_EA: 10, POS_MD: MAX })
            # 55-22
            elif pair:
                push = self.is_push(pos, blinds, { POS_EA: 8, POS_MD: 10, POS_CO: MAX })
            # AK, AQ
            elif hi == 14 and low >= 12:
                push = True
            # AJs, ATs
            elif suited and hi == 14 and low >= 10:
                push = self.is_push(pos, blinds, { POS_EA: 8, POS_MD: MAX })
            # A9s-A2s
            elif suited and hi == 14:
                push = self.is_push(pos, blinds, { POS_EA: 5, POS_MD: 7, POS_CO: 10, POS_BU: 10, POS_SB: MAX })
            # AJo, ATo
            elif hi == 14 and low >= 10:
                push = self.is_push(pos, blinds, { POS_EA: 7, POS_MD: 8, POS_CO: 11, POS_BU: MAX })
            # A9o-A2o
            elif hi == 14:
                push = self.is_push(pos, blinds, { POS_EA: 5, POS_MD: 5, POS_CO: 7, POS_BU: 9, POS_SB: MAX })
            # KQs-K9s, QJs-Q9s, JTs, J9s, T9s
            elif suited and low >= 9:
                push = self.is_push(pos, blinds, { POS_EA: 8, POS_MD: 10, POS_CO: MAX })
            # K8s-K4s, Q8s, J8s, T8s, 98s
            elif suited and (low >= 8 or hi == 13 and low >= 4):
                push = self.is_push(pos, blinds, { POS_EA: 5, POS_MD: 6, POS_CO: 8, POS_BU: 9, POS_SB: MAX })
            # KQo-KTo, QJo-QTo, JTo
            elif low >= 10:
                push = self.is_push(pos, blinds, { POS_EA: 5, POS_MD: 8, POS_CO: 10, POS_BU: 10, POS_SB: MAX })
            # Q7s, Q6s
            elif suited and hi == 12 and low >= 6:
                push = self.is_push(pos, blinds, { POS_EA: 4, POS_MD: 5, POS_CO: 6, POS_BU: 7, POS_SB: MAX })
            # 97s, 96s, 86s, 76s, 75s, 65s
            elif suited and ((low == 6 or low == 5) and (hi == 9 or hi == 8 or hi == 7) or low == 5 and (hi == 6 or hi == 7)):
                push = self.is_push(pos, blinds, { POS_EA: 4, POS_MD: 5, POS_CO: 6, POS_BU: 7, POS_SB: MAX })
        elif pos < POS_SB:
            # AA-JJ
            if pair and low >= 11:
                push = True
            # TT, 99
            elif pair and low >= 9:
                push = self.is_push(rpos, blinds, { POS_EA: 8, POS_MD: 9, POS_CO: 11 })
            # 88, 77
            elif pair and low >= 7:
                push = self.is_push(rpos, blinds, { POS_MD: 5, POS_CO: 7 })
            # AK
            elif low == 13 and hi == 14:
                push = True
            # AQ
            elif low == 12 and hi == 14:
                push = self.is_push(rpos, blinds, { POS_EA: 8, POS_MD: 9, POS_CO: 11 })
            # AJs, ATs
            elif suited and low >= 10 and hi == 14:
                push = self.is_push(rpos, blinds, { POS_MD: 6, POS_CO: 9 })
            # AJo
            elif low == 11 and hi == 14:
                push = self.is_push(rpos, blinds, { POS_MD: 5, POS_CO: 7 })
            # ATo, A9s
            elif low == 10 and hi == 14 or suited and low == 9 and hi == 14:
                push = self.is_push(rpos, blinds, { POS_CO: 6 })
        elif pos == POS_SB:
            # AA-JJ
            if pair and low >= 11:
                push = True
            # TT, 99
            elif pair and low >= 9:
                push = self.is_push(rpos, blinds, { POS_MD: MAX })
            # 88, 77
            elif pair and low >= 8:
                push = self.is_push(rpos, blinds, { POS_MD: 7, POS_CO: MAX })
            # 66, 55
            elif pair and low >= 5:
                push = self.is_push(rpos, blinds, { POS_CO: 5, POS_BU: 8 })
            # AK
            elif hi == 14 and low == 13:
                push = True
            # AQ
            elif hi == 14 and low == 12:
                push = self.is_push(rpos, blinds, { POS_MD: MAX })
            # AJs, ATs
            elif suited and hi == 14 and low >= 10:
                push = self.is_push(rpos, blinds, { POS_MD: 7, POS_CO: MAX })
            # AJo
            elif hi == 14 and low == 11:
                push = self.is_push(rpos, blinds, { POS_MD: 6, POS_CO: MAX })
            # ATo, A9s
            elif hi == 14 and (suited and low == 9 or low == 10):
                push = self.is_push(rpos, blinds, { POS_MD: 4, POS_CO: 8, POS_BU: 10 })
            # A8s-A4s, A9o-A7o
            elif hi == 14 and (suited and low >= 4 or low >= 7):
                push = self.is_push(rpos, blinds, { POS_CO: 4, POS_BU: 6 })
            # KQs, KJs, KQo
            elif hi == 13 and (suited and low >= 11 or low >= 12):
                push = self.is_push(rpos, blinds, { POS_CO: 4, POS_BU: 6 })
        elif pos == POS_BB:
            # AA-JJ
            if pair and low >= 11:
                push = True
            # TT, 99
            elif pair and low >= 9:
                push = self.is_push(rpos, blinds, { POS_MD: MAX })
            # 88, 77
            elif pair and low >= 7:
                push = self.is_push(rpos, blinds, { POS_MD: 8, POS_CO: MAX })
            # 66, 55
            elif pair and low >= 5:
                push = self.is_push(rpos, blinds, { POS_MD: 5, POS_CO: 8, POS_BU: 10, POS_SB: MAX })
            # 44, 33
            elif pair and low >= 3:
                push = self.is_push(rpos, blinds, { POS_MD: 4, POS_CO: 5, POS_BU: 6, POS_SB: 7 })
            # AK
            elif low == 13 and hi == 14:
                push = True
            # AQ
            elif low == 13 and hi == 14:
                push = self.is_push(rpos, blinds, { POS_MD: MAX })
            # AJs, ATs
            elif suited and hi == 14 and low >= 10:
                push = self.is_push(rpos, blinds, { POS_MD: 8, POS_CO: MAX })
            # AJo
            elif hi == 14 and low == 11:
                push = self.is_push(rpos, blinds, { POS_MD: 7, POS_CO: MAX })
            # ATo, A9s
            elif hi == 14 and low == 10 or suited and hi == 14 and low == 9:
                push = self.is_push(rpos, blinds, { POS_MD: 6, POS_CO: 10, POS_BU: MAX })
            # A8s-A4s, A9o-A7o
            elif hi == 14 and (suited and low >= 4 or low >= 7):
                push = self.is_push(rpos, blinds, { POS_MD: 3, POS_CO: 6, POS_BU: 8, POS_SB: MAX })
            # A3s, A2s, A6o-A2o
            elif hi == 14:
                push = self.is_push(rpos, blinds, { POS_MD: 2, POS_CO: 5, POS_BU: 6, POS_SB: 8 })
            # KQs, KJs, KQo
            elif hi == 13 and (suited and low >= 11 or low == 12):
                push = self.is_push(rpos, blinds, { POS_MD: 4, POS_CO: 5, POS_BU: 8, POS_SB: MAX })
            # KTs, K9s, QJs, KJo, KTo
            elif hi == 13 and (suited and low >= 9 or low >= 10) or hi == 12 and low == 11:
                push = self.is_push(rpos, blinds, { POS_MD: 3, POS_CO: 4, POS_BU: 6, POS_SB: 10 })

        if push:
            # if rpos >= 0:
            #     print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', blinds, pos, rpos, c1.rank, c2.rank, suited)
            return self.raise_or_call(valid_actions, MAX)
        return self.check_or_fold(valid_actions)

    def is_push(self, pos, blinds, m):
        for key in m:
            if pos >= key and blinds <= round(self.ins(m[key])):
                return True
        return False

    def get_positions_types(self, round_state):
        seat = self.get_seat(round_state)
        pos = self.get_position_type(round_state, seat)
        raiser_seat = self.get_raiser_seat(round_state)
        if raiser_seat < 0:
            rpos = -1
        else:
            rpos = self.get_position_type(round_state, raiser_seat)
        last_raiser_seat = self.get_last_raiser_seat(round_state)
        if last_raiser_seat < 0:
            lrpos = -1
        else:
            lrpos = self.get_position_type(round_state, last_raiser_seat)
        return pos, rpos, lrpos

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

    def get_last_raiser_seat(self, round_state):
        uuid = self.get_last_raiser_uuid(round_state)
        if uuid == '':
            return -1
        i = 0
        while i < len(self.start_seats):
            if self.start_seats[i]['uuid'] == uuid:
                return i
            i += 1
        raise RuntimeError('Raiser seat not found')

    def count_players(self, round_state):
        count = 0
        i = 0
        while i < len(round_state['seats']):
            seat = round_state['seats'][i]
            if seat['state'] == 'participating' or seat['state'] == 'allin':
                count += 1
            elif seat['state'] != 'folded':
                raise RuntimeError('Unknown state {}', seat['state'])
            i += 1
        return count

    def count_flop_raisers(self, round_state):
        return self.count_raisers(round_state, 'flop')

    def count_preflop_raisers(self, round_state):
        return self.count_raisers(round_state, 'preflop')

    def count_raisers(self, round_state, street):
        count = 0
        i = 0
        while i < len(round_state['action_histories'][street]):
            action = round_state['action_histories'][street][i]
            if action['action'] == 'RAISE':
                count += 1
            i += 1
        return count

    def get_raiser_uuid(self, round_state):
        i = 0
        while i < len(round_state['action_histories']['preflop']):
            action = round_state['action_histories']['preflop'][i]
            if action['action'] == 'RAISE':
                return action['uuid']
            i += 1
        return ''

    def get_last_raiser_uuid(self, round_state):
        i = len(round_state['action_histories']['preflop']) - 1
        while i >= 0:
            action = round_state['action_histories']['preflop'][i]
            if action['action'] == 'RAISE':
                return action['uuid']
            i -= 1
        return ''

    def raise_or_call(self, valid_actions, val):
        if valid_actions[2]['amount']['max'] < 0:
            return self.call(valid_actions)
        elif valid_actions[2]['amount']['max'] < val:
            return 'raise', valid_actions[2]['amount']['max']
        elif val < valid_actions[2]['amount']['min']:
            return 'raise', valid_actions[2]['amount']['min']
        return 'raise', val

    def call(self, valid_actions):
        return 'call', valid_actions[1]['amount']

    def check_or_fold(self, valid_actions):
        if valid_actions[1]['amount'] > 0:
            return 'fold', 0
        return self.call(valid_actions)

    def count_current_stacks(self, round_state):
        return self.count_stacks(round_state, round_state['seats'])

    def count_starting_stacks(self, round_state):
        return self.count_stacks(round_state, self.start_seats)

    def count_stacks(self, round_state, seats):
        own_stack = 0
        other_sum = 0
        other_num = 0

        i = 0
        while i < len(seats):
            seat = seats[i]
            if seat['state'] == 'participating' or seat['state'] == 'allin':
                if seat['uuid'] == self.uuid:
                    own_stack = seat['stack']
                else:
                    other_sum += seat['stack']
                    other_num += 1
            elif seat['state'] != 'folded':
                raise RuntimeError('Unknown state {}', seat['state'])
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
        self.short = False
        self.did_raise_preflop = False
        self.did_raise_turn = False
        self.bluff = False

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
