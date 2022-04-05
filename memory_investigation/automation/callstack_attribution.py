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

from FileSystemUtil import FileSystemUtil


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
    input_memgraphs = FileSystemUtil.get_paths_to_memgraphs(args.memgraphs_dir)
    print("{}".format("\n".join(input_memgraphs)))

    print("\n========= Picking memgraph(s) ======")
    first_memgraph, last_memgraph = FileSystemUtil.pick_two_memgraphs(paths_to_memgraphs=input_memgraphs,
                                                                      skip_first_if_more_than_two=True)
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
