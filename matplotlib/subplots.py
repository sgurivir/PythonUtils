import argparse
import numpy as np
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from LocationQA.Common.Motion.msl_parser import MSLFile

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Provide System and Replay MSL for Pedometer replay')
    parser.add_argument('--system_msl', '-s', dest="system_msl_path", default=None, required=True)
    parser.add_argument('--replay_msl', '-r', dest="mth_replay_output_path", default=None, required=True)
    parser.add_argument('--proto_file_path', '-p', dest="proto_file_path", default=None, required=True)
    args = parser.parse_args()

    # Check if arguments are well formed
    if not args.system_msl_path or not args.mth_replay_output_path or not args.proto_file_path:
        print" Usage: replay_pedometer.py -s <system_msl> -r <replay_msl> -p <path_to_proto>"
        sys.exit(-1)

    if not os.path.exists(args.system_msl_path):
        print "Cant find system msl file"
        sys.exit(-1)

    if not os.path.exists(args.mth_replay_output_path):
        print "Cant find output replay path"
        sys.exit(-1)

    if not os.path.exists(args.proto_file_path):
        print "Cant find proto file path"
        sys.exit(-1)

    # Load in-system msl file
    in_system_msl_file = MSLFile(args.system_msl_path, args.proto_file_path)
    in_system_msl_file.decode_proto()
    in_system_df = in_system_msl_file.to_dict(['stepCountEntry'])
    in_system_steps = in_system_df['stepCountEntry']

    # Load replay MSL file
    replay_msl_file = MSLFile(args.mth_replay_output_path, args.proto_file_path)
    replay_msl_file.decode_proto()
    replay_msl_file_df = replay_msl_file.to_dict(['stepCountEntry'])

    # ------------------- Plot WalkingSpeed "System vs Replay" --------------------------------
    # Get Step Count entries from System
    st = np.array(in_system_df['stepCountEntry']['cftime'], dtype=float)
    ss = np.array(in_system_df['stepCountEntry']['movementStats']['walkingVariable01'], dtype=float)

    # Get Step Count entries from replay
    rt = np.array(replay_msl_file_df['stepCountEntry']['cftime'], dtype=float)
    rs = np.array(replay_msl_file_df['stepCountEntry']['movementStats']['walkingVariable01'], dtype=float)

    # Adjust timestamps
    min_t = min(st[0], rt[0])
    st = st - st[0]
    rt = rt - rt[0]

    # -------------------- Cumulative distance ----------------
    sd = np.array(in_system_df['stepCountEntry']['distance'], dtype=float)
    rd = np.array(replay_msl_file_df['stepCountEntry']['distance'], dtype=float)

    # Adjust for initial distance in in-system as distance is cumulatively reported in MSL
    min_sd = min(sd)
    sd = sd - min_sd

    # Adjust for initial distance in replay as distance is cumulatively reported in MSL
    min_rd = min(rd)
    rd = rd - min_rd

    # --------------- Iterative distance -------------------
    sd_diffs = []
    prev_value = None
    for x in np.nditer(sd):
        sd_diffs.append(0 if prev_value is None else x - prev_value)
        prev_value = x

    rd_diffs = []
    prev_value = None
    for x in np.nditer(rd):
        rd_diffs.append(0 if prev_value is None else x - prev_value)
        prev_value = x

    # =====  Draw all the plots ================================
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 12))
    fig.suptitle("Pedometer MSL replay", fontsize=14, fontweight="bold")
    fig.subplots_adjust(hspace=0.5)

    # -- Walking speed --
    axes[0].set_xlabel('Seconds', fontsize=12)
    axes[0].set_ylabel('Meters/Sec', fontsize=12)
    axes[0].set_title('IPM Walking Speed: In-System vs. Replay', fontsize=12, fontweight="bold")
    axes[0].scatter(st, ss, color="blue", s=3, label='In System')
    axes[0].scatter(rt, rs, color="red", s=3, label='Replay')

    # -- Cumulative distance --
    axes[1].set_xlabel('Seconds', fontsize=12)
    axes[1].set_ylabel('Distance', fontsize=12)
    axes[1].set_title('Cumulative Distance: In-System vs. Replay', fontsize=12, fontweight="bold")
    axes[1].scatter(st, sd, color="blue", s=3, label='In System')
    axes[1].scatter(rt, rd, color="red", s=3, label='Replay')

    # --- Iterative Distance ------
    axes[2].set_xlabel('Seconds', fontsize=12)
    axes[2].set_ylabel('Distance per step', fontsize=12)
    axes[2].set_title('Iterative Distance: In-System vs. Replay', fontsize=12, fontweight="bold")
    axes[2].scatter(st, sd_diffs, color="blue", s=3, label='In System')
    axes[2].scatter(rt, rd_diffs, color="red", s=3, label='Replay')

    fig.savefig("/tmp/pedometer_replay.jpeg")