import matplotlib.pyplot as plt
import numpy as np
import fish_utils, fish_utils_tests

if __name__ == '__main__':
    base_avg = fish_utils_tests.get_average_value(factor=1)

    factors = [1 + i / 5 for i in range(100)]
    avg_value = [fish_utils_tests.get_average_value(factor=f) for f in factors]

    pc_increase_in = [i * 10 for i in range(28)]
    factor_out = [fish_utils.percent_increase_to_factor(pci) for pci in pc_increase_in]
    avg_value_2 = [fish_utils_tests.get_average_value(factor=f) for f in factor_out]

    for i in range(60):
        this_avg = fish_utils_tests.get_average_value(factor=1 + i / 4)
        print(f'Factor: {1 + i / 4}, Avg value: {this_avg},'
              f'Increase from base avg: +{(this_avg - base_avg) * 100 / base_avg:.3f}%')

    plt.plot(pc_increase_in, factor_out)
    plt.xlabel('pc_increase_in')
    plt.ylabel('avg_value_2')

    plt.show()

