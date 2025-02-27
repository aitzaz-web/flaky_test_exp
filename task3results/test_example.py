def test_function():
    x = 5
    y = 10
    assert x == y

def test_function2():
    numbers = [10, 20, 30, 40]
    value = sum(numbers) // len(numbers)  # Average value

    assert value == 25  # Assertion 1: Checking computed average

    x = 5
    y = x * 2 + 3
    assert y == 13  # Assertion 2: Arithmetic check

    def helper(a):
        return a * 2

    result = helper(7)
    assert result == 14  # Assertion 3: Function call check

    for i in range(3):
        assert numbers[i] < numbers[i + 1]  # Assertion 4: Loop-based check

    flag = True
    assert flag  # Assertion 5: Boolean condition check


import random
import numpy as np

def test_function3():
    x = random.randint(1, 100)
    y = np.random.rand()
    assert x < 100
    assert y < 1