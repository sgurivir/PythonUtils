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

LIST_OF_LOMO_DAEMONS = [
    "WirelessRadioManagerd",
    "gpsd",
    "routined",
    "airportd",
    "locationd",
    "sensorkitd",
    "bluetoothaudiod",
    "nearbyd",
    "timed",
    "bluetoothd",
    "pipelined",
    "wifid",
    "cloudpaird",
    "relatived",
    "wifivelocityd"]

ACTIVE_LIMITS = {
    "WirelessRadioManagerd" : 12,
    "gpsd" : 12,
    "routined" : 24,
    "airportd" : 6,
    "locationd" : 34,
    "sensorkitd" : 6,
    "bluetoothaudiod" : 12,
    "nearbyd" : 20,
    "timed" : 20,
    "bluetoothd" : 34,
    "pipelined" : 74,
    "wifid" : 17,
    "cloudpaird" : 8,
    "relatived" : 40,
    "wifivelocityd" : 9
}

INACTIVE_LIMITS =  {
    "WirelessRadioManagerd" : 12,
    "gpsd" : 10,
    "routined" : 24,
    "airportd" : 6,
    "locationd" : 26,
    "sensorkitd" : 6,
    "bluetoothaudiod" : 12,
    "nearbyd" : 7,
    "timed" : 10,
    "bluetoothd" : 24,
    "pipelined" : 9,
    "wifid" : 11,
    "cloudpaird" : 8,
    "relatived" : 40,
    "wifivelocityd" : 9
}


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


