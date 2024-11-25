from pathlib import Path
import json, time, random, os

FISHING_COOLDOWN = 10
RARE_ITEM_WEIGHT_THRESHOLD = 1.5

FISHING_ITEMS_PATH = Path("trackers\\fishing_items.json")
FISHING_DATABASE_PATH = Path("trackers\\fishing.json")
GENERAL_DATABASE_PATH = Path("trackers\\user_triggers.json")

class OnFishingCooldownError(Exception):
    pass

class FishingItem:
    def __init__(self, name, value, weight):
        self.name = name
        self.value = value
        self.weight = weight

def random_range(start: int, stop: int) -> int:
    """random.randrange but its inclusive so i don't keep forgetting the original function has an exclusive endpoint because i have fucking dementia"""
    return random.randrange(start, stop + 1)

def fish_to_dict(fish: FishingItem) -> dict:
    cock = dict()
    cock['name'] = fish.name
    cock['value'] = fish.value
    cock['weight'] = fish.weight

    return cock

def dict_to_fish(dick: dict) -> FishingItem:
    return FishingItem(dick['name'],
                       dick['value'],
                       dick['weight'])

def initialize_fishing_items() -> list[FishingItem]:
    all_da_fishies = []

    with open(FISHING_ITEMS_PATH, 'r') as file:
        list_of_fishies = json.load(file)

        for fishy in list_of_fishies:
            all_da_fishies.append(dict_to_fish(fishy))

    return all_da_fishies

def initialize_rares():
    rares = []

    for fish in fishing_items:
        if fish.weight <= RARE_ITEM_WEIGHT_THRESHOLD:
            rares.append(fish)

    return rares

def fish_event(username: str, is_extra_fish=False, jonklerfish_debug=False) -> str:
    all_users = get_all_users()
    jonklerfish = [fish for fish in fishing_items if fish.name == 'Jonklerfish'][0]

    random_num = random_range(1, 100)
    caught_fish = go_fish(username)

    penalty = 0
    lucky = random_num <= 7 # 7% chance
    unlucky = random_num >= 95 and not is_extra_fish # 6% chance

    output = ""

    if lucky:
        output += '*You caught more stuff than usual*\n'
    elif unlucky:
        update_fish_database(username)
        return 'Oops, your line broke'

    if caught_fish.name == 'Cop Fish' and not is_extra_fish:
        penalty = random_num + 19
        output += f'You caught the Cop Fish! (next cooldown is {random_num + FISHING_COOLDOWN + 19} seconds)'

    elif caught_fish.name == 'Jonklerfish' or jonklerfish_debug:
        penalty = random_num + 39
        output += (f'You caught the {caught_fish.name}! (+{caught_fish.value} moneys, everyone\'s cooldown '
                   f'increased to {penalty + FISHING_COOLDOWN} seconds')

        for user in all_users:
            update_fish_database(user, cd_penalty=penalty)

    elif caught_fish in rare_items:
        output += f'‼️ You caught: **{caught_fish.name}** (worth {caught_fish.value} moneys)'
    else:
        output += f'You caught: **{caught_fish.name}** (worth {caught_fish.value} moneys)'

    if lucky:
        output += f'\n{fish_event(username, is_extra_fish=True)}'

    update_fish_database(username, fish=jonklerfish if jonklerfish_debug else caught_fish, cd_penalty=penalty)
    return output

def go_fish(username: str, count=1) -> FishingItem:
    weights = [fish.weight for fish in fishing_items]
    last_fish_time = get_user_last_fish_time(username)
    current_time = int(time.time())

    if current_time - last_fish_time >= FISHING_COOLDOWN:
        return random.choices(fishing_items, weights=weights, k=count)[0]
    else:
        raise OnFishingCooldownError

def get_user_last_fish_time(username: str) -> int:
    with open(FISHING_DATABASE_PATH, 'r') as file:
        list_of_profiles = json.load(file)

        for profile in list_of_profiles:
            if profile['username'] == username:
                return profile['last_fish_time']

        return 0

def get_all_users() -> list[str]:
    with open(FISHING_DATABASE_PATH, 'r') as file:
        list_of_profiles = json.load(file)
        return [profile['username'] for profile in list_of_profiles]

