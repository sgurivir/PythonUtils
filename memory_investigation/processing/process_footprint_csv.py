import argparse
import os.path

import arrow
import csv
import shutil
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

    @staticmethod
    def convert_human_readbale_duration_to_hours(duration):
        """
        Converts duration reported by PS uptime (format: 01-00:00:53) to minutes
        :param duration:
        :return:
        """
        duration = duration.strip()
        count_of_colons = duration.count(":")

        if count_of_colons == 0:
            return float(int(duration))/3600   # convert seconds to hours
        if count_of_colons == 1:
            tokens = duration.split(":")
            return int(tokens[0])/60 + int(tokens[1])/3600
        if count_of_colons == 2:
            count_of_hyphens = duration.count("-")
            if count_of_hyphens == 0:
                tokens = duration.split(":")
                return int(tokens[0]) + int(tokens[1])/60 + float(int(tokens[2]))/3600
            else:
                tokens = duration.split("-")
                return int(tokens[0]) * 24 + TimeUtil.convert_human_readbale_duration_to_hours(tokens[1])

        raise Exception(f"Could not parse duration string: {duration}")

def timestamps_with_zero_transactions(timestamps_,
                                      pids_,
                                      num_os_transactions_):
    """
    Find indices in num_os_transactions_, which have zero transacations, and then return
    timestamps at those indices.

    :param timestamps_:
    :param pids_:
    :param num_os_transactions_:
    :return:
    """
    num_os_transactions_np_ = np.array(num_os_transactions_)

    # Get indices with zero value
    zero_indices = np.where(num_os_transactions_np_ == 0)

    # Return elements in timestamps_ at the indices
    return [timestamps_[i] for i in list(zero_indices[0])]


def plot_timestamp_to_footprint(timestamps_,
                                footprints_,
                                bytes_allocated_,
                                dirty_size_samples_,
                                timestamps_with_no_transactions_,
                                out_path):
    """
    timestamps: array of CFAbsoluteTimes
    footprints: array of footprints measured at the timestamps
    bytes_allocated: array of bytes allocated reported by vmstat at the timestamps
    dirty_size_samples_: array of dirty_size reported by footprint
    restart_timestamps: array of CFAbsoluteTimes, when process restarted
    timestamps_with_no_transactions_: Timestamps at which no os_transaction is taken
    out_path: path to file where plot should be written to
    """

    def x_tick_formatter(x, y):
        return TimeUtil.cftime_to_date(x, format="MM/DD HH:mm")

    x_points = np.array(timestamps_)
    y1_points = np.array(footprints_)
    y2_points = np.array(dirty_size_samples_)
    y3_points = np.array(bytes_allocated_)

    axes = plt.axes()
    axes.xaxis.set_major_formatter(
        plt.FuncFormatter(x_tick_formatter))

    plt.xticks(rotation='vertical')
    plt.xticks(fontsize=8, rotation=60)

    axes.set_title('Footprint over time', fontsize=12, fontweight="bold")
    axes.set_xlabel('Timestamp', fontsize=6)
    axes.set_ylabel('Footprint', fontsize=8)

    plt.tight_layout()

    print(y1_points)
    print(y2_points)
    print(y3_points)
    plt.plot(x_points, y1_points, color="blue", label="footprint")
    plt.plot(x_points, y2_points, color="brown", label="dirty_size")
    plt.plot(x_points, y3_points, color="orange", label="bytes_allocated")

    # Plot horizontal lines for locationd's Jetsam limits (inactive & active)
    plt.axhline(y=26, color='y', linestyle='dotted')
    plt.axhline(y=34, color='r', linestyle='dotted')

    # Calculte approximate duration between timestamps
    duration = 5
    if len(timestamps_) >=2:
        duration = timestamps_[1] - timestamps_[0]

    # Plot vertical lines where no transactions were taken
    for no_transaction_timestamp in timestamps_with_no_transactions_:
        axes.axvspan(no_transaction_timestamp-duration,
                     no_transaction_timestamp,
                     alpha=0.2)


    plt.legend(loc="upper left")
    plt.savefig(out_path, dpi=200)
    plt.clf()



