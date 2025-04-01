from pathlib import Path
from string_utils import seconds_to_descriptive_time as format_seconds
import shop_utils
import json, time, random, os, math

FISHING_ENABLED = True

FISHING_COOLDOWN = 10
RARE_ITEM_WEIGHT_THRESHOLD = 1.8
SUPER_RARE_ITEM_WEIGHT_THRESHOLD = 0.501
WEIGHT_CUTOFF = 13 # for highlighting items in inventory

FISHING_ITEMS_PATH = Path("values", "fishing_items.json")
FISHING_DATABASE_PATH = Path("trackers", "fishing.json")
SPECIALS_DATABASE_PATH = Path("trackers", "specials.json")
GENERAL_DATABASE_PATH = Path("trackers", "user_triggers.json")

BLUE_WHALE_CAP = 20
CATFISH_CAP = 9

HIGHER_BEINGS = ['epicmushroom.', 'test_user', 'test_user2', 'test_user3', 'joker_from_persona_5', 'bill_nye', 'hi_guys', 'welcome_back_to_my_yt_channel']

NEGATIVES = ['trollface.png', 'Negative Jamesfish', 'Bribe Fish',
                             'Thief Fish', 'Homeless Guy\'s Underwear', 'Brawl Starfish', 'Viola',
                             'How Unfortunate']
POSITIVES = ["Anti-Cyberbullying Pocket Guide",
             "This Item Should Be Unobtainable",
             'Illegal Refund Fish',
             'Contributing Member of Society Fish',
             'Homeless Guy\'s Bank Account',
             'Clam Royale', 'Grand Piano', 'How the Tables Turn']
SHINY_ITEMS = ['Rainbow Crystal Meth', 'Diamond Juice Box Peel', 'Shiny Jadenfish', 'Blue Crystal Meth', 'Midasfish', "KSI - Thick of It Vinyl Record",
               'Gold Goldfish', 'Golden Juice Box Peel', 'Brawl Starfish', 'Goldfish', 'Soda Can']
DRUG_ITEMS = ["Adderall (1840 Limited Edition)", "Blue Crystal Meth",
              "Caffeinated Worms", "P-Wing Boys Bathroom Cocaine", "Seaweed"]
UNDESIRABLES = ["Mogfish", "Astro Gruel", "Mr. Beast Fish"]

LIST_OF_NEW_SPECIALS = []

class OnFishingCooldownError(Exception):
    pass

class MaintenanceError(Exception):
    pass

class Profile:
    def __init__(self, username, wordle_wins = 0, wordle_losses = 0, wordle_points = 0, bj_games_played = 0, moneys_lost_to_gambling = 0, next_fish_time = 0, new_moneys = 0, new_catches = 0,
                 items = None, specials = None, upgrades = None, banned_until = 0, ban_reason = "", **kwargs):
        self.username = username
        self.wordle_wins = wordle_wins
        self.wordle_losses = wordle_losses
        self.wordle_points = wordle_points

        self.bj_games_played = bj_games_played
        self.moneys_lost_to_gambling = moneys_lost_to_gambling

        self.next_fish_time = next_fish_time
        self.new_moneys = new_moneys
        self.new_catches = new_catches
        self.items = items if items is not None else []
        self.specials = specials if specials is not None else dict()
        self.upgrades = upgrades if upgrades is not None else []

        self.banned_until = banned_until
        self.ban_reason = ban_reason

        if len(self.items) > 0 and isinstance(items[-1], dict):
            stack_list = []

            for stack_dict in self.items:
                temp_stack = Stack(**stack_dict)
                stack_list.append(temp_stack)

            self.items = stack_list

        for key, value in kwargs.items():
            if key not in ['times_fished', 'value']:
                setattr(self, key, value)

    def __str__(self):
        output: str = f"\n"
        output += (f"Moneys obtained: **{self.value():,}**\n" +
                   f"Items caught: **{self.items_caught():,}**\n\n")

        display_stacks = [stack for stack in self.items if stack.item.name != 'Credit' and stack.count > 0]
        # display_stacks.sort(key=lambda s: s.count * s.item.value, reverse=True)

        output += '**Items:**\n' if len(display_stacks) > 0 else ''

        for stack in display_stacks:
            if stack.item.weight <= WEIGHT_CUTOFF:
                output += f"**{stack.count:,}x** *{stack.item.name}*"
            else:
                output += f"{stack.count:,}x {stack.item.name}"

            if display_stacks.index(stack) != len(display_stacks) - 1:
                output += ', '
            else:
                output += '\n'

        active_specials = self.get_active_specials()
        if len(active_specials) > 0:
            output += f'\n**Active powerups:**\n'

            for special in active_specials:
                output += f'{self.specials[special]:,}x {special}\n'

        output += '\n'

        if len(self.upgrades) > 0:
            output += '**Upgrades purchased:**\n'

            for upgrade in self.upgrades:
                output += f'{upgrade}\n'
        else:
            output += '*No upgrades purchased*\n'

        output += '\n'
        output += f'**Moneys lost to gambling:** {self.moneys_lost_to_gambling:,}\n'

        if self.bj_games_played > 0:
            output += f'**Blackjack games played:** {self.bj_games_played:,}\n'

        if self.wordle_losses + self.wordle_wins > 0:
            output += '\n'
            output += f'**Wordle points:** {self.wordle_points:,}\n'

            wordle_wl = self.get_win_loss_ratio()
            if wordle_wl < 6969696969:
                output += f'**Wordle win/loss ratio:** {wordle_wl:.2f}\n'

            else:
                output += f'**Wordle win/loss ratio:** N/A\n'

        return output

    def add_cd(self, amount=FISHING_COOLDOWN):
        self.next_fish_time = time.time() + amount

    def add_fish(self, fish, count=1):
        fish_stack = next((stack for stack in self.items if stack.item.name == fish.name), None)

        if fish_stack is None:
            self.items.append(Stack(fish, count))
        else:
            fish_stack.count += count

        self.sort_items_by_value()

    def add_special(self, special, count=1):
        if special in self.specials.keys():
            self.specials[special] += count
        else:
            self.specials[special] = max(count, 0)

    def get_active_specials(self):
        return [key for key in self.specials.keys() if self.specials[key] > 0]

    def sort_items_by_value(self):
        self.items.sort(key=lambda stack: stack.item.value, reverse=True)

    def value(self):
        return round(sum(stack.item.value * stack.count for stack in self.items))

    def items_caught(self):
        return sum(stack.count for stack in self.items if stack.item.name != 'Credit')

    def on_cooldown(self) -> bool:
        return time.time() < self.next_fish_time

    def is_banned(self) -> bool:
        return time.time() < self.banned_until

    def ban(self, duration: int=60, reason="") -> int | float:
        self.banned_until = time.time() + duration
        self.ban_reason = reason

        self.next_fish_time += duration

        return self.banned_until

    def unban(self):
        self.next_fish_time -= (self.banned_until - time.time())

        self.banned_until = 0
        self.ban_reason = ""

    def get_win_loss_ratio(self):
        try:
            return self.wordle_wins / self.wordle_losses

        except ZeroDivisionError:
            return 6969696969

    def get_wordle_elo(self):
        return self.wordle_points / (self.wordle_wins + self.wordle_losses)