def plot_timestamp_to_footprint(daemon_name,
                                timestamps_,
                                footprints_,
                                bytes_allocated_,
                                dirty_size_samples_,
                                timestamps_with_no_transactions_,
                                active_jetsam_limit,
                                inactive_jetsam_limit,
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

    axes.set_title(f"({daemon_name}) Footprint over time", fontsize=12, fontweight="bold")
    axes.set_xlabel('Timestamp', fontsize=6)
    axes.set_ylabel('Footprint (MB)', fontsize=8)

    plt.tight_layout()

    plt.plot(x_points, y1_points, color="blue", label="footprint")
    plt.plot(x_points, y2_points, color="brown", label="dirty_size")
    plt.plot(x_points, y3_points, color="orange", label="bytes_allocated")

    # Plot horizontal lines for locationd's Jetsam limits (inactive & active)
    plt.axhline(y=inactive_jetsam_limit, color='y', linestyle='dotted', label="INACTIVE_LIMIT")
    plt.axhline(y=active_jetsam_limit, color='r', linestyle='dotted', label="ACTIVE_LIMIT")

    # Calculte approximate duration between timestamps
    duration = 5
    if len(timestamps_) >=2:
        duration = timestamps_[1] - timestamps_[0]

    # Set range for y-axis
    max_y = active_jetsam_limit * 1.3
    plt.ylim(top=max_y)

    # Plot vertical lines where no transactions were taken
    for no_transaction_timestamp in timestamps_with_no_transactions_:
        axes.axvspan(no_transaction_timestamp-duration/2,  # divided by 2, because we dont know when it started
                     no_transaction_timestamp,
                     alpha=0.2)

    # Show legend
    plt.legend(loc="center left", bbox_to_anchor = (1, 0.5))

    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.clf()



def plot_timestamp_to_bytes_lost_to_fragmentation(daemon_name,
                                                  timestamps_,
                                                  bytes_lost_to_fragmentation,
                                                  out_path):
    """
    timestamps_: array of cftimes
    bytes_lost_to_fragmentation: array of footprints measured at the timestamps
    out_path: path to file where plot should be written to
    """
    def x_tick_formatter(x, y):
        return TimeUtil.cftime_to_date(x, format="MM/DD HH:mm")


    bytes_lost_MB = [b/1000 for b in bytes_lost_to_fragmentation]
    x_points = np.array(timestamps_)
    y_points = np.array(bytes_lost_MB)

    axes = plt.axes()
    axes.xaxis.set_major_formatter(
        plt.FuncFormatter(x_tick_formatter))
    axes.set_title(f"({daemon_name}) Bytes lost to fragmentation", fontsize=12, fontweight="bold")
    axes.set_xlabel('Timestamp', fontsize=6)
    axes.set_ylabel('Bytes lost (MB)', fontsize=8)
    axes.grid(axis='y')

    plt.xticks(rotation='vertical')
    plt.xticks(fontsize=8, rotation=60)

    # Set range for y-axis
    max_y = np.max(y_points) * 1.1
    min_y = np.min(y_points) * 0.9
    axes.set_ylim([min_y, max_y])

    #plt.tight_layout()
    plt.plot(x_points, y_points, color="blue", label="Bytes lost (MB)")

    #plt.legend(loc="upper left")
    plt.savefig(out_path, dpi=200)
    plt.clf()


def plot_timestamp_to_allocation_count(daemon_name,
                                       timestamps_,
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

    axes.set_title(f"({daemon_name}) Allocation Count", fontsize=12, fontweight="bold")
    axes.set_xlabel('Timestamp', fontsize=6)
    axes.set_ylabel('Allocation Count', fontsize=8)

    # Set range for y-axis
    max_y = np.max(y_points) * 1.1
    min_y = np.min(y_points) * 0.9
    axes.set_ylim([min_y, max_y])

    #plt.tight_layout()
    plt.plot(x_points, y_points, color="blue", label="allocation count")

    # Calculate approximate duration between timestamps
    duration = 5
    if len(timestamps_) >=2:
        duration = timestamps_[1] - timestamps_[0]

    # Plot vertical lines where no transactions were taken
    for no_transaction_timestamp in timestamps_with_no_transactions_:
        axes.axvspan(no_transaction_timestamp-duration/2,  # divided by 2, because we dont know when it started
                     no_transaction_timestamp,
                     alpha=0.2)

    plt.legend(loc="upper left")
    plt.savefig(out_path, dpi=200)
    plt.clf()


def plot_timestamp_to_footprint_minus_malloc(daemon_name,
                                             timestamps_,
                                             footprint_minus_malloc_,
                                             timestamps_with_no_transactions_,
                                             out_path):
    """
    timestamps_: array of timestamps
    footprint_minus_malloc_: array of size counted against footprint, not coming from malloc regions
    timestamps_with_no_transactions_: Timestamps at which no os_transactions were taken
    out_path: path to file where plot should be written to
    """

    def x_tick_formatter(x, y):
        return TimeUtil.cftime_to_date(x, format="MM/DD HH:mm")

    x_points = np.array(timestamps_)
    y_points = np.array(footprint_minus_malloc_) / 1000 # Convert to MB


    axes = plt.axes()
    axes.grid(axis='y')
    axes.xaxis.set_major_formatter(
        plt.FuncFormatter(x_tick_formatter))

    plt.xticks(rotation='vertical')
    plt.xticks(fontsize=8, rotation=60)

    axes.set_title(f"({daemon_name}) Footprint minus malloc (MB)", fontsize=12, fontweight="bold")
    axes.set_xlabel('Timestamp', fontsize=6)
    axes.set_ylabel('Footprint minus Malloc (MB)', fontsize=8)

    # Set range for y-axis
    max_y = np.max(y_points) * 1.1
    min_y = np.min(y_points) * 0.9
    axes.set_ylim([min_y, max_y])

    #plt.tight_layout()
    plt.plot(x_points, y_points, color="blue", label="Footprint minus malloc (MB)")

    # Calculate approximate duration between timestamps
    duration = 5
    if len(timestamps_) >=2:
        duration = timestamps_[1] - timestamps_[0]

    # Plot vertical lines where no transactions were taken
    for no_transaction_timestamp in timestamps_with_no_transactions_:
        axes.axvspan(no_transaction_timestamp-duration/2,  # divided by 2, because we dont know when it started
                     no_transaction_timestamp,
                     alpha=0.2)

    #plt.legend(loc="upper left")
    plt.savefig(out_path, dpi=200)
    plt.clf()


def report_result(result, out_path):
    """
    Writes provided result string to file at out_path
    :param result: String to be written
    :param out_path: Path to output file
    :return:
    """
    with open(out_path, "a+") as f_:
        f_.write(result)
        f_.close()
    print(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process footprint csvs')
    parser.add_argument(
        '--dir',
        '-d',
        dest="footprint_dir",
        default=None,
        required=True,
        help="Path to DIR with footprint CSV files")
    parser.add_argument(
        '--g',
        '-out_dir',
        dest="out_dir",
        default="",
        required=False,
        help="Path to output directory")
    args = parser.parse_args()

    #LOCATIOND_INACTIVE_JETSAM_LIMIT = 26
   # LOCATIOND_ACTIVE_JETSAM_LIMIT = 34

    # Parse arguments
    footprint_dir = args.footprint_dir
    if not os.path.exists(footprint_dir):
        print(f"Can't find provided Directory : {footprint_dir}")

    # Create Output directory
    out_dir = args.out_dir
    if out_dir == "":
        out_dir = os.path.join(args.footprint_dir, "_plots")
    os.makedirs(out_dir, exist_ok=True)

    script_dir = os.path.dirname(os.path.abspath(__file__))


    #for daemon in LIST_OF_LOMO_DAEMONS:
    for daemon in LIST_OF_LOMO_DAEMONS:
        path_to_footprint_csv = os.path.join(footprint_dir, daemon, "footprint_and_transactions.csv")
        daemon_active_limit = ACTIVE_LIMITS[daemon]
        daemon_inactive_limit = INACTIVE_LIMITS[daemon]

        # Create output directory for this daemon
        out_dir_to_daemon_plots = os.path.join(out_dir, daemon)
        if not os.path.exists(out_dir_to_daemon_plots):
            os.makedirs(out_dir_to_daemon_plots)

        out_path_to_footprint_plot = os.path.join(out_dir_to_daemon_plots, "footprint_plot.png")
        out_path_to_fragmentation_plot = os.path.join(out_dir_to_daemon_plots, "fragmentation_plot.png")
        out_path_to_allocation_count_plot = os.path.join(out_dir_to_daemon_plots, "allocation_counts.png")
        out_path_to_footprint_minus_malloc_plot = os.path.join(out_dir_to_daemon_plots, "footprint_minus_malloc.png")
        out_path_to_results_summary = os.path.join(out_dir_to_daemon_plots, "summary.txt")

        # Clear previous results
        if os.path.exists(out_path_to_results_summary):
            os.remove(out_path_to_results_summary)

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
        footprint_minus_malloc_samples = []
        dirty_size_samples = []
        num_os_transactions_samples = []
        pids = []
        uptimes = []
        pid_change_timestamps = []

        print("\n Processing...")
        with open(path_to_footprint_csv, "r") as f_:
            headers = [h.strip() for h in f_.readline().split(',')]
            csv_reader = csv.DictReader(f_, delimiter=",", fieldnames=headers)

            for row in csv_reader:
                row.update({field_name: value.strip() for (field_name, value) in row.items()})

                try:
                    timestamp = float(row["cftime"].strip())

                    footprint = row["physical_footprint"]
                    if "K" in footprint:
                        footprint = float(row["physical_footprint"].strip().replace('K', '')) / 1000
                    elif "M" in footprint:
                        footprint = float(row["physical_footprint"].strip().replace('M', ''))
                    else:
                        footprint = float(footprint)

                    dirty_size = row["dirty_size"]
                    if "K" in dirty_size:
                        dirty_size = float(row["dirty_size"].strip().replace('K', '')) / 1000
                    elif "M" in dirty_size:
                        dirty_size = float(row["dirty_size"].strip().replace('M', ''))
                    else:
                        dirty_size = float(dirty_size)

                    bytes_allocated = row["bytes_allocated"]
                    if "K" in bytes_allocated:
                        bytes_allocated = float(row["bytes_allocated"].strip().replace('K', '')) / 1000
                    elif "M" in bytes_allocated:
                        bytes_allocated = float(row["bytes_allocated"].strip().replace('M', ''))
                    else:
                        bytes_allocated = float(bytes_allocated)

                    bytes_lost_to_fragmentation = row["bytes_lost_to_fragmentation"]
                    if "K" in bytes_lost_to_fragmentation:
                        bytes_lost_to_fragmentation = int(row["bytes_lost_to_fragmentation"].strip().replace('K', ''))
                    elif "M" in bytes_lost_to_fragmentation:
                        bytes_lost_to_fragmentation = float(row["bytes_lost_to_fragmentation"].strip().replace('M', ''))
                    else:
                        bytes_lost_to_fragmentation = float(bytes_lost_to_fragmentation)


                    allocation_count = int(row["allocation_count"])
                    fragmentation = float(row["fragmentation"].strip().replace('%', ''))
                    footprint_minus_malloc = int(row["non_malloc_section"])
                    num_os_transactions = int(row["num_os_transactions"].strip())
                    pid = row["pid"].strip()
                    uptime = row["uptime"].strip()
                    wallclock = row["wall_clock_time"].strip()

                    formatted_date = TimeUtil.cftime_to_date(timestamp)

                except Exception as e:
                    print(e)
                    print("Skipping line: {} due to exception {}".format(row, e))
                    continue

                timestamps.append(timestamp)
                footprints.append(footprint)
                bytes_allocated_samples.append(bytes_allocated)
                fragmentation_samples.append(fragmentation)
                allocation_count_samples.append(allocation_count)
                footprint_minus_malloc_samples.append(footprint_minus_malloc)
                bytes_lost_to_fragmentation_samples.append(bytes_lost_to_fragmentation)
                num_os_transactions_samples.append(num_os_transactions)
                dirty_size_samples.append(dirty_size)
                pids.append(pid)
                uptimes.append(uptime)

                if num_os_transactions == 0:
                    number_of_inactive_samples += 1

                    # Check if footprint breached active and inactive limits
                    if footprint > daemon_inactive_limit and num_os_transactions == 0:
                        number_of_inactive_breaches += 1
                        report_result(f"BREACHED INACTIVE: {formatted_date} : {footprint}, {num_os_transactions}\n",
                                      out_path_to_results_summary)

                if num_os_transactions > 0:
                    number_of_active_samples += 1

                    if footprint > daemon_active_limit:
                        number_of_active_breaches += 1
                        report_result(f"BREACHED ACTIVE: {formatted_date} : {footprint}, {num_os_transactions}\n",
                                      out_path_to_results_summary)

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
                        report_result(f"{daemon} restarted at : {formatted_date}\n",
                                      out_path_to_results_summary)
                        pid_changes += 1
                        pid_change_timestamps.append(timestamp)
                previous_pid = pid

        # Check if at least one entry is existing in CSV
        if len(timestamps) == 0:
            print(f"CSV could not be parsed. No entries found for {daemon}")
            continue

        # Calculate duration
        duration_of_test = max(timestamps) - min(timestamps)
        time_spent_in_active = number_of_active_samples * 100 / (number_of_active_samples + number_of_inactive_samples)

        timestamps_with_no_transactions = timestamps_with_zero_transactions(timestamps,
                                                                            pids,
                                                                            num_os_transactions_samples)

        report = f"\n ========================= REPORT  ==============================\n"
        report += f"                 {daemon}"
        report += f"\n ================================================================\n"
        report += f"Duration of test \t\t\t: {round(duration_of_test/3600, 2)} hrs \n"
        report += f"Time spent in active \t\t\t: {round(time_spent_in_active, 2)} % \n"
        report += f"Number of times {daemon} restarted\t: {pid_changes} \n"
        report += f"Number of Jetsam limit breaches\t\t: Active: {number_of_active_breaches}, " \
                  f"Inactive: {number_of_inactive_breaches} \n"
        report_result(report, out_path_to_results_summary)

        # Plot the data
        plot_timestamp_to_footprint(daemon_name=daemon,
                                    timestamps_=timestamps,
                                    footprints_=footprints,
                                    bytes_allocated_=bytes_allocated_samples,
                                    dirty_size_samples_=dirty_size_samples,
                                    timestamps_with_no_transactions_=timestamps_with_no_transactions,
                                    active_jetsam_limit=ACTIVE_LIMITS[daemon],
                                    inactive_jetsam_limit=INACTIVE_LIMITS[daemon],
                                    out_path=out_path_to_footprint_plot)

        plot_timestamp_to_allocation_count(daemon_name=daemon,
                                           timestamps_=timestamps,
                                           allocation_count_=allocation_count_samples,
                                           timestamps_with_no_transactions_=timestamps_with_no_transactions,
                                           out_path=out_path_to_allocation_count_plot)

        plot_timestamp_to_bytes_lost_to_fragmentation(daemon_name=daemon,
                                                      timestamps_=timestamps,
                                                      bytes_lost_to_fragmentation=bytes_lost_to_fragmentation_samples,
                                                      out_path=out_path_to_fragmentation_plot)

        plot_timestamp_to_footprint_minus_malloc(daemon_name=daemon,
                                                 timestamps_=timestamps,
                                                 footprint_minus_malloc_=footprint_minus_malloc_samples,
                                                 timestamps_with_no_transactions_=timestamps_with_no_transactions,
                                                 out_path=out_path_to_footprint_minus_malloc_plot)

        # Copy HTML to output directory
        report_html_path = os.path.join(script_dir, "report.html")
        shutil.copy(report_html_path, out_dir_to_daemon_plots)

        #print(TimeUtil.cftime_to_date(668199100.972570, format="MM/DD HH:mm"))
        print(f"\nOutput plots for {daemon} written to {out_dir_to_daemon_plots}")
        print("\n")

    # Copy index HTML to output directory
    index_html_path = os.path.join(script_dir, "index.html")
    shutil.copy(index_html_path, out_dir)