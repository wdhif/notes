#!/usr/bin/env python3

"""Fibonacci"""

import unittest


def fibonacci(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


class Test(unittest.TestCase):
    test_0 = [4, 3]
    test_1 = [5, 5]

    def test(self):
        result = fibonacci(self.test_0[0])
        self.assertEqual(result, self.test_0[1])

        result = fibonacci(self.test_1[0])
        self.assertEqual(result, self.test_1[1])


if __name__ == '__main__':
    unittest.main()
