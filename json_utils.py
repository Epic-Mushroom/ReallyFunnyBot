from pathlib import Path
import json, time, random, os

FISHING_COOLDOWN = 10
RARE_ITEM_WEIGHT_THRESHOLD = 1.5
SUPER_RARE_ITEM_WEIGHT_THRESHOLD = 0.501

FISHING_ITEMS_PATH = Path("trackers\\fishing_items.json")
FISHING_DATABASE_PATH = Path("trackers\\fishing.json")
SPECIALS_DATABASE_PATH = Path("trackers\\specials.json")
GENERAL_DATABASE_PATH = Path("trackers\\user_triggers.json")

class OnFishingCooldownError(Exception):
    pass

class Profile:
    def __init__(self, username, **kwargs):
        self.username = username
        for key, value in kwargs.items():
            setattr(self, key, value)

class FishingItem:
    def __init__(self, name, value, weight, **kwargs):
        self.name = name
        self.value = value
        self.weight = weight

def random_range(start: int, stop: int) -> int:
    """random.randrange but its inclusive so i don't keep forgetting the original function has an exclusive endpoint because i have fucking dementia"""
    return random.randrange(start, stop + 1)

def manipulated_weights(factor=1) -> list:
    fishing_items_sorted_by_weight = sorted(fishing_items, key=lambda item: item.weight)
    weights = [fish.weight for fish in fishing_items_sorted_by_weight]
    weight_sum = sum(weights)
    chances = [(100 * weight / weight_sum) for weight in weights]

    rarest_partition = []
    most_common_partition = []

    for i in range(len(chances)):
        rarest_partition.append(fishing_items_sorted_by_weight[i])
        if sum(chances[:i + 1]) >= 15:
            break

    for i in range(len(chances))[::-1]:
        most_common_partition.append(fishing_items_sorted_by_weight[i])
        if sum(chances[i:]) >= 30:
            break

    modified_weights = weights[:]
    for i in range(len(rarest_partition)):
        modified_weights[i] = factor * weights[i]
    for i in range(len(weights) - len(most_common_partition), len(weights)):
        modified_weights[i] = weights[i] / factor
    new_weight_sum = sum(modified_weights)
    new_chances = [(100 * weight / new_weight_sum) for weight in modified_weights]

    return modified_weights
    # print(chances)
    # print(new_chances)

def initialize_fishing_items() -> list[FishingItem]:
    all_da_fishies = []

    with open(FISHING_ITEMS_PATH, 'r') as file:
        list_of_fishies = json.load(file)

        for fishy in list_of_fishies:
            all_da_fishies.append(FishingItem(**fishy))

    return all_da_fishies

def initialize_rares():
    rares = []

    for fish in fishing_items:
        if 0 <= fish.weight <= RARE_ITEM_WEIGHT_THRESHOLD:
            rares.append(fish)

    return rares

def get_fish_from_name(name: str):
    the_fish = [fish for fish in fishing_items if fish.name == name][0]
    return the_fish

def fishing_database() -> list[dict]:
    with open(FISHING_DATABASE_PATH, 'r') as file:
        list_of_profiles = json.load(file)
        return list_of_profiles

def update_fish_file(json_object: list | dict):
    with open(FISHING_DATABASE_PATH, 'w') as file:
        json.dump(json_object, file, indent=4)
        file.truncate()

def specials_database() -> dict:
    with open(SPECIALS_DATABASE_PATH, 'r') as file:
        specials_dict = json.load(file)
        return specials_dict

def update_specials_file(json_object: list | dict):
    with open(SPECIALS_DATABASE_PATH, 'w') as file:
        json.dump(json_object, file, indent=4)
        file.truncate()

def get_active_specials(username: str) -> list[str]:
    specials_dict = specials_database()
    active_specials = []

    for key in specials_dict.keys():
        for user_status in specials_dict[key]:
            if user_status['username'] == username and user_status['count'] > 0:
                active_specials.append(key)
                break

    return active_specials

def use_up_special(username: str, special: str) -> None:
    specials_dict = specials_database()

    for user_status in specials_dict[special]:
        if user_status['username'] == username and user_status['count'] > 0:
            user_status['count'] -= 1
            break

    update_specials_file(specials_dict)

