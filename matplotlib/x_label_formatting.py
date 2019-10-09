
import argparse
import csv
import os
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def read_csv(path, names=None):
    """
    Reads a CSV file in Panda and catches exception if csv is empty
    :param path: path to CSV file
    :return: redirects to pd.read_csv() or returns None if CSV has empty data
    """
    try:
        pd_csv = pd.read_csv(path, names=names)
        return pd_csv
    except pd.io.common.EmptyDataError:
        return pd.DataFrame(columns=[])
    except IOError:
        return pd.DataFrame(columns=[])

def ios_time_formatter(iOSTime, tick_number):
    import arrow
    NSTIMEINTERVALSINCE1970 = 978307200
    return arrow.get(iOSTime + NSTIMEINTERVALSINCE1970).to('US/Pacific').format(
        'MM-DD_HH-mm-ss')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert timestamps on x-axis')
    parser.add_argument('--data', '-d', dest="data_path", default=None, required=True,
                        help="File where data collected by AMS is located")
    args = parser.parse_args()

    # Check if arguments are well formed
    data_path = os.path.expanduser(args.data_path)
    if not os.path.exists(data_path):
        print "Cant find the data file"
        sys.exit(-1)

    stride_cal = read_csv(args.data_path)
    if stride_cal.empty:
        sys.exit(-1)

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    axes.xaxis.set_major_formatter(plt.FuncFormatter(ios_time_formatter))
    plt.xticks(rotation='vertical')
    fig.suptitle("StrideCal", fontsize=14, fontweight="bold")
    fig.subplots_adjust(hspace=0.7)


    # -- heartRate --
    axes.set_title('Stride Cal', fontsize=12, fontweight="bold")
    axes.set_xlabel('startTime', fontsize=12)
    axes.set_ylabel('Distance', fontsize=12)
    axes.legend(loc="upper right")
    if stride_cal is not None:
        axes.scatter(stride_cal["startTime"], stride_cal["distance"], color="blue", s=3)

    fig.savefig("/tmp/striceCal.jpeg")