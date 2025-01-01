import fish_utils
import unittest

TEST_FACTOR = fish_utils.percent_increase_to_factor(0)

def get_average_value(factor=1.0) -> float:
    fish_items = fish_utils.fishing_items[:]
    weights = fish_utils.manipulated_weights(factor=factor)

    weight_sum = sum(weights)
    a_sum = sum(weights[i] * fish_items[i].value for i in range(len(fish_items)))
    return a_sum / weight_sum

def get_rare_item_chance(factor=1.0) -> float:
    fish_items = fish_utils.fishing_items[:]
    weights = fish_utils.manipulated_weights(factor=TEST_FACTOR)
    weight_sum = sum(weights)

    temp_chance_sum = 0
    for i in range(len(fish_items)):
        if fish_utils.RARE_ITEM_WEIGHT_THRESHOLD >= fish_items[i].weight > 0:
            temp_chance_sum += 100 * weights[i] / weight_sum

    return temp_chance_sum

class FishingTests(unittest.TestCase):
    def setUp(self):
        self.fishing_items = fish_utils.fishing_items[:]

    def test_percents_of_each_fish(self):
        weights = fish_utils.manipulated_weights(factor=TEST_FACTOR)
        weight_sum = sum(weights)

        print(f"Rare item chance: {get_rare_item_chance(factor=TEST_FACTOR):.3f}%")

        print(f"\n**All**\n")

        for i in range(len(self.fishing_items)):
            if self.fishing_items[i].weight > 0:
                print(f'{self.fishing_items[i].name}: {(100 * weights[i] / weight_sum):.3f}%')

        print(f"\n**Unobtainables**\n")

        for i in range(len(self.fishing_items)):
            if self.fishing_items[i].weight <= 0:
                print(f'{self.fishing_items[i].name}')

    def test_average_value(self):
        print(f'AVERAGE EXPECTED VALUE: {get_average_value(TEST_FACTOR):.3f}')

if __name__ == '__main__':
    unittest.main()