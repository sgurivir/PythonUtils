#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
This script analyzes generates a memtrend from a series of memgraphs for any daemon.
"""

import argparse
import glob
import os
import subprocess
import sys

MAX_MEMGRAPHS_TO_PROCESS = 6


class MemgraphEnumerator:
    @staticmethod
    def sorted_memgraphs_in_dir(path):
        """
        returns a list of memgraphs found in provided directory
        :param(path): directory to search memgraph files
        :return: Paths to memgraphs, sorted in canonical order
        """
        print("\n\n======Enumerating memgraphs ===")
        memgraphs_at_dir = glob.glob(path + '/*.memgraph', recursive=False)

        if len(memgraphs_at_dir) == 0:
            sys.exit("No memgraphs found in provided directory {path}")

        memgraphs_at_dir.sort()
        print("\n\t".join(memgraphs_at_dir))

        return memgraphs_at_dir

    @staticmethod
    def pick_memgraphs_for_analysis(daemon_name, memgraphs_, include_first_):
        """
        If there are more than MAX_MEMGRAPHS_TO_PROCESS, pick
        first few and last few with same pid
        """
        print("\n======= Picking Memgraphs for analysis ======= ")
        # Get daemon PID and filter only the memgraphs for which
        # PID of daemon has not changed. This is to prevent using memgraphs after daemon crash.
        daemon_pids = MemgraphProcessor.pids_from_memgraphs(daemon=daemon_name,
                                                            paths_to_memgraphs=memgraphs)

        start_index, end_index = indices_with_same_daemon_pid(daemon_pids)
        if end_index < start_index + 1:
            sys.exit("Too few memgraphs to do memory analysis. "
                     f"Memgraphs with same index: {memgraphs_}, {start_index}, {end_index}")

        # Filter memgraphs to only those with same PID
        memgraphs_ = memgraphs_[start_index:end_index + 1]

        # Override include_first, if only two memgraphs are available
        if len(memgraphs_) <= 2:
            include_first_ = True

        # remove first memgraph, if needed
        if not include_first_:
            memgraphs_ = memgraphs_[1:]

        # Use at most MAX_MEMGRAPHS_TO_PROCESS memgraphs
        if len(memgraphs_) > MAX_MEMGRAPHS_TO_PROCESS:
            memgraphs_ = memgraphs_[0:3] + memgraphs_[-4:-1]

        print("\t\n\t".join(memgraphs_))

        return memgraphs_

class MemgraphProcessor:
    @staticmethod
    def validate_memgraphs_are_for_daemon(paths_to_memgraphs,
                                          daemon_name):
        """
        :param paths_to_memgraphs: Paths to memgraphs
        :param daemon_name: Name of daemon
        :return: None
        """
        print("\n\n======Validating memgraphs ======")
        for memgraph in paths_to_memgraphs:
            with subprocess.Popen(["footprint", memgraph],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as p_1:
                with subprocess.Popen(['grep', daemon_name],
                                      stdin=p_1.stdout,
                                      stdout=subprocess.PIPE) as p_2:
                    p_1.stdout.close()
                    stdout, _ = p_2.communicate()
                    stdout = stdout.decode("utf-8")

                    # Validate the memgraph was generated for this daemon
                    if stdout == "":
                        sys.exit(f"ERROR: memgraph {memgraph} was not generated for daemon {daemon_name}. "
                                 "You can override daemon through arguments")

        print(f"Validation: Successful. All memgraphs were generated for process {daemon_name}")

    @staticmethod
    def pids_from_memgraphs(daemon, paths_to_memgraphs):
        """
        From a list of memgraphs, generate the pid of daemon from the memgraph
        :param daemon: process name for daemon
        :param paths_to_memgraphs: a list of collected memgraphs
        :return: a list of daemon pids and a dictionary of date to footprint
        """

        # The line producted by footprint command is like below. Extract footprint from the line
        # daemon [76] (memgraph): 64-bit\tFootprint: 71 MB (16384 bytes per page)\n'
        def pid_from(line):
            opening_bracket_index = line.index('[')
            closing_bracket_index = line.index(']')
            return line[opening_bracket_index + 1:closing_bracket_index]

        # iterate over memgraphs
        daemon_pids = []
        for memgraph in paths_to_memgraphs:
            with subprocess.Popen(["footprint", memgraph],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as p_1:
                with subprocess.Popen(['grep', daemon],
                                      stdin=p_1.stdout,
                                      stdout=subprocess.PIPE) as p_2:
                    p_1.stdout.close()
                    stdout, _ = p_2.communicate()
                    stdout = stdout.decode("utf-8")

                    pid = pid_from(stdout)
                    daemon_pids.append(pid)

        return daemon_pids

    @staticmethod
    def footprint_from_memgraphs(daemon, paths_to_memgraphs):
        """
        From a list of memgraphs, calculate footprint of memgraph
        :param daemon: process name for daemon
        :param paths_to_memgraphs: a list of collected memgraphs
        :return: dictionary of timestamp to footprint
        """
        def timestamp_for(path_to_memgraph):
            with subprocess.Popen(["leaks", "--processInfo", path_to_memgraph],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as p_1:
                with subprocess.Popen(['grep', "Date/Time"],
                                      stdin=p_1.stdout,
                                      stdout=subprocess.PIPE) as p_2:
                    p_1.stdout.close()
                    stdout, _ = p_2.communicate()
                    stdout = stdout.decode("utf-8")

                    stdout = stdout.replace("Date/Time:  ", "")
                    return stdout.replace("\n", "")

        def footprint_for(path_to_memgraph):
            # The line producted by footprint command is like below. Extract footprint from the line
            # daemon [76] (memgraph): 64-bit\tFootprint: 71 MB (16384 bytes per page)\n'
            def footprint_from(line):
                tokens = line.split()
                if "Footprint:" not in tokens[4]:
                    sys.exit(f"ERROR: Format of footprint line has changed {tokens[4]}")
                return f"{tokens[5]} {tokens[6]}"

            with subprocess.Popen(["footprint", path_to_memgraph],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as p_1:
                with subprocess.Popen(['grep', daemon],
                                      stdin=p_1.stdout,
                                      stdout=subprocess.PIPE) as p_2:
                    p_1.stdout.close()
                    stdout, _ = p_2.communicate()
                    stdout = stdout.decode("utf-8")

                    return footprint_from(stdout)

        # iterate over memgraphs
        footprints_ = {}  # Dictionary of Date to footprint
        for memgraph in paths_to_memgraphs:
            timestamp = timestamp_for(memgraph)
            footprint = footprint_for(memgraph)
            footprints_[timestamp] = footprint

        return footprints_


class Symbolicator:
    # We only want symbols for these frameworks and binaries
    # Symbol download is a slow network operation. We only download for
    # specific frameworks, we are interested in.
    FILTERED_DSYMS = [
        "locationd",
        "CoreLocation.framework",
        "CoreMotion.framework",
        "CoreRoutine.framework",
        "CoreBluetooth.framework",
        "CoreTime.framework",
        "GeoServicesCore.framework",
        "LocationSupport.framework",
        "TrackingAvoidance.framework",
        "CoreLocationProtobuf.framework",
        "CoreAccessories.framework",
        "CommonUtilities.framework",
        "CloudKit.framework",
        "CoreFoundation",
        "libswiftCore.",  # period here to prevent other swift library symbols to be downloaded
        "CFNetwork",
        "libsqlite3",
        "CloudKit",
        "libswiftFoundation",
        "ProtocolBuffer.framework",
        "libnetwork",
        "libdispatch"
    ]

    def get_dsym_paths_from_leaks(self, memgraph):
        """
        returns paths to symbols in BNI for the memgraph.
        Runs "leaks --processInfo" provides UUID of all dylibs in a binary.

        :param memgraph: Path to memgraph
        """
        print(f"Running leaks {memgraph} | tail -n 1000")
        tail_of_leaks_output = ""
        with subprocess.Popen(["leaks", "--processInfo", memgraph],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as p_1:
            with subprocess.Popen(['tail', '-n', '1000'],
                                  stdin=p_1.stdout,
                                  stdout=subprocess.PIPE) as p_2:
                p_1.stdout.close()
                stdout, _ = p_2.communicate()
                tail_of_leaks_output = stdout.decode("utf-8")
                p_2.stdout.close()

        binary_images_text = "Binary Images:"
        tokens = tail_of_leaks_output.split(binary_images_text, 1)
        if len(tokens) != 2:
            print(f"Could not find text Binary images in output of leaks - {tokens.count}")
            sys.exit(-1)

        symbol_path_lines = tokens[1].split("\n")
        symbol_paths_non_empty_lines = [line for line in symbol_path_lines if line != ""]

        return symbol_paths_non_empty_lines

    @staticmethod
    def get_uuids_from_symbol_paths(symbol_path_lines_in_leaks):
        """
        From lines in leaks command which provides paths to symbols,
        return UUIDs of binaries
        """
        symbol_uuids = []

        for path in symbol_path_lines_in_leaks:
            # Parse this kind of line
            # 0x2421a8000 -        0x24221dffb  com.apple.SocialLayer arm64e  \
            # <1e69ad92900f3f188e4860ac71bcf18f> /System/Library/PrivateFrameworks/SocialLayer.framework/SocialLayer
            tokens = path.split()

            # Sixth word is UUID
            uuid = tokens[5]
            binary_name = tokens[6]

            # Are we interested in downloading Dsym for this binary
            should_download_dsym = False
            for f_ in Symbolicator.FILTERED_DSYMS:
                if binary_name.find(f_) != -1:
                    should_download_dsym = True
                    break

            if not should_download_dsym:
                continue

            # UUID should have < and >
            if uuid.find("<") == -1 or uuid.find(">") == -1:
                print(f"Format of leaks has changed. Can't find UUID in line: {path}")
                sys.exit(-1)

            # Remove < and > to get uuid
            uuid = uuid.replace("<", "")
            uuid = uuid.replace(">", "")

            symbol_uuids.append(uuid)

        return symbol_uuids

    def copy_dsym_from_nfs(self, uuid, out_dir):
        """
        From UUID, get path of dsym on bursar.apple.com
        and then copy the symbols to provided output directory
        """

        # Create output directory
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        # Run the following command on UUID
        # dsymForUUID <UUID> |  grep -A 2 DBGDSYMBundlePath | grep com.apple.bni
        with subprocess.Popen(["dsymForUUID", uuid],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as p_1:
            with subprocess.Popen(['grep', '-A', '2', 'DBGDSYMBundlePath'],
                                  stdin=p_1.stdout,
                                  stdout=subprocess.PIPE) as p_2:
                p_1.stdout.close()
                stdout, _ = p_2.communicate()
                p_2.stdout.close()

        stdout = stdout.decode("utf-8")

        tag_beginning = stdout.find("<string>")
        tag_end = stdout.find("</string>")

        symbol_path_on_nfs = stdout[tag_beginning + len("<string>"): tag_end]
        print(f"\t Copying : {symbol_path_on_nfs}")
        os.system(f"cp -R {symbol_path_on_nfs} {out_dir}")

    def download_dsyms_for_memgraph(self, path_to_memgraph,
                                    out_symbols_directory):
        """
        Find UUIDs of dylibs for memgraph and download dsyms to
        the provided directory.
        """
        symbol_path_lines_in_leaks = self.get_dsym_paths_from_leaks(memgraph=path_to_memgraph)
        binary_uuids = Symbolicator.get_uuids_from_symbol_paths(symbol_path_lines_in_leaks=symbol_path_lines_in_leaks)
        for uuid in binary_uuids:
            print(f"\t Downloading Dsym for UUID: {uuid}")
            self.copy_dsym_from_nfs(uuid, out_dir=out_symbols_directory)

    def symbolicate_memgraphs(self, paths_to_memgraphs, symbol_path):
        print("\n\n=====Symbolicating memgraphs====")

        # If directory with trailing slash was passed in for symbol_path,
        # remove trailing slash
        if symbol_path.endswith('/'):
            symbol_path = symbol_path[:-1]
        if not os.path.exists(symbol_path):
            os.makedirs(symbol_path)

        print(f"\t Downloading Symbols to {symbol_path}")
        self.download_dsyms_for_memgraph(path_to_memgraph=paths_to_memgraphs[0],
                                         out_symbols_directory=symbol_path)

        # Symbolicate
        print("\n\t Symbolicating ...")
        for memgraph in paths_to_memgraphs:

            if symbol_path == "":
                print(f"\t leaks --symbolicate {memgraph}")
                os.system(f"leaks --symbolicate {memgraph}")
            else:
                print(f"\t leaks --symbolicate={symbol_path} {memgraph}")
                os.system(f"leaks --symbolicate={symbol_path} {memgraph}")


class MemoryTools:
    @staticmethod
    def generate_memtrend(paths_to_memgraphs, out_path):
        """
        Generate a memtrend from a list of memgraphs
        :param paths: Input memgraphs
        :param out_path: Output to memtrend
        :return: None
        """
        print("\n\n=====Generating memtrend ====")

        memgraphs_concatenated = " ".join(paths_to_memgraphs)
        command = f"memtrend  -guessNonObjects  -showSizes {memgraphs_concatenated}"

        print(f"Generating memtrend at {out_path} ....\n")
        print(f"\t Running: {command}")
        os.system(f"{command} > {out_path}")

    @staticmethod
    def generate_heap_diff(paths_to_memgraphs, out_dir):
        """
        Generate a memtrend from a list of memgraphs
        :param paths_to_memgraphs: Input memgraphs
        :param out_dir: Output directory
        :return: None
        """
        print("\n\n=====Generating heap_diff ====")

        out_path = os.path.join(out_dir, "heap_diff.txt")
        command = "heap -s --guessNonObjects --sumObjectFields {} --diffFrom {} > {}".format(
            paths_to_memgraphs[-1],
            paths_to_memgraphs[0],
            out_path)

        print(f"Generating Heap diff at {out_path} ....\n")
        print(f"\t Running: {command}")
        os.system(f"{command} > {out_path}")

    @staticmethod
    def generate_malloc_history(paths_to_memgraphs, out_dir):
        """
        Run malloc_history on memgraphs
        :param paths: Input memgraphs
        :param out_dir: Output directory
        :return: None
        """
        print("\n\n=====Generating malloc_history for memgraphs====")

        for memgraph in paths_to_memgraphs:
            out_path = memgraph
            out_path = out_path.replace(".memgraph", ".txt")

            consolidated_out_path = out_path.replace("memgraph_", "malloc_history_consolidated_")
            command = f"malloc_history -callTree -consolidateAllBySymbol {memgraph} > {consolidated_out_path}"
            print(command)
            os.system(f"{command}")

        # Generate malloc_history with fullStacks for last memgraph
        out_path = os.path.join(out_dir, "malloc_history_fullStacks.txt")
        command = f"malloc_history --fullStacks -allBySize  {paths_to_memgraphs[-1]} > {out_path}"
        print(command)
        os.system(f"{command}")


    @staticmethod
    def generate_flamegraph(paths_to_memgraphs, out_path):
        """
        Generate a flamegraph from a list of memgraphs
        :param paths_to_memgraphs: Input memgraphs
        :param out_path: Output to flamegraph
        :return: None
        """
        print("\n\n======Generating flamegraph=====")
        paths_to_memgraphs.sort()

        memgraphs_concatenated = " ".join(paths_to_memgraphs)
        command = f"ardiff callstacks  -o {out_path}  --flame  {memgraphs_concatenated}"

        print(f"Generating flamegraph at {out_path}")
        print(f"Running: {command}")
        os.system(f"{command}")


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
        default="",
        required=False,
        help="Path to output where memtrend should be generated")

    parser.add_argument(
        '--ardiff_flame',
        '-f',
        dest="path_to_ardiff_flame",
        default="",
        required=False,
        help="Path to output where ardiff should be generated")

    parser.add_argument(
        '--dont-symbolicate',
        dest="dont_symbolicate_memgraphs",
        type=bool,
        default=False,
        help="Dont symbolicate memgraphs")

    parser.add_argument(
        '--include_first',
        '-i',
        dest="include_first",
        type=bool,
        default=False,
        help="Should include first memgraph in analysis")

    args = parser.parse_args()
    if not os.path.isdir(args.memgraphs_dir):
        sys.exit(f"Invalid directory provided : {args.memgraphs_dir}")

    # Where we should output ardiff
    path_to_ardiff_flame = args.path_to_ardiff_flame
    if path_to_ardiff_flame == "":
        path_to_ardiff_flame = os.path.join(args.memgraphs_dir,
                                            f"ardiff_{args.daemon_name}.html")

    # Where we should output memtrend
    path_to_memtrend = args.path_to_memtrend
    if path_to_memtrend == "":
        path_to_memtrend = os.path.join(args.memgraphs_dir,
                                        f"{args.daemon_name}_memtrend.txt")

    # List memgraphs in provided directory
    memgraphs = MemgraphEnumerator.sorted_memgraphs_in_dir(args.memgraphs_dir)

    # Validate memgraphs
    MemgraphProcessor.validate_memgraphs_are_for_daemon(memgraphs, args.daemon_name)

    # Pick which memgraphs to be used for analysis
    memgraphs = MemgraphEnumerator.pick_memgraphs_for_analysis(memgraphs_=memgraphs,
                                                               daemon_name=args.daemon_name,
                                                               include_first_=args.include_first)

    # Symbolicate
    if not args.dont_symbolicate_memgraphs:
        symbol_path = args.symbol_path
        if symbol_path is None:
            symbol_path = os.path.join(args.memgraphs_dir, "symbols/")
        Symbolicator().symbolicate_memgraphs(memgraphs, symbol_path)

    # Generate malloc_history
    MemoryTools.generate_malloc_history(paths_to_memgraphs=memgraphs,
                                        out_dir=args.memgraphs_dir)

    # Generate memtrend
    MemoryTools.generate_memtrend(paths_to_memgraphs=memgraphs,
                                  out_path=path_to_memtrend)

    # Generate heap diff
    MemoryTools.generate_heap_diff(paths_to_memgraphs=memgraphs,
                                   out_dir=args.memgraphs_dir)

    # Generate flamegraph
    MemoryTools.generate_flamegraph(paths_to_memgraphs=memgraphs,
                                    out_path=path_to_ardiff_flame)

    # Print footprint growth
    timestamps_and_footprints = MemgraphProcessor.footprint_from_memgraphs(daemon=args.daemon_name,
                                                                           paths_to_memgraphs=memgraphs)

    print("\n============= FootPrints =================")
    for idx, val in enumerate(timestamps_and_footprints):
        print(f"\t {val} : {timestamps_and_footprints[val]}")
