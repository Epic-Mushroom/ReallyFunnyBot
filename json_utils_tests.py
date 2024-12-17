import json_utils
import unittest

from json_utils import update_inventory


class FishingTests(unittest.TestCase):
    def setUp(self):
        self.empty_inv = []
        self.nonempty_inv = [
            {
                "item": {
                    "name": "Hook",
                    "value": 1,
                    "weight": 100
                },
                "count": 1
            }
        ]
        self.fishing_items = json_utils.fishing_items[:]
        self.old_boot = self.fishing_items[1]

    def test_add_fish_to_inv(self):
        update_inventory(self.nonempty_inv, self.old_boot)
        print(self.nonempty_inv)

    def test_percents_of_each_fish(self):
        weight_sum = sum(fish.weight for fish in self.fishing_items)
        for fish in self.fishing_items:
            print(f'{fish.name}: {(100 * fish.weight / weight_sum):.3f}%')

    def test_average_value(self):
        weight_sum = sum(fish.weight for fish in self.fishing_items)
        a_sum = sum(fish.weight * fish.value for fish in self.fishing_items)
        print(f'AVERAGE EXPECTED VALUE: {a_sum / weight_sum:.3f}')

if __name__ == '__main__':
    unittest.main()