# Name: Weevern Gong
# Project Title: MSCS532_Assignment6
# Description: This program compares deterministic and randomized selection.
# It saves individual timing trials, summary times, and the experiment environment.

# Performance comparison explanation: Test 100, 1000, and 10000 values using random,
# sorted, and reverse-sorted input. Each paired trial uses the same input and rank,
# and the algorithms alternate which runs first. Check one untimed warm-up and five
# measured trials per algorithm and condition. Input copying and partition allocation
# inside the public function are timed. Input creation, oracle sorting, generator
# setup, validation, warm-up, and file output are outside the timed call.
# Existing timing files are preserved; another run requires a separate output folder.


import csv
import gc
import hashlib
import json
import os
import platform
import random
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from selection import deterministic_select, randomized_select

SIZES = (100, 1000, 10000)
DISTRIBUTIONS = ('random', 'sorted', 'reverse-sorted')
REPEATS = 5
SEED = 532


def fingerprint(values):

    return hashlib.sha256(json.dumps(values, separators=(',', ':')).encode('ascii')).hexdigest()


def main():

    out = Path(__file__).resolve().parent / 'evidence'
    out.mkdir(exist_ok=True)
    targets = [out / ('benchmark_' + suffix) for suffix in
               ('raw.csv', 'summary.csv', 'environment.json')]
    # Stop before timing if this folder already contains recorded results
    if any(p.exists() for p in targets):
        raise FileExistsError('Preserve the previous evidence before running a new experiment.')
    started = datetime.now(timezone.utc).isoformat()
    wall_start = time.perf_counter()
    rows = []
    for n in SIZES:
        data_seed = SEED + n
        rng = random.Random(data_seed)
        cases = {'random': [rng.randrange(-n, n + 1) for _ in range(n)],
                 'sorted': list(range(n)),
                 'reverse-sorted': list(range(n - 1, -1, -1))}
        for distribution, values in cases.items():
            original = values.copy()
            input_sha256 = fingerprint(values)
            # Select the one-based lower median; for n = 100 the requested rank is 50
            k = (n + 1) // 2
            expected = sorted(values)[k - 1]

            # Check a separate untimed warm-up for each algorithm and condition
            warmups = (deterministic_select(values, k),
                       randomized_select(values, k, random.Random(SEED - 1)))
            if warmups != (expected, expected) or values != original:
                raise AssertionError('Warm-up output or input preservation failure')
            for trial in range(1, REPEATS + 1):
                # Alternate the first algorithm while keeping each paired input unchanged
                order = (('deterministic', 'randomized') if trial % 2 else
                         ('randomized', 'deterministic'))
                pivot_seed = SEED + trial - 1
                for order_position, name in enumerate(order, start=1):
                    pivot_rng = random.Random(pivot_seed)
                    # Generator setup stays outside timing; pivot draws remain inside selection
                    start = time.perf_counter_ns()
                    result = (deterministic_select(values, k) if name == 'deterministic'
                              else randomized_select(values, k, pivot_rng))
                    elapsed = time.perf_counter_ns() - start
                    # Accept the timing only after checking the result and the original input
                    if result != expected or values != original:
                        raise AssertionError('Measured output or input preservation failure')
                    rows.append(dict(n=n, distribution=distribution, algorithm=name,
                                     trial=trial, order_position=order_position, k=k,
                                     data_seed=data_seed, pivot_seed=pivot_seed,
                                     input_sha256=input_sha256, expected=expected,
                                     result=result, input_preserved=True, nanoseconds=elapsed))
    if len(rows) != 90:
        raise AssertionError('Expected exactly 90 observations')
    # Summarize exactly five observations for each algorithm and condition
    summary = []
    for n in SIZES:
        for distribution in DISTRIBUTIONS:
            record = dict(n=n, distribution=distribution, repetitions_per_algorithm=REPEATS)
            for name in ('deterministic', 'randomized'):
                samples = [r['nanoseconds'] for r in rows if r['n'] == n and
                           r['distribution'] == distribution and r['algorithm'] == name]
                if len(samples) != REPEATS:
                    raise AssertionError('Incomplete condition')
                record[name + '_median_ms'] = statistics.median(samples) / 1e6
                record[name + '_min_ms'] = min(samples) / 1e6
                record[name + '_max_ms'] = max(samples) / 1e6
            summary.append(record)
    # Record the environment, timing scope, limitations, and measured source hashes
    finished = datetime.now(timezone.utc).isoformat()
    metadata = dict(started_utc=started, finished_utc=finished,
                    experiment_wall_seconds=time.perf_counter() - wall_start,
                    python=sys.version, executable=sys.executable,
                    platform=platform.platform(), processor=platform.processor(),
                    machine=platform.machine(), logical_cpus=os.cpu_count(),
                    timer='perf_counter_ns', timer_info=vars(time.get_clock_info('perf_counter')),
                    gc_enabled=gc.isenabled(), sizes=SIZES, distributions=DISTRIBUTIONS,
                    seed=SEED, data_seed_rule='532 + n (used for random input only)',
                    pivot_seeds=list(range(SEED, SEED + REPEATS)), repeats=REPEATS,
                    measured_observations=len(rows), warmup_calls=18,
                    warmup_pivot_seed=SEED-1, rank='one-based lower median: (n + 1) // 2',
                    pairing='identical values and rank for both algorithms in each trial',
                    order='odd trials deterministic first; even trials randomized first',
                    timed='public API including input copy and partition allocations',
                    excluded='generation, oracle, RNG construction, warm-up, assertions, output',
                    limitations='one array per condition; five trials; median ranks; single machine; no memory measurements; background activity uncontrolled',
                    source_sha256={name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()
                                   for name in ('selection.py','structures.py','benchmark.py')})
    # Create new output files only after every measured call has passed validation
    for path, records in ((targets[0], rows), (targets[1], summary)):
        with path.open('x', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
    with targets[2].open('x', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(json.dumps(summary, indent=2))
    print('90 measured outputs and input preservation checks passed; 18 untimed warm-up calls passed.')


if __name__ == '__main__':
    main()
