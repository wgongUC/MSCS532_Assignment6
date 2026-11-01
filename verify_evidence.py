# Name: Weevern Gong
# Project Title: MSCS532_Assignment6
# Description: This program verifies the saved selection measurements and source files

# Evidence verification explanation:
# Recreate the seeded input lists, check the result and rank from every trial,
# and calculate the summary statistics again from the saved nanosecond values
# Source hashes identify the measured code and any later documentation-only edits
# The program reads evidence from its own folder and does not replace saved results

import ast
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import random
import statistics


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def executable_hash(path):
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=path.name)

    # Documentation strings do not change the algorithm or test statements
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.body and isinstance(node.body[0], ast.Expr):
                value = node.body[0].value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    node.body.pop(0)
    normalized = ast.dump(tree, include_attributes=False).encode('utf-8')
    return hashlib.sha256(normalized).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    root = Path(__file__).resolve().parent
    evidence = root / 'evidence'
    with (evidence / 'benchmark_raw.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    with (evidence / 'benchmark_summary.csv').open(newline='', encoding='utf-8') as stream:
        summaries = list(csv.DictReader(stream))
    metadata = json.loads((evidence / 'benchmark_environment.json').read_text(encoding='utf-8'))

    # Each size and input arrangement has five measured trials for both algorithms
    sizes = (100, 1000, 10000)
    distributions = ('random', 'sorted', 'reverse-sorted')
    algorithms = ('deterministic', 'randomized')
    require(len(rows) == 90 and len(summaries) == 9, 'Unexpected measurement or summary count')
    expected = {(str(n), distribution, algorithm): 5
                for n in sizes for distribution in distributions for algorithm in algorithms}
    actual = Counter((row['n'], row['distribution'], row['algorithm']) for row in rows)
    require(actual == expected, 'Incomplete measurement conditions')
    summary_conditions = [(int(row['n']), row['distribution']) for row in summaries]
    require(Counter(summary_conditions) == Counter((n, d) for n in sizes for d in distributions),
            'Missing or repeated summary condition')

    for n in sizes:
        generator = random.Random(532 + n)
        cases = {'random': [generator.randrange(-n, n + 1) for _ in range(n)],
                 'sorted': list(range(n)), 'reverse-sorted': list(range(n - 1, -1, -1))}
        for distribution, values in cases.items():
            digest = hashlib.sha256(json.dumps(values, separators=(',', ':')).encode('ascii')).hexdigest()
            k = (n + 1) // 2
            expected_value = sorted(values)[k - 1]
            case_rows = [row for row in rows if int(row['n']) == n and row['distribution'] == distribution]

            # A trial pair must contain the same input and rank in the recorded order
            for trial in range(1, 6):
                pair = [row for row in case_rows if int(row['trial']) == trial]
                require(len(pair) == 2 and {row['algorithm'] for row in pair} == set(algorithms),
                        'Missing or repeated algorithm within a trial pair')
                order = list(algorithms) if trial % 2 else list(reversed(algorithms))
                ordered_pair = sorted(pair, key=lambda row: int(row['order_position']))
                require([int(row['order_position']) for row in ordered_pair] == [1, 2],
                        'Invalid execution positions')
                require([row['algorithm'] for row in ordered_pair] == order, 'Incorrect alternating order')
                for row in pair:
                    require(int(row['k']) == k and row['input_sha256'] == digest, 'Input or rank mismatch')
                    require(int(row['expected']) == int(row['result']) == expected_value, 'Incorrect selected value')
                    require(int(row['data_seed']) == 532 + n and int(row['pivot_seed']) == 531 + trial,
                            'Unexpected input or pivot seed')
                    require(row['input_preserved'] == 'True', 'Input preservation check did not pass')
                    require(int(row['nanoseconds']) >= 0, 'Negative elapsed time')

            # Recalculate the medians and ranges instead of trusting the summary file
            summary = next(row for row in summaries
                           if int(row['n']) == n and row['distribution'] == distribution)
            require(int(summary['repetitions_per_algorithm']) == 5, 'Unexpected trial count')
            for algorithm in algorithms:
                samples = [int(row['nanoseconds']) for row in case_rows if row['algorithm'] == algorithm]
                for label, calculation in (('median', statistics.median), ('min', min), ('max', max)):
                    field = algorithm + '_' + label + '_ms'
                    require(float(summary[field]) == calculation(samples) / 1e6, 'Summary mismatch: ' + field)

    require(metadata['measured_observations'] == 90 and metadata['warmup_calls'] == 18
            and metadata['repeats'] == 5, 'Environment counts do not match the experiment')
    require(metadata['sizes'] == list(sizes) and metadata['distributions'] == list(distributions),
            'Environment conditions do not match the experiment')

    # A fresh run records the current source hashes directly
    integrity_path = evidence / 'source_integrity.json'
    integrity = json.loads(integrity_path.read_text(encoding='utf-8')) if integrity_path.exists() else None
    require(set(metadata['source_sha256']) == {'selection.py', 'structures.py', 'benchmark.py'},
            'Measured source inventory is incomplete')
    for name, measured_hash in metadata['source_sha256'].items():
        require(name in ('selection.py', 'structures.py', 'benchmark.py'), 'Unexpected measured source file')
        current_hash = file_hash(root / name)
        if current_hash != measured_hash:
            require(integrity is not None, 'Measured source differs without an integrity record: ' + name)
            record = integrity['files'][name]
            require(record['historical_sha256'] == measured_hash, 'Historical source hash mismatch: ' + name)
            require(record['submission_sha256'] == current_hash, 'Submission source hash mismatch: ' + name)
            require(record['executable_ast_unchanged'] is True, 'Executable change recorded: ' + name)
            require(record['executable_ast_sha256'] == executable_hash(root / name),
                    'Executable statements changed: ' + name)

    # The submission record also covers tests and this portable verification program
    if integrity is not None:
        require(set(integrity['files']) == {'selection.py', 'structures.py', 'benchmark.py',
                                          'test_assignment.py', 'verify_evidence.py'},
                'Submission source inventory is incomplete')
        for name, record in integrity['files'].items():
            require(Path(name).name == name and name.endswith('.py'), 'Invalid source filename')
            require(file_hash(root / name) == record['submission_sha256'], 'Source integrity mismatch: ' + name)
            if 'executable_ast_sha256' in record:
                require(executable_hash(root / name) == record['executable_ast_sha256'],
                        'Executable integrity mismatch: ' + name)

    print(json.dumps({'status': 'PASS', 'observations': 90, 'paired_trials': 45,
                      'summary_rows': 9, 'input_rank_result_seed_order_checks': 'PASS',
                      'summary_arithmetic': 'PASS', 'source_integrity': 'PASS'}, indent=2))


if __name__ == '__main__':
    main()
