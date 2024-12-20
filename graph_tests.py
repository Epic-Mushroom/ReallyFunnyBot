import matplotlib.pyplot as plt
import numpy as np
import json_utils, json_utils_tests

if __name__ == '__main__':
    factors = [1 + i / 5 for i in range(100)]
    avg_value = [json_utils_tests.get_average_value(factor=f) for f in factors]

    plt.plot(factors, avg_value)
    plt.xlabel('factors')
    plt.ylabel('avg_value')

    plt.show()

