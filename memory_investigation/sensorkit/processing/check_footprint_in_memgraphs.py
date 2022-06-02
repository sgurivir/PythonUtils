#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
This script analyzes generates a memtrend from a series of memgraphs for daemon.
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
    memgraphs = glob.glob(path + '/*.memgraph', recursive=False)

    if len(memgraphs) == 0:
        raise Exception("No memgraphs found in provided direcory {path}")

    memgraphs.sort()

    return memgraphs


def footprint_of_memgraph(path_to_memgraph):
    """
    returns footprint from memgraph
    :param path_to_memgraph: Path to memgraph
    :return:
    """
    p1 = subprocess.Popen(["footprint", path_to_memgraph], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", "phys_footprint: "], stdin=p1.stdout, stdout=subprocess.PIPE)
    footprint = p2.communicate()[0].decode("utf-8")

    footprint = footprint.replace("phys_footprint: ", "")
    footprint = footprint.replace("\n", "")
    footprint = footprint.replace("\t", "")
    return footprint


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Inspect footprint growth of daemon in memgraphs')
    parser.add_argument(
        '--dir',
        '-d',
        dest="memgraphs_dir",
        default=None,
        required=True,
        help="Path to directory with daemon memgraphs")
    parser.add_argument(
        '--daemon_name',
        '-n',
        dest="daemon_name",
        default="locationd",
        required=False,
        help="Name of daemon")

    args = parser.parse_args()
    if not os.path.isdir(args.memgraphs_dir):
        raise Exception("Invalid directory provided : {args.memgraphs_dir}")

    # List memgraphs in provided directory
    memgraphs = sorted_memgraphs_in_dir(args.memgraphs_dir)

    footprints = []
    for memgraph in memgraphs:
        footprints.append( footprint_of_memgraph(memgraph) )

    print(footprints)
    print("Footprint of process changed from {} to {}".format(footprints[0], footprints[-1]))
