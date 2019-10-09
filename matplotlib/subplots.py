import argparse
import numpy as np
import os
import sys

import matplotlib.pyplot as plt

from LocationQA.Common.Motion.msl_parser import MSLFile

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Provide System and Replay MSL for Pedometer replay')
    parser.add_argument('--system_msl', '-s', dest="system_msl_path", default=None, required=True)
    parser.add_argument('--proto_file_path', '-p', dest="proto_file_path", default=None, required=True)
    parser.add_argument('--output_chart_path', '-o', dest="output_chart_path", default=None, required=True)
    args = parser.parse_args()

    # Check if arguments are well formed
    if not os.path.exists(args.system_msl_path):
        print "Cant find system msl file"
        sys.exit(-1)


    if not os.path.exists(args.proto_file_path):
        print "Cant find proto file path"
        sys.exit(-1)

    # Load in-system msl file
    in_system_msl_file = MSLFile(args.system_msl_path, args.proto_file_path)
    in_system_msl_file.decode_proto()


    in_system_df = in_system_msl_file.to_dict(['workoutRecorderAccel', 'super'])

    # ------------------- Prepare data for  WalkingSpeed "System vs Replay" --------------------------------
    # Get Step Count entries from System
    st = np.array(in_system_df['workoutRecorderAccel']['super']['timestamp'], dtype=float)


    # Adjust timestamps
    st = st - st[0]
    rt = rt - rt[0]

    # -------------------- Prepare data for Cumulative distance ----------------
    x = np.array(in_system_df['workoutRecorderAccel']['super']['x'], dtype=float)
    y = np.array(replay_msl_file_df['workoutRecorderAccel']['super']['y'], dtype=float)
    z = np.array(replay_msl_file_df['workoutRecorderAccel']['super']['z'], dtype=float)

    # Adjust for initial distance in in-system as distance is cumulatively reported in MSL
    sd = sd - min(sd)

    # -------------------Prepare data for 'Accel' -----------
    accel_t = np.array(in_system_accel["cftime"])
    accel_x = np.array(in_system_accel['x'])
    accel_y = np.array(in_system_accel['y'])
    accel_z = np.array(in_system_accel['z'])

    # =====  Draw all the plots ================================
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(15, 12))
    fig.suptitle("Pedometer MSL replay", fontsize=14, fontweight="bold")
    fig.subplots_adjust(hspace=0.5)
    st_min, st_max = min(st), max(st)
    rt_min, rt_max = min(rt), max(rt)
    st = st - min(st)
    rt = rt - min(rt)
    accel_t = accel_t - min(accel_t)
    x_min, x_max = min(st_min, rt_min), max(st_max, rt_max)
    accel_t_min, accel_t_max = min(accel_t), max(accel_t)

    # --- Accel -----
    axes[0].set_xlabel('Seconds', fontsize=12)
    axes[0].set_ylabel('In System Accel', fontsize=12)
    axes[0].set_xlim(x_min, x_max)
    axes[0].scatter(accel_t, accel_x, color="blue", s=3, label='x')
    axes[0].scatter(accel_t, accel_y, color="red", s=3, label='y')
    axes[0].scatter(accel_t, accel_z, color="green", s=3, label='z')
    axes[0].set_title('In System Accel', fontsize=12, fontweight="bold")
    axes[0].legend(loc="upper left")

    fig.savefig(args.output_chart_path)