class AllProfiles:
    LB_BANNED = ['test_user', 'test_user2', 'StickyBot', 'Reminder', 'ReallyFunnyBotTEST']

    def __init__(self):
        list_of_profiles = fishing_database()

        self.profiles = [Profile(**pf) for pf in list_of_profiles]
        self.real_profiles = [pf for pf in self.profiles if not pf.username in AllProfiles.LB_BANNED]

        for pf in self.profiles:
            pf.upgrades.sort()

    def profile_from_name(self, username) -> Profile:
        return next((pf for pf in self.profiles if pf.username == username), None)

    def add_new_profile(self, profile: Profile):
        self.profiles.append(profile)
        self.real_profiles = [pf for pf in self.profiles if not pf.username in AllProfiles.LB_BANNED]

    def house_profits(self):
        return sum(pf.moneys_lost_to_gambling for pf in self.real_profiles)

    def write_data(self):
        update_fish_file(to_dict(self.profiles))

    def fish_obtained(self, fish):
        for pf in self.real_profiles:
            for stack in pf.items:
                if stack.item.name == fish.name:
                    return True

        return False

    def __str__(self):
        output = (f"Moneys obtained: **{round(sum(profile.value() for profile in self.real_profiles)):,}**\n" +
               f"Items caught: **{sum(profile.items_caught() for profile in self.real_profiles):,}*" +
               f"*\n\n")

        fishing_items_sorted_by_value = sorted(fishing_items, key=lambda item: item.value, reverse=True)
        display_items = [item for item in fishing_items_sorted_by_value if item.name != 'Credit' and self.fish_obtained(item)]

        for fish in display_items:
            temp_name = fish.name
            temp_total = 0

            for profile in self.real_profiles:
                for stack in profile.items:
                    if stack.item.name == temp_name:
                        temp_total += stack.count

            if temp_total > 0:
                if fish.weight <= WEIGHT_CUTOFF:
                    output += f"**{temp_total:,}x** *{temp_name}*"
                else:
                    output += f"{temp_total:,}x {temp_name}"
                if display_items.index(fish) != len(display_items) - 1:
                    output += ', '

        return output

class Stack:
    def __init__(self, item, count=1):
        if isinstance(item, dict):
            self.item = FishingItem(**item)
        elif isinstance(item, FishingItem):
            self.item = item
        else:
            raise ValueError

        self.count = count

    def __str__(self):
        return f'{self.count:,}x {self.item.name}'

class FishingItem:
    def __init__(self, name, value, weight, **kwargs):
        self.name = name
        self.value = value
        self.weight = weight

        self.effective_value = self.value

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return self.name

class FishEvent:
    ...

def switch_fishing() -> bool:
    global FISHING_ENABLED

    FISHING_ENABLED = not FISHING_ENABLED
    return FISHING_ENABLED

def random_range(start: int, stop: int) -> int:
    """random.randrange but it's inclusive"""
    return random.randrange(start, stop + 1)

