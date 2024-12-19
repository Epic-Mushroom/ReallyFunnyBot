from pathlib import Path
import json, time, random, os, math

FISHING_ENABLED = True

FISHING_COOLDOWN = 10
RARE_ITEM_WEIGHT_THRESHOLD = 1.62
SUPER_RARE_ITEM_WEIGHT_THRESHOLD = 0.501
TRASH_CUTOFF = 10 # for highlighting items in inventory
WEIGHT_CUTOFF = 13 # for highlighting items in inventory

FISHING_ITEMS_PATH = Path("trackers\\fishing_items.json")
FISHING_DATABASE_PATH = Path("trackers\\fishing.json")
SPECIALS_DATABASE_PATH = Path("trackers\\specials.json")
GENERAL_DATABASE_PATH = Path("trackers\\user_triggers.json")

class OnFishingCooldownError(Exception):
    pass

class MaintenanceError(Exception):
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

def switch_fishing() -> bool:
    global FISHING_ENABLED

    FISHING_ENABLED = not FISHING_ENABLED
    return FISHING_ENABLED

def random_range(start: int, stop: int) -> int:
    """random.randrange but its inclusive so i don't keep forgetting the original function has an exclusive endpoint because i have fucking dementia"""
    return random.randrange(start, stop + 1)

def to_dict(obj):
    if isinstance(obj, dict):
        data = {}
        for key, value in obj.items():
            data[key] = to_dict(value)
        return data
    elif hasattr(obj, "__dict__"):
        data = obj.__dict__.copy()
        for key, value in data.items():
            data[key] = to_dict(value)
        return data
    elif isinstance(obj, list):
        return [to_dict(item) for item in obj]
    else:
        return obj

def manipulated_weights(factor=1.0) -> list:
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

def fishing_manifesto_factor(username: str) -> float:
    list_of_profiles = fishing_database()
    x = next((profile['value'] for profile in list_of_profiles if profile['username'] == username), 0)
    m = max([profile['value'] for profile in list_of_profiles if profile['username'] != 'test_user'])

    return 21 * ((420 * x / m) + 1) ** -0.2 - 4.55

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

def add_special(username: str, special: str, count: int) -> None:
    specials_dict = specials_database()

    if count < 0:
        for user_status in specials_dict[special]:
            if user_status['username'] == username and user_status['count'] > 0:
                user_status['count'] += count
                break

    else:
        user_status = next(
            (user_status for user_status in specials_dict[special] if user_status['username'] == username),
            None)

        if user_status:
            user_status['count'] += count
        else:
            specials_dict[special].append({'username': username, 'count': count})

    update_specials_file(specials_dict)

