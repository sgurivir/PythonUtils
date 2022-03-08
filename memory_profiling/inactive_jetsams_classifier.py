#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
This script analyzes JSON crash reports received from analytics team. You can find example of
JSON reports attached to the radar rdar://81920864

Example usage:
 python ./inactive_jetsams_classifier.py -d <directory_with_json_crash_files>

The script ignores active jetsams and then counts crash reports by offending callstack.
 At the end, the script prints callstacks in order of occurrences.
"""

import argparse
import json
import os
import shutil
import re

JETSAM_LIMIT_PHONE_LOCATIOND_ACTIVE = "34"
JETSAM_LIMIT_PHONE_LOCATIOND_INACTIVE = "26"
JETSAM_LIMIT_WATCH_LOCATIOND_ACTIVE = "20"
JETSAM_LIMIT_WATCH_LOCATIOND_INACTIVE = "14"


def active_limit_for_device_type(device_type=""):
    """
    Returns currently configured active jetsam limit for locationd
    :param device_type: Phone (or) Watch
    :return:
    """
    if re.search("Watch", device_type, re.IGNORECASE):
        return JETSAM_LIMIT_WATCH_LOCATIOND_ACTIVE
    if re.search("Phone", device_type, re.IGNORECASE):
        return JETSAM_LIMIT_PHONE_LOCATIOND_ACTIVE

    raise Exception("Invalid device model identifier")


def inactive_limit_for_device_type(device_type=""):
    """
    Returns currently configured inactive jetsam limit for locationd
    :param device_type: Phone (or) Watch
    :return:
    """
    if re.search("Watch", device_type, re.IGNORECASE):
        return JETSAM_LIMIT_WATCH_LOCATIOND_INACTIVE
    if re.search("Phone", device_type, re.IGNORECASE):
        return JETSAM_LIMIT_PHONE_LOCATIOND_INACTIVE

    raise Exception("Invalid device model identifier")


def categorize_callstacks_in_jetsams(directory):
    """
    Categorizes JSON crash reports by signature

    :param(directory) : Directory with JSON jetsam files received from analytics
    """
    _crash_signatures = []       # Array of hash signatures of crashes
    _crash_stacks = {}           # Dictionary of hash to callstacks
    _crash_counts = {}           # Dictionary of hash to counts
    _crash_messages = {}         # Dictionary of hash to exception message
    _crash_report_files = {}     # Dictionary of hash to files containing the signature

    for crash_report in os.listdir(directory):
        path = os.path.join(directory, crash_report)

        # ignore directories and hidden files
        if os.path.isdir(path) or crash_report.startswith("."):
            continue

        with open(path, encoding='utf-8', errors='ignore') as json_data:
            try:
                crash_json = json.load(json_data, strict=False)
                crash_hash = crash_json["crashpointSha1Hash"]
            except json.decoder.JSONDecodeError:
                print(f"Loading of json at {path} failed.. Ignoring")
                continue

        if crash_hash not in _crash_signatures:
            # We are seeing this signature for first time
            _crash_signatures.append(crash_hash)
            _crash_counts[crash_hash] = 1
            _crash_messages[crash_hash] = crash_json["exception"]["message"]
            _crash_stacks[crash_hash] = crash_json["crashStack"]
            _crash_report_files[crash_hash] = [path]
        else:
            # Increment counts
            _crash_counts[crash_hash] += 1
            _crash_report_files[crash_hash].append(path)

    return _crash_signatures, _crash_stacks, _crash_counts, _crash_messages, _crash_report_files


def analyze_frontmost_processes_in_jetsams(device_type,
                                           directory,
                                           out_directory):
    """
    Categorizes JSON crash reports by signature
    :param(device_type) : Type of Device : Watch or Phone
    :param(directory) : Directory with JSON jetsam files received from analytics
    :param(out_directory) : Directory where results should be created
    """
    _counts_of_foreground_processes = {}     # Dictionary of foreground process to counts of Jetsam events
    _counts_of_largest_processes = {}        # Dictionary of largest process to counts of Jetsam events

    for crash_report in os.listdir(directory):
        path = os.path.join(directory, crash_report)

        # ignore directories and hidden files
        if os.path.isdir(path) or crash_report.startswith("."):
            continue

        with open(path, encoding='utf-8', errors='ignore') as json_data:
            try:
                crash_json = json.load(json_data, strict=False)
                model_code = crash_json["modelCode"]
                print(model_code)
            except json.decoder.JSONDecodeError:
                print(f"Loading of json at {path} failed.. Ignoring")
                continue

    return _counts_of_foreground_processes, _counts_of_largest_processes


def report_statistics_for_inactive_jetsams(device_type,
                                           stacks,
                                           counts,
                                           messages,
                                           out_directory,
                                           report_path):
    """
    Generates report from categorization done by categorize_jetsams()
    :param device_type: Phone (or) Watch
    :param stacks: list of callstacks found by categorize_jetsams
    :param counts: counts found by categorize_jetsams
    :param messages: messages found by categorize_jetsams
    :param out_directory: Output directory where buckets of crash reports should be created
    :param report_path: Output path where report with callstacks should be created
    :return:
    """
    # Counts is a dictionary of Key to count of occurances
    # Extract keys to get signatures and sort by counts
    signatures = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    # Sum of crash counts
    total_crashes = sum(counts.values())

    with open(report_path, "w") as f_:
        for signature in signatures:
            # We are only interested in inactive Jetsams
            inactive_limit = inactive_limit_for_device_type(device_type)

            print(messages[signature])

            if inactive_limit not in messages[signature]:
                continue


            # Print JSON of crash signature
            formatted_callstack = json.dumps(stacks[signature], indent=2)

            # Calculate percent of total crashes
            percent_occurrences = counts[signature] * 100 / total_crashes

            # Print statistics
            f_.write(f"\n{signature}")
            f_.write("\n{} jetsams ({} %) with {} at the callstack \n {}".format(
                counts[signature],
                percent_occurrences,
                messages[signature],
                formatted_callstack))
            f_.write("\n===============================================\n")

            # Copy matching reports to output directory
            dir_for_signature = os.path.join(out_directory, signature)
            os.makedirs(dir_for_signature)
            for crash_report_file in crash_report_files[signature]:
                shutil.copy(crash_report_file, dir_for_signature)


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Process locationd JSON jetsam reports')
    parser.add_argument(
        '--dir',
        '-d',
        dest="crash_reports_dir",
        default=None,
        required=True,
        help="Path to directory with JSON Jetsam crash reports")

    parser.add_argument(
        '--product',
        '-p',
        dest="product_identifier",
        default="Phone",
        required=False,
        help="Device Type - Watch or Phone")

    parser.add_argument(
        '--output',
        '-o',
        dest="out_dir",
        default=None,
        required=False,
        help="Directory to report results")

    args = parser.parse_args()
    if not os.path.isdir(args.crash_reports_dir):
        raise Exception("Invalid directory provided : {args.crash_reports_dir}")

    # Clean old artifacts
    out_dir = os.path.join(args.crash_reports_dir, "analysis")
    if args.out_dir:
        out_dir = out_dir
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.mkdir(out_dir)

    # Parse Crash reports
    crash_signatures, crash_stacks, crash_counts, crash_messages, crash_report_files =\
        categorize_callstacks_in_jetsams(directory=args.crash_reports_dir)

    # Report callstacks for inactive Jetsams
    path_to_inactive_jetsam_report = os.path.join(out_dir, "inactive_jetsams.txt")
    report_statistics_for_inactive_jetsams(device_type=args.product_identifier,
                                           stacks=crash_stacks,
                                           counts=crash_counts,
                                           messages=crash_messages,
                                           out_directory=out_dir,
                                           report_path=path_to_inactive_jetsam_report)
    print(f"Inactive Jetsam callstacks written to : \n\t {path_to_inactive_jetsam_report}")

    """
    # Count foreground process(e)s at the time of Jetsam event
    analyze_frontmost_processes_in_jetsams(device_type=args.product_identifier,
                                           directory=args.crash_reports_dir,
                                           out_directory=out_dir)
    """