def fish_event(username: str, is_extra_fish=False, force_fish_name=None, bypass_fish_cd=False) -> str:

    def other_player_with_catfish() -> str | None:

        specials_dict = specials_database()
        catfish_list = specials_dict['catfish']

        for user_status in catfish_list:
            if user_status['username'] != username and user_status['count'] > 0:
                return user_status['username']

        return None

    def handle_specials():
        """
        Not finished
        """
        active_specials = get_active_specials(username)

        if not is_test_user:
            if other_player_with_catfish():
                ...
            elif ...:
                pass

    all_users = get_all_users()
    is_test_user = username == 'test_user'
    original_user = username

    last_fish_time = get_user_last_fish_time(username)
    current_time = int(time.time())

    random_num = random_range(1, 100)

    penalty = 0
    lucky = random_num <= 7 # 7% chance
    unlucky = random_num >= 95 and not is_extra_fish # 6% chance

    catfish_holder = other_player_with_catfish()
    if catfish_holder:
        username = catfish_holder
        bypass_fish_cd = True

    output = "(test_user)" if is_test_user else ""

    if bypass_fish_cd or current_time - last_fish_time >= FISHING_COOLDOWN:
        if is_test_user:
            caught_fish = go_fish(factor=18)
        elif not force_fish_name:
            caught_fish = go_fish()
        else:
            caught_fish = go_fish(force_fish_name=force_fish_name)

        if lucky:
            output += '*You caught more stuff than usual*\n'
        elif unlucky:
            update_fish_database(username, bypass_fish_cd=bypass_fish_cd)
            return 'Oops, your line broke'

        if caught_fish.name == 'Cop Fish' and not is_extra_fish:
            penalty = random_num + 19
            output += f'You caught the Cop Fish! (next cooldown is {random_num + FISHING_COOLDOWN + 19} seconds)'

        elif caught_fish.name == 'Fish Soap':
            output += f'‼️ You caught: **Fish Soap** (all items with negative value removed)'
            fish_soap(username)

        elif caught_fish.name == 'Jonklerfish' and not is_test_user:
            penalty = random_num + 39
            output += (f'You caught the {caught_fish.name}! (+{caught_fish.value} moneys, everyone\'s cooldown '
                       f'increased to {penalty + FISHING_COOLDOWN} seconds)')

            for user in all_users:
                update_fish_database(user, cd_penalty=penalty)

        elif caught_fish.name == 'Mercenary Fish' and not is_test_user:
            output += f'You caught the Mercenary Fish!'

            for i in range(random_range(5, 6)):
                # steal_fish_from_random also updates the thief's profile with the fish that was stolen
                heist_tuple = steal_fish_from_random(username)
                temp_username = heist_tuple[0]
                stolen_fish = heist_tuple[1]

                output += f'\nStole {stolen_fish.name} from {temp_username}'

        elif caught_fish.name == 'CS:GO Fish' and not is_test_user:
            output += f'You caught: **CS:GO Fish** ('

            for i in range(random_range(1, 1)):
                heist_tuple = steal_fish_from_random(username, shoot=True)
                temp_username = heist_tuple[0]
                stolen_fish = heist_tuple[1]

                output += f'{temp_username}\'s {stolen_fish.name} was shot)'

        elif caught_fish.name == 'Sea Bass':
            output += f'You caught: **{caught_fish.name}**... no it\'s at least a C+ (worth {caught_fish.value} moneys)'

        elif caught_fish.weight < SUPER_RARE_ITEM_WEIGHT_THRESHOLD:
            output += f'‼️‼️ You caught: **{caught_fish.name}** (worth {caught_fish.value} moneys)'

        elif caught_fish in rare_items:
            output += f'‼️ You caught: **{caught_fish.name}** (worth {caught_fish.value} moneys)'

        else:
            output += f'You caught: **{caught_fish.name}** (worth {caught_fish.value} moneys)'

    else:
        raise OnFishingCooldownError

    if lucky:
        output += f'\n{fish_event(username, is_extra_fish=True, bypass_fish_cd=True)}'

    update_fish_database(username, fish=caught_fish, cd_penalty=penalty, bypass_fish_cd=bypass_fish_cd)

    # uses up all specials except the catfish because it should only be used up when
    # another player fishes with the catfish active
    for special in get_active_specials(username):
        if special != 'catfish':
            use_up_special(username, special)

    if catfish_holder:
        update_fish_database(original_user, bypass_fish_cd=False)
        use_up_special(catfish_holder, 'catfish')
        output += f'\n*Fish taken by {catfish_holder}*'

    return output

def go_fish(factor=1, force_fish_name: str=None) -> FishingItem:
    weights = manipulated_weights(factor=factor)
    fishing_items_sorted_by_weight = sorted(fishing_items, key=lambda item: item.weight)

    if not force_fish_name:
        return random.choices(fishing_items_sorted_by_weight, weights=weights, k=1)[0]
    else:
        force_fish = [fish for fish in fishing_items if fish.name == force_fish_name][0]
        return force_fish

def fish_soap(username: str):
    list_of_profiles = fishing_database()

    for profile in list_of_profiles:
        if profile['username'] == username:
            player_inv = profile['items']
            profile['items'] = [stack for stack in player_inv if stack['item']['value'] >= 0]

    update_fish_file(list_of_profiles)

def steal_fish_from_random(thief_name: str, shoot=False) -> tuple[str, FishingItem]:
    list_of_profiles = fishing_database()

    while True:
        weights = [profile['times_fished'] for profile in list_of_profiles]
        player_profile = random.choices(list_of_profiles, weights=weights, k=1)[0]
        player_inv = player_profile['items']
        player_name = player_profile['username']

        if (player_name != thief_name or shoot) and player_name != 'test_user':
            break

    weights = [stack['count'] for stack in player_inv]
    stolen_fish = FishingItem(**random.choices(player_inv, weights=weights, k=1)[0]['item'])

    # Removes the stolen fish from the player who was being stolen from, not modifying the time they last fished
    update_fish_database(player_name, fish=stolen_fish, count=-1, bypass_fish_cd=True)

    if not shoot:
        update_fish_database(thief_name, fish=stolen_fish)

    return player_name, stolen_fish

