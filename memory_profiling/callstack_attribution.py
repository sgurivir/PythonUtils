#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
This script finds callstacks where a particular type of object is allocated.

Example:
    callback_attribution.py -i <dir_with_memgraphs> -t "icu::DecimalFormatSymbols"
"""

import argparse
import glob
import os
import sys


def sorted_memgraphs_in_dir(path):
    """
    returns a list of memgraphs found in provided directory
    :param(path): directory to search memgraph files
    :return: Paths to memgraphs, sorted in canonical order
    """
    memgraphs = glob.glob(path + '/*.memgraph', recursive=False)

    if len(memgraphs) == 0:
        sys.exit(f"No memgraphs found in provided directory {path}")

    memgraphs.sort()
    return memgraphs


def get_paths_to_memgraphs(file_or_directory):
    """
    Enumerate memgraphs in a directory
    """
    if not os.path.exists(file_or_directory):
        sys.exit(f"Path provided does not exist : {file_or_directory}")

    if os.path.isfile(file_or_directory):
        return [file_or_directory]

    if os.path.isdir(file_or_directory):
        memgraphs = sorted_memgraphs_in_dir(file_or_directory)

        if len(memgraphs) == 0:
            sys.exit(f"No memgraphs found in directory provided : {file_or_directory}")

        return memgraphs

    return []


def pick_memgraphs(paths_to_memgraphs):
    """
    If we have more than two memgraphs, pick two which would best fit for analysis.

    We need two memgraphs to do a diff of heaps. For the first one, we pick memgraph at
    around 20% of time (based on count). Then we pick the last memgraph.

    We do it this way because we need to give locationd some time to warm up and fillup
    all the caches.
    """
    num_memgraphs = len(paths_to_memgraphs)

    if num_memgraphs <= 1:
        sys.exit(f"Too few memgraphs {num_memgraphs}. Can't investigate growth")

    first = paths_to_memgraphs[0]
    twentieth_percentile = int(0.2 * num_memgraphs)
    if num_memgraphs >= 4:
        first = paths_to_memgraphs[twentieth_percentile]

    return first, paths_to_memgraphs[-1]


def generate_callstack_attribution(memgraph1,
                                   memgraph2,
                                   object_type,
                                   out_dir):
    """
    Runs the following command

    heap -s --addresses='NSMutableDictionary.*Storage.*' --guessNonObjects --sumObjectFields \
    new.memgraph --diffFrom old.memgraph | grep NSMutableDictionary\
     |  cut -f1 -d":" |grep 0x | \
     xargs -L1 malloc_history -fullStacks new.memgraph

    returns path to file where callstacks are generated.
    """
    # Replace special characters with ".*"
    datatype = object_type
    datatype = datatype.replace(" ", ".*")
    datatype = datatype.replace("(", ".*")
    datatype = datatype.replace(")", ".*")
    datatype = datatype.replace("::", ".*")
    datatype = datatype.replace("<", ".*")
    datatype = datatype.replace(">", ".*")
    datatype = datatype.replace(", ", ".*")
    print(f"Using datatype: {datatype} ")

    # Generate Output file path name
    output_file_name = "{}_callstacks.txt".format(datatype.replace(".*", "_"))
    output_path = os.path.join(out_dir, output_file_name)

    command = "heap -s --addresses='{}' --guessNonObjects --sumObjectFields ".format(datatype)
    command += "{} --diffFrom {}".format(memgraph2, memgraph1)
    command += " | grep \"{}\" ".format(object_type)
    command += " | cut -f1 -d\":\" "
    command += " | grep 0x "
    command += " | xargs -L1 malloc_history -fullStacks {} ".format(memgraph2)
    command += " > {}".format(output_path)

    print(f"Running : {command}")
    os.system(command)

    return output_path


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Identify callstacks which allocated a type of object')

    parser.add_argument(
        '--input',
        '-i',
        dest="memgraphs_dir",
        default=None,
        required=True,
        help="Path to a memgraph")

    parser.add_argument(
        '--type',
        '-t',
        dest="object_type",
        default=None,
        required=True,
        help="Type of Object to be investigated")

    args = parser.parse_args()
    print("\n========== Validating arguments ===========")
    if not os.path.isdir(args.memgraphs_dir):
        print(f"Invalid directory provided: {args.memgraphs_dir}")
        sys.exit(-1)

    print("\n========= Collecting memgraph(s) =====")
    input_memgraphs = get_paths_to_memgraphs(args.memgraphs_dir)
    print("{}".format("\n".join(input_memgraphs)))

    print("\n========= Picking memgraph(s) ======")
    first_memgraph, last_memgraph = pick_memgraphs(paths_to_memgraphs=input_memgraphs)
    print(f"Picked for analysis: \n\t {first_memgraph} and \n\t {last_memgraph}")

    print(f"\n========= Generating callstack attribution for Object {args.object_type} ======")
    attribution_result_file = generate_callstack_attribution(memgraph1=first_memgraph,
                                                             memgraph2=last_memgraph,
                                                             object_type=args.object_type,
                                                             out_dir=args.memgraphs_dir)
    print("\n === Results ====")
    if os.stat(attribution_result_file).st_size == 0:
        print(f"**** NO Memory growth was identified for the object => {args.object_type} \n")
    else:
        print(f"Attribution generated at {attribution_result_file} \n")