def to_dict(obj):
    if isinstance(obj, dict):
        data = dict()
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

def percent_increase_to_factor(pc_inc=0) -> float:
    return 1.0082 ** pc_inc

def factor_to_percent_increase(factor=1) -> float:
    return math.log(factor, 1.0082)

def manipulated_weights(factor=1.0, uncatchable=None) -> list:
    if uncatchable is None:
        uncatchable = []

    fishing_items_sorted_by_weight = sorted([item for item in fishing_items if item.name not in uncatchable], key=lambda item: item.weight)
    weights = [fish.weight for fish in fishing_items_sorted_by_weight]
    weight_sum = sum(weights)
    chances = [(100 * weight / weight_sum) for weight in weights]

    rarest_partition = []
    most_common_partition = []

    rarest_cutoff = 15
    common_cutoff_a = 30
    common_cutoff_b = factor * 3

    for i in range(len(chances)):
        rarest_partition.append(fishing_items_sorted_by_weight[i])
        if sum(chances[:i + 1]) >= rarest_cutoff:
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

    return modified_weights

def fishing_manifesto_factor(username: str) -> float:
    pf = all_pfs.profile_from_name(username)
    x_ = max(pf.value(), 0) if pf is not None else 0
    m_ = max(profile.value() for profile in all_pfs.real_profiles)
    old_formula = 21 * ((420 * x_ / m_) + 1) ** -0.2 - 4.45
    new_formula = percent_increase_to_factor(500 * ((420 * x_ / m_) + 1) ** -0.2 - 70)

    return new_formula

def initialize_fishing_items() -> list[FishingItem]:
    result = []

    with open(FISHING_ITEMS_PATH, 'r') as file:
        list_of_fish_items = json.load(file)

        for fishy in list_of_fish_items:
            result.append(FishingItem(**fishy))

    return result

def get_fish_from_name(name: str):
    return next((fish for fish in fishing_items if fish.name == name), None)

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
    pf = all_pfs.profile_from_name(username)
    active_specials_ = [key for key in pf.specials.keys() if pf.specials[key] > 0]

    return active_specials_

