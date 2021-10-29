from enum import Enum, auto

from state import State


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
            self.modified_state.data['upgrades'].append(item['name'])
            self.modified_state.data['purchasable_upgrades'].remove(item)
            item_name = item['name']
            item_cost = float(item['cost'])

        self.modification = {
            'action': action,
            'item': item_name,
            'total_cost': item_cost,
            'remaining_cost': max(0, item_cost - self.modified_state.data['cookie_count'])
        }
        self.modified_state.data['cookie_count'] = max(0, self.modified_state.data['cookie_count'] - item_cost)
