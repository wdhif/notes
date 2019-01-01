#!/usr/bin/env python3

"""Linked List"""

class LinkedList(object):
    
class LinkedList(object):
    class Node(object):
        def __init__(self, data):
            self.data = data
            self.next = None

    def __init__(self):
        self.root = None

    def insert(self, data):
        if self.root == None:
            self.root = self.Node(data)
        else:
            self._insert(self.root, data)

    def _insert(self, node, data):
        if node.next is None:
            node.next = self.Node(data)
        else:
            self._insert(node.next, data)

    def insert_at_start(self, data):
        new_node = self.Node(data)
        if self.root is not None:
            new_node.next = self.root
            self.root = new_node

    def walk(self):
        if self.root == None:
            print('empty linked list')
        else:
            self._walk(self.root)
    
    def _walk(self, node):
        print(node.data)
        if node.next is not None:
            self._walk(node.next)

    def remove(self, data):
        node = self.root
        if node is not None:
            if node.data == data:
                node = node.next


linked_list = LinkedList()
linked_list.insert(1)
linked_list.insert(2)
linked_list.insert(3)
linked_list.walk()
linked_list.remove(1)
linked_list.insert_at_start(9)
linked_list.walk()
