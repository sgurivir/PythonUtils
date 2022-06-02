import argparse
import arrow
import csv
import sys

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# This script processes a CSV in this format and plots
# footprint over time

# cftime, footprint, number_of_transactions, pid, process_uptime
# 668143143.004371, 15.4, 5,  84, 00:50


class FootprintMeasurement:
    date = ""
    footprint = 0
    num_os_transactions = 0
    pid = 0
    uptime = 0

    def __init__(self, date, footprint, num_os_transactions, pid, uptime):
        self.date = date
        self.footprint = footprint
        self.num_os_transactions = num_os_transactions
        self.pid = pid
        self.uptime = uptime


class TimeUtil:
    @staticmethod
    def cftime_to_date(cfTime, format='MM/DD HH:mm:ss'):
        NSTIMEINTERVALSINCE1970 = 978307200

        return arrow.get(
            cfTime +
            NSTIMEINTERVALSINCE1970).to('US/Pacific').format(format)


def plot_timestamp_to_footprint(timestamps_,
                                footprints_,
                                bytes_allocated_,
                                out_path):
    """
    timestamps: array of CFAbsoluteTimes
    footprints: array of footprints measured at the timestamps
    bytes_allocated: array of bytes allocated reported by vmstat at the timestamps
    restart_timestamps: array of CFAbsoluteTimes, when process restarted
    out_path: path to file where plot should be written to
    """

    def x_tick_formatter(x, y):
        return TimeUtil.cftime_to_date(x, format="MM/DD HH:mm")

    x_points = np.array(timestamps_)
    y1_points = np.array(footprints_)
    y2_points = np.array(bytes_allocated_)

    axes = plt.axes()
    axes.xaxis.set_major_formatter(
        plt.FuncFormatter(x_tick_formatter))

    plt.xticks(rotation='vertical')
    plt.xticks(fontsize=8, rotation=60)

    axes.set_title('Footprint over time', fontsize=12, fontweight="bold")
    axes.set_xlabel('Timestamp', fontsize=6)
    axes.set_ylabel('Footprint', fontsize=8)

    plt.tight_layout()
    plt.axhline(y=26, color='y', label='inactive', linestyle='dotted')
    plt.axhline(y=34, color='r', label='active', linestyle='dotted')

    print(y1_points)
    print(y2_points)
    plt.plot(x_points, y1_points, color="blue")
    plt.plot(x_points, y2_points, color="orange")
    plt.savefig(out_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process footprint csv')
    parser.add_argument(
        '--csv',
        '-c',
        dest="footprint_csv",
        default=None,
        required=True,
        help="Path to footprint CSV file")
    parser.add_argument(
        '--g',
        '-out_graph_path',
        dest="out_graph_path",
        default="/tmp/footprints.png",
        required=False,
        help="Path to output PNG file")
    args = parser.parse_args()

    LOCATIOND_INACTIVE_JETSAM_LIMIT = 26
    LOCATIOND_ACTIVE_JETSAM_LIMIT = 34

    footprint_csv = args.footprint_csv
    max_active_footprint = 0
    max_inactive_footprint = 0
    max_active_footprint_timestamp = None
    max_inactive_footprint_timestamp = None
    timestamp_max = 0
    timestamp_min = float("inf")
    pid_changes = 0
    previous_pid = None
    number_of_inactive_breaches = 0
    number_of_active_breaches = 0

    number_of_active_samples = 0
    number_of_inactive_samples = 0

    timestamps = []
    footprints = []
    bytes_allocated_samples = []
    fragmentation_samples = []
    num_os_transactions_samples = []
    pids = []
    uptimes = []
    pid_change_timestamps = []

    print("\n Processing...")
    with open(footprint_csv, "r") as f_:
        headers = [h.strip() for h in f_.readline().split(',')]
        csv_reader = csv.DictReader(f_, delimiter=",", fieldnames=headers)
        for row in csv_reader:
            row.update({field_name: value.strip() for (field_name, value) in row.items()})

            try:
                timestamp = float(row["cftime"].strip())
                footprint = float(row["physical_footprint"].strip().replace('M', ''))
                dirty_size = float(row["dirty_size"].strip().replace('M', ''))
                bytes_allocated = float(row["bytes_allocated"].strip().replace('M', ''))
                fragmentation = float(row["fragmentation"].strip().replace('%', ''))
                num_os_transactions = int(row["num_os_transactions"].strip())
                pid = row["pid_of_locationd"].strip()
                uptime = row["uptime_locationd"].strip()
                wallclock = row["wall_clock_time"].strip()

                formatted_date = TimeUtil.cftime_to_date(timestamp)
            except:
                print("Skipping line: {} ".format(row))
                continue

            timestamps.append(timestamp)
            footprints.append(footprint)
            bytes_allocated_samples.append(bytes_allocated)
            fragmentation_samples.append(fragmentation)
            num_os_transactions_samples.append(num_os_transactions)
            pids.append(pid)
            uptimes.append(uptime)

            if num_os_transactions == 0:
                number_of_inactive_samples += 1

                # Check if footprint breached active and inactive limits
                if footprint > LOCATIOND_INACTIVE_JETSAM_LIMIT and num_os_transactions == 0:
                    number_of_inactive_breaches += 1
                    print("BREACHED INACTIVE: {} : {}, {}".format(formatted_date, footprint, num_os_transactions))

            if num_os_transactions > 0:
                number_of_active_samples += 1

                if footprint > LOCATIOND_ACTIVE_JETSAM_LIMIT:
                    number_of_active_breaches += 1
                    print("BREACHED ACTIVE: {} : {}, {}".format(formatted_date, footprint, num_os_transactions))

            if num_os_transactions == 0:
                if footprint > max_inactive_footprint:
                    max_inactive_footprint_timestamp = formatted_date
                    max_inactive_footprint = footprint
            else:
                if footprint > max_active_footprint:
                    max_active_footprint_timestamp = formatted_date
                    max_active_footprint = footprint

            # Track PID changes
            if previous_pid is not None:
                if not previous_pid == pid:
                    print("locationd restarted at : {}".format(formatted_date))
                    pid_changes += 1
                    pid_change_timestamps.append(timestamp)
            previous_pid = pid

    # Check if at least one entry is existing in CSV
    if len(timestamps) == 0:
        print("CSV could not be parsed. No entries found")
        sys.exit(-1)

    # Calculate duration
    duration_of_test = max(timestamps) - min(timestamps)
    time_spent_in_active = number_of_active_samples * 100 / (number_of_active_samples + number_of_inactive_samples)

    print("\n ========================= REPORT  ==============================")
    print(f"Duration of test \t\t\t: {round(duration_of_test/3600, 2)} hrs")
    print(f"Max Inactive Footprint \t\t\t: {max_inactive_footprint} MB \t"
          f"{max_inactive_footprint_timestamp} \t Limit: {LOCATIOND_INACTIVE_JETSAM_LIMIT}")
    print(f"Max Active Footprint   \t\t\t: {max_active_footprint} MB \t"
          f"{max_active_footprint_timestamp} \t Limit: {LOCATIOND_ACTIVE_JETSAM_LIMIT}")
    print(f"Time spent in active \t\t\t: {round(time_spent_in_active, 2)} %")
    print(f"Number of times locationd restarted\t: {pid_changes}")
    print(f"Number of Jetsam limit breaches\t\t: Active: {number_of_active_breaches}, "
          f"Inactive: {number_of_inactive_breaches}")

    # Plot the data
    plot_timestamp_to_footprint(timestamps_=timestamps,
                                footprints_=footprints,
                                bytes_allocated_=bytes_allocated_samples,
                                out_path=args.out_graph_path)

    #print(TimeUtil.cftime_to_date(668199100.972570, format="MM/DD HH:mm"))
    print("\n")