import argparse
import arrow
import csv
import os
import subprocess
import sys

import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from MemgraphUtil import MemgraphUtil


class TimeUtil:
    @staticmethod
    def cftime_to_date(cfTime, format='MM/DD HH:mm:ss'):
        NSTIMEINTERVALSINCE1970 = 978307200

        return arrow.get(
            cfTime +
            NSTIMEINTERVALSINCE1970).to('US/Pacific').format(format)


class FootprintPlotter:
    """ Plots an array of timestamps to footprints.
    :param(timestamps): Dictionary of DateTime to Footprint(MB)
    :param(out_path): Path to output graph (PNG)
    """
    @staticmethod
    def plot_timestamps_to_footprints(timestamps_to_footprints,
                                      timestamps_to_bytes_allocated,
                                      out_path):
        """
        footprints: Dictionary of DateTimeObject:footprint
        timestamps_to_bytes_allocated: Dictionary of DateTimeObject:Bytes allocated
        out_path: path to file where plot should be written to
        """
        timestamps = list(timestamps_to_footprints.keys())
        footprints = [timestamps_to_footprints[t] for t in timestamps]
        bytes_allocated = [timestamps_to_bytes_allocated[t] for t in timestamps]

        x_points = timestamps
        y_points = footprints

        print(x_points)
        print(y_points)

        axes = plt.axes()

        plt.xticks(rotation='vertical')
        plt.xticks(fontsize=8, rotation=60)

        plt.gcf().autofmt_xdate()

        axes.set_title('Footprint over time', fontsize=12, fontweight="bold")
        axes.set_xlabel('Timestamp', fontsize=6)
        axes.set_ylabel('Footprint', fontsize=8)

        plt.tight_layout()
        plt.axhline(y=26, color='y', label='inactive', linestyle='dotted')
        plt.axhline(y=34, color='r', label='active', linestyle='dotted')

        plt.plot(x_points, y_points)
        plt.savefig(out_path)

    @staticmethod
    def plot_footprints(paths_to_memgraphs, out_path):
        """
        Plots footprints for memgraphs
        :param(memgraphs): List of memgraphs
        :param(out_path): Path where plot should be created
        """
        print("\n============= Plotting FootPrints =================")
        timestamps_and_footprints = {}
        timestamps_and_bytes_allocated = {}

        for memgraph in paths_to_memgraphs:
            timestamp = MemgraphUtil.timestamp_for(path=memgraph)

            footprint = MemgraphUtil.footprint_for(path=memgraph)
            timestamps_and_footprints[timestamp] = float(footprint.replace("MB", ""))

            bytes_allocated = MemgraphUtil.fragmentation_stats_for(path=memgraph)["bytes_allocated"]
            timestamps_and_bytes_allocated[timestamp] = float(bytes_allocated.replace("M", ""))

            print(f"\t {timestamp} : {footprint} {bytes_allocated}")

        try:
            FootprintPlotter.plot_timestamps_to_footprints(timestamps_and_footprints,
                                                           timestamps_and_bytes_allocated,
                                                           out_path)
        except Exception as e:
            print(f"Failed to generate plot of footprints : {e}")
            return

        print(f"Footprint plot saved to {out_path}")