def fish_event(username: str, force_fish_name = None, factor=1.0, bypass_fish_cd=False) -> str:

    def other_profile_with_taxation() -> Profile | None:
        pass

    def other_profile_with_catfish() -> Profile | None:
        return None if catfish_immunity else next((prof for prof in all_pfs.real_profiles if 'catfish' in prof.specials.keys() and prof.specials['catfish'] > 0 and prof.username != original_user), None)

    def find_random_user_to_donate_to() -> Profile:
        usable_profiles = [prof for prof in all_pfs.real_profiles if prof.username != original_user]
        weights_ = [max(prof.value(), 0) ** 0.37 for prof in usable_profiles]

        return random.choices(usable_profiles, weights=weights_, k=1)[0]

    def activate_special() -> list[str | None]:
        groups = [['catfish', 'tax_collector'], # not used when the user is fishing, only when other users are fishing
                  ['mrbeast_fish'], # fish transfers from user to other players
                  ['mogfish', 'fishing_manifesto', 'luck_boost'], # changes factor
                  ['bribe_fish'], # puts Cop Fish in uncatchable
                  ['unregistered_firearm', 'mercenary_contract', 'testing_only'], # forces a fish item
                  ['caffeine_bait'], # makes it more likely to catch multiple items
                  ['no_negative_items'], # i wonder what this does
                  ['double_items'], # i wonder what this does
                  ['8x_items'],
                  ['midasfish', 'drug_magnet'], # x% chance to get items from a group of items
                  ['curse'],
                  ['astro_gruel', 'astro_fuel']] # modifies cooldown

        user_specials = get_active_specials(username)
        activated_specials = []

        for n in range(len(groups)):
            for special in groups[n]:
                if special in user_specials:
                    activated_specials.append(special)
                    break

                if special == groups[n][-1]:
                    # checks if no powerups from this group was found for the user
                    activated_specials.append(None)

        # catfish and similar powerups cannot be used up when its holder is the one fishing
        activated_specials[0] = None

        if activated_specials[10] is not None:
            # curse cannot use up mrbeast
            activated_specials[1] = None

        if force_fish_name is not None:
            # if force_fish_name is passed as not None, no powerups shall be used up
            activated_specials = [None] * len(activated_specials)

        if activated_specials[4] is not None:
            # force fish powerups cannot use up powerups of another kind that modify the type of item produced
            activated_specials[2] = None
            activated_specials[3] = None
            activated_specials[6] = None
            activated_specials[9] = None

        if other_profile_with_catfish():
            # mrbeast fish, bribe fish, and curse cannot be used if the user is being catfished
            activated_specials[1] = None
            activated_specials[3] = None
            activated_specials[10] = None

        return activated_specials

    def handle_specials() -> None:
        nonlocal cd, factor, force_fish_name, caffeine_active, pf, bypass_fish_cd, double_items, midas_active, octuple_items, drug_magnet_active, curse_active

        for active_special in active_specials:
            if active_special == 'mrbeast_fish':
                pf = find_random_user_to_donate_to()
                bypass_fish_cd = True
            elif active_special == 'fishing_manifesto':
                factor = fishing_manifesto_factor(original_pf.username)
            elif active_special == 'luck_boost':
                factor = percent_increase_to_factor(167)
            elif active_special == 'mogfish':
                factor = 0.04
            elif active_special == 'mercenary_contract':
                force_fish_name = 'Mercenary Fish'
            elif active_special == 'unregistered_firearm':
                force_fish_name = 'CS:GO Fish'
            elif active_special == 'testing_only':
                force_fish_name = random.choice(['Blue Whale'])
            elif active_special == 'midasfish':
                midas_active = True
            elif active_special == 'drug_magnet':
                drug_magnet_active = True
            elif active_special == 'curse':
                curse_active = True
            elif active_special == 'bribe_fish':
                uncatchable.append('Cop Fish')
            elif active_special == 'no_negative_items':
                uncatchable.extend(NEGATIVES)
            elif active_special == 'caffeine_bait':
                caffeine_active = True
            elif active_special == 'double_items':
                double_items = True
            elif active_special == '8x_items':
                octuple_items = True
            elif active_special == 'astro_gruel':
                cd *= 2
            elif active_special == 'astro_fuel':
                cd = 1

    def handle_upgrades() -> None:
        nonlocal sffi_tiers, double_mercenary, octuple_items, ml_tiers
        active_upgrades = shop_utils.get_user_upgrades(original_user)

        for upgrade in active_upgrades:
            if upgrade.startswith("State Farm Fishing Insurance"):
                sffi_tiers += 1
            elif upgrade.startswith("Money Laundering"):
                ml_tiers += 1

        if "Espionage Tactics Book" in active_upgrades:
            double_mercenary = True

        if "Supreme Joblessness Trophy" in active_upgrades:
            octuple_items = True

    def catch_count(boost=False) -> int:
        random_num = random_range(1, 500)
        count = 1

        insanely_lucky = random_num <= 2  # 0.4% chance
        super_lucky = random_num <= 8  # 1.6% chance
        lucky = random_num <= (140 if boost else 35)  # 7% chance without boost, 28% with
        if curse_active:
            unlucky = random_num >= (301 + 25 * sffi_tiers if boost else 251 + 25 * sffi_tiers)
            # with boost: 40%, 35%, 30%, 25% for 0, 1, 2, 3 sffi tiers
            # without boost: 50%, 45%, 40%, 35% for 0, 1, 2, 3 sffi tiers
        else:
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
            count -= 999 if curse_active else 1

        return max(count, 0)
    
    def rare_prefix(fishing_item: FishingItem) -> str:
        result = ''
        bangbangbangbang = f'‼️‼️ '
        bangbang = f'‼️ '

        if 0 < fishing_item.weight <= SUPER_RARE_ITEM_WEIGHT_THRESHOLD:
            result = bangbangbangbang

        elif 0 < fishing_item.weight <= RARE_ITEM_WEIGHT_THRESHOLD:
            result = bangbang
            
        return result

    if not username in HIGHER_BEINGS and FISHING_ENABLED == False:
        raise MaintenanceError

    pf = all_pfs.profile_from_name(username)
    if pf is None:
        pf = Profile(username)
        all_pfs.add_new_profile(pf)

    all_users = get_all_users()
    original_user = username
    original_pf = pf

    next_fish_time = pf.next_fish_time
    old_value = pf.value() # to determine new luck lb stats

    cd = FISHING_COOLDOWN
    penalty = 0
    stolen_amt = 0
    money_laundered = False
    eldritch_beings_caught = False

    output = ""

    # Flags and variables for handling specials/upgrades
    uncatchable: list[str | None] = [] # list of fish names that can't be caught
    caffeine_active = False
    midas_active = False
    drug_magnet_active = False
    curse_active = False
    double_items = False
    octuple_items = False
    double_mercenary = False
    catfish_immunity = True if force_fish_name is not None else False # automatic catfish immunity if force_fish_name is being passed as not None
    mrbeast_immunity = False
    sffi_tiers = 0
    ml_tiers = 0

    active_specials = activate_special()
    handle_specials()
    handle_upgrades()

    tax_collector = other_profile_with_taxation()

    catfish_holder_pf = other_profile_with_catfish()
    if catfish_holder_pf:
        # user cannot pay taxes if another player has catfish active, other players with catfish
        # will also take priority over paying taxes
        tax_collector = None
        pf = catfish_holder_pf
        bypass_fish_cd = True

    # caps catfish at CATFISH_CAP
    if 'catfish' in pf.get_active_specials() and pf.specials['catfish'] > CATFISH_CAP - 3:
        uncatchable.append('Catfish')

    if original_pf.is_banned():
        return f"You're banned from fishing for {format_seconds(original_pf.banned_until - time.time())}. Reason: {original_pf.ban_reason}"

    elif original_pf.on_cooldown():
        return f"You're on fishing cooldown ({format_seconds(next_fish_time - time.time(), True)} until you can fish again)"

    else:
        caught_fish = []
        caught_fish_count = catch_count(boost=caffeine_active)

        very_lucky = caught_fish_count >= 4
        lucky = caught_fish_count >= 2
        unlucky = caught_fish_count <= 0

        caught_fish_count *= 2 if double_items else 1
        caught_fish_count *= 8 if octuple_items else 1

        for j in range(caught_fish_count):
            temp_fish = go_fish(factor=factor, force_fish_name=force_fish_name, uncatchable=uncatchable)

            if midas_active:
                # Will override the original fish
                if random_range(1, 100) <= 25:
                    temp_fish = get_fish_from_name(random.choice(SHINY_ITEMS))
            elif drug_magnet_active:
                if random_range(1, 100) <= 33:
                    temp_fish = get_fish_from_name(random.choice(DRUG_ITEMS))

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

            chosen_msg = random.choice(unlucky_messages) if not curse_active else '**you were cursed by Eldritch beings**'
            output += f'You caught nothing ({chosen_msg})\n'

        for one_fish in caught_fish:
            output += rare_prefix(one_fish)
            output += '⭐ First catch! ' if one_fish.value >= 0 and not all_pfs.fish_obtained(one_fish) else ''

            if one_fish.name == 'Cop Fish' and not bypass_fish_cd:
                temp_rand = random_range(19, 119)
                penalty += temp_rand
                output += f'You caught: **{one_fish.name}** (next cooldown increased to {cd + penalty} seconds)'

            elif one_fish.name == 'Reminder to Go Outside' and not bypass_fish_cd:
                penalty += 1800 - cd
                output += f'You caught: **{one_fish.name}** (+{one_fish.value:,} moneys, can\'t fish for 30 minutes)'

            elif one_fish.name == 'Catfish':
                output += f'You caught: **{one_fish.name}** (next 3 catches by other players will be transferred to you)'
                pf.add_special('catfish', count=3)

            elif one_fish.name == 'Fishing Manifesto':
                output += (f'You caught: **{one_fish.name}** (next 8 catches by you are more likely to include rare items;' +
                           f' the luck boost is more the farther you are from #1 on the leaderboard)')
                pf.add_special('fishing_manifesto', count=8)

            elif one_fish.name == 'Mr. Beast Fish':
                output += (
                    f'You caught: **{one_fish.name}** (next 2 catches by you will be donated to a random player)')
                pf.add_special('mrbeast_fish', count=2)

            elif one_fish.name == 'Eldritch Beings':
                output += (
                    f'You caught: **{one_fish.name}** (cursed for 6 catches)')
                original_pf.add_special('curse', count=6)
                eldritch_beings_caught = True

            elif one_fish.name == 'Caffeinated Worms':
                output += (
                    f'You caught: **{one_fish.name}** (next 60 catches are more likely to reel up multiple items at once and less likely to pull zero items)')
                pf.add_special('caffeine_bait', count=60)

            elif one_fish.name == 'Mercenary Contract':
                output += f'You caught: **{one_fish.name}** (next 3 catches are guaranteed to include Mercenary Fish)'
                pf.add_special('mercenary_contract', count=3)

            elif one_fish.name == 'Astro Gruel':
                output += f'You caught: **{one_fish.name}** (cooldown doubled for next 5 catches)'
                pf.add_special('astro_gruel', count=5)

            elif one_fish.name == 'Astro Fuel':
                output += f'You caught: **{one_fish.name}** (cooldown set to 1 second for next 7 catches)'
                pf.add_special('astro_fuel', count=7)

            elif one_fish.name == 'Unregistered Firearm':
                output += f'You caught: **{one_fish.name}** (+177.6 moneys, next 3 catches are guaranteed to include CS:GO Fish)'
                pf.add_special('unregistered_firearm', count=3)
    
            elif one_fish.name == 'Nemo':
                output += f'You caught: **{one_fish.name}** (next 12 catches by you are much more likely to include rare items)'
                pf.add_special('luck_boost', count=12)

            elif one_fish.name == 'Midasfish':
                output += f'You caught: **{one_fish.name}** (next catch is more likely to include a "shiny" item)'
                pf.add_special('midasfish', count=1)

            elif one_fish.name == 'Russia':
                output += f'You caught: **{one_fish.name}** (+{one_fish.value} moneys, next 2 catches are more likely to include a "drug" item)'
                pf.add_special('drug_magnet', count=2)

            elif one_fish.name == 'Blue Whale':
                output += f'You caught: **{one_fish.name}** (everyone\'s next catch is much more likely to include rare items)'

                for prof in all_pfs.profiles:
                    if not ('luck_boost' in prof.get_active_specials() and prof.specials['luck_boost'] >= BLUE_WHALE_CAP):
                        prof.add_special('luck_boost', count=1)

            elif one_fish.name == 'Bribe Fish':
                output += f'You caught: **{one_fish.name}** (-50 moneys, but immune to Cop Fish for next 60 catches)'
                pf.add_special('bribe_fish', count=60)

            elif one_fish.name == 'Blue Crystal Meth':
                output += f'You caught: **{one_fish.name}** (doubles number of items caught for next 10 catches)'
                pf.add_special('double_items', count=10)

            elif one_fish.name == 'Rainbow Crystal Meth':
                output += f'You caught: **{one_fish.name}** (+{one_fish.value} moneys, doubles number of items caught for next 85 catches)'
                pf.add_special('double_items', count=85)

            elif one_fish.name == 'Octopus':
                output += f'You caught: **{one_fish.name}** (+{one_fish.value} moneys, octuples number of items for next catch)'
                pf.add_special('8x_items', count=1)

            elif one_fish.name == 'Mogfish':
                output += f'You caught: **{one_fish.name}** (next 12 catches by you are nearly guaranteed to include trash items)'
                pf.add_special('mogfish', count=12)
    
            elif one_fish.name == 'Fish Soap':
                output += f'You caught: **{one_fish.name}** (all items with negative value in your inventory removed)'
                fish_soap(username)

            elif one_fish.name == 'Absolute Value Fish':
                output += f'You caught: **{one_fish.name}** (all items with negative value turned to positive value)'
                fish_soap(username, absolute=True)

            elif one_fish.name == 'Security Guard Fish':
                output += f'You caught: **{one_fish.name}** (this item is literally unobtainable)'
                pf.add_special('no_negative_items', count=1)
    
            elif one_fish.name == 'God (Real)':
                output += f'You caught: **{one_fish.name}** (duplicated a random stack in your inventory)'

                stack_to_dupe = random.choice([stack for stack in pf.items if
                                                 stack.item.value > 0 and stack.item.name != "Credit" and stack.count > 0])
                amount_to_add = stack_to_dupe.count
                pf.add_fish(stack_to_dupe.item, amount_to_add)
                output += f'\nMaterialized {amount_to_add:,} {stack_to_dupe.item.name}'
    
            elif one_fish.name == 'Jonklerfish':
                penalty = random_range(44, 144)
                output += (f'You caught: **{one_fish.name}** (+{one_fish.value} moneys, everyone\'s next cooldown ' +
                           f'set to {cd + penalty} seconds)')
    
                for user in all_users:
                    all_pfs.profile_from_name(user).add_cd(cd + penalty)
    
            elif one_fish.name == 'Mercenary Fish':
                output += f'You caught: **Mercenary Fish**'
    
                for i in range(random_range(8 if double_mercenary else 4, 12 if double_mercenary else 6)):
                    # steal_fish_from_random also updates the thief's profile with the fish that was stolen
                    try:
                        heist_tuple = steal_fish_from_random(original_user, recipient_name=pf.username)
                        temp_username, stolen_fish = heist_tuple

                        output += f'\nStole {rare_prefix(stolen_fish)}**{stolen_fish.name}** from {temp_username}'
                        stolen_amt += stolen_fish.value
                    except IndexError:
                        output += f'\nBut there was nothing to steal'
                    except ValueError:
                        output += f'\nBut there was nothing to steal'
    
            elif one_fish.name == 'CS:GO Fish':
                output += f'You caught: **CS:GO Fish** ('

                try:
                    for i in range(random_range(1, 1)):
                        heist_tuple = steal_fish_from_random(original_user, shoot=True)
                        temp_username, stolen_fish = heist_tuple

                        output += f'{temp_username}\'s {rare_prefix(stolen_fish)}**{stolen_fish.name}** was shot)'
                except Exception as e:
                    output += f'Somehow, there was nothing to shoot [{e}])'
    
            elif one_fish.name == 'Sea Bass':
                output += f'You caught: **{one_fish.name}**... no it\'s at least a C+ (worth {one_fish.value} moneys)'
    
            else:
                output += f'You caught: **{one_fish.name}** (worth {one_fish.value:,} moneys)'

            output += '\n'
            if one_fish.name != 'Eldritch Beings':
                pf.add_fish(fish=one_fish)
            else:
                original_pf.add_fish(fish=one_fish)

    # adds cooldown to the user, unless the user is being catfished or have donated
    original_pf.add_cd(cd + penalty)

    # uses up all specials except the catfish because it should only be used up when
    # another player fishes with the catfish active
    if caught_fish_count > 0:
        for active_special in active_specials:
            if active_special is not None:
                original_pf.add_special(active_special, count=-1)

    if stolen_amt > 0:
        output += f'\n*Stole {stolen_amt:,} moneys from players*'

    if ml_tiers > 0:
        if random_range(1, 3 - ml_tiers) == 1:
            pf.add_fish(get_fish_from_name('Credit'), 10)
            output += f'\n*+10 moneys (Money Laundering bonus)*'
            money_laundered = True

    if curse_active:
        if random_range(1, 150) <= 2: # 1.5% chance for each curse
            money_to_remove = min(15000, int(pf.value() * 0.1))
            pf.add_fish(get_fish_from_name('Credit'), 0 - money_to_remove)
            output += f'\n*Oops! Lost {money_to_remove:,} moneys (Curse)*'

            if caught_fish_count == 0:
                pf.add_special('curse', count=-1)

        elif random_range(1, 100) <= 1: # 1% chance for each curse
            stack_to_remove = random.choice([stack for stack in pf.items if stack.item.value > 0 and stack.item.name != "Credit" and stack.count > 0])
            amount_to_remove = stack_to_remove.count
            pf.add_fish(stack_to_remove.item, 0 - amount_to_remove)
            output += f'\n*Oops! Lost all {amount_to_remove:,} {stack_to_remove.item.name} in your inventory (Curse)*'

            if caught_fish_count == 0:
                pf.add_special('curse', count=-1)

    # adds cooldown to the original user if they are being catfished or have donated
    if pf != original_pf:
        addl_msg = ' except Eldritch Beings' if eldritch_beings_caught else ''

        if caught_fish_count > 0:
            if catfish_holder_pf:
                catfish_holder_pf.add_special('catfish', count=-1)
                output += f'\n*Fish{' and money' if money_laundered else ''}{addl_msg} taken by {catfish_holder_pf.username} (Catfish powerup)*'
            else:
                output += f'\n*Fish{' and money' if money_laundered > 0 else ''}{addl_msg} donated to {pf.username} (Mr. Beast powerup)*'

    # increments new_moneys and new_catches stats for the new luck lb
    original_pf.new_catches += 1
    original_pf.new_moneys += original_pf.value() - old_value

    return output

