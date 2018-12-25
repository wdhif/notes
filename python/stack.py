#!/usr/bin/env python3

"""Stack"""


class Stack(object):
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def pop(self):
        return self.items.pop()

    def push(self, data):
        self.items.append(data)

    def peek(self):
        return self.items[-1]

    def size(self):
        return len(self.items)

