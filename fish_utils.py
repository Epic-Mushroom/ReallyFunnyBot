from pathlib import Path
import shop_utils
import json, time, random, os, math

FISHING_ENABLED = True

FISHING_COOLDOWN = 10
RARE_ITEM_WEIGHT_THRESHOLD = 2
SUPER_RARE_ITEM_WEIGHT_THRESHOLD = 0.501
WEIGHT_CUTOFF = 13 # for highlighting items in inventory

FISHING_ITEMS_PATH = Path("values", "fishing_items.json")
FISHING_DATABASE_PATH = Path("trackers", "fishing.json")
SPECIALS_DATABASE_PATH = Path("trackers", "specials.json")
GENERAL_DATABASE_PATH = Path("trackers", "user_triggers.json")

NEGATIVES = ['trollface.png', 'Negative Jamesfish', 'Bribe Fish',
                             'Thief Fish', 'Homeless Guy\'s Underwear', 'Brawl Starfish', 'Viola',
                             'How Unfortunate']
POSITIVES = ["Anti-Cyberbullying Pocket Guide",
             "This Item Should Be Unobtainable",
             'Illegal Refund Fish',
             'Contributing Member of Society Fish',
             'Homeless Guy\'s Bank Account',
             'Clam Royale', 'Grand Piano', 'How the Tables Turn']

LIST_OF_NEW_SPECIALS = []

class OnFishingCooldownError(Exception):
    pass

class MaintenanceError(Exception):
    pass

class Profile:
    def __init__(self, username, **kwargs):
        self.username = username

        for key, value in kwargs.items():
            if key == 'items':
                stack_list = []

                for stack_dict in value:
                    temp_stack = Stack(**stack_dict)
                    stack_list.append(temp_stack)

                self.items = stack_list

            else:
                setattr(self, key, value)

    def __str__(self):
        return profile_to_string(self.username)

class Stack:
    def __init__(self, item, count=1, **kwargs):
        if isinstance(item, dict):
            self.item = FishingItem(**item)
        elif isinstance(item, FishingItem):
            self.item = item
        else:
            raise ValueError

        self.count = count

    def __str__(self):
        return f'{self.count}x {self.item.name}'

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

    rarest_cutoff_a = 15
    rarest_cutoff_b = 50 - factor * 4
    common_cutoff_a = 30
    common_cutoff_b = factor * 3

    for i in range(len(chances)):
        rarest_partition.append(fishing_items_sorted_by_weight[i])
        if sum(chances[:i + 1]) >= rarest_cutoff_a:
            break

    for i in range(len(chances))[::-1]:
        most_common_partition.append(fishing_items_sorted_by_weight[i])
        if sum(chances[i:]) >= max([common_cutoff_a, common_cutoff_b]):
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

    return 21 * ((420 * x / m) + 1) ** -0.2 - 4.45

def initialize_fishing_items() -> list[FishingItem]:
    all_da_fishies = []

    with open(FISHING_ITEMS_PATH, 'r') as file:
        list_of_fishies = json.load(file)

        for fishy in list_of_fishies:
            all_da_fishies.append(FishingItem(**fishy))

    return all_da_fishies

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