def go_fish(factor=1.0, force_fish_name: str=None, uncatchable=None) -> FishingItem:
    if uncatchable is None:
        uncatchable = []

    weights = manipulated_weights(factor=factor, uncatchable=uncatchable)
    fishing_items_sorted_by_weight = sorted([item for item in fishing_items if item.name not in uncatchable], key=lambda item: item.weight)

    if not force_fish_name:
        return random.choices(fishing_items_sorted_by_weight, weights=weights, k=1)[0]
    else:
        force_fish = get_fish_from_name(force_fish_name)
        return force_fish

def fish_soap(username: str, absolute=False):
    pf = all_pfs.profile_from_name(username)
    inv_copy = pf.items[:]

    if absolute:
        for stack in inv_copy:
            if stack.item.name in NEGATIVES:
                temp_index = NEGATIVES.index(stack.item.name)
                positive_equivalent = get_fish_from_name(POSITIVES[temp_index])
                pf.add_fish(positive_equivalent, count=stack.count)

    pf.items = [stx for stx in pf.items if stx.item.value >= 0]

def steal_fish_from_random(thief_name: str, recipient_name: str=None, shoot=False) -> tuple[str, FishingItem]:
    if recipient_name is None:
        recipient_name = thief_name

    iterations = 0
    while True:
        weights = [pf.value() for pf in all_pfs.real_profiles]
        player_pf: Profile = random.choices(all_pfs.real_profiles, weights=weights, k=1)[0]
        player_name = player_pf.username

        if iterations >= 2000 or (len(all_pfs.real_profiles) <= 1 and not shoot):
            raise IndexError

        if player_name != thief_name or shoot or len(all_pfs.real_profiles) == 1:
            break

        iterations += 1

    stealable = [stack for stack in player_pf.items if stack.item.name != 'Credit' and stack.item.value != 0]

    weights = [max(stack.count, 0) for stack in stealable]
    stolen_fish = random.choices(stealable, weights=weights, k=1)[0].item

    # Removes the stolen fish from the player who was being stolen from, not modifying the time they last fished
    player_pf.add_fish(stolen_fish, count=-1)

    if not shoot:
        all_pfs.profile_from_name(recipient_name).add_fish(stolen_fish)

    return player_pf.username, stolen_fish

