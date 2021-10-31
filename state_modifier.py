from enum import Enum, auto

from state import State

from constants.upgrades import upgrades as u_data


class StateModifier():
    class Action(Enum):
        PURCHASE_BUILDING = auto()
        PURCHASE_UPGRADE = auto()
        PURCHASE_COOKIE = auto()

    def __init__(self, state: State):
        self.base_state = State(state)

    def modify(self, action, item):
        self.modified_state = State(self.base_state)

        if action is self.Action.PURCHASE_BUILDING:
            self.modified_state.data['buildings'][item]['owned'] += 1
            item_name = item
            item_cost = self.base_state.get_building_cost(item)

        elif action is self.Action.PURCHASE_UPGRADE:
            self.modified_state.data['upgrades'][item]['purchased'] = True
            upgrade_data = u_data[item]
            item_name = upgrade_data['name']
            item_cost = upgrade_data['cost']

        self.modification = {
            'action': action,
            'item': item_name,
            'total_cost': item_cost,
            'remaining_cost': max(0, item_cost - self.modified_state.data['misc']['cookies_current'])
        }
        self.modified_state.data['misc']['cookies_current'] = max(
            0, self.modified_state.data['misc']['cookies_current'] - item_cost)