def fish_event(username: str, is_extra_fish=False, force_fish_name=None, factor=1.0, bypass_fish_cd=False) -> str:

    def other_player_with_catfish() -> str | None:

        specials_dict = specials_database()
        catfish_list = specials_dict['catfish']

        for user_status in catfish_list:
            if user_status['username'] != original_user and user_status['count'] > 0:
                return user_status['username']

        return None

    def find_random_user_to_donate_to():
        undonatable = ['test_user', original_user]

        list_of_profiles = fishing_database()
        list_of_profiles = [profile for profile in list_of_profiles if not profile['username'] in undonatable]
        weights = [max(profile['value'], 0) ** 0.37 for profile in list_of_profiles if not profile['username'] in undonatable]

        return random.choices(list_of_profiles, weights=weights, k=1)[0]['username']

    def activate_special() -> list[str | None]:
        groups = [['catfish'],
                  ['mrbeast_fish'],
                  ['mogfish', 'fishing_manifesto', 'nemo'],
                  ['bribe_fish'],
                  ['unregistered_firearm', 'mercenary_contract']]

        user_specials = [special for special in get_active_specials(username) if special != 'catfish']
        activated_specials = []

        for n in range(len(groups)):
            for special in groups[n]:
                if special in user_specials:
                    activated_specials.append(special)
                    break

                if special == groups[n][-1]:
                    # checks if no powerups from this group was found for the user
                    activated_specials.append(None)

        if activated_specials[4] is not None:
            # force fish powerups cannot use up powerups of another kind unless it is mrbeast
            activated_specials[2] = None
            activated_specials[3] = None

        if other_player_with_catfish():
            # mrbeast fish and bribe fish cannot be used if the user is being catfished
            activated_specials[1] = None
            activated_specials[3] = None

        return activated_specials

    def handle_specials() -> None:
        nonlocal factor, force_fish_name, bribe_active, username, bypass_fish_cd
        # i should really put this into a class or something but ehhh lazy

        for active_special in active_specials:
            if active_special == 'mrbeast_fish':
                username = find_random_user_to_donate_to()
                bypass_fish_cd = True
            elif active_special == 'fishing_manifesto':
                factor = fishing_manifesto_factor(username)
            elif active_special == 'nemo':
                factor = 9.5
            elif active_special == 'mogfish':
                factor = 0.04
            elif active_special == 'mercenary_contract':
                force_fish_name = 'Mercenary Fish'
            elif active_special == 'bribe_fish':
                bribe_active = True

    def catch_count() -> int:
        random_num = random_range(1, 500)
        count = 1

        insanely_lucky = random_num <= 2 # 0.4% chance
        super_lucky = random_num <= 8 # 1.6% chance
        lucky = random_num <= 45  # 9% chance
        unlucky = random_num >= 471  # 6% chance

        if insanely_lucky:
            for j in range(4):
                count += catch_count()
        elif super_lucky:
            for j in range(2):
                count += catch_count()
        elif lucky:
            count += catch_count()
        elif unlucky:
            count -= 1

        return count

    if username != 'epicmushroom.' and FISHING_ENABLED == False:
        raise MaintenanceError

    all_users = get_all_users()
    is_test_user = username == 'test_user'
    original_user = username

    last_fish_time = get_user_last_fish_time(username)
    current_time = int(time.time())

    random_num = random_range(1, 100)

    penalty = 0

    output = "(test_user)" if is_test_user else ""

    bribe_active = False

    active_specials = activate_special()
    handle_specials()

    catfish_holder = other_player_with_catfish()
    if catfish_holder:
        username = catfish_holder
        bypass_fish_cd = True

    if is_test_user or current_time - last_fish_time >= FISHING_COOLDOWN:
        caught_fish = []
        caught_fish_count = catch_count()

        very_lucky = caught_fish_count >= 4
        lucky = caught_fish_count >= 2
        unlucky = caught_fish_count <= 0

        for j in range(caught_fish_count):
            if is_test_user:
                caught_fish.append(go_fish(factor=factor * 1.9, force_fish_name=force_fish_name))
            else:
                caught_fish.append(go_fish(factor=factor, force_fish_name=force_fish_name))

        if very_lucky:
            output += '*You caught a lot more stuff than usual*\n'
        elif lucky:
            output += '*You caught more stuff than usual*\n'
        elif unlucky:
            unlucky_messages = [
                'your line broke',
                'other than air',
                'you tripped and fell into the water',
                'you got distracted by subway surfers gameplay',
                'rng doesn\'t like you',
                'you were cursed by Eldritch beings',
                'you used gas station bait'
            ]

            update_fish_database(username, bypass_fish_cd=bypass_fish_cd)
            output += f'You caught nothing ({random.choice(unlucky_messages)})'

        for one_fish in caught_fish:
            if one_fish.weight <= SUPER_RARE_ITEM_WEIGHT_THRESHOLD:
                output += f'‼️‼️ '

            elif one_fish in rare_items:
                output += f'‼️ '

            if one_fish.name == 'Cop Fish' and not bypass_fish_cd and not bribe_active:
                penalty += random_num + 19
                output += f'You caught the Cop Fish! ({random_num + 19} seconds added to next cooldown)'
    
            elif one_fish.name == 'Catfish' and not is_test_user:
                output += f'You caught: **Catfish** (next 4 fish caught by other players will be transferred to you)'
                add_special(username, 'catfish', count=4)

            elif one_fish.name == 'Fishing Manifesto':
                output += (f'You caught: **{one_fish.name}** (next 8 fish caught by you are more likely to be rare items;'
                           f' the luck boost is more if you are lower on the leaderboard)')
                add_special(username, 'fishing_manifesto', count=8)

            elif one_fish.name == 'Mr. Beast Fish':
                output += (
                    f'You caught: **{one_fish.name}** (next 4 fish caught by you will be donated to a random player)')
                add_special(username, 'mrbeast_fish', count=4)

            elif one_fish.name == 'Mercenary Contract':
                output += f'You caught: **{one_fish.name}** (next 4 fish are guaranteed Mercenary Fish)'
                add_special(username, 'mercenary_contract', count=4)

            elif one_fish.name == 'Unregistered Firearm':
                output += f'You caught: **{one_fish.name}** (+177.6 moneys, next 3 fish are guaranteed CS:GO Fish)'
                add_special(username, 'unregistered_firearm', count=3)
    
            elif one_fish.name == 'Nemo':
                output += f'You caught: **Nemo** (next 12 fish caught by you are much more likely to be rare items)'
                add_special(username, 'nemo', count=12)

            elif one_fish.name == 'Bribe Fish':
                output += f'You caught: **{one_fish.name}** (-50 moneys, but immune to Cop Fish for next 40 fish)'
                add_special(username, 'bribe_fish', count=40)

            elif one_fish.name == 'Mogfish':
                output += f'You caught: **{one_fish.name}** (next 12 fish caught by you are nearly guaranteed to be trash items)'
                add_special(username, 'mogfish', count=12)
    
            elif one_fish.name == 'Fish Soap':
                output += f'You caught: **Fish Soap** (all items with negative value removed)'
                fish_soap(username)
    
            elif one_fish.name == 'Jonklerfish' and not is_test_user:
                penalty = random_num + 39
                output += (f'You caught the {one_fish.name}! (+{one_fish.value} moneys, everyone\'s next cooldown '
                           f'set to {penalty + FISHING_COOLDOWN} seconds)')
    
                for user in all_users:
                    update_fish_database(user, cd_penalty=penalty)
    
            elif one_fish.name == 'Mercenary Fish' and not is_test_user:
                output += f'You caught the Mercenary Fish!'
    
                for i in range(random_range(6, 7)):
                    # steal_fish_from_random also updates the thief's profile with the fish that was stolen
                    heist_tuple = steal_fish_from_random(username)
                    temp_username = heist_tuple[0]
                    stolen_fish = heist_tuple[1]
    
                    output += f'\nStole {stolen_fish.name} from {temp_username}'
    
            elif one_fish.name == 'CS:GO Fish' and not is_test_user:
                output += f'You caught: **CS:GO Fish** ('
    
                for i in range(random_range(1, 1)):
                    heist_tuple = steal_fish_from_random(username, shoot=True)
                    temp_username = heist_tuple[0]
                    stolen_fish = heist_tuple[1]
    
                    output += f'{temp_username}\'s {stolen_fish.name} was shot)'
    
            elif one_fish.name == 'Sea Bass':
                output += f'You caught: **{one_fish.name}**... no it\'s at least a C+ (worth {one_fish.value} moneys)'
    
            else:
                output += f'You caught: **{one_fish.name}** (worth {one_fish.value} moneys)'

            output += '\n'
            # just adds the fish to the user's profile without adding the cooldown
            update_fish_database(username, fish=one_fish, bypass_fish_cd=True)

    else:
        raise OnFishingCooldownError

    # adds cooldown to the user, unless the user is being catfished or donated from
    update_fish_database(username, cd_penalty=penalty, bypass_fish_cd=bypass_fish_cd)

    # uses up all specials except the catfish because it should only be used up when
    # another player fishes with the catfish active
    if caught_fish_count > 0:
        for active_special in active_specials:
            if active_special is not None:
                add_special(original_user, active_special, count=-1)

    if catfish_holder and caught_fish_count > 0:
        update_fish_database(original_user, cd_penalty=penalty, bypass_fish_cd=False)
        add_special(catfish_holder, 'catfish', count=-1)
        output += f'\n*Fish taken by {catfish_holder} (Catfish powerup)*'
    elif username != original_user:
        # this should only happen if mr beast fish is used
        update_fish_database(original_user, cd_penalty=penalty, bypass_fish_cd=False)
        output += f'\n*Fish donated to {username} (Mr. Beast powerup)*'

    return output

