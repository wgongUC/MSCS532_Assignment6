# Name: Weevern Gong
# Project Title: MSCS532_Assignment6
# Description: This program implements arrays, matrices, stacks, queues, and linked lists.
# Array storage uses fixed-size Python reference buffers with explicit growth and shifts.

# Data structures explanation: Arrays provide direct indexed access, stacks remove
# the newest value, queues remove the oldest value, and linked lists follow node links.
# Buffers double when full and keep their capacity after deletion. Removed references
# are cleared. The implementations do not use list.insert, list.pop, deque, or a
# ready-made linked list. Indices are zero-based; negative indices are rejected.
# Noninteger and Boolean indices raise TypeError. Invalid indices and empty removals
# raise IndexError. Storage grows with buffer capacity or the number of linked nodes.


from dataclasses import dataclass


def _index(index, limit, insertion=False):

    if isinstance(index, bool) or not isinstance(index, int):
        raise TypeError("index must be an integer")
    if not 0 <= index < limit + int(insertion):
        raise IndexError("index out of range")


# Dynamic array explanation: Access is O(1); indexed shifts take O(n) worst-case time
# Doubling gives amortized O(1) append, with O(n) work on a growth operation
class DynamicArray:

    def __init__(self):

        self._data = [None] * 4
        self._size = 0

    def __len__(self):

        return self._size

    def __iter__(self):

        for i in range(self._size):
            yield self._data[i]

    def __getitem__(self, index):

        _index(index, self._size)
        return self._data[index]

    def __setitem__(self, index, value):

        _index(index, self._size)
        self._data[index] = value

    def insert(self, index, value):

        _index(index, self._size, insertion=True)
        # Copy into a doubled buffer when the current capacity is full
        if self._size == len(self._data):
            buffer = [None] * (2 * len(self._data))
            for i in range(self._size):
                buffer[i] = self._data[i]
            self._data = buffer
        # Shift backward so insertion does not overwrite a value that still needs moving
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._size += 1

    def append(self, value):

        self.insert(self._size, value)

    def delete(self, index):

        _index(index, self._size)
        value = self._data[index]
        # Close the gap, then release the reference in the unused final slot
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._size -= 1
        self._data[self._size] = None
        return value


# Matrix explanation: Independent row lists are stored in the dynamic array
# Cell access and assignment take O(1); row insertion takes O(r + c) and deletion O(r)
# Structural changes operate on rows; the column count stays fixed even when empty
class Matrix:

    def __init__(self, rows, columns, fill=None):

        # Dimensions must be nonnegative integers; Boolean and noninteger values are rejected
        for value in (rows, columns):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError("dimensions must be integers")
            if value < 0:
                raise ValueError("dimensions must be nonnegative")
        self.columns = columns
        self._rows = DynamicArray()
        # Row containers are independent, but mutable fill objects are not deep-copied
        for _ in range(rows):
            self.insert_row(len(self._rows), [fill] * columns)

    @property
    def shape(self):

        return len(self._rows), self.columns

    def get(self, row, column):

        _index(column, self.columns)
        return self._rows[row][column]

    def set(self, row, column, value):

        _index(column, self.columns)
        self._rows[row][column] = value

    def insert_row(self, index, values):

        # Copy the supplied row and reject a width that differs from the fixed column count
        row = list(values)
        if len(row) != self.columns:
            raise ValueError("row width must equal column count")
        self._rows.insert(index, row)

    def delete_row(self, index):

        return self._rows.delete(index)


# Stack explanation: Push at the array end for amortized O(1) time
# Growth takes O(n); pop and peek at the same end take O(1)
class Stack:

    def __init__(self):

        self._items = DynamicArray()

    def __len__(self):

        return len(self._items)

    def push(self, value):

        self._items.append(value)

    def peek(self):

        return self._items[len(self) - 1]

    def pop(self):

        return self._items.delete(len(self) - 1)


# Queue explanation: A circular buffer gives amortized O(1) enqueue
# Growth takes O(n), while dequeue and peek take O(1) without shifting later values
class Queue:

    def __init__(self):

        self._data = [None] * 4
        self._head = 0
        self._size = 0

    def __len__(self):

        return self._size

    def enqueue(self, value):

        # Copy into a doubled buffer when the current capacity is full
        if self._size == len(self._data):
            buffer = [None] * (2 * len(self._data))
            # Copy from the logical head so growth preserves the order of a wrapped queue
            for i in range(self._size):
                buffer[i] = self._data[(self._head + i) % len(self._data)]
            self._data = buffer
            self._head = 0
        # Locate the next free position using the head and current queue size
        self._data[(self._head + self._size) % len(self._data)] = value
        self._size += 1

    def peek(self):

        if not self._size:
            raise IndexError("queue is empty")
        return self._data[self._head]

    def dequeue(self):

        value = self.peek()
        # Clear the removed reference and move the head to the next circular position
        self._data[self._head] = None
        self._head = (self._head + 1) % len(self._data)
        self._size -= 1
        return value


@dataclass
class _Node:

    value: object
    next: object = None


# Linked list explanation: A head reference and size are kept, with no tail reference
# Head insertion and deletion take O(1); indexed changes and traversal take O(n) worst case
class SinglyLinkedList:

    def __init__(self):

        self._head = None
        self._size = 0

    def __len__(self):

        return self._size

    def __iter__(self):

        node = self._head
        while node is not None:
            yield node.value
            node = node.next

    def _node(self, index):

        _index(index, self._size)
        node = self._head
        # Follow links from the head to reach the requested position
        for _ in range(index):
            node = node.next
        return node

    def insert(self, index, value):

        _index(index, self._size, insertion=True)
        if index == 0:
            self._head = _Node(value, self._head)
        else:
            previous = self._node(index - 1)
            # Link the new node between its predecessor and the remaining list
            previous.next = _Node(value, previous.next)
        self._size += 1

    def delete(self, index):

        _index(index, self._size)
        if index == 0:
            removed = self._head
            self._head = removed.next
        else:
            previous = self._node(index - 1)
            removed = previous.next
            # Bypass the removed node while keeping the remaining nodes connected
            previous.next = removed.next
        self._size -= 1
        return removed.value
