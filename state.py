from functools import reduce
from copy import deepcopy
import math
from pprint import pprint

from constants.buildings import buildings as b_data
from constants.upgrades import upgrades as u_data
from save import Save


# self.data = {
#                 'cookie_count': deepcopy(float(base['cookie_count'])),
#                 'buildings': deepcopy(base['buildings']),
#                 'upgrades': deepcopy(base['upgrades']),
#                 'achievement_count': deepcopy(base['achievement_count']),
#                 'purchasable_upgrades': deepcopy(save['purchasable_upgrades']),
#             }

class State():
    def __init__(self, base, override: bool = False):
        if isinstance(base, State):
            self.data = deepcopy(base.data)
        elif isinstance(base, Save):
            self.data = deepcopy(base.sections)
        # elif override:
        #     self.data = {
        #         'cookie_count': deepcopy(float(base['cookie_count'])),
        #         'buildings': deepcopy(base['buildings']),
        #         'upgrades': deepcopy(base['upgrades']),
        #         'achievement_count': deepcopy(base['achievement_count']),
        #         'purchasable_upgrades': deepcopy(base['purchasable_upgrades']),
        #     }
        else:
            raise TypeError("State must be initialized with a Save or State object")

    def get_purchasable_buildings(self) -> "list[str]":
        return self.data['buildings'].keys()

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
        purchased_upgrade_ids = self.get_purchased_upgrade_ids()
        building_type_upgrade_ids = self.get_upgrade_ids_of_type(building)
        mod = 2 ** match_count(purchased_upgrade_ids, building_type_upgrade_ids)
        if building == 'grandma':
            mod *= 2 ** match_count(purchased_upgrade_ids, self.get_upgrade_ids_of_type('grandma_type'))
            if 64 in purchased_upgrade_ids:
                mod *= 4
        return mod

    def get_grandma_mod(self, building):
        grandma_count = self.data['buildings']['grandma']['owned']
        purchased_upgrade_ids = self.get_purchased_upgrade_ids()
        if building == 'farm' and 57 in purchased_upgrade_ids:
            return 1 + (0.01*(grandma_count/1))
        elif building == 'mine' and 58 in purchased_upgrade_ids:
            return 1 + (0.01*(grandma_count/2))
        elif building == 'factory' and 59 in purchased_upgrade_ids:
            return 1 + (0.01*(grandma_count/3))
        elif building == 'bank' and 250 in purchased_upgrade_ids:
            return 1 + (0.01*(grandma_count/4))
        elif building == 'temple' and 251 in purchased_upgrade_ids:
            return 1 + (0.01*(grandma_count/5))
        elif building == 'wizard_tower' and 252 in purchased_upgrade_ids:
            return 1 + (0.01*(grandma_count/6))
        elif building == 'shipment' and 60 in purchased_upgrade_ids:
            return 1 + (0.01*(grandma_count/7))
        elif building == 'alchemy_lab' and 61 in purchased_upgrade_ids:
            return 1 + (0.01*(grandma_count/8))
        elif building == 'portal' and 62 in purchased_upgrade_ids:
            return 1 + (0.01*(grandma_count/9))
        return 1

    def get_level_mod(self, building):
        building_level = self.data['buildings'][building]['level']
        return 1 + (0.01 * building_level)

    def get_misc_adj(self, building):
        adjustment = 0
        if building == 'cursor':
            purchased_upgrade_ids = self.get_purchased_upgrade_ids()
            non_cursor_building_count = sum(
                map(lambda b: b['owned'], self.data['buildings'].values()), -self.data['buildings']['cursor']['owned'])
            # total_buildings_count = reduce(lambda sum, a: sum + a['owned'], self.data['buildings'].values(), 0)
            # non_cursor_buildings_count = total_buildings_count - self.data['buildings']['cursor']['owned']
            # level = match_count(self.data['upgrades'], {'CURSOR_SPEC_1', 'CURSOR_SPEC_2', 'CURSOR_SPEC_3',
            #                                             'CURSOR_SPEC_4', 'CURSOR_SPEC_5', 'CURSOR_SPEC_6',
            #                                             'CURSOR_SPEC_7', 'CURSOR_SPEC_8', 'CURSOR_SPEC_9', })
            if 3 in purchased_upgrade_ids:
                adjustment = 0.1 * non_cursor_building_count
            if 4 in purchased_upgrade_ids:
                adjustment *= 5
            if 5 in purchased_upgrade_ids:
                adjustment *= 10
            if 6 in purchased_upgrade_ids:
                adjustment *= 20
            if 43 in purchased_upgrade_ids:
                adjustment *= 20

        return adjustment

    def get_global_mod(self):
        return self.get_kitten_mod() * self.get_cookie_mod() * self.get_minigame_mod()

    def get_kitten_mod(self):
        kitten_mod = 1
        milk_level = 0.04 * self.data['achievement_count']
        purchased_kitten_upgrade_ids = (set(self.get_upgrade_ids_of_type('kitten'))
                                        & set(self.get_purchased_upgrade_ids()))
        for kitten_upgrade_id in purchased_kitten_upgrade_ids:
            kitten_mod *= 1 + (milk_level * u_data[kitten_upgrade_id]['milk_factor'])
        return kitten_mod

    def get_cookie_mod(self):
        cookie_mod = 1
        purchased_upgrade_ids = self.get_purchased_upgrade_ids()
        # print(self.get_purchasable_upgrade_ids())
        for upgrade_id in purchased_upgrade_ids:
            upgrade = u_data[upgrade_id]
            if upgrade['type'] == 'flavored_cookie':
                cookie_mod *= upgrade['multiplier']
        return cookie_mod

    def get_minigame_mod(self):
        return self.get_garden_mod() * self.get_stock_market_mod() * self.get_pantheon_mod() * self.get_grimoire_mod()

    def get_garden_mod(self):
        return 1

    def get_stock_market_mod(self):
        return 1

    def get_pantheon_mod(self):
        pantheon_mod = 1

        pantheon_data = self.data['buildings']['temple']['minigame']
        # pprint(pantheon_data)
        diamond_spirit = pantheon_data['diamond']
        ruby_spirit = pantheon_data['ruby']
        jade_spirit = pantheon_data['jade']

        # diamond slot
        if diamond_spirit == 0:
            pantheon_mod *= 1.15
        elif diamond_spirit == 3:
            print('WARNING: Cyclius equipped! Will not yield accurate results here yet')
            # TODO: Handle Cyclius case
        elif diamond_spirit == 5:
            print('WARNING: Dotjeiess equipped! Will not yield accurate results here yet')
            # TODO: Handle Dotjeiess case
        elif diamond_spirit == 7:
            pantheon_mod *= 1.10
        elif diamond_spirit == 8:
            print('WARNING: Mokalsium equipped! Will not yield accurate results here yet')
            # TODO: Handle Mokalsium case

        # ruby slot
        if ruby_spirit == 0:
            pantheon_mod *= 1.10
        elif ruby_spirit == 3:
            print('WARNING: Cyclius equipped! Will not yield accurate results here yet')
            # TODO: Handle Cyclius case
        elif ruby_spirit == 5:
            print('WARNING: Dotjeiess equipped! Will not yield accurate results here yet')
            # TODO: Handle Dotjeiess case
        elif ruby_spirit == 7:
            pantheon_mod *= 1.06
        elif ruby_spirit == 8:
            print('WARNING: Mokalsium equipped! Will not yield accurate results here yet')
            # TODO: Handle Mokalsium case

        # jade slot
        if jade_spirit == 0:
            pantheon_mod *= 1.05
        elif jade_spirit == 3:
            print('WARNING: Cyclius equipped! Will not yield accurate results here yet')
            # TODO: Handle Cyclius case
        elif jade_spirit == 5:
            print('WARNING: Dotjeiess equipped! Will not yield accurate results here yet')
            # TODO: Handle Dotjeiess case
        elif jade_spirit == 7:
            pantheon_mod *= 1.03
        elif jade_spirit == 8:
            print('WARNING: Mokalsium equipped! Will not yield accurate results here yet')
            # TODO: Handle Mokalsium case

        return pantheon_mod

    def get_grimoire_mod(self):
        return 1

    def get_upgrade_ids_of_type(self, upgrade_type):
        return [id for id, u in u_data.items() if u['type'] == upgrade_type]

    def get_achievement_count(self):
        return self.data['achievement_count']

    def get_earned_achievement_ids(self):
        return [i for i, a in enumerate(self.data['achievements']) if a]

    def get_purchased_upgrade_ids(self):
        pu = [i for i, u in enumerate(self.data['upgrades']) if u['purchased']]
        # pprint(pu)
        return pu

    def get_unlocked_upgrade_ids(self):
        return [i for i, u in enumerate(self.data['upgrades']) if u['unlocked']]

    def get_purchasable_upgrade_ids(self) -> "set[int]":
        return set(self.get_unlocked_upgrade_ids()) - set(self.get_purchased_upgrade_ids())
        # upgrades: "list[dict]" = self.data['upgrades']
        # return [i for i in range(len(upgrades)) if upgrades[i]['unlocked'] and not upgrades[i]['purchased']]

    def get_purchased_upgrade_names(self):
        return map(lambda i: u_data.get(i, '__UNKNOWN__'), self.get_purchased_upgrade_ids())


def match_count(collection, match):
    try:
        return len(set(collection) & set(match))
    except Exception as e:
        print(e)
        print(type(collection))
        print(type(match))
        return 0
