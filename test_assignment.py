# Name: Weevern Gong
# Project Title: MSCS532_Assignment6
# Description: This program checks both selection algorithms and the elementary data structures.
# The tests cover representative inputs, invalid operations, and reproducible generated cases.

# Correctness testing explanation: Compare selected values with a sorted reference,
# array and linked-list changes with a Python list, and queue operations with deque.
# Check input preservation, duplicate values, boundary ranks, growth, wraparound,
# removal order, and matrix row independence. Seeded generators reproduce the cases.


import random
import unittest
from collections import deque

from selection import deterministic_select, randomized_select
from structures import DynamicArray, Matrix, Queue, SinglyLinkedList, Stack


class SelectionTests(unittest.TestCase):

    def test_representative_duplicates_and_group_boundaries(self):

        # Include small group boundaries, duplicate values, and an all-equal input
        cases = ([4], [2, 1], [3, 1, 2], [4, 1, 3, 2],
                 [5, 1, 4, 2, 3], [6, 1, 5, 2, 4, 3],
                 [3, 1, 3, 2, 1, 3, 0], [7] * 11,
                 list(range(26, 0, -1)))
        for values in cases:
            original = list(values)
            # Check minimum, lower-median, and maximum ranks without repeating a rank
            for k in sorted({1, (len(values) + 1) // 2, len(values)}):
                for fn in (deterministic_select, randomized_select):
                    with self.subTest(n=len(values), k=k, algorithm=fn.__name__):
                        result = (fn(values, k, random.Random(532 + k))
                                  if fn is randomized_select else fn(values, k))
                        self.assertEqual(result, sorted(values)[k - 1])
                        self.assertEqual(values, original)

    def test_large_distributions_and_input_preservation(self):

        rng = random.Random(532)
        for values in (list(range(101)), list(range(101, 0, -1)),
                       [7] * 101, [rng.randrange(-100, 101) for _ in range(101)]):
            original = values.copy()
            for k in (1, 51, 101):
                for fn in (deterministic_select, randomized_select):
                    self.assertEqual(fn(values, k, random.Random(532 + k)) if fn is randomized_select
                                     else fn(values, k), sorted(values)[k - 1])
                    self.assertEqual(values, original)

    def test_invalid_ranks(self):

        for fn in (deterministic_select, randomized_select):
            for values, k in (([], 1), ([1], -1), ([1], 0), ([1], 2)):
                with self.assertRaises(ValueError):
                    fn(values, k)
            for k in (True, 1.0, '1'):
                with self.assertRaises(TypeError):
                    fn([1], k)


class StructureTests(unittest.TestCase):

    def test_array_and_linked_list_against_model(self):

        for cls in (DynamicArray, SinglyLinkedList):
            actual, model = cls(), []
            with self.assertRaises(IndexError):
                actual.delete(0)
            with self.assertRaises(IndexError):
                actual.delete(-1)
            rng = random.Random(532)
            # Apply the same seeded insertions and deletions to the implementation and reference
            for _ in range(40):
                if not model or rng.random() < .6:
                    i, value = rng.randrange(len(model) + 1), rng.randrange(12)
                    model.insert(i, value)
                    actual.insert(i, value)
                else:
                    i = rng.randrange(len(model))
                    self.assertEqual(actual.delete(i), model.pop(i))
                self.assertEqual(list(actual), model)
                self.assertEqual(len(actual), len(model))
            for i in (-1, len(model) + 1):
                with self.assertRaises(IndexError):
                    actual.insert(i, 0)
            with self.assertRaises(IndexError):
                actual.delete(len(model))
            with self.assertRaises(TypeError):
                actual.insert(True, 0)

    def test_array_access_and_released_slot(self):

        a = DynamicArray()
        a.append(1)
        a[0] = 9
        self.assertEqual(a[0], 9)
        self.assertEqual(a.delete(0), 9)
        # Removing the value must also clear its stored reference
        self.assertIsNone(a._data[0])
        with self.assertRaises(IndexError):
            _ = a[0]

    def test_stack_lifo_and_underflow(self):

        s = Stack()
        for i in range(12):
            s.push(i)
            self.assertEqual(s.peek(), i)
        self.assertEqual([s.pop() for _ in range(12)], list(reversed(range(12))))
        for operation in (s.pop, s.peek):
            with self.assertRaises(IndexError):
                operation()

    def test_queue_wrap_growth_and_underflow(self):

        q, model = Queue(), deque()
        for i in range(4):
            q.enqueue(i)
            model.append(i)
        for _ in range(2):
            self.assertEqual(q.dequeue(), model.popleft())
        self.assertEqual(q._head, 2)
        for i in (4, 5):
            q.enqueue(i)
            model.append(i)
        # Fill the wrapped queue before checking growth and preserved FIFO order
        self.assertEqual(q._size, len(q._data))
        q.enqueue(6)
        model.append(6)
        self.assertEqual(len(q._data), 8)
        self.assertEqual(q._head, 0)
        while model:
            self.assertEqual(q.peek(), model[0])
            self.assertEqual(q.dequeue(), model.popleft())
            self.assertEqual(len(q), len(model))
        # Reuse an empty queue across repeated circular positions
        for i in range(12):
            q.enqueue(i)
            self.assertEqual(q.dequeue(), i)
        self.assertTrue(all(x is None for x in q._data))
        for operation in (q.peek, q.dequeue):
            with self.assertRaises(IndexError):
                operation()

    def test_matrix_rows_and_boundaries(self):

        m = Matrix(2, 3, 0)
        m.set(0, 1, 8)
        self.assertEqual(m.get(1, 1), 0)
        self.assertEqual(m.get(0, 1), 8)
        row = [1, 2, 3]
        m.insert_row(1, row)
        # Changing the supplied row must not change the stored row copy
        row[0] = 99
        self.assertEqual(m.delete_row(1), [1, 2, 3])
        self.assertEqual(m.shape, (2, 3))
        with self.assertRaises(ValueError):
            m.insert_row(0, [1])
        for r, c in ((-1, 0), (0, -1), (2, 0), (0, 3)):
            with self.assertRaises(IndexError):
                m.get(r, c)
        # The fixed column count must remain available after the last row is removed
        m.delete_row(0)
        m.delete_row(0)
        m.insert_row(0, [4, 5, 6])
        self.assertEqual(m.shape, (1, 3))
        self.assertEqual(Matrix(0, 0).shape, (0, 0))
        with self.assertRaises(ValueError):
            Matrix(-1, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
