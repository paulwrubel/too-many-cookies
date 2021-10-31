import base64
from datetime import datetime
from pprint import pprint
import urllib.parse

from constants.achievements import shadow_achievement_ids as shadow_achievement_ids
# from constants.buildings import buildings as b_data
from constants.upgrades import upgrades as u_data


class Save:
    # constant for save suffix
    ENCODING_SUFFIX = '!END!'

    def __init__(self, file_path):
        self.file_path = file_path
        self.__parse()

    def __parse(self):
        with open(self.file_path, 'r') as f:
            unquoted_line = urllib.parse.unquote(f.readlines()[0])
            save_string_encoded = unquoted_line.rstrip().replace(self.ENCODING_SUFFIX, '')

        self.save_raw = base64.b64decode(save_string_encoded).decode('utf-8')
        self.sections_raw_list = self.save_raw.split('|')

        # save sections under labels
        self.sections_raw = {}
        self.sections_raw['version'] = self.sections_raw_list[0]
        self.sections_raw['reserved'] = self.sections_raw_list[1]
        self.sections_raw['run_details'] = self.sections_raw_list[2]
        self.sections_raw['preferences'] = self.sections_raw_list[3]
        self.sections_raw['misc'] = self.sections_raw_list[4]
        self.sections_raw['buildings'] = self.sections_raw_list[5]
        self.sections_raw['upgrades'] = self.sections_raw_list[6]
        self.sections_raw['achievements'] = self.sections_raw_list[7]
        self.sections_raw['buffs'] = self.sections_raw_list[8]

        # parse sections
        self.sections = {}
        for section_name, section_raw in self.sections_raw.items():
            self.__parse_section(section_name, section_raw)

        # for section_name, section in self.sections.items():
        #     pprint(section_name)
        #     pprint(section)

    def __parse_section(self, section_name, section_raw):
        if section_name == 'version':
            self.sections['version'] = {}
            self.sections['version']['version'] = section_raw
        elif section_name == 'run_details':
            run_details_raw_list = section_raw.split(';')
            self.sections['run_details'] = {}
            self.sections['run_details']['ascension_start_time'] = datetime.utcfromtimestamp(
                int(run_details_raw_list[0])/1000)
            self.sections['run_details']['game_start_time'] = datetime.utcfromtimestamp(
                int(run_details_raw_list[1])/1000)
            self.sections['run_details']['last_opened_time'] = datetime.utcfromtimestamp(
                int(run_details_raw_list[2])/1000)
            self.sections['run_details']['bakery_name'] = run_details_raw_list[3]
            self.sections['run_details']['seed'] = run_details_raw_list[4]
        elif section_name == 'preferences':
            print(f'SKIPPING PARSING PREFERENCES')
        elif section_name == 'misc':
            misc_raw_list = section_raw.split(';')
            self.sections['misc'] = {}
            self.sections['misc']['cookies_current'] = float(misc_raw_list[0])
            self.sections['misc']['cookies_total_this_ascension'] = float(misc_raw_list[1])
            self.sections['misc']['cookies_clicked_this_ascension'] = float(misc_raw_list[2])
            self.sections['misc']['golden_cookies_clicked_total'] = float(misc_raw_list[3])
            self.sections['misc']['cookies_total_this_ascension_by_clicking'] = float(misc_raw_list[4])
            self.sections['misc']['golden_cookies_missed'] = float(misc_raw_list[5])
            self.sections['misc']['background_type'] = misc_raw_list[6]
            self.sections['misc']['milk_type'] = misc_raw_list[7]
            self.sections['misc']['cookies_forfeited'] = float(misc_raw_list[8])
            self.sections['misc']['grandmapocalypse_stage'] = misc_raw_list[9]
            self.sections['misc']['elder_pledges'] = float(misc_raw_list[10])
            self.sections['misc']['elder_pledge_time_remaining'] = datetime.utcfromtimestamp(
                int(misc_raw_list[11])/1000)
            self.sections['misc']['current_research_id'] = misc_raw_list[12]
            self.sections['misc']['research_time_remaining'] = datetime.utcfromtimestamp(int(misc_raw_list[13])/1000)
            self.sections['misc']['ascension_count'] = float(misc_raw_list[14])
            self.sections['misc']['golden_cookies_clicked_this_ascension'] = float(misc_raw_list[15])
            self.sections['misc']['cookies_sucked_by_wrinklers'] = float(misc_raw_list[16])
            self.sections['misc']['wrinklers_popped'] = float(misc_raw_list[17])
            self.sections['misc']['santa_level'] = misc_raw_list[18]
            self.sections['misc']['reindeer_clicked'] = float(misc_raw_list[19])
            self.sections['misc']['season_time_remaining'] = datetime.utcfromtimestamp(int(misc_raw_list[20])/1000)
            self.sections['misc']['season_switcher_use_count'] = float(misc_raw_list[21])
            self.sections['misc']['current_season'] = misc_raw_list[22]
            self.sections['misc']['cookies_in_normal_wrinklers'] = float(misc_raw_list[23])
            self.sections['misc']['wrinkler_normal_count'] = float(misc_raw_list[24])
            self.sections['misc']['prestige_level'] = misc_raw_list[25]
            self.sections['misc']['heavenly_chips_current'] = float(misc_raw_list[26])
            self.sections['misc']['heavenly_chips_spent'] = float(misc_raw_list[27])
            self.sections['misc']['heavenly_cookies'] = float(misc_raw_list[28])
            self.sections['misc']['ascension_mode'] = misc_raw_list[29]
            self.sections['misc']['permanent_upgrade_1_id'] = misc_raw_list[30]
            self.sections['misc']['permanent_upgrade_2_id'] = misc_raw_list[31]
            self.sections['misc']['permanent_upgrade_3_id'] = misc_raw_list[32]
            self.sections['misc']['permanent_upgrade_4_id'] = misc_raw_list[33]
            self.sections['misc']['permanent_upgrade_5_id'] = misc_raw_list[34]
            self.sections['misc']['dragon_level'] = misc_raw_list[35]
            self.sections['misc']['dragon_aura_1_id'] = misc_raw_list[36]
            self.sections['misc']['dragon_aura_2_id'] = misc_raw_list[37]
            self.sections['misc']['golden_cookie_chime_type'] = misc_raw_list[38]
            self.sections['misc']['volume'] = misc_raw_list[39]
            self.sections['misc']['wrinkler_shiny_count'] = float(misc_raw_list[40])
            self.sections['misc']['cookies_in_shiny_wrinklers'] = float(misc_raw_list[41])
            self.sections['misc']['sugar_lumps_current'] = float(misc_raw_list[42])
            self.sections['misc']['sugar_lumps_made'] = float(misc_raw_list[43])
            self.sections['misc']['sugar_lump_start_time'] = datetime.utcfromtimestamp(int(misc_raw_list[44])/1000)
            self.sections['misc']['sugar_lump_last_minigame_refill_time'] = datetime.utcfromtimestamp(
                int(misc_raw_list[45])/1000)
            self.sections['misc']['sugar_lump_type'] = misc_raw_list[46]
            self.sections['misc']['upgrades_in_vault_ids'] = misc_raw_list[47].split(',')
        elif section_name == 'buildings':
            buildings_raw_list = section_raw.split(';')
            building_names = [
                'cursor', 'grandma', 'farm',  'mine',  'factory',
                'bank', 'temple', 'wizard_tower', 'shipment', 'alchemy_lab',
                'portal', 'time_machine', 'antimatter_condenser', 'prism', 'chancemaker',
                'fractal_engine', 'javascript_console', 'idleverse',
            ]
            self.sections['buildings'] = {}
            for index, building_name in enumerate(building_names):
                self.sections['buildings'][building_name] = self.__parse_building(
                    building_name, buildings_raw_list[index])
        elif section_name == 'upgrades':
            self.sections['upgrades'] = []
            for i in range(0, len(section_raw), 2):
                upgrade_data = {
                    'unlocked': section_raw[i] == '1',
                    'purchased': section_raw[i+1] == '1',
                }
                if (upgrade_data['unlocked'] or upgrade_data['purchased']) and i // 2 not in u_data.keys():
                    raise Exception('Sanity check failed: Unknown upgrade id: ' + str(i // 2))
                self.sections['upgrades'].append(upgrade_data)
        elif section_name == 'achievements':
            # print(f'\t{section_raw}')
            self.sections['achievements'] = []
            achievement_count = 0
            for id, achievement_raw in enumerate(section_raw):
                if achievement_raw == '1':
                    self.sections['achievements'].append(True)
                    if id not in shadow_achievement_ids:
                        achievement_count += 1
                else:
                    self.sections['achievements'].append(False)
            self.sections['achievement_count'] = achievement_count
        elif section_name == 'buffs':
            print(f'SKIPPING PARSING BUFFS')

    def __parse_building(self, building_name, building_raw):
        building_raw_list = building_raw.split(',')
        building = {}
        building['owned'] = int(building_raw_list[0])
        building['bought'] = int(building_raw_list[1])
        building['cookies_produced'] = float(building_raw_list[2])
        building['level'] = int(building_raw_list[3])
        building['minigame'] = {}
        if building_name == 'farm':
            print(f'SKIPPING PARSING GARDEN MINIGAME')
            # TODO: parse garden minigame data
        elif building_name == 'bank':
            print(f'SKIPPING PARSING STOCK MARKET MINIGAME')
            # TODO: parse stock market minigame data
        elif building_name == 'temple':
            pantheon_raw_list = building_raw_list[4].split(' ')
            slots = pantheon_raw_list[0].split('/')
            building['minigame']['diamond'] = int(slots[0])
            building['minigame']['ruby'] = int(slots[1])
            building['minigame']['jade'] = int(slots[2])
            building['minigame']['swaps'] = int(pantheon_raw_list[1])
            building['minigame']['swap_refill_time_remaining'] = datetime.utcfromtimestamp(
                int(pantheon_raw_list[2])/1000)
            building['minigame']['is_open'] = pantheon_raw_list[3] == '1'
        elif building_name == 'wizard_tower':
            print(f'SKIPPING PARSING GRIMOIRE MINIGAME')
            # TODO: parse grimoire minigame data
        building['muted'] = building_raw_list[5]
        return building