def plot_uptimes_to_bytes_lost_to_fragmentation(uptimes_,
                                                bytes_lost_to_fragmentation,
                                                out_path):
    """
    uptimes: array of uptimes of locationd
    bytes_lost_to_fragmentation: array of footprints measured at the timestamps
    out_path: path to file where plot should be written to
    """
    uptimes_hours = [TimeUtil.convert_human_readbale_duration_to_hours(t) for t in uptimes_]
    bytes_lost_MB = [b/1000 for b in bytes_lost_to_fragmentation]
    x_points = np.array(uptimes_hours)
    y1_points = np.array(bytes_lost_MB)

    axes = plt.axes()

    plt.xticks(rotation='vertical')
    plt.xticks(fontsize=8, rotation=60)

    axes.set_title('Bytes lost to fragmentation', fontsize=12, fontweight="bold")
    axes.set_xlabel('Uptime of locationd (Hours)', fontsize=6)
    axes.set_ylabel('Bytes lost (MB)', fontsize=8)
    axes.grid(axis='y')

    #plt.tight_layout()
    plt.plot(x_points, y1_points, color="blue", label="Bytes lost (MB)")

    plt.legend(loc="upper left")
    plt.savefig(out_path, dpi=200)
    plt.clf()


def plot_timestamp_to_allocation_count(timestamps_,
                                       allocation_count_,
                                       timestamps_with_no_transactions_,
                                       out_path):
    """
    timestamps_: array of timestamps
    allocation_count_: array of total number of allocations
    timestamps_with_no_transactions_: Timestamps at which no os_transactions were taken
    out_path: path to file where plot should be written to
    """

    def x_tick_formatter(x, y):
        return TimeUtil.cftime_to_date(x, format="MM/DD HH:mm")

    x_points = np.array(timestamps_)
    y_points = np.array(allocation_count_)

    axes = plt.axes()
    axes.grid(axis='y')
    axes.xaxis.set_major_formatter(
        plt.FuncFormatter(x_tick_formatter))

    plt.xticks(rotation='vertical')
    plt.xticks(fontsize=8, rotation=60)

    axes.set_title('Allocation Count', fontsize=12, fontweight="bold")
    axes.set_xlabel('Timestamp', fontsize=6)
    axes.set_ylabel('Allocation Count', fontsize=8)

    #plt.tight_layout()
    plt.plot(x_points, y_points, color="blue", label="allocation count")


    plt.legend(loc="upper left")
    plt.savefig(out_path, dpi=200)
    plt.clf()

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
        '-out_dir',
        dest="out_dir",
        default="",
        required=False,
        help="Path to output directory")
    args = parser.parse_args()

    LOCATIOND_INACTIVE_JETSAM_LIMIT = 26
    LOCATIOND_ACTIVE_JETSAM_LIMIT = 34

    # Parse arguments
    footprint_csv = args.footprint_csv
    if not os.path.exists(footprint_csv):
        print(f"Can't find provided CSV : {footprint_csv}")

    # Create Output directory
    out_dir = args.out_dir
    if out_dir == "":
        out_dir = os.path.join(os.path.dirname(footprint_csv),
                               "_plots")
    os.makedirs(out_dir, exist_ok = True)

    out_path_to_footprint_plot = os.path.join(out_dir, "footprint_plot.png")
    out_path_to_fragmentation_plot = os.path.join(out_dir, "fragmentation_plot.png")
    out_path_to_allocation_count_plot = os.path.join(out_dir, "allocation_counts.png")

    # Calculate
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
    allocation_count_samples = []
    fragmentation_samples = []
    bytes_lost_to_fragmentation_samples = []
    dirty_size_samples = []
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
                allocation_count = int(row["allocation_count"])
                fragmentation = float(row["fragmentation"].strip().replace('%', ''))
                if "bytes_lost_to_fragmentation" in row:
                    bytes_lost_to_fragmentation = int(row["bytes_lost_to_fragmentation"].strip().replace('K', ''))
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
            allocation_count_samples.append(allocation_count)
            bytes_lost_to_fragmentation_samples.append(bytes_lost_to_fragmentation)
            num_os_transactions_samples.append(num_os_transactions)
            dirty_size_samples.append(dirty_size)
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

    timestamps_with_no_transactions = timestamps_with_zero_transactions(timestamps,
                                                                        pids,
                                                                        num_os_transactions_samples)

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
                                dirty_size_samples_=dirty_size_samples,
                                timestamps_with_no_transactions_=timestamps_with_no_transactions,
                                out_path=out_path_to_footprint_plot)

    plot_timestamp_to_allocation_count(timestamps_=timestamps,
                                       allocation_count_=allocation_count_samples,
                                       timestamps_with_no_transactions_=timestamps_with_no_transactions,
                                       out_path=out_path_to_allocation_count_plot)

    plot_uptimes_to_bytes_lost_to_fragmentation(uptimes_=uptimes,
                                                bytes_lost_to_fragmentation=bytes_lost_to_fragmentation_samples,
                                                out_path=out_path_to_fragmentation_plot)

    # Copy HTML to output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_html_path = os.path.join(script_dir, "report.html")
    shutil.copy(report_html_path, out_dir)

    #print(TimeUtil.cftime_to_date(668199100.972570, format="MM/DD HH:mm"))
    print(f"\nOutput plots written to {out_dir}")
    print("\n")