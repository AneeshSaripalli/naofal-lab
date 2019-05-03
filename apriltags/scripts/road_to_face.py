import argparse
import csv

import numpy as np
import pandas as pd
import scipy.io as sio

POSE_MATRIX_NAME = "pose_all"

def get_cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("visualize_output", help="Output .mat file path from the visualize.py script", type=str)
    parser.add_argument("road_to_back_normalized", help="Output .csv file path from the move_road_to_back script", type=str)
    parser.add_argument("delta_back_minus_road", help="Frame offset back_sync - road_sync.\
                                                    Ex: if back and road are synced in the CSV files at frame 48 and 34, respectively"\
                                                    "Input 48-34 = 14 frame offset", type=int)

    args = parser.parse_args()
    return args

X = 0
Y = 1
Z = 2


"""
    ROW FORMAT for POSE_ALL
    frame id | x   |   y   |   z   |   a |   bi |   cj |   dk
    NOTE:   x,y,z are defined according to the OpenGL reference frame

    x:      double      -x is left, +x is right (rel. to camera)
    y:      double      -y is down, +y is up    (rel. to camera)
    z:      double      -z is forward, +z is back   (rel. to camera)
    a:    double      quarternion scalar
    bi:    double      ^i scalar in the vector portion
    cj:    double      ^j scalar in the vector portion
    dk:    double      ^z scalar in the vector portion

    (a + bi + cj + dk):    quarternion describing the rotation of the head relative to forward
"""

def get_road_data(POSE_ALL, R2B, offset, face_csv_file):
    vis_row_ptr = 0
    road_row_ptr = 0

    vis_frames = len(POSE_ALL)
    road_rows = len(R2B)

    print("Total Center of Mass Frames", vis_frames)
    print("Total # of lines of Road Data", road_rows)

    R2B = R2B.T # transposing so we can iterate over (what were) rows rather of columns
    POSE_ALL = POSE_ALL.T

    if offset > 0: # back data starts before road video
        # need to move frame pointer ahead in visualize data to sync with road_to_back
        print("need to move visualize data ptr")
        vis_row_ptr = offset

    elif offset < 0: # road data starts before back video
        # need to move row pointer ahead in road_to_back data to sync with visualize
        print("need to move road row ptr")
        frame_counter = 0
        while frame_counter != -offset:
            if str(R2B[road_row_ptr]['frameId']) == "nan" or int(R2B[road_row_ptr]['frameId']) == 2222:
                print("New frame")
                frame_counter = frame_counter + 1
            road_row_ptr = road_row_ptr + 1

    face_header = "frame id\tfaceX\tfaceY\tfaceZ\n"
    face_csv_file.write(face_header)

    # doing frame by frame syncing
    print("Vis Frame %d, Road Row Ptr %d" % (vis_row_ptr, road_row_ptr))

    while vis_row_ptr < vis_frames and road_row_ptr < road_rows:
        vis_row = POSE_ALL[vis_row_ptr]
        road_row = R2B[road_row_ptr]

        curr_frame = road_row['frameId']

        print(vis_row)
        print(road_row)
        print('\n')

        vis_row_ptr = vis_row_ptr + 1

        while R2B[road_row_ptr]['frameId'] == curr_frame:
            road_row_ptr = road_row_ptr + 1
        
        road_row_ptr + 1
 
def main():
    args = get_cmd_line_args()

    ROAD_TO_BACK_FILE = open(args.road_to_back_normalized, 'r')
    VISUALIZE = open(args.visualize_output, 'r')

    R2B = pd.read_csv(ROAD_TO_BACK_FILE, sep='\t') # creating pandas dataframe from Road to Back CSV file
    POSE_ALL = pd.read_csv(VISUALIZE, sep='\t') # gettng head pose matrix from matlab file

    face_csv_file = open("../../output/face_data.csv", 'w+') # opening output file for face csv data

    offset = args.delta_back_minus_road 

    print("Syncing %s and %s with purported offset %d" % (args.road_to_back, args.visualize_output, offset))

    get_road_data(POSE_ALL, R2B, offset, face_csv_file)
    

if __name__ == '__main__':
    main()
