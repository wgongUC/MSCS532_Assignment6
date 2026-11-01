# Name: Weevern Gong
# Project Title: MSCS532_Assignment6
# Description: This program implements deterministic and randomized selection.
# Both versions find the one-based kth smallest value without changing the input.

# Selection explanation: Divide values into lower, equal, and upper portions,
# then continue only in the portion containing the requested rank. Equal values
# occupy separate ranks. Median-of-medians selects a pivot from groups of five
# for O(n) worst-case time. Random pivot selection takes O(n) expected time and
# O(n^2) worst-case time. Both versions use O(n) peak auxiliary reference storage.
# Values must support a total order; NaN and other unordered values are excluded.


import random


def _prepare(values, k):

    # Copy the input before checking the one-based rank
    # Invalid rank types raise TypeError; ranks outside the input raise ValueError
    data = list(values)
    if isinstance(k, bool) or not isinstance(k, int):
        raise TypeError("k must be an integer")
    if not 1 <= k <= len(data):
        raise ValueError("k must be between 1 and the input length")
    return data, k - 1


def _partition(data, pivot):

    low, equal, high = [], [], []
    # Keep equal values together so duplicate ranks do not prevent progress
    for value in data:
        if value < pivot:
            low.append(value)
        elif value > pivot:
            high.append(value)
        else:
            equal.append(value)
    return low, equal, high


def _deterministic(data, index):

    while len(data) > 5:
        # Find each small group median, then select the middle of those medians
        medians = []
        for start in range(0, len(data), 5):
            group = sorted(data[start:start + 5])
            medians.append(group[len(group) // 2])
        pivot = _deterministic(medians, len(medians) // 2)
        low, equal, high = _partition(data, pivot)
        # Continue in one strict portion or return when the rank falls among the ties
        if index < len(low):
            data = low
        elif index < len(low) + len(equal):
            return pivot
        else:
            index -= len(low) + len(equal)
            data = high
    return sorted(data)[index]


def deterministic_select(values, k):

    data, index = _prepare(values, k)
    return _deterministic(data, index)


def randomized_select(values, k, rng=None):

    data, index = _prepare(values, k)
    # Callers can supply random.Random(seed) to reproduce the pivot choices
    rng = rng if rng is not None else random.Random()
    # Iterate through the selected portions so poor pivots cannot exhaust recursion depth
    while len(data) > 1:
        pivot = rng.choice(data)
        low, equal, high = _partition(data, pivot)
        # Continue in one strict portion or return when the rank falls among the ties
        if index < len(low):
            data = low
        elif index < len(low) + len(equal):
            return pivot
        else:
            index -= len(low) + len(equal)
            data = high
    return data[0]
