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
    lucky = random_num <= (150 if boost else 45)  # 9% chance without boost, 30% with
    unlucky = random_num >= 471 and not boost  # 6% chance

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

    total = 0
    iterations = 300000
    for i in range(iterations):
        total += catch_count()

    print("FACTOR APPLIED: ", fish_utils_tests.TEST_FACTOR, '\n')

    print("Average (without boost):", avg_val * total / iterations)
    w_line_snaps = avg_val * total / iterations

    total = 0
    for i in range(iterations):
        total += catch_count(boost=True)

    print("Average (with boost):", avg_val * total / iterations)
    wo_line_snaps = avg_val * total / iterations

    print("Percent increase with boost: ", wo_line_snaps / w_line_snaps * 100 - 100, "%")
    print("Flat increase per go fish command on average: ", wo_line_snaps - w_line_snaps)