#!/usr/bin/env python3

"""Queue"""


class Queue(object):
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def pop(self):
        first_item = self.items[0]
        del self.items[0]

        return first_item

    def push(self, data):
        self.items.append(data)

    def peek(self):
        return self.items[0]

    def size(self):
        return len(self.items)