def update_inventory(inventory: list[dict], fish: FishingItem):
    item_found = False

    for stack in inventory:
        if stack['item']['name'] == fish.name:
            stack['count'] += 1
            item_found = True

    if not item_found:
        stack = dict()
        stack['item'] = fish_to_dict(fish)
        stack['count'] = 1

        inventory.append(stack)

    sort_inventory(inventory)

def sort_inventory(inventory: list[dict]):
    inventory.sort(key=lambda stack: stack['item']['value'], reverse=True)

def sort_fishing_items():
    with open(FISHING_ITEMS_PATH, 'r+') as file:
        items = json.load(file)
        items.sort(key=lambda fish: fish['weight'])

        file.seek(0)
        json.dump(items, file, indent=4)
        file.truncate()

def profile_to_string(username: str) -> str:
    output: str = f"*{username}*\n"

    with open(FISHING_DATABASE_PATH, 'r') as file:
        list_of_profiles = json.load(file)
        user_found = False

        for profile in list_of_profiles:
            if profile['username'] == username:
                output += (f"Moneys obtained: **{profile['value']}**\n"
                           f"Times fished: **{profile['times_fished']}**\n\n")

                for stack in profile['items']:
                    output += f"**{stack['count']}x** *{stack['item']['name']}*\n"

                return output

    return output + f"Moneys obtained: **0**\nTimes fished: **0**\n\nNo fish caught"

def universal_profile_to_string() -> str:
    output: str = f"*Universal Stats*\n"

    with open(FISHING_DATABASE_PATH, 'r') as file:
        list_of_profiles = json.load(file)
        user_found = False

        output += (f"Moneys obtained: **{sum(profile['value'] for profile in list_of_profiles)}**\n"
                   f"Times fished: **{sum(profile['times_fished'] for profile in list_of_profiles)}*"
                   f"*\n\n")

        for fish in fishing_items:
            temp_name = fish.name
            temp_total = 0

            for profile in list_of_profiles:
                for stack in profile['items']:
                    if stack['item']['name'] == temp_name:
                        temp_total += stack['count']

            if temp_total > 0:
                output += f"**{temp_total}x** *{temp_name}*\n"

        return output


def leaderboard_string() -> str:
    output = '*Leaderboard*\n\n'

    with open(FISHING_DATABASE_PATH, 'r') as file:
        list_of_profiles = json.load(file)
        list_of_profiles.sort(key=lambda prof: prof['value'], reverse=True)

        for index in range(len(list_of_profiles)):
            output += f'{index + 1}. {list_of_profiles[index]['username']}: **{
                         list_of_profiles[index]['value']} moneys**\n'

    return output

def update_fish_database(username: str, fish: FishingItem=None, cd_penalty=0) -> None:
    with open(FISHING_DATABASE_PATH, 'r+') as file:
        list_of_profiles = json.load(file)
        user_found = False

        for profile in list_of_profiles:
            if profile['username'] == username:
                if fish:
                    update_inventory(profile['items'], fish)

                profile['last_fish_time'] = int(time.time()) + cd_penalty
                profile['value'] = sum(stack['item']['value'] * stack['count']
                                       for stack in profile['items'])
                profile['times_fished'] = sum(stack['count'] for stack in profile['items'])
                user_found = True

        if not user_found:
            new_profile = dict()
            new_profile['username'] = username
            new_profile['times_fished'] = 1
            new_profile['last_fish_time'] = int(time.time()) + cd_penalty
            new_profile['items'] = []

            if fish:
                update_inventory(new_profile['items'], fish)
                new_profile['value'] = fish.value

            list_of_profiles.append(new_profile)

        file.seek(0)
        json.dump(list_of_profiles, file, indent=4)
        file.truncate()

def update_user_database(username: str, increment=1) -> None:
    with open(GENERAL_DATABASE_PATH, 'r+') as file:
        list_of_dickshunarys = json.load(file)
        user_found = False

        for dickshunary in list_of_dickshunarys:
            if dickshunary['username'] == username:
                user_found = True
                dickshunary['value'] += increment

        if not user_found:
            cock = dict()
            cock['username'] = username
            cock['value'] = increment
            list_of_dickshunarys.append(cock)

        file.seek(0)
        json.dump(list_of_dickshunarys, file, indent=4)
        file.truncate()

script_directory = Path(__file__).parent.resolve()
os.chdir(script_directory)

fishing_items = initialize_fishing_items()
sort_fishing_items()
rare_items = initialize_rares()