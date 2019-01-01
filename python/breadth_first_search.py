#!/usr/bin/env python3

"""Breadth-first search"""

import unittest

graph = {
    'A': [0, ['B', 'C']],
    'B': [1, ['A', 'C', 'D']],
    'C': [2, ['A', 'B']],
    'D': [3, ['B']],
}


def breadth_first_search(graph, node, visited, search):
    queue = []
    queue.append(node)
    visited.append(node)
    if graph[node][0] == search:
        return node
    while len(queue) > 0:
        node = queue[0]
        del queue[0]
        for n in graph[node][1]:
            if graph[n][0] == search:
                return n
            if n not in visited:
                queue.append(n)
                visited.append(n)
            if n[0] == search:
                    return node
    


class Test(unittest.TestCase):
    def test(self):
        result = breadth_first_search(graph, 'A', [], 1)
        self.assertEqual(result, 'B')


if __name__ == '__main__':
    unittest.main()
