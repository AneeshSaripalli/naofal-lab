import argparse
import pickle
import numpy as np
import pandas as pd
import csv

from math import pi, cos, sin, isnan

from calibration import CalibrationOnce
from calibration import kabschTransformMarkers

import matplotlib.pyplot as plt


"""
@author Aneesh Saripalli
        aps170830@utdallas.edu
    
Calibration for converting back reference position to face current position
"""

DEBUG_FLAG = False


def parse_kabsch_transform_dump(dump_path):
    transform = open(dump_path, "rb")

    rot = pickle.load(transform)
    c_curr = pickle.load(transform)
    c_goal = pickle.load(transform)

    return (rot, c_curr, c_goal)


"""
    transform expects to be a 3-tuple with the form
        (rotation matrix, centroid current frame, centroid goal frame)
"""


def apply_kabsch_tfm(vec, transform):
    (rot, c_curr, c_goal) = transform

    return np.matmul(rot, vec - c_curr) + c_goal


def parse_com(row):
    return (row["Xcom"], row["Ycom"], row["Zcom"])


def parse_target(row):
    return (row["Xtarget"], row["Ytarget"], row["Ztarget"])


def apply_tfms(vec, back_back_tfm, back_face_tfm, face_ref_curr_tfm):
    # converts from back curr to back ref
    target_back_ref = apply_kabsch_tfm(vec, back_back_tfm)

    # converts from back ref to face ref
    target_face_ref = apply_kabsch_tfm(vec, back_face_tfm)

    # converts from face ref to face curr
    target_face_cur = apply_kabsch_tfm(target_face_ref, face_ref_curr_tfm)

    return target_face_cur


def cont_gaze_calib_row(row, back_back_tfm, back_face_tfm, face_ref_curr_tfm):
    tgt = parse_target(row)
    com = parse_com(row)

    tgt_tfm = apply_tfms(tgt, back_back_tfm, back_face_tfm, face_ref_curr_tfm)
    com_tfm = apply_tfms(com, back_back_tfm, back_face_tfm, face_ref_curr_tfm)

    return (tgt_tfm, com_tfm)


def ConvertToSpherical_np(xyz):
    ptsnew = np.zeros(xyz.shape)
    xy = xyz[0]**2 + xyz[1]**2
    ptsnew[0] = np.sqrt(xy + xyz[2]**2)
    # for elevation angle defined from Z-axis down
    ptsnew[1] = np.arctan2(np.sqrt(xy), xyz[2])
    # ptsnew[:,1] = np.arctan2(xyz[:,2], np.sqrt(xy)) # for elevation angle defined from XY-plane up
    ptsnew[2] = np.arctan2(xyz[1], xyz[0])
    return ptsnew


