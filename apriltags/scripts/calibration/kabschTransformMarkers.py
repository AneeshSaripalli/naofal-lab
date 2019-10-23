# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 20:04:13 2019
Transforming from XYZ_current coordinate to ref coordinate

@author: mfm160330
"""


import csv
import numpy as np
import pickle
import rmsd

### --- CONSTANTS --- ###
# These values are only used if you run this file indvidully. If you run pipeline these parameters are not used(bec. you call only the needed functions)
FACE_CURR = "./calib_files/FaceCurr2019-6-14.pickle"  
FACE_REF = "./calib_files/FaceCalib2019-6-20.pickle"
BACK_REF = "./calib_files/BackCalibAll2019-6-20Rmv300.pickle"
FACE_TRANSFORM_PATH = "./calib_files/FaceCurrToRef.pickle"
BACK_TO_FACE_TRANSFORM_PATH = "./calib_files/BackToFaceRefCalib.pickle"

### --- FACE REFERENCE TO FACE CURRENT TRANSFORMATION --- ###
"""
CURR_FRAME_PATH = FACE_REF
GOAL_FRAME_PATH = FACE_CURR
OUTPUT_PATH = FACE_TRANSFORM_PATH
"""
### --- END --- ###

### --- BACK REFERENCE TO FACE REFERNCE TRANSFORMATION --- ####
CURR_FRAME_PATH = BACK_REF
GOAL_FRAME_PATH = FACE_REF
OUTPUT_PATH = BACK_TO_FACE_TRANSFORM_PATH
### --- END --- ###

### --- END CONSTANTS --- ###


def find_common_markers(marker_list_1, marker_list_2):
    return list(set(marker_list_1) & set(marker_list_2))


def get_count(path):
    pickle_in = open(path, "rb")
    pickle.load(pickle_in)
    pickle.load(pickle_in)
    pickle.load(pickle_in)
    pickle.load(pickle_in)
    return np.ravel(pickle.load(pickle_in))


def parse_pickle(path, marker_indexes):
    print("loading pickle from", path)
    pickle_in = open(path, "rb")
    pickle.load(pickle_in)

    x = pickle.load(pickle_in)
    y = pickle.load(pickle_in)
    z = pickle.load(pickle_in)

    XlabelUni = np.array(np.ravel(x)[np.array(marker_indexes)])
    XlabelUni = np.reshape(XlabelUni, (len(marker_indexes), 1))

    YlabelUni = np.array(np.ravel(y)[np.array(marker_indexes)])
    YlabelUni = np.reshape(YlabelUni, (len(marker_indexes), 1))

    ZlabelUni = np.array(np.ravel(z)[np.array(marker_indexes)])
    ZlabelUni = np.reshape(ZlabelUni, (len(marker_indexes), 1))

    matrix = np.hstack((XlabelUni, YlabelUni, ZlabelUni))

    print('Kabsch Calibration Matrix:\n', matrix)

    return matrix


def read_markers(path):
    print(path)
    return pickle.load(open(path, "rb"))


"""
    Returns a tuple consisting of (R, C_curr, C_ref)
        specifiying the rotation, current centroid, and reference centroid
    Uses Kabsch algorithm to minimize rmsd through a matrix transformation
        between pointsCurrent to pointsRef
"""


def kabsch(pointsCurrent, pointsRef):

    C_curr = rmsd.centroid(pointsCurrent)
    C_ref = rmsd.centroid(pointsRef)

    points_curr_norm = pointsCurrent - C_curr  # XYZ current after centering
    points_ref_norm = pointsRef - C_ref

    # the optimal rotation matrix to rotate XYZcurrent to XYZref
    R = rmsd.kabsch(points_curr_norm, points_ref_norm)

    return (R, C_curr, C_ref)


def find_transform(curr_path, goal_path):
    curr_markers = read_markers(curr_path)
    print("Found {} in curr.".format(curr_markers))
    goal_markers = read_markers(goal_path)
    print("Found {} in goal.".format(goal_markers))
    common_markers = find_common_markers(curr_markers, goal_markers)

    if len(common_markers) < 3:
        print("Can't run Kabsch algorithm. Only found {} common markers.".format(
            common_markers))
        exit()

    print("Found common markers {}.".format(common_markers))
    print("Using {} for Kabsch transformation.".format(common_markers))

    #count_1 = get_count(curr_path)
    #count_2 = get_count(goal_path)

    #common_markers = list(filter(lambda x: (count_1[np.where(curr_markers == x)[
    #                      0][0]] != 0 and count_2[np.where(goal_markers == x)[0][0]] != 0), common_markers))

    curr_indexes = [(np.where(curr_markers == cm)[0][0])
                    for cm in common_markers]
    goal_indexes = [(np.where(goal_markers == cm)[0][0])
                    for cm in common_markers]

    print('Shared markers correspond to CURR indices {}'.format(list(curr_indexes)))
    print('Shared markers correspond to GOAL indices {}'.format(list(goal_indexes)))

    curr_calib_matrix = parse_pickle(curr_path, curr_indexes)
    goal_calib_matrix = parse_pickle(goal_path, goal_indexes)

    return kabsch(curr_calib_matrix, goal_calib_matrix)


"""
    Rotation process from P to Q:
        (R, c_cur, c_ref) = kabsh(P, Q)

    To rotate a point V:
        np.matmul(V - c_cur, R) + c_ref
"""


def find_and_dump_transform(CURR_FRAME_PATH, GOAL_FRAME_PATH, OUTPUT_PATH):
    (R, c_curr, c_goal) = find_transform(CURR_FRAME_PATH, GOAL_FRAME_PATH)

    calib_once_output = open(OUTPUT_PATH, "wb")

    print("Rotation\n", R)
    print("Centroid of curr reference frame", c_curr)
    print("Centroid of goal reference frame", c_goal)

    print("Dumping rotation and centroids to pickle file \"{}\"".format(OUTPUT_PATH))

    pickle.dump(R, calib_once_output)
    pickle.dump(c_curr, calib_once_output)
    pickle.dump(c_goal, calib_once_output)


def main():
    find_and_dump_transform(CURR_FRAME_PATH, GOAL_FRAME_PATH, OUTPUT_PATH)


if __name__ == '__main__':
    main()
