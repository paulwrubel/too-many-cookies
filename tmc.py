from os import times
import sys
import traceback
import yaml
import time

from state import State
from state_modifier import StateModifier


class TooManyCookies():
    def run(self):
        print("starting TooManyCookies")

        print('loading state file')
        state_file_loc = sys.argv[1]
        print(state_file_loc)
        try:
            with open(state_file_loc) as state_file:
                initial_state_data = yaml.safe_load(state_file)
        except Exception as e:
            oops(e, f'error opening state file: {e}')

        # calculate initial state from provided state file
        initial_state = State(initial_state_data)

        # calculate optimal next 5 states
        current_state = initial_state
        optimal_state_modifications = []
        for i in range(10):
            possible_modifiers = self.calculate_all_possible_modifiers(current_state)
            preferred_modifier = self.find_preferred_modifier(possible_modifiers)
            optimal_state_modifications.append(preferred_modifier)

            current_state = preferred_modifier.modified_state

        # print current CPS
        print()
        print(f'Current CPS: {initial_state.get_cps():>20,.2f}')
        print()

        # print CPS for each building
        for building in initial_state.data['buildings']:
            if initial_state.data['buildings'][building]['owned'] > 0:
                b_cps = initial_state.get_cps_single(building)
                print(f'{building:>15}: {pretty_number_string(b_cps):>20}')
        print()

        # print results
        for i, modifier in enumerate(optimal_state_modifications):
            mod = modifier.modification
            print(f'{i+1:2d}: Purchase a {mod["item"]:<18} ' +
                  f'| Cost = {pretty_number_string(mod["remaining_cost"]):>20} ' +
                  f'| TTA = {pretty_time_delta(mod["tta"]):>20} ' +
                  f'| weight = {mod["weight"]:>10,.2f} ')

    def calculate_all_possible_modifiers(self, initial_state):
        print('calculating modified states')
        possible_modifiers = []
        purchasable_buildings = initial_state.get_purchasable_buildings()
        for b in purchasable_buildings:
            modifier = StateModifier(initial_state)
            modifier.modify(StateModifier.Action.PURCHASE_BUILDING, b)
            possible_modifiers.append(modifier)
        purchasable_upgrades = initial_state.get_purchasable_upgrades()
        for u in purchasable_upgrades:
            modifier = StateModifier(initial_state)
            modifier.modify(StateModifier.Action.PURCHASE_UPGRADE, u)
            possible_modifiers.append(modifier)
        return possible_modifiers

    def find_preferred_modifier(self, possible_modifiers):
        print('calculating preferred next state')

        # calcuate some intermediate values
        for mod in possible_modifiers:
            mod.modification['cps_delta'] = mod.modified_state.get_cps() - mod.base_state.get_cps()
            mod.modification['value'] = mod.modification['cps_delta'] / mod.modification['total_cost']
            mod.modification['tta'] = mod.modification['remaining_cost'] / mod.base_state.get_cps()

        # find minimum non-zero value
        min_value = None
        for mod in possible_modifiers:
            if mod.modification['value'] > 0:
                if min_value is None or mod.modification['value'] < min_value:
                    min_value = mod.modification['value']

        # scale value by minimum value to determine weights
        for mod in possible_modifiers:
            mod.modification['weight'] = mod.modification['value'] / min_value

        possible_modifiers.sort(
            key=lambda m: m.modification['value'], reverse=True)

        return possible_modifiers[0]


def pretty_number_string(number: float) -> str:
    if number > 1e15:
        return f'{number/1e15:.3f} quadrillion'
    elif number > 1e12:
        return f'{number/1e12:.3f}    trillion'
    elif number > 1e9:
        return f'{number/1e09:.3f}     billion'
    elif number > 1e6:
        return f'{number/1e06:.3f}     million'
    return f'{number:,.0f}            '


def pretty_time_delta(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%2dd %2dh %2dm %2ds' % (days, hours, minutes, seconds)
    elif hours > 0:
        return '%2dh %2dm %2ds' % (hours, minutes, seconds)
    elif minutes > 0:
        return '%2dm %2ds' % (minutes, seconds)
    else:
        return '%2ds' % (seconds,)


def oops(e, err_string):
    print(err_string)
    traceback.print_exc()


if __name__ == '__main__':
    tmc = TooManyCookies()
    try:
        tmc.run()
    except Exception as e:
        oops(e, f'error while running agent: {e}')
