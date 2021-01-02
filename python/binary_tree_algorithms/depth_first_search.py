#!/usr/bin/env python3

"""depth_first_search"""

import unittest

graph = {
    'A': [0, ['B', 'C']],
    'B': [1, ['A', 'C', 'D']],
    'C': [2, ['A', 'B']],
    'D': [3, ['B']],
}


def depth_first_search(graph, node, visited, search):
    if node not in visited:
        visited.append(node)
        if graph[node][0] == search:
            return node
        for n in graph[node][1]:
            return depth_first_search(graph, n, visited, search)
    
    return None


class Test(unittest.TestCase):
    def test(self):
        result = depth_first_search(graph, 'A', [], 1)
        self.assertEqual(result, 'B')


if __name__ == '__main__':
    unittest.main()
