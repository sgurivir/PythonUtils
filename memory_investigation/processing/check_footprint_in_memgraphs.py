#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
This script analyzes generates a memtrend from a series of memgraphs for daemon.
"""

import argparse
import os

from FileSystemUtil import FileSystemUtil
from MemgraphUtil import MemgraphUtil


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
    memgraphs = FileSystemUtil.get_paths_to_memgraphs(args.memgraphs_dir)

    footprints = []
    for memgraph in memgraphs:
        footprints.append( MemgraphUtil.footprint_for(memgraph) )

    print(footprints)
    print("Footprint of process changed from {} to {}".format(footprints[0], footprints[-1]))