def get_user_profile(username: str):
    list_of_profiles = fishing_database()

    return next((profile for profile in list_of_profiles if profile['username'] == username), None)

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
                  ['unregistered_firearm', 'mercenary_contract'],
                  ['caffeine_bait'],
                  ['no_negative_items']]

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
            # force fish powerups cannot use up powerups of another kind unless it is mrbeast or caffeine
            activated_specials[2] = None
            activated_specials[3] = None
            activated_specials[6] = None

        if other_player_with_catfish():
            # mrbeast fish and bribe fish cannot be used if the user is being catfished
            activated_specials[1] = None
            activated_specials[3] = None

        return activated_specials

    def handle_specials() -> None:
        nonlocal factor, force_fish_name, uncatchable, caffeine_active, username, bypass_fish_cd
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
            elif active_special == 'unregistered_firearm':
                force_fish_name = 'CS:GO Fish'
            elif active_special == 'bribe_fish':
                uncatchable.append('Cop Fish')
            elif active_special == 'no_negative_items':
                uncatchable.extend(NEGATIVES)
            elif active_special == 'caffeine_bait':
                caffeine_active = True

    def handle_upgrades() -> None:
        nonlocal sffi_tiers
        active_upgrades = shop_utils.get_user_upgrades(original_user)

        for upgrade in active_upgrades:
            if upgrade.startswith("State Farm Fishing Insurance"):
                sffi_tiers += 1

    def catch_count(boost=False) -> int:
        random_num = random_range(1, 500)
        count = 1

        insanely_lucky = random_num <= 2  # 0.4% chance
        super_lucky = random_num <= 8  # 1.6% chance
        lucky = random_num <= (140 if boost else 35)  # 7% chance without boost, 28% with
        unlucky = random_num >= (471 + 10 * sffi_tiers if boost else 456 + 15 * sffi_tiers)
        # with boost: 6%, 4%, 2%, 0% for 0, 1, 2, 3 sffi tiers
        # without boost: 9%, 6%, 3%, 0% for 0, 1, 2, 3 sffi tiers

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
    
    def rare_prefix(fishing_item: FishingItem) -> str:
        result = ''
        bangbangbangbang = f'‼️‼️ '
        bangbang = f'‼️ '

        if 0 < fishing_item.weight <= SUPER_RARE_ITEM_WEIGHT_THRESHOLD:
            result = bangbangbangbang

        elif 0 < fishing_item.weight <= RARE_ITEM_WEIGHT_THRESHOLD:
            result = bangbang
            
        return result

    higher_beings = ['epicmushroom.', 'test_user', 'test_user2', 'test_user3']

    if not username in higher_beings and FISHING_ENABLED == False:
        raise MaintenanceError

    all_users = get_all_users()
    is_test_user = username == 'test_user'
    original_user = username

    last_fish_time = get_user_last_fish_time(username)
    current_time = int(time.time())

    random_num = random_range(1, 100)

    penalty = 0

    output = "(test_user)" if is_test_user else ""

    # Flags and variables for handling specials/upgrades
    uncatchable: list[str | None] = [None] # list of fish names that can't be caught
    caffeine_active = False
    sffi_tiers = 0

    active_specials = activate_special()
    handle_specials()
    handle_upgrades()

    catfish_holder = other_player_with_catfish()
    if catfish_holder:
        username = catfish_holder
        bypass_fish_cd = True

    if is_test_user or current_time - last_fish_time >= FISHING_COOLDOWN:
        caught_fish = []
        caught_fish_count = catch_count(boost=caffeine_active)

        very_lucky = caught_fish_count >= 4
        lucky = caught_fish_count >= 2
        unlucky = caught_fish_count <= 0

        for j in range(caught_fish_count):
            temp_fish = None
            temp_fish_name = None

            while temp_fish_name in uncatchable:
                if is_test_user:
                    temp_fish = go_fish(factor=factor * 1.9, force_fish_name=force_fish_name)
                else:
                    temp_fish = go_fish(factor=factor, force_fish_name=force_fish_name)

                temp_fish_name = temp_fish.name

            caught_fish.append(temp_fish)

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
                'you used gas station bait',
                'the fish grew wings and flew away'
            ]

            update_fish_database(username, bypass_fish_cd=bypass_fish_cd)
            output += f'You caught nothing ({random.choice(unlucky_messages)})'

        for one_fish in caught_fish:
            output += rare_prefix(one_fish)

            if one_fish.name == 'Cop Fish' and not bypass_fish_cd:
                penalty += random_num + 19
                output += f'You caught the Cop Fish! ({random_num + 19} seconds added to next cooldown)'
    
            elif one_fish.name == 'Catfish' and not is_test_user:
                output += f'You caught: **{one_fish.name}** (next 4 catches by other players will be transferred to you)'
                add_special(username, 'catfish', count=4)

            elif one_fish.name == 'Fishing Manifesto':
                output += (f'You caught: **{one_fish.name}** (next 8 catches by you are more likely to include rare items;' +
                           f' the luck boost is more if you are lower on the leaderboard)')
                add_special(username, 'fishing_manifesto', count=8)

            elif one_fish.name == 'Mr. Beast Fish':
                output += (
                    f'You caught: **{one_fish.name}** (next 2 catches by you will be donated to a random player)')
                add_special(username, 'mrbeast_fish', count=2)

            elif one_fish.name == 'Caffeinated Worms':
                output += (
                    f'You caught: **{one_fish.name}** (next 60 catches are more likely to reel up multiple items at once and less likely to pull zero items)')
                add_special(username, 'caffeine_bait', count=60)

            elif one_fish.name == 'Mercenary Contract':
                output += f'You caught: **{one_fish.name}** (next 4 catches are guaranteed to include Mercenary Fish)'
                add_special(username, 'mercenary_contract', count=4)

            elif one_fish.name == 'Unregistered Firearm':
                output += f'You caught: **{one_fish.name}** (+177.6 moneys, next 3 catches are guaranteed to include CS:GO Fish)'
                add_special(username, 'unregistered_firearm', count=3)
    
            elif one_fish.name == 'Nemo':
                output += f'You caught: **{one_fish.name}** (next 12 catches by you are much more likely to include rare items)'
                add_special(username, 'nemo', count=12)

            elif one_fish.name == 'Bribe Fish':
                output += f'You caught: **{one_fish.name}** (-50 moneys, but immune to Cop Fish for next 40 catches)'
                add_special(username, 'bribe_fish', count=40)

            elif one_fish.name == 'Mogfish':
                output += f'You caught: **{one_fish.name}** (next 12 catches by you are nearly guaranteed to include trash items)'
                add_special(username, 'mogfish', count=12)
    
            elif one_fish.name == 'Fish Soap':
                output += f'You caught: **{one_fish.name}** (all items with negative value in your inventory removed)'
                fish_soap(username)

            elif one_fish.name == 'Absolute Value Fish':
                output += f'You caught: **{one_fish.name}** (all items with negative value turned to positive value)'
                fish_soap(username, absolute=True)

            elif one_fish.name == 'Security Guard Fish':
                output += f'You caught: **{one_fish.name}** (this item is literally unobtainable)'
                add_special(username, 'no_negative_items', count=1)
    
            elif one_fish.name == 'Jonklerfish' and not is_test_user:
                penalty = random_num + 39
                output += (f'You caught the {one_fish.name}! (+{one_fish.value} moneys, everyone\'s next cooldown ' +
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
    
                    output += f'\nStole {rare_prefix(stolen_fish)}**{stolen_fish.name}** from {temp_username}'
    
            elif one_fish.name == 'CS:GO Fish' and not is_test_user:
                output += f'You caught: **CS:GO Fish** ('
    
                for i in range(random_range(1, 1)):
                    heist_tuple = steal_fish_from_random(username, shoot=True)
                    temp_username = heist_tuple[0]
                    stolen_fish = heist_tuple[1]
    
                    output += f'{temp_username}\'s {rare_prefix(stolen_fish)}**{stolen_fish.name}** was shot)'
    
            elif one_fish.name == 'Sea Bass':
                output += f'You caught: **{one_fish.name}**... no it\'s at least a C+ (worth {one_fish.value} moneys)'
    
            else:
                output += f'You caught: **{one_fish.name}** (worth {one_fish.value} moneys)'

            output += '\n'
            # just adds the fish to the user's profile without adding the cooldown
            update_fish_database(username, fish=one_fish, bypass_fish_cd=True)

    else:
        raise OnFishingCooldownError

    # adds cooldown to the user, unless the user is being catfished or have donated
    update_fish_database(username, cd_penalty=penalty, bypass_fish_cd=bypass_fish_cd)

    # uses up all specials except the catfish because it should only be used up when
    # another player fishes with the catfish active
    if caught_fish_count > 0:
        for active_special in active_specials:
            if active_special is not None:
                add_special(original_user, active_special, count=-1)

    # adds cooldown to the original user if they are being catfished or have donated
    if username != original_user:
        if caught_fish_count > 0:
            if catfish_holder:
                add_special(catfish_holder, 'catfish', count=-1)
                output += f'\n*Fish taken by {catfish_holder} (Catfish powerup)*'
            else:
                output += f'\n*Fish donated to {username} (Mr. Beast powerup)*'

        update_fish_database(original_user, cd_penalty=penalty, bypass_fish_cd=False)

    return output

def go_fish(factor=1.0, force_fish_name: str=None) -> FishingItem:
    weights = manipulated_weights(factor=factor)
    fishing_items_sorted_by_weight = sorted(fishing_items, key=lambda item: item.weight)

    if not force_fish_name:
        return random.choices(fishing_items_sorted_by_weight, weights=weights, k=1)[0]
    else:
        force_fish = [fish for fish in fishing_items if fish.name == force_fish_name][0]
        return force_fish

def fish_soap(username: str, absolute=False):
    list_of_profiles = fishing_database()

    for profile in list_of_profiles:
        if profile['username'] == username:
            # copy used to prevent modifying the list while iterating through it
            player_inv = profile['items']
            p_inv_copy = player_inv[:]

            if absolute:
                for stack in p_inv_copy:
                    if stack['item']['name'] in NEGATIVES:
                        temp_index = NEGATIVES.index(stack['item']['name'])
                        update_inventory(player_inv, fish=get_fish_from_name(POSITIVES[temp_index]), count=stack['count'])

            profile['items'] = [stack for stack in player_inv if stack['item']['value'] >= 0]

    update_fish_file(list_of_profiles)

def steal_fish_from_random(thief_name: str, shoot=False) -> tuple[str, FishingItem]:
    list_of_profiles = fishing_database()

    while True:
        weights = [profile['value'] for profile in list_of_profiles]
        player_profile = random.choices(list_of_profiles, weights=weights, k=1)[0]
        player_inv = player_profile['items']
        player_name = player_profile['username']

        if (player_name != thief_name or shoot) and player_name != 'test_user':
            break

    weights = [max(stack['count'], 0) for stack in player_inv]
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
            # print(stack['count'])
            item_found = True

    if not item_found:
        stack = dict()
        stack['item'] = fish.__dict__
        stack['count'] = count

        inventory.append(stack)

    sort_inventory_by_value(inventory)

def sort_inventory_by_value(inventory: list[dict]):
    inventory.sort(key=lambda stack: stack['item']['value'], reverse=True)
    # print(inventory[0]['count'])

def sort_fishing_items_by_value():
    with open(FISHING_ITEMS_PATH, 'r+') as file:
        items = json.load(file)
        items.sort(key=lambda fish: fish['value'], reverse=True)

        file.seek(0)
        json.dump(items, file, indent=4)
        file.truncate()

def sort_fishing_items_by_weight():
    with open(FISHING_ITEMS_PATH, 'r+') as file:
        items = json.load(file)
        items.sort(key=lambda fish: fish['weight'])

        file.seek(0)
        json.dump(items, file, indent=4)
        file.truncate()

def profile_to_string(username: str) -> str:
    output: str = f"\n"

    list_of_profiles = fishing_database()

    for profile in list_of_profiles:
        if profile['username'] == username:
            output += (f"Moneys obtained: **{profile['value']}**\n" +
                       f"Items caught: **{profile['times_fished']}**\n\n")

            display_stacks = [stack for stack in profile['items'] if stack['item']['name'] != 'Credit']

            for stack in display_stacks:
                if stack['item']['weight'] <= WEIGHT_CUTOFF:
                    output += f"**{stack['count']}x** *{stack['item']['name']}*"
                else:
                    output += f"{stack['count']}x {stack['item']['name']}"

                if display_stacks.index(stack) != len(display_stacks) - 1:
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

            output += '\n'

            if len(profile['upgrades']) > 0:
                output += '**Upgrades purchased:**\n'

                for upgrade in profile['upgrades']:
                    output += f'{upgrade}\n'
            else:
                output += '*No upgrades purchased*\n'

            return output

    return output + f"Moneys obtained: **0**\nItems caught: **0**\n\nNo fish caught"

def universal_profile_to_string() -> str:
    output: str = ''

    list_of_profiles = fishing_database()

    output += (f"Moneys obtained: **{round(sum(profile['value'] for profile in list_of_profiles if profile['username'] != 'test_user'))}**\n" +
               f"Items caught: **{sum(profile['times_fished'] for profile in list_of_profiles if profile['username'] != 'test_user')}*" +
               f"*\n\n")

    fishing_items_sorted_by_value = sorted(fishing_items, key=lambda item: item.value, reverse=True)
    display_items = [item for item in fishing_items_sorted_by_value if item.name != 'Credit']

    for fish in display_items:
        temp_name = fish.name
        temp_total = 0

        if fish.name != 'Credit':
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
                # print(display_items.index(fish))
                if display_items.index(fish) != len(display_items) - 1:
                    output += ', '

    return output


def leaderboard_string(sort_by_luck=False) -> str:
    output = ''
    index = 1
    unshown = 0

    list_of_profiles = fishing_database()
    list_of_profiles = [profile for profile in list_of_profiles if profile['times_fished'] > 0]

    if sort_by_luck:
        # you'll be horizontally scrolling for years to see the end of this next line                                                                                                   ok maybe not that much
        list_of_profiles.sort(key=lambda prof: sum([stack['count'] * stack['item']['value'] for stack in prof['items'] if stack['item']['name'] != 'Credit']) / prof['times_fished'], reverse=True)
    else:
        list_of_profiles.sort(key=lambda prof: prof['value'], reverse=True)

    for profile in [profile for profile in list_of_profiles if profile['username'] != 'test_user']:
        try:
            trophy = '🥇 ' if index == 1 else '🥈 ' if index == 2 else '🥉 ' if index == 3 else ''

            more_accurate_val = profile['value'] if not sort_by_luck else sum([stack['count'] * stack['item']['value'] for stack in profile['items'] if stack['item']['name'] != 'Credit'])

            if not sort_by_luck or profile['times_fished'] >= 10:
                output += (f'{index}. {trophy}{profile['username']}: **{(more_accurate_val if not sort_by_luck else round(more_accurate_val / profile['times_fished'], 2))} '
                           f'moneys{'/catch' if sort_by_luck else ''}**\n')

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
            profile['times_fished'] = sum(stack['count'] for stack in profile['items'] if stack['item']['name'] != 'Credit')

            if not bypass_fish_cd:
                profile['last_fish_time'] = int(time.time()) + cd_penalty

            user_found = True

    if not user_found:
        new_profile = dict()
        new_profile['username'] = username
        new_profile['times_fished'] = count
        new_profile['items'] = []
        new_profile['upgrades'] = []
        new_profile['last_fish_time'] = 0

        if not bypass_fish_cd:
            new_profile['last_fish_time'] = int(time.time()) + cd_penalty

        if fish:
            update_inventory(new_profile['items'], fish, count=count)

        new_profile['value'] = round(sum(stack['item']['value'] * stack['count'] for stack in new_profile['items']))

        list_of_profiles.append(new_profile)

    update_fish_file(list_of_profiles)

def recalculate_fish_database() -> int:
    """
    Modifies value/weights of fish already in fishing.json to reflect those in fishing_items.json
    Also adds the upgrades key/value pair to profiles without it
    """
    list_of_profiles = fishing_database()
    items_changed = 0

    for profile in list_of_profiles:
        temp_inv = profile['items']

        if not 'upgrades' in profile.keys():
            profile['upgrades'] = []

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

def _add_new_specials():
    specials_dict = specials_database()
    added = []

    for spec in LIST_OF_NEW_SPECIALS:
        if not spec in specials_dict.keys():
            specials_dict[spec] = []
            added.append(spec)

    update_specials_file(specials_dict)
    return added

script_directory = Path(__file__).parent.resolve()
os.chdir(script_directory)

sort_fishing_items_by_weight()
fishing_items = initialize_fishing_items()

recalculate_fish_database()
_add_new_specials()

test_file = None
try:
    test_file = open(Path("testing", "test_file.txt"))
    FISHING_ENABLED = False
except FileNotFoundError:
    FISHING_ENABLED = True
finally:
    if test_file:
        test_file.close()

if __name__ == '__main__':
    while True:
        user_input = input()
        iterations = 1

        if user_input == 'recalc':
            print(recalculate_fish_database())
        elif user_input == 'j':
            print(fishing_manifesto_factor('paliopolis'))
        elif user_input == 'e':
            print(fishing_manifesto_factor('epicmushroom.'))
        elif user_input == 'proftest':
            print(Profile(**get_user_profile('epicmushroom.')))
        elif user_input.startswith('>fishtest'):
            parts = user_input.split(' ')

            if len(parts) > 1:
                iterations = int(parts[1])

            for i in range(iterations):
                print(fish_event('test_user2'))

        elif user_input == 'exit':
            break