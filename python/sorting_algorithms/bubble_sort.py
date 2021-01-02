#!/usr/bin/env python3

"""Bubble sort"""

import unittest


def bubble_sort(array):
    # O(N^2) time and O(1) space complexity.
    swapped = True
    while swapped:
        swapped = False
        for index in range(1, len(array)):  # Jump the first element
            if array[index - 1] > array[index]:
                array[index - 1], array[index] = array[index], array[index - 1]
                swapped = True

    return array


class Test(unittest.TestCase):
    test_0 = [[54, 26, 93, 17, 77, 31, 44, 55, 20], [17, 20, 26, 31, 44, 54, 55, 77, 93]]
    test_1 = [[], []]
    test_2 = [[1, 2, 3], [1, 2, 3]]

    def test(self):
        result = bubble_sort(self.test_0[0])
        self.assertEqual(result, self.test_0[1])

        result = bubble_sort(self.test_1[0])
        self.assertEqual(result, self.test_1[1])

        result = bubble_sort(self.test_2[0])
        self.assertEqual(result, self.test_2[1])


if __name__ == '__main__':
    unittest.main()

