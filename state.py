from functools import reduce
from copy import deepcopy
import math

from constants.buildings import buildings as b_data


class State():
    def __init__(self, base_state):
        if isinstance(base_state, State):
            self.data = deepcopy(base_state.data)
            return

        state_data = base_state

        self.data = {
            'cookie_count': deepcopy(float(state_data['cookie_count'])),
            'buildings': deepcopy(state_data['buildings']),
            'upgrades': deepcopy(state_data['upgrades']),
            'achievement_count': deepcopy(state_data['achievement_count']),
            'purchasable_upgrades': deepcopy(state_data['purchasable_upgrades']),
        }

    def get_purchasable_buildings(self) -> "list[str]":
        return self.data['buildings'].keys()

    def get_purchasable_upgrades(self) -> "list[dict]":
        return self.data['purchasable_upgrades']

    def get_building_cost(self, building):
        return math.ceil(
            (b_data[building]['base_cost'] * (
                (1.15 ** (self.data['buildings'][building]['owned'] + 1)) -
                (1.15 ** self.data['buildings'][building]['owned'])
            )) / 0.15
        )

    def get_cps(self, building='all', post_mod=True):
        global_mod = self.get_global_mod() if post_mod else 1
        if building is not 'all':
            return self.get_cps_single(building, False) * self.data['buildings'][building]['owned'] * global_mod

        def reduce_cps(cps, b):
            if b in self.data['buildings'] and self.data['buildings'][b].get('owned', 0) is not 0:
                return cps + self.get_cps(b)
            return cps
        return reduce(reduce_cps, b_data, 0)

    def get_cps_single(self, building, post_mod=True):
        global_mod = self.get_global_mod() if post_mod else 1
        upgrade_mod = self.get_upgrade_mod(building)
        grandma_mod = self.get_grandma_mod(building)
        level_mod = self.get_level_mod(building)
        misc_adj = self.get_misc_adj(building)
        return ((b_data[building]['cps'] * upgrade_mod * grandma_mod * level_mod) + misc_adj) * global_mod

    def get_upgrade_mod(self, building):
        if building == 'cursor':
            return 2 ** match_count(self.data['upgrades'],
                                    {'CURSOR_1', 'CURSOR_2', 'CURSOR_3'})
        elif building == 'grandma':
            mod = 2 ** match_count(self.data['upgrades'],
                                   {'GRANDMA_1', 'GRANDMA_2', 'GRANDMA_3',
                                    'GRANDMA_4', 'GRANDMA_5', 'GRANDMA_6',
                                    'GRANDMA_7', 'GRANDMA_8', 'GRANDMA_9',
                                    'GRANDMA_10', 'GRANDMA_11', 'GRANDMA_12',
                                    'GRANDMA_13', 'GRANDMA_14', 'GRANDMA_15', })
            if 'BINGO_RESEARCH_CENTER' in self.data['upgrades']:
                mod = mod * 4
            return mod
        elif building == 'farm':
            return 2 ** match_count(self.data['upgrades'],
                                    {'FARM_1', 'FARM_2', 'FARM_3',
                                     'FARM_4', 'FARM_5', })
        elif building == 'mine':
            return 2 ** match_count(self.data['upgrades'],
                                    {'MINE_1', 'MINE_2', 'MINE_3',
                                     'MINE_4', 'MINE_5', })
        elif building == 'factory':
            return 2 ** match_count(self.data['upgrades'],
                                    {'FACTORY_1', 'FACTORY_2', 'FACTORY_3',
                                     'FACTORY_4', 'FACTORY_5', })
        elif building == 'bank':
            return 2 ** match_count(self.data['upgrades'],
                                    {'BANK_1', 'BANK_2', 'BANK_3',
                                     'BANK_4', 'BANK_5', })
        elif building == 'temple':
            return 2 ** match_count(self.data['upgrades'],
                                    {'TEMPLE_1', 'TEMPLE_2', 'TEMPLE_3',
                                     'TEMPLE_4', 'TEMPLE_5', })
        elif building == 'wizard_tower':
            return 2 ** match_count(self.data['upgrades'],
                                    {'WIZARD_TOWER_1', 'WIZARD_TOWER_2', 'WIZARD_TOWER_3',
                                     'WIZARD_TOWER_4', 'WIZARD_TOWER_5', })
        elif building == 'shipment':
            return 2 ** match_count(self.data['upgrades'],
                                    {'SHIPMENT_1', 'SHIPMENT_2', 'SHIPMENT_3',
                                     'SHIPMENT_4', 'SHIPMENT_5', })
        elif building == 'alchemy_lab':
            return 2 ** match_count(self.data['upgrades'],
                                    {'ALCHEMY_LAB_1', 'ALCHEMY_LAB_2', 'ALCHEMY_LAB_3',
                                     'ALCHEMY_LAB_4', 'ALCHEMY_LAB_5', })
        elif building == 'portal':
            return 2 ** match_count(self.data['upgrades'],
                                    {'PORTAL_1', 'PORTAL_2', 'PORTAL_3',
                                     'PORTAL_4', 'PORTAL_5', })
        elif building == 'time_machine':
            return 2 ** match_count(self.data['upgrades'],
                                    {'TIME_MACHINE_1', 'TIME_MACHINE_2', 'TIME_MACHINE_3',
                                     'TIME_MACHINE_4', 'TIME_MACHINE_5', })
        elif building == 'antimatter_condenser':
            return 2 ** match_count(self.data['upgrades'],
                                    {'ANTIMATTER_CONDENSER_1', 'ANTIMATTER_CONDENSER_2', 'ANTIMATTER_CONDENSER_3',
                                     'ANTIMATTER_CONDENSER_4', 'ANTIMATTER_CONDENSER_5', })
        elif building == 'prism':
            return 2 ** match_count(self.data['upgrades'],
                                    {'PRISM_1', 'PRISM_2', 'PRISM_3',
                                     'PRISM_4', 'PRISM_5', })

    def get_grandma_mod(self, building):
        grandma_count = self.data['buildings']['grandma']['owned']
        if building == 'farm' and 'GRANDMA_6' in self.data['upgrades']:
            return 1 + (0.01*grandma_count)
        elif building == 'mine' and 'GRANDMA_7' in self.data['upgrades']:
            return 1 + (0.01*(grandma_count/2))
        elif building == 'factory' and 'GRANDMA_8' in self.data['upgrades']:
            return 1 + (0.01*(grandma_count/3))
        elif building == 'bank' and 'GRANDMA_9' in self.data['upgrades']:
            return 1 + (0.01*(grandma_count/4))
        elif building == 'temple' and 'GRANDMA_10' in self.data['upgrades']:
            return 1 + (0.01*(grandma_count/5))
        elif building == 'wizard_tower' and 'GRANDMA_11' in self.data['upgrades']:
            return 1 + (0.01*(grandma_count/6))
        elif building == 'shipment' and 'GRANDMA_12' in self.data['upgrades']:
            return 1 + (0.01*(grandma_count/7))
        elif building == 'alchemy_lab' and 'GRANDMA_13' in self.data['upgrades']:
            return 1 + (0.01*(grandma_count/8))
        elif building == 'portal' and 'GRANDMA_14' in self.data['upgrades']:
            return 1 + (0.01*(grandma_count/9))
        return 1

    def get_level_mod(self, building):
        building_level = self.data['buildings'][building].get('level', 0)
        return 1 + (0.01 * building_level)

    def get_misc_adj(self, building):
        if building == 'cursor':
            total_buildings_count = reduce(lambda sum, a: sum + a['owned'], self.data['buildings'].values(), 0)
            non_cursor_buildings_count = total_buildings_count - self.data['buildings']['cursor']['owned']
            level = match_count(self.data['upgrades'], {'CURSOR_4', 'CURSOR_5', 'CURSOR_6'})
            if level == 0:
                return 0
            elif level == 1:
                return 0.1 * non_cursor_buildings_count
            elif level == 2:
                return 0.5 * non_cursor_buildings_count
            elif level == 3:
                return 5 * non_cursor_buildings_count

        return 0

    def get_global_mod(self):
        return self.get_kitten_mod() * self.get_cookie_mod() * self.get_garden_mod()

    def get_kitten_mod(self):
        kitten_mod = 1
        milk_level = 0.04 * self.data['achievement_count']
        if 'KITTEN_HELPERS' in self.data['upgrades']:
            kitten_mod *= 1 + (milk_level * 0.1)
        if 'KITTEN_WORKERS' in self.data['upgrades']:
            kitten_mod *= 1 + (milk_level * 0.125)
        if 'KITTEN_ENGINEERS' in self.data['upgrades']:
            kitten_mod *= 1 + (milk_level * 0.15)
        return kitten_mod

    def get_cookie_mod(self):
        cookie_mod = 1
        for upgrade in self.data['upgrades']:
            if upgrade == 'COOKIE_1':
                cookie_mod *= 1.01
            elif upgrade == 'COOKIE_2':
                cookie_mod *= 1.02
            elif upgrade == 'COOKIE_5':
                cookie_mod *= 1.05
        return cookie_mod

    def get_garden_mod(self):
        return 1


def match_count(collection, match):
    try:
        return len(set(collection) & set(match))
    except Exception as e:
        print(e)
        print(type(collection))
        print(type(match))
        return 0
