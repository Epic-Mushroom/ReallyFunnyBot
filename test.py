import json
from pathlib import Path
from json_utils import random_range

test_path = Path('trackers\\test.json')


def catch_count() -> int:
    random_num = random_range(1, 500)
    count = 1

    insanely_lucky = random_num <= 1  # 0.2% chance
    super_lucky = random_num <= 5  # 1% chance
    lucky = random_num <= 35  # 7% chance
    unlucky = random_num >= 471  # 6% chance

    if insanely_lucky:
        for j in range(7):
            count += catch_count()
    elif super_lucky:
        for j in range(3):
            count += catch_count()
    elif lucky:
        count += catch_count()
    elif unlucky:
        count -= 1

    return count

if __name__ == '__main__':

    while True:
        user_input = input()

        if user_input != 'exit':
            print(catch_count())
        else:
            break