def orchestrate_cg(back_ap, face_ap, anglesId, refBack, refFace):
    print("Continous Gaze Calibration")

    BACK_OUTPUT_PICKLE = './output/Curr_Back.pickle'
    FACE_OUTPUT_PICKLE = "./output/Curr_Face.pickle"

    print("Running calibration once on AprilTag CSV file, store to {}".format(
        BACK_OUTPUT_PICKLE))
    CalibrationOnce.calib(back_ap, BACK_OUTPUT_PICKLE)

    print("Running calibration once on AprilTag CSV file, store to {}".format(
        FACE_OUTPUT_PICKLE))
    CalibrationOnce.calib(face_ap, FACE_OUTPUT_PICKLE)

    BACK_CURR_REF_TFM_OUTPUT = './output/Back_Curr_Ref.pickle'
    BACK_FACE_REF_TFM_OUTPUT = "./output/Back_Face_Ref.pickle"
    FACE_REF_TO_CURR_TFM_OUTPUT = "./output/Face_Ref_Curr.pickle"

    kabschTransformMarkers.find_and_dump_transform(
        BACK_OUTPUT_PICKLE, refBack, BACK_CURR_REF_TFM_OUTPUT)

    kabschTransformMarkers.find_and_dump_transform(
        refBack, refFace, BACK_FACE_REF_TFM_OUTPUT)

    kabschTransformMarkers.find_and_dump_transform(
        refFace, FACE_OUTPUT_PICKLE, FACE_REF_TO_CURR_TFM_OUTPUT)

    back_back_tfm = parse_kabsch_transform_dump(
        BACK_CURR_REF_TFM_OUTPUT)

    back_face_tfm = parse_kabsch_transform_dump(
        BACK_FACE_REF_TFM_OUTPUT)

    face_face_tfm = parse_kabsch_transform_dump(
        FACE_REF_TO_CURR_TFM_OUTPUT)

    angles = pd.read_csv(anglesId, sep="\t")

    minE = 2 * pi - .001
    maxE = -(2 * pi - .001)
    minA = minE
    maxA = maxE

    xpts = []
    ypts = []

    elevs = []

    for i, row in angles.iterrows():
        if DEBUG_FLAG:
            print('Target Label:', row["labels"])

        (target_tfmd, com_tfmd) = cont_gaze_calib_row(
            row, back_back_tfm, back_face_tfm, face_face_tfm)
        target_tfmd[0] = -target_tfmd[0]
        com_tfmd[0] = -com_tfmd[0]

        gaze_vector = np.subtract(target_tfmd, com_tfmd)

        if DEBUG_FLAG:
            print("ORG TGT", parse_target(row))
            print("ORG COM", parse_com(row))
            print("ORG Gaze", np.subtract(parse_target(row), parse_com(row)))
            print("TFM TGT", target_tfmd)
            print("TFM COM", com_tfmd)
            print("TFM Gaze", gaze_vector)
            print("TFM Angles", ConvertToSpherical_np(gaze_vector))

        gaze_angles = ConvertToSpherical_np(gaze_vector)

        (rho, elev, azim) = gaze_angles

        if isnan(elev) is False:
            xpts.append(cos(azim))
            ypts.append(sin(azim))

            elevs.append(azim)

        if DEBUG_FLAG:
            print('Rho: {}, Elev: {}, Azim: {}'.format(rho, elev, azim))
            print()

        minE = min(minE % (2 * pi), gaze_angles[1] % (2 * pi))
        maxE = max(maxE % (2 * pi), gaze_angles[1] % (2 * pi))

        maxA = max(maxA % (2 * pi), gaze_angles[2] % (2 * pi))
        minA = min(minA % (2 * pi), gaze_angles[2] % (2 * pi))

        angles.ix[i, "Rho"] = gaze_angles[0]
        angles.ix[i, "Elev"] = gaze_angles[1]
        angles.ix[i, "Azim"] = gaze_angles[2]

        angles.ix[i, "Xcom"] = com_tfmd[0]
        angles.ix[i, "Ycom"] = com_tfmd[1]
        angles.ix[i, "Zcom"] = com_tfmd[2]

        angles.ix[i, "Xtarget"] = target_tfmd[0]
        angles.ix[i, "Ytarget"] = target_tfmd[1]
        angles.ix[i, "Ztarget"] = target_tfmd[2]

    angles.to_csv(r'./output/AnglesId_Cont_Gaze_Calib.csv',
                  sep='\t', index=False)

    print("Azim := ({}, {})".format(minA, maxA))
    print("Elev := ({}, {})".format(minE, maxE))

    print("Finished orchestration")

    # plt.scatter(xpts, ypts, vmax=1, vmin=-1)
    # plt.figure()

    # plt.hist(elevs, bins=36, range=(-pi,pi))
    # plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "back_ap", help="File path to AprilTag back video output.", type=str)
    parser.add_argument(
        "face_ap", help="File path to AprilTag face video output.", type=str)
    parser.add_argument(
        "anglesId", help="File path to the original AnglesIdFile.csv", type=str)

    parser.add_argument(
        "refBack", help="File path to pickle describing the back reference", type=str)

    parser.add_argument(
        "refFace", help="File path to pickle describing the face reference", type=str)

    args = parser.parse_args()

    orchestrate_cg(args.back_ap, args.face_ap,
                   args.anglesId, args.refBack, args.refFace)
