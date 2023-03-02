import numpy as np


def get_probablity(prob):
    max_num = 10**4
    num = np.random.randint(low=1, high=max_num)
    if num <= prob * max_num:
        return True
    return False