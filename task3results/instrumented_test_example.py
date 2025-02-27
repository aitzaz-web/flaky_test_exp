def test_function():
    x = 5
    y = 10
    assert x == y


def test_function2():
    numbers = [10, 20, 30, 40]
    value = sum(numbers) // len(numbers)
    assert value == 25
    x = 5
    y = x * 2 + 3
    assert y == 13

    def helper(a):
        return a * 2
    result = helper(7)
    assert result == 14
    for i in range(3):
        print('log>> numbers[i]:', numbers[i])
        print('log>> numbers[i + 1]:', numbers[i + 1])
        assert numbers[i] < numbers[i + 1]
    flag = True
    assert flag


import random
import numpy as np


def test_function3():
    x = random.randint(1, 100)
    y = np.random.rand()
    assert x < 100
    assert y < 1