def get_all_users() -> list[str]:
    return [pf.username for pf in all_pfs.profiles]

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
    return str(all_pfs.profile_from_name(username))

def universal_profile_to_string() -> str:
    return str(all_pfs)

def leaderboard_string(sort_by_luck = False) -> str:
    output = ''
    index = 1

    list_of_profiles = [profile for profile in all_pfs.real_profiles if profile.items_caught() > 0]
    unshown = len(all_pfs.profiles) - len(list_of_profiles)

    if sort_by_luck:
        list_of_profiles.sort(key=lambda prof: sum([stack.count * stack.item.value for stack in prof.items if stack.item.name != 'Credit']) / prof.items_caught(), reverse=True)
    else:
        list_of_profiles.sort(key=lambda prof: prof.value(), reverse=True)

    for profile in list_of_profiles:
        try:
            trophy = '🥇 ' if index == 1 else '🥈 ' if index == 2 else '🥉 ' if index == 3 else ''

            more_accurate_val = profile.value() if not sort_by_luck else sum([stack.count * stack.item.value for stack in profile.items if stack.item.name != 'Credit'])

            if not sort_by_luck or profile.items_caught() >= 10:
                output += (f'{index:,}. {trophy}{profile.username}: **{(more_accurate_val if not sort_by_luck else round(more_accurate_val / profile.items_caught(), 2)):,} '
                           f'moneys{'/item' if sort_by_luck else ''}**\n')

                index += 1
            else:
                unshown += 1

        except KeyError:
            pass

        except ZeroDivisionError:
            pass

    if unshown > 0:
        output += f'\n*{unshown:,} players not counted*'

    return output

