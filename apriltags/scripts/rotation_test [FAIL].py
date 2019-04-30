import numpy as np
from scipy.spatial.transform import Rotation as R
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("rx", type=float)
    parser.add_argument("ry", type=float)
    parser.add_argument("rz", type=float)
    
    parser.add_argument("bx", type=float)
    parser.add_argument("by", type=float)
    parser.add_argument("bz", type=float)
    return parser.parse_args()

# left multiply by the rotation matrix produced from here
def construct_zyx_rot(rx, ry, rz):
    rot_x = np.array([
                    [1, 0, 0],
                    [0, np.cos(rx), -np.sin(rx)],
                    [0, np.sin(rx),  np.cos(rx)]
                    ])
    rot_y = np.array([
                    [np.cos(ry), 0, np.sin(ry)],
                    [0, 1, 0],
                    [np.sin(ry), 0, np.cos(ry)]
                    ])
    rot_z = np.array([
        [np.cos(rz), -np.sin(rz), 0],
        [np.sin(rz), np.cos(rz), 0],
        [0, 0, 1]
        ])

    return np.matmul(rot_z, np.matmul(rot_y, rot_x))                           

def main():
    args = parse_args()

    mat_road = construct_zyx_rot(args.rx, args.ry, args.rz)
    mat_back = construct_zyx_rot(args.bx, args.by, args.bz)

    mat_back_inv = np.linalg.inv(mat_back)

    delta = mat_back_inv * mat_road
    print("Rotation between Road Cam and Back Cam")
    print(delta)
    


if __name__ == "__main__":
    main()
    