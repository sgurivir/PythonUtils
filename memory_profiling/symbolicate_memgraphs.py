#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
This script downloads dsyms for a memgraph to a provided output directory.
"""

import argparse
import glob
import os
import subprocess
import sys

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


def get_dsym_paths_from_leaks(memgraph):
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
        raise Exception(f"Could not find text Binary images in output of leaks - {tokens.count}")

    symbol_path_lines = tokens[1].split("\n")
    symbol_paths_non_empty_lines = [line for line in symbol_path_lines if line != ""]

    return symbol_paths_non_empty_lines


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
        for f in FILTERED_DSYMS:
            if binary_name.find(f) != -1:
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


def copy_dsym_from_nfs(uuid, out_dir):
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

    symbol_path_on_nfs = stdout[tag_beginning + len("<string>") : tag_end]
    print(f"\t Copying : {symbol_path_on_nfs}")
    os.system(f"cp -R {symbol_path_on_nfs} {out_dir}")


def sorted_memgraphs_in_dir(path):
    """
    returns a list of memgraphs found in provided directory
    :param(path): directory to search memgraph files
    :return: Paths to memgraphs, sorted in canonical order
    """
    memgraphs = glob.glob(path + '/*.memgraph', recursive=False)

    if len(memgraphs) == 0:
        raise Exception(f"No memgraphs found in provided directory {path}")

    memgraphs.sort()
    return memgraphs


def get_paths_to_memgraphs(file_or_directory):
    """
    Enumerate memgraphs in a directory
    """
    if not os.path.exists(file_or_directory):
        raise Exception(f"Path provided does not exist : {file_or_directory}")

    if os.path.isfile(file_or_directory):
        return [file_or_directory]

    if os.path.isdir(file_or_directory):
        memgraphs = sorted_memgraphs_in_dir(file_or_directory)

        if len(memgraphs) == 0:
            raise Exception(f"No memgraphs found in directory provided : {file_or_directory}")

        return memgraphs

    return []


def output_dir_for_symbols(input_memgraph,
                           symbols_directory):
    """
    Determines where to download the symbols to
    """
    if symbols_directory is not None:
        return symbols_directory

    symbols_dir = f"/tmp/symbols"

    if os.path.isdir(input_memgraph):
        symbols_dir = os.path.join(input_memgraph, "symbols")
        os.makedirs(symbols_dir, exist_ok=True)

    elif os.path.isfile(input_memgraph):
        directory = os.path.dirname(input_memgraph)
        symbols_dir = os.path.join(directory, "symbols")
        os.makedirs(symbols_dir, exist_ok=True)

    return symbols_dir


def download_dsyms_for_memgraph(path_to_memgraph,
                                out_symbols_directory):
    """
    Find UUIDs of dylibs for memgraph and download dsyms to
    the provided directory.
    """
    symbol_path_lines_in_leaks = get_dsym_paths_from_leaks(memgraph=path_to_memgraph)
    binary_uuids = get_uuids_from_symbol_paths(symbol_path_lines_in_leaks=symbol_path_lines_in_leaks)
    for uuid in binary_uuids:
        print(f"\t Downloading Dsym for UUID: {uuid}")
        copy_dsym_from_nfs(uuid, out_dir=out_symbols_directory)


def symbolicate_memgraph(path_to_memgraph, symbols_directory):
    """
    Symbolicate memgraph with symbols in the directory
    path_to_memgraph: Input memgraph
    symbols_directory: Directory where symbols are located
    """
    print(f"Symbolicating {path_to_memgraph}")
    result = subprocess.run(["leaks", f"--symbolicate={symbols_directory}", path_to_memgraph],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout = result.stdout.decode("utf-8")
    stderr = result.stderr.decode("utf-8")

    if stdout:
        print(f"\t {stdout}")
    if stderr:
        print(f"\t {stderr}")


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Process daemon memgraphs and generate memtrend')
    parser.add_argument(
        '--input',
        '-i',
        dest="memgraph_dir",
        default=None,
        required=False,
        help="Path to a memgraph")

    parser.add_argument(
        '--symbols',
        '-s',
        dest="symbols_directory",
        default=None,
        required=False,
        help="Path to directory where symbols should be saved")

    args = parser.parse_args()

    print("\n=========Collecting memgraph(s) =====\n")
    input_memgraphs = get_paths_to_memgraphs(args.memgraph_dir)
    print("{}".format("\n\t".join(input_memgraphs)))

    # Determine where to download symbols to
    out_symbols_dir = output_dir_for_symbols(input_memgraph=args.memgraph_dir,
                                             symbols_directory=args.symbols_directory)

    print("\n=========Downloading Symbols ======\n")
    download_dsyms_for_memgraph(path_to_memgraph=input_memgraphs[0],
                                out_symbols_directory=out_symbols_dir)

    print("\n=========Symbolicating memgraphs======\n")
    for memgraph in input_memgraphs:
        symbolicate_memgraph(memgraph, out_symbols_dir)

    print(f"\nDownloaded symbols to {out_symbols_dir}")
