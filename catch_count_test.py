import json
from pathlib import Path

import fish_utils_tests, fish_utils

test_path = Path('trackers\\test.json')

def catch_count(boost=False, sffi_tiers=0) -> int:
    random_num = fish_utils.random_range(1, 500)
    count = 1

    insanely_lucky = random_num <= 2  # 0.4% chance
    super_lucky = random_num <= 8  # 1.6% chance
    lucky = random_num <= (
        140 if boost else 35)  # 7% chance without boost, 28% with
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

def simulate_avg(iterations=300000, factor=fish_utils_tests.TEST_FACTOR, sffi=0, boost=False):
    avg_val = fish_utils_tests.get_average_value(factor=factor)
    total = 0

    for i in range(iterations):
        total += catch_count(boost=boost, sffi_tiers=sffi)
    result_avg = avg_val * total / iterations

    print("FACTOR APPLIED: ", fish_utils_tests.TEST_FACTOR, '\n')
    print("Average: ", result_avg)

    factor = fish_utils_tests.TEST_FACTOR
    avg_val = fish_utils_tests.get_average_value(factor=factor)
    total = 0

    for i in range(iterations):
        total += catch_count()
    control_avg = avg_val * total / iterations

    print("Average with no buffs: ", control_avg)
    print("Flat increase per command on average: ", result_avg - control_avg)

def simulate_user(test_username='welcome_back_to_my_yt_channel', test_username_2='hi_guys', iterations=12500):
    fish_utils.fish_event(test_username)
    fish_utils.fish_event(test_username_2)

    pf = fish_utils.all_pfs.profile_from_name(test_username)
    pf_2 = fish_utils.all_pfs.profile_from_name(test_username_2)
    starting = pf.value if pf else 0
    starting_2 = pf_2.value if pf_2 else 0
    pf.next_fish_time = 0
    pf_2.next_fish_time = 0

    for i in range(iterations):
        try:
            event = fish_utils.fish_event(test_username)
            pf.next_fish_time = 0
            pf_2.next_fish_time = 0
            event_2 = fish_utils.fish_event(test_username_2)
            pf.next_fish_time = 0
            pf_2.next_fish_time = 0
        except ValueError:
            iterations = i
            break

    gained = pf.value - starting
    gained_2 = pf_2.value - starting_2

    print(pf)
    print(pf_2)

    print(f'1:\n===========GAINED: {gained}\nITERATIONS: {iterations}\nPER COMMAND: {gained / iterations}\n')
    print(f'2:\n===========GAINED: {gained_2}\nITERATIONS: {iterations}\nPER COMMAND: {gained_2 / iterations}')
    print("FACTOR APPLIED: ", 1, '\n')

    fish_utils.all_pfs.write_data()

if __name__ == '__main__':
    simulate_user()