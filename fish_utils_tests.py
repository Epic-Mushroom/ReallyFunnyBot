import fish_utils
import unittest

TEST_FACTOR = 1

def get_average_value(factor=1.0) -> float:
    fish_items = fish_utils.fishing_items[:]
    weights = fish_utils.manipulated_weights(factor=factor)

    weight_sum = sum(weights)
    a_sum = sum(weights[i] * fish_items[i].value for i in range(len(fish_items)))
    return a_sum / weight_sum

class FishingTests(unittest.TestCase):
    def setUp(self):
        self.fishing_items = fish_utils.fishing_items[:]

    def test_percents_of_each_fish(self):
        weights = fish_utils.manipulated_weights(factor=TEST_FACTOR)
        weight_sum = sum(weights)
        for i in range(len(self.fishing_items)):
            print(f'{self.fishing_items[i].name}: {(100 * weights[i] / weight_sum):.3f}%')

    def test_average_value(self):
        print(f'AVERAGE EXPECTED VALUE: {get_average_value(TEST_FACTOR):.3f}')

if __name__ == '__main__':
    unittest.main()