def luck_leaderboard_string() -> str:
    """
    New rng leaderboard calculation using number of new catches instead of just total number of items
    Doesn't get affected when you receive fish via catfish/mr beast, or when you get items removed
    from mercenary or cs:go, or buying items from the shop
    """
    output = ''
    index = 1

    list_of_profiles = [profile for profile in all_pfs.real_profiles if profile.new_catches > 0]
    unshown = len(all_pfs.profiles) - len(list_of_profiles)

    list_of_profiles.sort(key=lambda prof: prof.new_moneys / prof.new_catches, reverse=True)

    for profile in list_of_profiles:
        try:
            trophy = '🥇 ' if index == 1 else '🥈 ' if index == 2 else '🥉 ' if index == 3 else ''

            if profile.new_catches >= 10:
                output += f'{index:,}. {trophy}{profile.username}: **{round(profile.new_moneys / profile.new_catches, 2):,} moneys/catch**\n'

                index += 1
            else:
                unshown += 1

        except KeyError:
            pass
        except ZeroDivisionError:
            pass

    if unshown > 0:
        output += f'\n*{unshown:,} players not shown*'

    return output

def wordle_leaderboard_string() -> str:
    output = ''
    index = 1

    list_of_profiles: list[Profile] = [profile for profile in all_pfs.profiles if profile.wordle_wins + profile.wordle_losses > 0]
    list_of_profiles.sort(key = lambda p: p.wordle_points, reverse = True)

    for profile in list_of_profiles:
        trophy = '🥇 ' if index == 1 else '🥈 ' if index == 2 else '🥉 ' if index == 3 else ''

        output += f'{index:,}. {trophy}{profile.username}: **{profile.wordle_points} points**\n'

        index += 1

    return output

