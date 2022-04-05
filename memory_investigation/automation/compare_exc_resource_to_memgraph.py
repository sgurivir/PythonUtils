#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
This script helps triage incoming radars with ExcResource files...a.k.a.  investigate a ExcResource file
generated on a device with MallocStackLogging NOT enabled.

To investigate ExcResource file, we extract counts of heap objects from the file. Then, we compare the growth
of objects in memgraphs generated on a different device. From the Object Types in ExcResource file, we make a best
guess on which callstacks are contributing to memory growth.

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
    parser = argparse.ArgumentParser(description='Makes best guess on which callstacks are '
                                                 'contributing to memory growth. Takes two memgraphs and a ExcResource'
                                                 'generated by OS. Compares ExcResource to baseline memgraph'
                                                 'and then finds who is allocating these objects in newer memgraph')
    parser.add_argument(
        '--beginning',
        '-b',
        dest="beginning_memgraph",
        default=None,
        required=True,
        help="Path to memgraph generated right after locationd warms up")

    parser.add_argument(
        '--end',
        '-e',
        dest="end_memgraph",
        default=None,
        required=True,
        help="Path to memgraph generated after living on")

    parser.add_argument(
        '--execResource',
        '-e',
        dest="exc_resource",
        default=None,
        required=True,
        help="ExecResource file to be investigated")

    # Validate input
    args = parser.parse_args()
    if not os.path.isfile(args.beginning_memgraph):
        print("Invalid memgraph provided : {}".format(args.beginning_memgraph))
    if not os.path.isfile(args.end_memgraph):
        print("Invalid memgraph provided : {}".format(args.end_memgraph))
    if not os.path.isfile(args.execResource):
        print("Invalid ExcResource provided : {}".format(args.execResource))

    if not os.path.isfile(args.target_heap_diff):
        raise Exception("Invalid target provided : {}".format(args.target_heap_diff))

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
    for t in diff_counts:
        class_name = t[0]  # Class name
        object_counts = t[1]  # Counts
        print("{}, {}, {}, {}".format(object_counts["diff"],
                                      object_counts["baseline_count"],
                                      object_counts["target"],
                                      class_name))