def go_fish(factor=1.0, force_fish_name: str=None) -> FishingItem:
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
    output: str = f"\n"

    list_of_profiles = fishing_database()

    for profile in list_of_profiles:
        if profile['username'] == username:
            output += (f"Moneys obtained: **{profile['value']}**\n"
                       f"Items caught: **{profile['times_fished']}**\n\n")

            for stack in profile['items']:
                if stack['item']['weight'] <= WEIGHT_CUTOFF:
                    output += f"**{stack['count']}x** *{stack['item']['name']}*"
                else:
                    output += f"{stack['count']}x {stack['item']['name']}"

                if profile['items'].index(stack) != len(profile['items']) - 1:
                    output += ', '
                else:
                    output += '\n'

            active_specials = get_active_specials(username)

            if len(active_specials) > 0:
                output += f'\n**Active powerups:**\n'

                specials_dict = specials_database()

                for special in active_specials:
                    for user_status in specials_dict[special]:
                        if user_status['username'] == username:
                            output += f'{user_status['count']}x {special}\n'
                            break

            return output

    return output + f"Moneys obtained: **0**\nItems caught: **0**\n\nNo fish caught"

def universal_profile_to_string() -> str:
    output: str = ''

    list_of_profiles = fishing_database()

    output += (f"Moneys obtained: **{round(sum(profile['value'] for profile in list_of_profiles if profile['username'] != 'test_user'))}**\n"
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
            if fish.weight <= WEIGHT_CUTOFF:
                output += f"**{temp_total}x** *{temp_name}*"
            else:
                output += f"{temp_total}x {temp_name}"

            if fishing_items.index(fish) != len(fishing_items) - 1:
                output += ', '

    return output


def leaderboard_string(sort_by_luck=False) -> str:
    output = ''
    index = 1
    unshown = 0

    list_of_profiles = fishing_database()

    if sort_by_luck:
        list_of_profiles = [profile for profile in list_of_profiles if profile['times_fished'] > 0]
        list_of_profiles.sort(key=lambda prof: prof['value'] / prof['times_fished'], reverse=True)
    else:
        list_of_profiles.sort(key=lambda prof: prof['value'], reverse=True)

    for profile in [profile for profile in list_of_profiles if profile['username'] != 'test_user']:
        try:
            trophy = '🥇 ' if index == 1 else '🥈 ' if index == 2 else '🥉 ' if index == 3 else ''

            if not sort_by_luck or (sort_by_luck and profile['times_fished'] >= 10):
                output += (f'{index}. {trophy}{profile['username']}: **{
                            profile['value'] if not sort_by_luck else
                            round(profile['value'] / profile['times_fished'], 2)} moneys'
                           f'{'/catch' if sort_by_luck else ''}**\n')

                index += 1
            else:
                unshown += 1

        except KeyError:
            pass
        except ZeroDivisionError:
            pass

    if unshown > 0:
        output += f'\n*{unshown} players not counted*'

    return output

