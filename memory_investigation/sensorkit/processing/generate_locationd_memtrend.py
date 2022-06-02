#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
This script analyzes generates a memtrend from a series of memgraphs for locationd.
"""

import argparse
import glob
import os
import subprocess
import re


def sorted_memgraphs_in_dir(path):
    """
    returns a list of memgraphs found in provided directory
    :param(path): directory to search memgraph files
    :return:
    """
    print("======Enumerating memgraphs ===")
    memgraphs = glob.glob(path + '/*.memgraph', recursive=False)

    if len(memgraphs) == 0:
        raise Exception("No memgraphs found in provided direcory {path}")

    memgraphs.sort()

    return memgraphs


def pids_from_memgraphs(paths_to_memgraphs):
    """
    From a list of memgraphs, generate the pid of locationd from the memgraph
    :param paths_to_memgraphs: a list of collected memgraphs
    :return: a list of locationd pids
    """
    locationd_pids = []

    for memgraph in paths_to_memgraphs:
        print(memgraph)
        p1 = subprocess.Popen(["footprint", memgraph],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        p2 = subprocess.Popen(['grep', 'locationd'],
                              stdin=p1.stdout,
                              stdout=subprocess.PIPE)
        p1.stdout.close()
        stdout, _ = p2.communicate()
        stdout = stdout.decode("utf-8")

        # The line would like
        # locationd [76] (memgraph): 64-bit\tFootprint: 71 MB (16384 bytes per page)\n'
        # Extract PID from such a line
        opening_bracket_index = stdout.index('[')
        closing_bracket_index = stdout.index(']')
        pid = stdout[opening_bracket_index + 1:closing_bracket_index]
        locationd_pids.append(pid)

    return locationd_pids


def symbolicate_memgraphs(paths_to_memgraphs):
    print("=====Symbolicating memgraphs====")
    for memgraph in paths_to_memgraphs:
        print("\t Symbolicating {} ".format(memgraph))
        os.system("leaks --symbolicate {}".format(memgraph))


def generate_memtrend(paths_to_memgraphs, out_path, ignore_first_memgraph):
    """
    Generate a memtrend from a list of memgraphs
    :param paths: Input memgraphs
    :param out_path: Output to memtrend
    :return: None
    """
    if ignore_first_memgraph == True:
        paths_to_memgraphs.pop(0)

    memgraphs_concatenated = " ".join(paths_to_memgraphs)
    command = "memtrend  -guessNonObjects  -showSizes {}".format(memgraphs_concatenated)

    print("=====Generating memtrend at {} ....\n".format(out_path))
    print("\t Running: {}".format(command))
    os.system("{} > {}".format(command,
                               out_path))


def generate_malloc_history(paths_to_memgraphs, out_dir, ignore_first_memgraph):
    """
    Run malloc_history on memgraphs
    :param paths: Input memgraphs
    :param out_dir: Output directory
    :return: None
    """
    print("=====Generating malloc_history for memgraphs====")
    if ignore_first_memgraph == True:
        paths_to_memgraphs.pop(0)
  
    for memgraph in paths_to_memgraphs:
        out_path = memgraph
        out_path = out_path.replace(".memgraph", ".txt")

        consolidated_out_path = out_path.replace("memgraph_", "malloc_history_consolidated_")
        command = "malloc_history -callTree -consolidateAllBySymbol {} > {}".format(memgraph, consolidated_out_path)
        print(command)
        os.system("{}".format(command))

    # Generate malloc_history with fullStacks for last memgraph
    out_path = "{}/{}".format(out_dir, "malloc_history_fullStacks.txt")
    command = "malloc_history --fullStacks -allBySize  {} > {}".format(paths_to_memgraphs[-1],
                                                                       out_path)
    print(command)
    os.system("{}".format(command))


def generate_flamegraph(paths_to_memgraphs, out_path):
    """
    Generate a flamegraph from a list of memgraphs
    :param paths: Input memgraphs
    :param out_path: Output to flamegraph
    :return: None
    """
    paths_to_memgraphs.sort()

    memgraphs_concatenated = " ".join(paths_to_memgraphs)
    command = "ardiff callstacks  -o {}  --flame  {}".format(out_path,
                                                             memgraphs_concatenated)

    print("======Generating flamegraph at {} ....\n".format(out_path))
    print("\t Running: {}".format(command))
    os.system("{}".format(command))
    print("Done")


def indices_with_same_locationd_pid(pids):
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
    parser = argparse.ArgumentParser(description='Process locationd memgraphs and generate memtrend')
    parser.add_argument(
        '--dir',
        '-d',
        dest="memgraphs_dir",
        default=None,
        required=True,
        help="Path to directory with locationd memgraphs")

    parser.add_argument(
        '--memtrend',
        '-m',
        dest="path_to_memtrend",
        default="/tmp/memtrend.txt",
        required=False,
        help="Path to output where memtrend should be generated")

    parser.add_argument(
        '--ardiff_flame',
        '-f',
        dest="path_to_ardiff_flame",
        default="/tmp/ardiff.html",
        required=False,
        help="Path to output where ardiff should be generated")
        
    
    parser.add_argument(
        '--ignore_first',
        '-i',
        dest="ignore_first_memgraph",
        action='store_true',
        help="Should ignore first memgraph in analysis")

    args = parser.parse_args()
    if not os.path.isdir(args.memgraphs_dir):
        raise Exception("Invalid directory provided : {args.memgraphs_dir}")

    # List memgraphs in provided directory
    memgraphs = sorted_memgraphs_in_dir(args.memgraphs_dir)

    # Get locationd PIDs and filter
    locationd_pids = pids_from_memgraphs(memgraphs)
    start_index, end_index = indices_with_same_locationd_pid(locationd_pids)

    # Symbolicate
    symbolicate_memgraphs(memgraphs)
    
    
    # Generate malloc_history
    generate_malloc_history(paths_to_memgraphs=memgraphs,
                            out_dir=args.memgraphs_dir,
                            ignore_first_memgraph=args.ignore_first_memgraph)

    # Generate memtrend
    generate_memtrend(paths_to_memgraphs=memgraphs,
                      out_path=args.path_to_memtrend,
                      ignore_first_memgraph=args.ignore_first_memgraph)

    # Generate flamegraph
    generate_flamegraph(paths_to_memgraphs=memgraphs,
                        out_path=args.path_to_ardiff_flame)
