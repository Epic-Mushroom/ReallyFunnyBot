import json
from pathlib import Path

import fish_utils_tests
from fish_utils import random_range
from fish_utils_tests import get_average_value
from fish_utils import fish_event

test_path = Path('trackers\\test.json')

def catch_count(boost=False, sffi_tiers=0) -> int:
    random_num = random_range(1, 500)
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
    avg_val = get_average_value(factor=factor)
    total = 0

    for i in range(iterations):
        total += catch_count(boost=boost, sffi_tiers=sffi)
    result_avg = avg_val * total / iterations

    print("FACTOR APPLIED: ", fish_utils_tests.TEST_FACTOR, '\n')
    print("Average: ", result_avg)

    factor = fish_utils_tests.TEST_FACTOR
    avg_val = get_average_value(factor=factor)
    total = 0

    for i in range(iterations):
        total += catch_count()
    control_avg = avg_val * total / iterations

    print("Average with no buffs: ", control_avg)
    print("Flat increase per command on average: ", result_avg - control_avg)

def simulate_user(iterations=500):
    total = 0

    for i in range(iterations):
        fish_event('test_user3', bypass_fish_cd=True)

    print("FACTOR APPLIED: ", fish_utils_tests.TEST_FACTOR, '\n')

if __name__ == '__main__':
    simulate_avg(iterations=3000000, sffi=0, boost=True)