def update_fish_database(username: str, fish: FishingItem=None, count=1, cd_penalty=0, bypass_fish_cd=False) -> None:
    """
    """
    list_of_profiles = fishing_database()
    user_found = False

    for profile in list_of_profiles:
        if profile['username'] == username:
            if fish:
                update_inventory(profile['items'], fish, count=count)

            profile['value'] = round(sum(stack['item']['value'] * stack['count'] for stack in profile['items']))
            profile['times_fished'] = sum(stack['count'] for stack in profile['items'])

            if not bypass_fish_cd:
                profile['last_fish_time'] = int(time.time()) + cd_penalty

            user_found = True

    if not user_found:
        new_profile = dict()
        new_profile['username'] = username
        new_profile['times_fished'] = count
        new_profile['items'] = []
        new_profile['last_fish_time'] = 0

        if not bypass_fish_cd:
            new_profile['last_fish_time'] = int(time.time()) + cd_penalty

        if fish:
            update_inventory(new_profile['items'], fish, count=count)

        new_profile['value'] = round(sum(stack['item']['value'] * stack['count'] for stack in new_profile['items']))

        list_of_profiles.append(new_profile)

    update_fish_file(list_of_profiles)

def recalculate_fish_database() -> int:
    list_of_profiles = fishing_database()
    items_changed = 0

    for profile in list_of_profiles:
        temp_inv = profile['items']

        for stack in temp_inv:
            fish_in_file = FishingItem(**stack['item'])
            fish_obj = get_fish_from_name(stack['item']['name'])

            if fish_in_file.value != fish_obj.value or fish_in_file.weight != fish_obj.weight:
                items_changed += 1

            stack['item'] = fish_obj.__dict__

    update_fish_file(list_of_profiles)
    return items_changed

def update_user_database(username: str, increment=1) -> None:
    with open(GENERAL_DATABASE_PATH, 'r+') as file:
        list_of_dicts = json.load(file)
        user_found = False

        for one_dict in list_of_dicts:
            if one_dict['username'] == username:
                user_found = True
                one_dict['value'] += increment

        if not user_found:
            new_dict = dict()
            new_dict['username'] = username
            new_dict['value'] = increment
            list_of_dicts.append(new_dict)

        file.seek(0)
        json.dump(list_of_dicts, file, indent=4)
        file.truncate()

script_directory = Path(__file__).parent.resolve()
os.chdir(script_directory)

fishing_items = initialize_fishing_items()
sort_fishing_items()
rare_items = initialize_rares()

recalculate_fish_database()

if __name__ == '__main__':
    while True:
        user_input = input()

        if user_input == 'recalc':
            print(recalculate_fish_database())
        elif user_input == 'e':
            print(fishing_manifesto_factor('jamescheung24578'))
        elif user_input == 'exit':
            break