def get_user_last_fish_time(username: str) -> int:
    list_of_profiles = fishing_database()

    for profile in list_of_profiles:
        if profile['username'] == username:
            return profile['last_fish_time']

    return 0

def get_all_users() -> list[str]:
    list_of_profiles = fishing_database()
    return [profile['username'] for profile in list_of_profiles]

def update_inventory(inventory: list[dict], fish: FishingItem, count=1):
    """
    This does not modify any files!
    """
    item_found = False

    for stack in inventory:
        if stack['item']['name'] == fish.name:
            stack['count'] += count
            print(stack['count'])
            item_found = True

    if not item_found:
        stack = dict()
        stack['item'] = fish.__dict__
        stack['count'] = count

        inventory.append(stack)

    sort_inventory(inventory)

def sort_inventory(inventory: list[dict]):
    inventory.sort(key=lambda stack: stack['item']['value'], reverse=True)
    # print(inventory[0]['count'])

def sort_fishing_items():
    with open(FISHING_ITEMS_PATH, 'r+') as file:
        items = json.load(file)
        items.sort(key=lambda fish: fish['value'], reverse=True)

        file.seek(0)
        json.dump(items, file, indent=4)
        file.truncate()

def profile_to_string(username: str) -> str:
    output: str = f"*{username}*\n"

    list_of_profiles = fishing_database()

    for profile in list_of_profiles:
        if profile['username'] == username:
            output += (f"Moneys obtained: **{profile['value']}**\n"
                       f"Items caught: **{profile['times_fished']}**\n\n")

            for stack in profile['items']:
                output += f"**{stack['count']}x** *{stack['item']['name']}*\n"

            return output

    return output + f"Moneys obtained: **0**\nItems caught: **0**\n\nNo fish caught"

def universal_profile_to_string() -> str:
    output: str = f"*Universal Stats*\n"

    list_of_profiles = fishing_database()

    output += (f"Moneys obtained: **{sum(profile['value'] for profile in list_of_profiles if profile['username'] != 'test_user')}**\n"
               f"Items caught: **{sum(profile['times_fished'] for profile in list_of_profiles if profile['username'] != 'test_user')}*"
               f"*\n\n")

    for fish in fishing_items:
        temp_name = fish.name
        temp_total = 0

        for profile in list_of_profiles:
            if profile['username'] != 'test_user':
                for stack in profile['items']:
                    if stack['item']['name'] == temp_name:
                        temp_total += stack['count']

        if temp_total > 0:
            output += f"**{temp_total}x** *{temp_name}*\n"

    return output


def leaderboard_string() -> str:
    output = '*Leaderboard*\n\n'
    index = 1

    list_of_profiles = fishing_database()
    list_of_profiles.sort(key=lambda prof: prof['value'], reverse=True)

    for profile in [profile for profile in list_of_profiles if profile['username'] != 'test_user']:
        try:
            output += f'{index}. {profile['username']}: **{
                        profile['value']} moneys**\n'
            index += 1
        except KeyError:
            pass

    return output

def update_fish_database(username: str, fish: FishingItem=None, count=1, cd_penalty=0, bypass_fish_cd=False) -> None:
    """
    bypass_fish_cd: if True, does not modify the time the user last fished
    """
    list_of_profiles = fishing_database()
    user_found = False

    for profile in list_of_profiles:
        if profile['username'] == username:
            if fish:
                update_inventory(profile['items'], fish, count=count)

            profile['value'] = sum(stack['item']['value'] * stack['count'] for stack in profile['items'])
            profile['times_fished'] = sum(stack['count'] for stack in profile['items'])

            profile['last_fish_time'] = int(time.time()) + cd_penalty
            if bypass_fish_cd:
                profile['last_fish_time'] -= FISHING_COOLDOWN

            user_found = True

    if not user_found:
        new_profile = dict()
        new_profile['username'] = username
        new_profile['times_fished'] = count
        new_profile['items'] = []

        new_profile['last_fish_time'] = int(time.time()) + cd_penalty
        if bypass_fish_cd:
            new_profile['last_fish_time'] -= FISHING_COOLDOWN

        if fish:
            update_inventory(new_profile['items'], fish, count=count)

        new_profile['value'] = sum(stack['item']['value'] * stack['count'] for stack in new_profile['items'])

        list_of_profiles.append(new_profile)

    update_fish_file(list_of_profiles)

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

if __name__ == '__main__':
    my_profile_list = fishing_database()
    my_inv = my_profile_list[0]['items']
    # update_inventory(my_inv, get_fish_from_name('Salmon'), count=-3)
    update_fish_file(my_profile_list)