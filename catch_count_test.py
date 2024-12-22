import json
from pathlib import Path

import fish_utils_tests
from fish_utils import random_range
from fish_utils_tests import get_average_value

test_path = Path('trackers\\test.json')


def catch_count(boost=False) -> int:
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

if __name__ == '__main__':
    avg_val = get_average_value(factor=fish_utils_tests.TEST_FACTOR)

    sffi_tiers = 0
    total = 0
    iterations = 300000
    for i in range(iterations):
        total += catch_count()

    print("FACTOR APPLIED: ", fish_utils_tests.TEST_FACTOR, '\n')

    print("Average (without boost):", avg_val * total / iterations)
    base_val = avg_val * total / iterations

    while sffi_tiers < 3:
        sffi_tiers += 1
        total = 0
        for i in range(iterations):
            total += catch_count()

        print(f"Average (with {sffi_tiers} sffi tiers):", avg_val * total / iterations)
        powered_up_val = avg_val * total / iterations

        print(f"Percent increase with {sffi_tiers} sffi tiers: ", powered_up_val / base_val * 100 - 100, "%")
        print("Flat increase per go fish command on average: ", powered_up_val - base_val)

    total = 0
    for i in range(iterations):
        total += catch_count(boost=True)

    print(f"Average (with {sffi_tiers} sffi tiers and caffeine boost):", avg_val * total / iterations)
    powered_up_val = avg_val * total / iterations

    print(f"Percent increase with {sffi_tiers} sffi tiers and boost: ", powered_up_val / base_val * 100 - 100, "%")
    print("Flat increase per go fish command on average: ", powered_up_val - base_val)

    total = 0
    sffi_tiers = 0
    for i in range(iterations):
        total += catch_count(boost=True)

    print(f"Average (with {sffi_tiers} sffi tiers and caffeine boost):", avg_val * total / iterations)
    powered_up_val = avg_val * total / iterations

    print(f"Percent increase with {sffi_tiers} sffi tiers and boost: ", powered_up_val / base_val * 100 - 100, "%")
    print("Flat increase per go fish command on average: ", powered_up_val - base_val)