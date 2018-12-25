#!/usr/bin/env python3

"""Insertion sort"""

import unittest


def insertion_sort(array):
    for index, value in enumerate(array):
        while index > 0 and array[index - 1] > value:
            array[index] = array[index - 1]
            index = index - 1
        array[index] = value
    
    return array


class Test(unittest.TestCase):
    test_0 = [[54, 26, 93, 17, 77, 31, 44, 55, 20], [17, 20, 26, 31, 44, 54, 55, 77, 93]]
    test_1 = [[], []]
    test_2 = [[1, 2, 3], [1, 2, 3]]

    def test(self):
        result = insertion_sort(self.test_0[0])
        self.assertEqual(result, self.test_0[1])

        result = insertion_sort(self.test_1[0])
        self.assertEqual(result, self.test_1[1])

        result = insertion_sort(self.test_2[0])
        self.assertEqual(result, self.test_2[1])


if __name__ == '__main__':
    unittest.main()
