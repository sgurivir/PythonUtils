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


class HeapObjectAndCounts:
    def __init__(self,
                 class_name,
                 object_type,
                 object_count,
                 total_bytes,
                 avg_size,
                 binary_name):
        self.class_name = class_name
        self.object_type = object_type
        self.object_count = object_count
        self.total_bytes = total_bytes
        self.avg_size = avg_size
        self.binary_name = binary_name

    @staticmethod
    def generate_from(line_in_heap_diff):
        """
        :param line_in_heap_diff:  text line in heap diff
        :return: An tuple of [object_type: HeapObjectAndCounts]
        """

        # Parse a string like
        #  17      55424    3260.2   _NSCallStackArray._frames (malloc[])              C       Foundation

        # Remove extra spaces
        line_in_heap_diff = " ".join(line_in_heap_diff.split())

        tokens = line_in_heap_diff.split(" ")
        if len(tokens) < 5:
            if not line_in_heap_diff.isspace():
                print("Ignoring line {}".format(line_in_heap_diff))
            return None

        object_count = tokens[0]
        total_bytes = tokens[1]
        avg_size = tokens[2]
        binary_name = tokens[-1]
        object_type = tokens[-2]
        class_name = "".join(tokens[3:-2])

        h = HeapObjectAndCounts(class_name=class_name,
                                object_type=object_type,
                                object_count=object_count,
                                total_bytes=total_bytes,
                                avg_size=avg_size,
                                binary_name=binary_name)

        return h


def count_of_objects_from_heap_diff(path):
    """
    :param path: Path to heap diff file
    :return: A dictionary of [Object_type: HeapObjectAndCounts]
    """
    object_type_and_counts = {}  # Dictionary of [String: HeapObjectAndCounts]

    with open(path, 'r') as f:
        # Keep reading until we find line with ==="
        line_underscored_before_metrics_found = False

        line = f.readline()
        while line:
            if "====" in line:
                line_underscored_before_metrics_found = True
                break
            line = f.readline()

        if line_underscored_before_metrics_found:
            line = f.readline()
            while line:
                counts = HeapObjectAndCounts.generate_from(line)
                if object_type is not None:
                    object_type_and_counts[counts.object_type] = counts
                line = f.readline()
        f.close()

    return object_type_and_counts


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
        baseline_counts = baseline.get(object_type, None)
        if baseline_counts:
            baseline_count = baseline_counts.object_count
        else:
            baseline_count = 0

        diff_counts[object_type] = {"target": target_count,
                                    "baseline_count": baseline_count,
                                    "diff": int(target_count) - int(baseline_count)}

    return sorted(diff_counts.items(), key=lambda x: x[1]["diff"], reverse=True)


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
        default="/tmp/heap_diff_second_derivative.txt",
        required=False,
        help="Output path where heap difference growth between two releases will be generated")

    # Validate input
    args = parser.parse_args()
    if not os.path.isfile(args.baseline_heap_diff):
        raise Exception("Invalid Baseline provided : {}".format(args.baseline_heap_diff))

    if not os.path.isfile(args.target_heap_diff):
        raise Exception("Invalid target provided : {}".format(args.target_heap_diff))

    # Parse two heap_diffs
    baseline_object_counts = count_of_objects_from_heap_diff(path=args.baseline_heap_diff)
    if len(baseline_object_counts) == 0:
        sys.exit("Heap diff at {} could not be parsed".format(args.baseline_heap_diff))

    target_object_counts = count_of_objects_from_heap_diff(path=args.target_heap_diff)
    if len(target_object_counts) == 0:
        sys.exit("Heap diff at {} could not be parsed".format(args.baseline_heap_diff))

    # Diff heap_diffs (second derivative)
    diff_counts = diff_object_counts(baseline=baseline_object_counts,
                                     target=target_object_counts)
    for t in diff_counts:
        class_name = t[0]  # Class name
        object_counts = t[1]  # Counts
        print("{}, {}, {}, {}".format(object_counts["diff"],
                                      object_counts["baseline_count"],
                                      object_counts["target"],
                                      class_name))
