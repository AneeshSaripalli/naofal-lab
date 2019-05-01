import scipy.io as sio
import argparse
import numpy as np
import csv
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("back", help="Back CSV file", type=str)
    parser.add_argument('visualize', help='Visualize.py Outpt file', type=str)

    return parser.parse_args()

def main():
    args = get_args()

    visualize_frames = open('../../output/visualize_frames.csv', 'w+')
    
    df_back = pd.read_csv(args.back, sep='\t')

    visualize = sio.loadmat(args.visualize)

    pose_all = visualize.get('pose_all')

    counter = 0
    rows = len(df_back)

    print(len(df_back), len(pose_all))

    length = min(len(df_back), len(pose_all))

    df_back = df_back.T

    print(df_back.keys)


    for i in range(0, length):
        frame = int(df_back[i]['frame id'])
        vis_info = pose_all[i]

        output_str = str(frame) + '\t'
        
        for ele in vis_info:
            output_str = output_str + str(ele) + '\t'

        visualize_frames.write(output_str + "\n")
    
if __name__ == '__main__':
    main()
