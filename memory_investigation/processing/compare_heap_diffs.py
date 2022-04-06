#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
Generates second differential for heap.

This script helps us filter out objects in heap, which we have already investigated in a baseline train.

Let's say we have two iOS trains (Sky and Azul). We collect memgraphs on Azul, A1, A2, A3.. A9.

We calculate heap diff between A1 and A9 and write output in heap_diff_A.txt
Now, we caluclate heap diff on memgraphs collected for Sky;  S1,S2, .. S9 and write output in heap_diff_S.txt

To investigate new memory growth areas in S, we need to diff  heap_diff_A.txt and heap_diff_S.txt
"""

import argparse
import os

from HeapCommon import HeapObjectAndCountGenerator


def diff_object_counts(baseline,
                       target):
    """
    Compares two dictionaries of [Object_type: HeapObjectAndCounts]
    :param baseline: Dictionary [Object_type: HeapObjectAndCounts] for baseline
    :param target: Dictionary [Object_type: HeapObjectAndCounts] for target
    :return: None

    Prints metrics for differences in count
    """
    diff_counts = {}

    for object_type in target.keys():
        target_count = target.get(object_type).object_count
        target_bytes = target.get(object_type).total_bytes
        baseline_counts = baseline.get(object_type, None)

        baseline_count = 0
        baseline_size = 0
        if baseline_counts:
            baseline_count = baseline_counts.object_count
            baseline_size = baseline_counts.total_bytes

        diff_counts[object_type] = {"target": target_count,
                                    "baseline_count": baseline_count,
                                    "diff_count": int(target_count) - int(baseline_count),
                                    "diff_bytes": int(target_bytes) - int(baseline_size)}

    return sorted(diff_counts.items(), key=lambda x: x[1]["diff_bytes"], reverse=True)


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Compares heap growth across releases. '
                                                 'Collect heap_diff for two iOS releases '
                                                 'and then use this script to check where memory growth has increased')
    parser.add_argument(
        '--baseline',
        '-b',
        dest="baseline_heap_diff",
        default=None,
        required=True,
        help="Path to heap_diff generated from memgraphs on baseline build")

    parser.add_argument(
        '--target',
        '-t',
        dest="target_heap_diff",
        default=None,
        required=True,
        help="Path to heap_diff generated from memgraphs on build under test")

    parser.add_argument(
        '--output',
        '-o',
        dest="out_path",
        default="/tmp/heap_diff.csv",
        required=False,
        help="Output path where heap diff will be generated")

    # Validate input
    args = parser.parse_args()
    if not os.path.isfile(args.baseline_heap_diff):
        print("Invalid Baseline provided : {}".format(args.baseline_heap_diff))
        sys.exit(-1)

    if not os.path.isfile(args.target_heap_diff):
        print("Invalid target provided : {}".format(args.target_heap_diff))
        sys.exit(-1)

    # Parse two heap_diffs
    baseline_object_counts = HeapObjectAndCountGenerator.generate_from_heap(path=args.baseline_heap_diff)
    if len(baseline_object_counts) == 0:
        sys.exit("Heap diff at {} could not be parsed".format(args.baseline_heap_diff))

    target_object_counts = HeapObjectAndCountGenerator.generate_from_heap(path=args.target_heap_diff)
    if len(target_object_counts) == 0:
        sys.exit("Heap diff at {} could not be parsed".format(args.baseline_heap_diff))

    # Diff heap_diffs (second derivative)
    diff_counts = diff_object_counts(baseline=baseline_object_counts,
                                     target=target_object_counts)

    with open(args.out_path, "w") as f_:
        for t in diff_counts:
            class_name = t[0]  # Class name
            object_counts = t[1]  # Counts

            if object_counts["diff_count"] != 0:
                f_.write("{}, {}, {}, {}, {}\n".format(class_name,
                                                       object_counts["diff_count"],
                                                       object_counts["diff_bytes"],
                                                       object_counts["baseline_count"],
                                                       object_counts["target"]))
        f_.close()

        print(f"Output CSV created at: {args.out_path}")
