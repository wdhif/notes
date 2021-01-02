#!/usr/bin/env python3

"""Bubble sort"""

import unittest


def selection_sort(array):
    # O(N^2) time and O(1) space complexity.
    sorted_index = 0
    while sorted_index < len(array):
        minimum_index = None
        for index, element in enumerate(array[sorted_index:]):
            if minimum_index == None or element < array[minimum_index]:
                minimum_index = index + sorted_index  # Remember that enumerate starts at 0, even when using slices.
        array[sorted_index], array[minimum_index] = array[minimum_index], array[sorted_index]
        sorted_index += 1

    return array

class Test(unittest.TestCase):
    test_0 = [[54, 26, 93, 17, 77, 31, 44, 55, 20], [17, 20, 26, 31, 44, 54, 55, 77, 93]]
    test_1 = [[], []]
    test_2 = [[1, 2, 3], [1, 2, 3]]

    def test(self):
        result = selection_sort(self.test_0[0])
        self.assertEqual(result, self.test_0[1])

        result = selection_sort(self.test_1[0])
        self.assertEqual(result, self.test_1[1])

        result = selection_sort(self.test_2[0])
        self.assertEqual(result, self.test_2[1])


if __name__ == '__main__':
    unittest.main()

