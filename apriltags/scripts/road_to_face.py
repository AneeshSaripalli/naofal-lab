import argparse
import csv

import numpy as np
import pandas as pd
import scipy.io as sio

POSE_MATRIX_NAME = "pose_all"

def get_cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("visualize_output", help="Path of output from visualize_frames.py", type=str)
    parser.add_argument("road_to_back_normalized", help="Path of output from normalize_road.py", type=str)
    parser.add_argument("delta_back_minus_road", help="Frame offset back_sync - road_sync.\
                                                    Ex: if back and road are synced in the CSV files at frame 48 and 34, respectively\
                                                    Input 48-34 = 14 frame offset", type=int)

    args = parser.parse_args()
    return args

X = 0
Y = 1
Z = 2

"""
    Takes in pos which is a 3 tuple representing
        (x, y, z)
    Returns a new tuple (r, phi, theta) which is the spherical
        representation of (x,y,z)
    - r is the magnitude of the vector
    - phi is the angle between the vector and the z+ axis, where a vector along z+ has a phi of 0 
    - theta is the right-handed rotation along the xy plane (rotation around the z+ axis)
"""
def calc_spherical(pos):
    xy = pos[0]**2 + pos[1]**2 

    sph = np.zeros(3)
    sph[0] = np.sqrt(xy + pos[2]**2) #
    sph[1] = np.arctan2(np.sqrt(xy), pos[2]) # for elevation angle defined from Z-axis down
    sph[2] = np.arctan2(pos[1], pos[0])  # 

    return sph

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
    road_frames = len(R2B)

    print("Total Center of Mass Frames", vis_frames)
    print("Total # of lines of Road Data", road_frames)

    R2B = R2B.T # transposing so we can iterate over (what were) rows rather of columns
    POSE_ALL = POSE_ALL.T

    if offset > 0: # back data starts before road video
        # need to move frame pointer ahead in visualize data to sync with road_to_back
        print("need to move visualize data ptr")
        vis_row_ptr = offset

    elif offset < 0: # road data starts before back video
        # need to move row pointer ahead in road_to_back data to sync with visualize
        print("need to move road row ptr")
        road_row_ptr = offset

    face_header = "frame id\tfaceX\tfaceY\tfaceZ\tcomX\tcomY\tcomZ\tr\tphi\ttheta\n"
    face_csv_file.write(face_header)

    # doing frame by frame syncing
    print("Vis Frame %d, Road Row Ptr %d" % (vis_row_ptr, road_row_ptr))

    while vis_row_ptr < vis_frames and road_row_ptr < road_frames:
        vis_row = POSE_ALL[vis_row_ptr]
        road_row = R2B[road_row_ptr]

        vis_f = vis_row['frame id']
        
        if str(road_row['detectionId']) == str(np.nan) or str(vis_row['x']) == str(np.nan):
            row = "%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (int(vis_f), "nan", "nan", "nan", "nan", "nan", "nan", "nan", "nan", "nan") 
            face_csv_file.write(row)
        else:
            road_trans = np.asarray((road_row['projX'], road_row['projY'], road_row['projZ']))
            vis_trans = np.asarray((vis_row['x'], vis_row['y'], vis_row['z']))

            face_to_april = road_trans - vis_trans

            sph = calc_spherical(face_to_april)

            row = "%d\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\n" % (int(vis_f), face_to_april[0], face_to_april[1], face_to_april[2], 
                vis_row['x'], vis_row['y'], vis_row['z'], sph[0], sph[1], sph[2]) 
            face_csv_file.write(row)

        road_row_ptr = road_row_ptr + 1
        vis_row_ptr = vis_row_ptr + 1
    face_csv_file.close()
 
def main():
    args = get_cmd_line_args()

    ROAD_TO_BACK_FILE = open(args.road_to_back_normalized, 'r')
    VISUALIZE = open(args.visualize_output, 'r')

    R2B = pd.read_csv(ROAD_TO_BACK_FILE, sep='\t') # creating pandas dataframe from Road to Back CSV file
    POSE_ALL = pd.read_csv(VISUALIZE, sep='\t') # gettng head pose matrix from matlab file

    face_csv_file = open("output/face_data.csv", 'w+') # opening output file for face csv data

    offset = args.delta_back_minus_road 

    print("Syncing %s and %s with purported offset %d" % (args.road_to_back_normalized, args.visualize_output, offset))

    get_road_data(POSE_ALL, R2B, offset, face_csv_file)
    

if __name__ == '__main__':
    main()
