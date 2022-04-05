#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
This script analyzes generates a memtrend from a series of memgraphs for any daemon.
"""

import argparse
import os
import sys


from FileSystemUtil import FileSystemUtil
from FootprintPlotter import FootprintPlotter
from Symbolicator import Symbolicator
from MemgraphUtil import MemgraphUtil
from MemoryTools import MemoryTools

MAX_MEMGRAPHS_TO_PROCESS = 6


def indices_with_same_daemon_pid(pids):
    """
    From a list of pids, find the consequtive block of indices with same PID as last one.
    Example
        Input: pids: [2 3 4 5 5 5 5 5 5 5 5]
        Return : 3, 10 { Indices from 3 -10 have same PID
    :param pids:
    :return:
    """
    last_pid = pids[-1]
    first_index_with_same_pid = pids.index(last_pid)

    return first_index_with_same_pid, len(pids) - 1


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Process daemon memgraphs and generate memtrend')
    parser.add_argument(
        '--dir',
        '-d',
        dest="memgraphs_dir",
        default=None,
        required=True,
        help="Path to directory with daemon memgraphs")

    parser.add_argument(
        '--symbolPath',
        '-s',
        dest="symbol_path",
        default=None,
        required=False,
        help="Path to daemon dSYMs")

    parser.add_argument(
        '--daemon_name',
        '-n',
        dest="daemon_name",
        default="locationd",
        required=False,
        help="Name of daemon - locationd, sensorkitd")

    parser.add_argument(
        '--memtrend',
        '-m',
        dest="path_to_memtrend",
        default=None,
        required=False,
        help="Path to output where memtrend should be generated")

    parser.add_argument(
        '--ardiff_flame',
        '-f',
        dest="path_to_ardiff_flame",
        default=None,
        required=False,
        help="Path to output where ardiff should be generated")

    parser.add_argument(
        '--fragmentation_report',
        '-z',
        dest="path_to_fragmentation_report",
        default=None,
        required=False,
        help="Path to output where fragmentation report should be generated")

    parser.add_argument(
        '--out_footprint_plot',
        '-p',
        dest="path_to_footprint_plot",
        default=None,
        required=False,
        help="Path to output where footprint plot should be generated")

    parser.add_argument(
        '--include_first',
        '-i',
        dest="include_first",
        type=bool,
        default=False,
        help="Should include first memgraph in analysis")

    parser.add_argument('--no_symbolication',
                        dest='no_symbolication',
                        action='store_true',
                        help="Don't symbolicate memgraphs")
    parser.set_defaults(no_symbolication=False)

    args = parser.parse_args()
    if not os.path.isdir(args.memgraphs_dir):
        sys.exit(f"Invalid directory provided : {args.memgraphs_dir}")

    # Where we should output ardiff
    path_to_ardiff_flame = args.path_to_ardiff_flame
    if path_to_ardiff_flame is None:
        path_to_ardiff_flame = os.path.join(args.memgraphs_dir,
                                            f"ardiff_{args.daemon_name}.html")

    # Where we should output memtrend
    path_to_memtrend = args.path_to_memtrend
    if path_to_memtrend is None:
        path_to_memtrend = os.path.join(args.memgraphs_dir,
                                        f"{args.daemon_name}_memtrend.txt")

    # Where we should output fragmentation report
    path_to_fragmentation_report = args.path_to_fragmentation_report
    if path_to_fragmentation_report is None:
        path_to_fragmentation_report = os.path.join(args.memgraphs_dir,
                                                   f"{args.daemon_name}_fragmentation_report.txt")

    # Where we should output Plot of footprints
    path_to_footprint_plot = args.path_to_footprint_plot
    if path_to_footprint_plot is None:
        path_to_footprint_plot = os.path.join(args.memgraphs_dir,
                                        f"{args.daemon_name}_footprints.png")

    # Where should we output CSV of memgraphs with os_transaction
    path_to_zero_os_transactions_csv = os.path.join(args.memgraphs_dir,
                                                    "zero_os_transactions.csv")

    # List memgraphs in provided directory
    memgraphs = FileSystemUtil.sorted_files_in_dir(args.memgraphs_dir, extension="memgraph")

    # Validate memgraphs
    MemgraphUtil.validate_is_generated_for_daemon(memgraphs, args.daemon_name)
    MemgraphUtil.validate_pid_has_not_changed(memgraphs, args.daemon_name)

    # Pick which memgraphs to be used for analysis
    memgraphs = FileSystemUtil.pick_memgraphs_for_analysis(memgraphs_=memgraphs,
                                                           max_count=MAX_MEMGRAPHS_TO_PROCESS,
                                                           skip_first_if_more_than_two=args.include_first)

    # Symbolicate
    if not args.no_symbolication:
        symbol_path = args.symbol_path
        if symbol_path is None:
            symbol_path = os.path.join(args.memgraphs_dir, "symbols/")
        Symbolicator.symbolicate_memgraphs(memgraphs, symbol_path)

    # Generate malloc_history
    MemoryTools.generate_malloc_history(paths_to_memgraphs=memgraphs,
                                        out_dir=args.memgraphs_dir)

    # Generate memtrend
    MemoryTools.generate_memtrend(paths_to_memgraphs=memgraphs,
                                  out_path=path_to_memtrend)

    # Generate heap diff
    MemoryTools.generate_heap_diff(paths_to_memgraphs=memgraphs,
                                   out_dir=args.memgraphs_dir)

    # Find memgraphs with zero transactions
    MemoryTools.find_memgraphs_with_zero_transactions(paths_to_memgraphs=memgraphs,
                                                      out_csv=path_to_zero_os_transactions_csv)

    # Generate flamegraph
    MemoryTools.generate_flamegraph(paths_to_memgraphs=memgraphs,
                                    out_path=path_to_ardiff_flame)

    # Find fragmentation
    MemoryTools.generate_fragmentation_stats(paths_to_memgraphs=memgraphs,
                                             out_path=path_to_fragmentation_report)

