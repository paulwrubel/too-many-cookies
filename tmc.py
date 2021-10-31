from os import times
import sys
import traceback
import yaml
import time
from pprint import pprint

from constants.upgrades import upgrades as u_data

from state import State
from state_modifier import StateModifier
from save import Save


class TooManyCookies():
    def run(self):
        print("starting TooManyCookies...")
        print()

        print('loading config file...')
        config_file_loc = sys.argv[1]
        save_file_loc = sys.argv[2]
        try:
            with open(config_file_loc) as config_file:
                config = yaml.safe_load(config_file)
        except Exception as e:
            oops(e, f'error opening state file: {e}')
        print('state file loaded')

        print('parsing save file...')
        save = Save(save_file_loc)
        print('save file parsed')
        initial_state = State(save)

        # print(f'{len(initial_state.get_purchased_upgrade_ids())} upgrades purchased')
        # print('purchased upgrades:')
        # print(initial_state.get_purchased_upgrade_ids())
        # print(f'{len(initial_state.get_unlocked_upgrade_ids())} upgrades unlocked')
        # print('unlocked upgrades:')
        # print(initial_state.get_unlocked_upgrade_ids())
        # print(f'{len(initial_state.get_purchasable_upgrade_ids())} upgrades available to purchase')
        # print('purchasable upgrades:')
        # print(initial_state.get_purchasable_upgrade_ids())
        # print(f'{len(u_data)} upgrades registered in total')
        # print('registered upgrades:')
        # print(u_data.keys())

        # calculate initial state from provided state file
        # initial_state_old = State(initial_state_data, True)

        modifier_lists = {}
        strategy = config['preferred_strategy']
        iterations_r = config['iterations']
        iterations = iterations_r if iterations_r > 0 else None
        modifier_lists[strategy] = self.calculate_optimal_modifications(initial_state, strategy, iterations)
        # modifier_lists['fast'] = self.calculate_optimal_modifications(initial_state, strategy='fast')
        # modifier_lists['partial'] = self.calculate_optimal_modifications(initial_state, strategy='partial')
        # modifier_lists['pure'] = self.calculate_optimal_modifications(initial_state, strategy='pure')

        # print misc data
        print()
        print(f'Current Cookies:   {pretty_number_string(initial_state.data["misc"]["cookies_current"]):<25}')
        print(f'Current CPS Exact: {initial_state.get_cps():<25,.2f}')
        print(f'Current CPS:       {pretty_number_string(initial_state.get_cps()):<25}')
        print(f'Global Mod:        {initial_state.get_global_mod():<25,.2f}')
        print(f'Achievement Count: {initial_state.get_achievement_count():<25}')
        print()

        # print CPS for each building
        for building_name, building_info in initial_state.data['buildings'].items():
            if building_info['owned'] > 0:
                b_cps = initial_state.get_cps_single(building_name)
                b_cps_total = initial_state.get_cps(building_name)
                b_cps_perc = b_cps_total / initial_state.get_cps()
                print(
                    f'{building_name:>20}({b_cps_perc*100:>6,.2f}%): {pretty_number_string(b_cps):>20} x {building_info["owned"]:>4} = {pretty_number_string(b_cps_total):>20}')
        print()

        # print results
        self.output_mod_tables(modifier_lists)

    def output_mod_tables(self, modifier_lists):
        print('outputting modification tables')
        for name, modifiers in modifier_lists.items():
            self.output_mod_summary(modifiers, name)
            self.output_mod_table(modifiers, name)

    def output_mod_summary(self, modifiers, name):
        print()
        print(f'{"_"*50}{name.upper():^12}{"_"*50}')
        summary = self.calculate_summary_from_modifiers(modifiers)
        print(f'Total Cost: {pretty_number_string(summary["total_cost"]):<25}')
        print(f'Total TTA:  {pretty_time_delta(summary["total_tta"]):<25}')
        print(f'Total %+:   {summary["total_cps_percentage_delta"]*100:<25,.2f}%')
        print(f'Total CPS:  {pretty_number_string(summary["total_cps_delta"]):<25}')
        print()
        print('---Purchases---')

        # print buildings
        print('Buildings:')
        for building, count in summary['buildings'].items():
            print(f'\t{building:<20}: {count:>5}')
        print()

        print('Upgrades:')
        # print upgrades
        for upgrade in summary['upgrades']:
            print(f'\t{upgrade:<20}')

    def output_mod_table(self, modifiers, name: str):
        print()
        print(f'{"_"*50}{name.upper():^12}{"_"*50}')
        for i, modifier in enumerate(modifiers):
            mod = modifier.modification
            print(f'{i+1:2d}: Purchase a {mod["item"]:<24} ' +
                  f'| Cost = {pretty_number_string(mod["remaining_cost"]):>20} ' +
                  f'| TTA = {pretty_time_delta(mod["remaining_tta"]):>20} ' +
                  f'| weight = {mod["weight"]:>10,.2f} ' +
                  f'| %+ = {mod["cps_percentage_delta"]*100:>5,.2f}% ')

    def calculate_summary_from_modifiers(self, modifiers):
        summary = {
            'total_cost': 0,
            'total_tta': 0,
            'total_cps_percentage_delta': 0,
            'total_cps_delta': 0,
            'buildings': {},
            'upgrades': []
        }
        for mod in modifiers:
            if mod.modification['action'] == StateModifier.Action.PURCHASE_BUILDING:
                if mod.modification['item'] not in summary['buildings']:
                    summary['buildings'][mod.modification['item']] = 0
                summary['buildings'][mod.modification['item']] += 1
            elif mod.modification['action'] == StateModifier.Action.PURCHASE_UPGRADE:
                summary['upgrades'].append(mod.modification['item'])
            summary['total_cost'] += mod.modification['total_cost']
            summary['total_tta'] += mod.modification['total_tta']
            summary['total_cps_percentage_delta'] += mod.modification['cps_percentage_delta']
            summary['total_cps_delta'] += mod.modification['cps_delta']
        return summary

    def calculate_optimal_modifications(self, initial_state, strategy='pure', n=None):
        print('calculating optimal modifications')
        print(f'Strategy: {strategy}')
        print(f'Number of iterations: {n}')
        print()

        # calculate optimal next 5 states
        current_state = initial_state
        optimal_state_modifications = []
        if n is not None:
            for i in range(n):
                possible_modifiers = self.calculate_all_possible_modifiers(current_state)
                optimal_modifier = self.find_optimal_modifier(possible_modifiers, strategy)
                optimal_state_modifications.append(optimal_modifier)
                current_state = optimal_modifier.modified_state
        else:
            while current_state.data['misc']['cookies_current'] > 0:
                possible_modifiers = self.calculate_all_possible_modifiers(current_state)
                optimal_modifier = self.find_optimal_modifier(possible_modifiers, strategy)
                if optimal_modifier.modified_state.data['misc']['cookies_current'] == 0:
                    break
                optimal_state_modifications.append(optimal_modifier)
                current_state = optimal_modifier.modified_state

        return optimal_state_modifications

    def calculate_all_possible_modifiers(self, initial_state: State):
        print('calculating modified states')
        possible_modifiers = []
        purchasable_buildings = initial_state.get_purchasable_buildings()
        for b in purchasable_buildings:
            modifier = StateModifier(initial_state)
            modifier.modify(StateModifier.Action.PURCHASE_BUILDING, b)
            possible_modifiers.append(modifier)
        purchasable_upgrade_ids = initial_state.get_purchasable_upgrade_ids()
        for u_id in purchasable_upgrade_ids:
            modifier = StateModifier(initial_state)
            modifier.modify(StateModifier.Action.PURCHASE_UPGRADE, u_id)
            possible_modifiers.append(modifier)
        return possible_modifiers

    def find_optimal_modifier(self, possible_modifiers, strategy):
        print('calculating preferred next state')

        # calcuate some intermediate values
        for mod in possible_modifiers:
            mod.modification['cps_delta'] = mod.modified_state.get_cps() - mod.base_state.get_cps()
            mod.modification['cps_percentage_delta'] = mod.modification['cps_delta'] / mod.base_state.get_cps()
            mod.modification['total_tta'] = mod.modification['total_cost'] / mod.base_state.get_cps()
            mod.modification['remaining_tta'] = mod.modification['remaining_cost'] / mod.base_state.get_cps()
            if strategy == 'pure':
                mod.modification['value'] = mod.modification['cps_delta'] / mod.modification['total_cost']
            elif strategy == 'fast':
                mod.modification['value'] = (mod.modification['cps_delta'] / mod.modification['total_cost'] /
                                             mod.modification['total_tta'])
            elif strategy == 'partial':
                mod.modification['value'] = ((mod.modification['cps_delta'] / mod.modification['total_cost']) *
                                             (mod.modification['cps_delta'] / mod.modification['total_cost'] /
                                             mod.modification['total_tta']))

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
