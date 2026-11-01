# MSCS532_Assignment6 by Weevern Gong

## Description

This project implements deterministic and randomized selection in Python, together with dynamic arrays, matrices, array-backed stacks, circular queues, and singly linked lists. Both selection functions return the one-based kth smallest value without changing the original input. The deterministic version selects its pivot using median-of-medians, while the randomized version chooses a pivot uniformly from the current list. Both use three-way partitioning to handle repeated values.

## Requirements

- Python 3; tested with Python 3.14.3
- No third-party Python packages are required

## Instructions

1. Open the folder containing the project files. If you downloaded a ZIP file, extract it first. Check the Python version:

```powershell
python --version
```

2. Run a selection example:

```powershell
python -B -c "from selection import deterministic_select, randomized_select; import random; values = [7, 2, 5, 2, 9]; print(deterministic_select(values, 3)); print(randomized_select(values, 3, random.Random(532)))"
```

Both lines print `5`. The `selection.py` and `structures.py` files provide reusable functions and classes; running those files directly does not print a demonstration. Their operations are exercised by the unit tests.

3. Run the unit tests:

```powershell
python -B -m unittest -v
```

The test file can also be run directly:

```powershell
python -B test_assignment.py
```

The eight test methods check both selection functions on representative lists and edge cases, including duplicates, invalid ranks, fixed seeds, and input preservation. They also check array and linked-list edits against reference models, stack order and underflow, queue wraparound and growth, and matrix row operations and boundaries. Indices are zero-based for the data structures, negative indices are rejected, and empty stack or queue removals raise `IndexError`. Selection values must have a total order; NaN and mutually incomparable values are outside that contract.

4. Verify the included measurements and source integrity:

```powershell
python -B verify_evidence.py
```

This reconstructs the seeded input lists, checks all 90 recorded results and trial pairs, recalculates the nine summary rows, and verifies the documented source hashes. It does not rerun the experiment or change the evidence.

5. Run the performance comparison in a separate folder to preserve the included measurements. Copy the five Python files into a new folder with no existing benchmark evidence. Open that folder and run:

```powershell
python -B benchmark.py
```

The benchmark creates an `evidence` subfolder and saves `benchmark_raw.csv`, `benchmark_summary.csv`, and `benchmark_environment.json`. Running it where any of those files already exists raises `FileExistsError` before measurements are replaced. This is intentional; the results included in this project support the report and must remain available.

The comparison tests random, sorted, and reverse-sorted inputs at sizes 100, 1,000, and 10,000. Each condition includes one checked, untimed warm-up per algorithm and five paired measured trials, giving 90 observations and 18 warm-up calls. Both algorithms receive identical values and ranks within each pair. Execution order alternates, with deterministic selection first on odd-numbered trials.

Random input uses integers from `-n` through `n`, generated with seed `532 + n`. Sorted and reverse-sorted inputs contain the distinct integers from `0` through `n - 1`. Randomized pivot seeds are `532` through `536`, and the warm-up pivot seed is `531`. One input array is reused per condition. Each call selects `k = (n + 1) // 2`, which is the lower median for these even input sizes, rather than the average of the two central values.

Execution time is measured with `time.perf_counter_ns()`. Input copying and partition allocation occur inside the public selection call and are included in timing. Input generation, oracle sorting, random-generator creation, warm-up, correctness checks, and file output occur outside timing. Every result is checked against `sorted(values)[k - 1]`, and input preservation is checked after each call. Fixed seeds reproduce the inputs and pivot sequences when used with the same Python version; elapsed times will vary.

The included measurements were recorded on October 23, 2026, at 00:33 UTC using Python 3.14.3 on Windows 11 build 26300, with 24 logical CPUs. The environment file retains the original run metadata and source hashes. Source comments and documentation were later revised without changing the executable algorithm, benchmark, or test statements; `evidence/source_integrity.json` records the corresponding historical and current hashes. The portable evidence verifier was added for independent checks. Measurement values remain unchanged.

## Files

| File | Purpose |
| --- | --- |
| `selection.py` | Contains deterministic and randomized selection with one-based ranks and input preservation |
| `structures.py` | Implements dynamic arrays, matrices, array-backed stacks, circular queues, and singly linked lists |
| `test_assignment.py` | Contains eight unit-test methods for selection and data-structure behavior |
| `benchmark.py` | Runs the paired selection experiment and saves verified measurements without overwriting an existing run |
| `verify_evidence.py` | Independently checks recorded results, summary arithmetic, and source integrity without changing files |
| `evidence/benchmark_raw.csv` | Stores 90 individual timing observations, ranks, seeds, execution order, input hashes, and correctness checks |
| `evidence/benchmark_summary.csv` | Stores nine condition summaries with median, minimum, and maximum times for each algorithm |
| `evidence/benchmark_environment.json` | Records the original runtime, measurement method, limitations, and source hashes |
| `evidence/source_integrity.json` | Records documentation-only source changes, executable statement hashes, and the portable verifier |
| `WeevernGong_Assignment6_Medians_and_Order_Statistics_and_Elementary_Data_Structures.docx` | Formal report covering implementation, analysis, measurements, applications, and references |

## Example

Input and requested rank:

```text
values = [7, 2, 5, 2, 9]
k = 3
```

Both functions return:

```text
5
```

The sorted order is `[2, 2, 5, 7, 9]`, so the third smallest value is `5`. Repeated values count as separate occurrences, and the original list remains `[7, 2, 5, 2, 9]`.

## Summary of Findings

Randomized selection had a lower median execution time in all nine measured conditions. At 10,000 elements, the random-input medians were 1.9821 ms for deterministic selection and 0.9120 ms for randomized selection. Sorted-input medians were 1.4784 ms and 0.6349 ms, while reverse-sorted medians were 1.5050 ms and 0.6360 ms. Sorting small groups and recursively selecting the deterministic pivot may explain some of its additional runtime, but the experiment does not measure those costs separately.

Median-of-medians provides O(n) worst-case time. Randomized selection provides O(n) expected time but can still take O(n²) with repeatedly poor pivots. Both implementations use O(n) peak auxiliary reference storage because they copy the input and allocate partitions. These bounds assume constant-cost comparisons and reference operations; Python object memory was not measured.

The data structures have different operation costs. Dynamic arrays provide O(1) indexed access and amortized O(1) append, while arbitrary insertion or deletion requires shifts. Array-stack pushes and circular-queue enqueues are amortized O(1); stack pops and queue dequeues take O(1). The queue avoids shifting values on removal. Linked-list head operations take O(1), while locating a node by index requires traversal. Matrix cell access takes O(1), and structural changes insert or remove rows with a fixed column count. The report explains their memory costs and where each representation is useful.

The timing comparison uses one machine, one input array per condition, three sizes, and five trials per algorithm and condition. Background activity was uncontrolled. These results compare the implemented programs but do not prove their asymptotic bounds or worst-case latency. Duplicate-heavy and all-equal inputs were tested for correctness rather than timed separately. The targeted tests provide evidence for the checked cases, not exhaustive correctness.
