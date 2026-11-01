# MSCS532_Assignment6 by Weevern Gong

## Description

Python implementations of median-of-medians selection, randomized Quickselect, dynamic arrays, matrices, array-based stacks and queues, and singly linked lists.

## Requirements

- Python 3, tested with Python 3.14.3
- No third-party packages

## Instructions

Open a terminal in the project folder.

1. Run the tests for both selection algorithms and all data structures:

```powershell
python -B -m unittest -v
```

2. Check the saved measurements and source integrity:

```powershell
python -B verify_evidence.py
```

3. To repeat the benchmark, copy the five Python files into a separate empty folder. Open that folder and run:

```powershell
python -B benchmark.py
```

The benchmark saves new results in an `evidence` subfolder and refuses to overwrite existing measurements. It tests random, sorted, and reverse-sorted inputs at sizes 100, 1,000, and 10,000, with five trials per algorithm and condition.

## Files

| File | Purpose |
| --- | --- |
| `selection.py` | Deterministic and randomized selection |
| `structures.py` | Arrays, matrices, stacks, queues, and linked lists |
| `test_assignment.py` | Correctness and edge-case tests |
| `benchmark.py` | Selection timing comparison |
| `verify_evidence.py` | Measurement and source-integrity checks |
| `evidence/` | Saved measurements and reproducibility details |
| [Report](WeevernGong_Assignment6_Medians_and_Order_Statistics_and_Elementary_Data_Structures.docx) | Design choices, complexity analysis, results, and applications |

## Example

Run this example in Python from the project folder:

```python
from selection import deterministic_select, randomized_select

values = [7, 2, 5, 2, 9]
print(deterministic_select(values, 3))
print(randomized_select(values, 3))
```

Both calls return `5`, the third smallest value, without changing the input.

## Summary of Findings

Median-of-medians has O(n) worst-case time. Randomized selection has O(n) expected time and O(n²) worst-case time. Both implementations use O(n) extra space.

Randomized selection had lower median times in all nine measured conditions. For 10,000 random values, its median was 0.9120 ms compared with 1.9821 ms for deterministic selection. These measurements describe the tested programs on one machine and do not prove the complexity bounds.

Arrays and matrices provide O(1) indexed access. Array edits may require shifting elements, while linked-list indexed operations require traversal. Linked-list head operations take O(1). Array-stack pushes and circular-queue enqueues take amortized O(1), and removals take O(1). The report explains the memory costs and practical uses of each structure.
