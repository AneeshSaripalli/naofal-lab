import scipy.io as sio
import argparse
import numpy as np
import csv
import pandas as pd

POSE_MATRIX_NAME = "pose_all"

def get_cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("visualize_output", help="Output .mat file path from the visualize.py script", type=str)
    parser.add_argument("road_to_back", help="Output .csv file path from the move_road_to_back script", type=str)
    parser.add_argument("delta_back_minus_road", help="Frame offset back_sync - road_sync.\
                                                    Ex: if back and road are synced in the CSV files at frame 48 and 34, respectively"\
                                                    "Input 48-34 = 14 frame offset", type=int   )

    args = parser.parse_args()
    return args

X = 0
Y = 1
Z = 2

def write_to_face_data_file(fptr, write_str):
    fptr.write(write_str)

"""
    ROW FORMAT for POSE_ALL
    x   |   y   |   z   |   q_w |   q_x |   q_y |   q_z

    NOTE:   x,y,z are defined according to the OpenGL reference frame

    x:      double      -x is left, +x is right (rel. to camera)
    y:      double      -y is down, +y is up    (rel. to camera)
    z:      double      -z is forward, +z is back   (rel. to camera)
    q_x:    double      quarternion scalar
    q_w:    double      ^i scalar in the vector portion
    q_y:    double      ^j scalar in the vector portion
    q_z:    double      ^z scalar in the vector portion

    (q):    quarternion describing the rotation of the head relative to forward
"""
def main():
    args = get_cmd_line_args()

    VIS_FILE = sio.loadmat(args.visualize_output)
    ROAD_TO_BACK_FILE = open(args.road_to_back, 'r')

    R2B = pd.read_csv(ROAD_TO_BACK_FILE, sep='\t') # transposing so we can iterate over (what were) rows rather of columns
    
    POSE_ALL = VIS_FILE.get(POSE_MATRIX_NAME)

    face_csv_file = open("../output/face_data.csv", 'w+')

    offset = args.delta_back_minus_road

    b2f_rptr = 0
    r2b_rptr = 0

    b2f_len = len(POSE_ALL)
    r2b_len = len(R2B)

    R2B = R2B.T

    if offset > 0:
        b2f_rptr = offset
    elif offset < 0:
        r2b_rptr = offset


    face_header = "faceX\tfaceY\tfaceZ\n"
    write_to_face_data_file(face_csv_file, face_header)

    while b2f_rptr < b2f_len and r2b_rptr < r2b_len:
        if R2B[r2b_rptr]['frameId'] == 2222:
            faceX = 2222
            faceY = 2222
            faceZ = 2222
        else:
            faceX = float(POSE_ALL[b2f_rptr][X]) + R2B[r2b_rptr]['projX']
            faceY = float(POSE_ALL[b2f_rptr][Y]) + R2B[r2b_rptr]['projY']
            faceZ = float(POSE_ALL[b2f_rptr][Z]) + R2B[r2b_rptr]['projZ']
        
        face_data = (faceX, faceY, faceZ)

        face_str = str(faceX) + "\t" + str(faceY) + "\t" + str(faceZ) + "\n"
        write_to_face_data_file(face_csv_file, face_str)


        b2f_rptr = b2f_rptr+1
        r2b_rptr = r2b_rptr+1
    

def testr2breader(r2breader):
    for row in r2breader:
        print(row[0])

if __name__ == '__main__':
    main()