def gambling_losses_leaderboard_string() -> str:
    output = ''
    index = 1

    list_of_profiles: list[Profile] = all_pfs.real_profiles
    list_of_profiles.sort(key = lambda p: (p.moneys_lost_to_gambling, p.value()), reverse = True)

    for profile in list_of_profiles:
        trophy = '🥇 ' if index == 1 else '🥈 ' if index == 2 else '🥉 ' if index == 3 else ''

        if profile.moneys_lost_to_gambling >= 0:
            output += f'{index:,}. {trophy}{profile.username}: **{profile.moneys_lost_to_gambling:,} moneys lost**\n'

        else:
            output += f'{index:,}. {trophy}{profile.username}: **{-profile.moneys_lost_to_gambling:,} moneys gained**\n'

        index += 1

    return output

def recalculate_fish_database() -> int:
    """
    Modifies value/weights of fish already in fishing.json to reflect those in fishing_items.json
    Also adds the upgrades key/value pair to profiles without it
    """
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

def wipe_banned_users_wordle():
    from wordle import WordleGame

    profiles_to_wipe = [pf for pf in all_pfs.real_profiles if pf.username in WordleGame.BANNED and pf.wordle_points > 0]

    for pf in profiles_to_wipe:
        pf.wordle_wins, pf.wordle_losses, pf.wordle_points = 0, 0, 0

def _manual_data_changes() -> str:
    output = ''

    for pf in all_pfs.profiles:
        if 'State Farm Fishing Insurance II' in pf.upgrades:
            refund_fish = 'Credit'
            refund_count = 6166

            # pf.add_fish(get_fish_from_name(refund_fish), refund_count)
            # output += f'Gave {refund_count} {refund_fish} to {pf.username} (for sffi 2)\n'

    return output + '** **'

script_directory = Path(__file__).parent.resolve()
os.chdir(script_directory)

sort_fishing_items_by_weight()
fishing_items = initialize_fishing_items()

recalculate_fish_database()
all_pfs = AllProfiles()

# wipe_banned_users_wordle()

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

        if user_input == 'recalc':
            print(recalculate_fish_database())
        elif user_input == 'j':
            print(fishing_manifesto_factor('paliopolis'))
        elif user_input == 'e':
            print(fishing_manifesto_factor('epicmushroom.'))
        elif user_input == 'proftest':
            print(all_pfs.profile_from_name('epicmushroom.'))
        elif user_input.startswith('>fishtest') or user_input.startswith('go fish'):
            parts = user_input.split(' ')

            if len(parts) > 1:
                try:
                    iterations = int(parts[-1])
                except ValueError:
                    iterations = 1

            for i in range(iterations):
                print(fish_event('epicmushroom.'))
                all_pfs.write_data()

        elif user_input == 'fishobtest':
            test_items = ['Credit', 'Ohlone Rejection Letter', 'Boops boops', 'Floating Wood EX', 'Blue Whale']

            for name in test_items:
                fish_ = get_fish_from_name(name)
                print(f'{fish_.name} obtained: {'yes' if all_pfs.fish_obtained(fish_) else 'no'}')
        elif user_input == 'shinyitemavgtest':
            print((sum([get_fish_from_name(n).value for n in SHINY_ITEMS[:]]) + 95 * 18.5) / len(SHINY_ITEMS))
        elif user_input == 'drugitemavgtest':
            print((sum([get_fish_from_name(n).value for n in DRUG_ITEMS[:]]) + 185) / len(SHINY_ITEMS))
        elif user_input == 'exit':
            break