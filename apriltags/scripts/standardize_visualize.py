import argparse
import csv

import numpy as np
import pandas as pd
import scipy.io as sio


"""
    The script takes visualize.py output and appends a frame count to it using
        the source apriltag back data file as a reference.
    
    For this to make sense, the visualize file arg but be the output of
        the back arg after processing it through visualize.py
"""


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("back", help="Back CSV file", type=str)
    parser.add_argument('visualize', help='Visualize.py Output file', type=str)

    return parser.parse_args()

def sync_back_and_visualize(visualize_path, back_path, visualize_frames):
    df_back = pd.read_csv(back_path, sep='\t')
    visualize = sio.loadmat(visualize_path)
    pose_all = visualize.get('pose_all')

    row_counter = 0
    frame_counter = 0

    csv_header = "frame id\tx\ty\tz\ta\tbi\tcj\tdk"
    visualize_frames.write(csv_header+"\n")

    data_rows = len(df_back)
    frames = len(pose_all)

    df_back = df_back.T

    print("Back Data Rows:", data_rows)
    print("Unique frames:", frames)

    while row_counter < data_rows and frame_counter < frames:
        frame = int(df_back[row_counter]['frame id'])
        detectionID = int(df_back[row_counter]['detection id'])
        

        if detectionID == 2222:
            visualize_frames.write(
                str(frame) + "\tnan\tnan\tnan\t1.0\t0.0\t0.0\t0.0" + "\n")
        else:

            vis_info = pose_all[frame_counter]

            output_str = str(frame)

            for ele in vis_info:
                output_str = output_str + '\t' + str(ele)

            visualize_frames.write(output_str + "\n")

        frame_counter = frame_counter + 1

        while row_counter < data_rows and not (int(df_back[row_counter]['detection id']) == 2222):
            row_counter = row_counter + 1
        row_counter = row_counter + 1



def main():
    args = get_args()

    visualize_frames = open('output/visualize_frames.csv', 'w+')
    sync_back_and_visualize(args.visualize, args.back, visualize_frames)
    
if __name__ == '__main__':
    main()
