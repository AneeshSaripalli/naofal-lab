import argparse
import pickle
import numpy as np
import pandas as pd
import csv

from calibration import CalibrationOnce
from calibration import kabschTransformMarkers

"""
@author Aneesh Saripalli
        aps170830@utdallas.edu
    
Calibration for converting back reference position to face current position
"""


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


def move_target_pos_to_back(row):
    com = parse_com(row)
    target_from_com = parse_target(row)
    target_from_back = np.add(com, target_from_com)
    return target_from_back


def apply_tfms(vec, back_face_tfm, face_ref_curr_tfm):
    target_face_ref = apply_kabsch_tfm(vec, back_face_tfm)
    target_face_cur = apply_kabsch_tfm(target_face_ref, face_ref_curr_tfm)

    return target_face_cur


def calib_target(row, back_face_tfm, face_ref_curr_tfm):
    target_pos = move_target_pos_to_back(row)
    return apply_tfms(target_pos, back_face_tfm, face_ref_curr_tfm)


def calib_com(row, back_face_tfm, face_ref_curr_tfm):
    com = parse_com(row)
    return apply_tfms(com, back_face_tfm, face_ref_curr_tfm)


def calib_row(row, back_face_tfm, face_ref_curr_tfm):
    return (calib_target(row, back_face_tfm, face_ref_curr_tfm), calib_com(row, back_face_tfm, face_ref_curr_tfm))


def orchestrate(apriltag, anglesId, refBack, refFace):
    print("Calib")
    FACE_OUTPUT_PICKLE = "./output/Curr_Face.pickle"

    CalibrationOnce.calib(apriltag, FACE_OUTPUT_PICKLE)

    BACK_FACE_REF_TFM_OUTPUT = "./output/Back_Face_Ref.pickle"
    FACE_REF_TO_CURR_TFM_OUTPUT = "./output/Face_Ref_Curr.pickle"
    kabschTransformMarkers.find_and_dump_transform(

        refBack, refFace, BACK_FACE_REF_TFM_OUTPUT)
    kabschTransformMarkers.find_and_dump_transform(
        refFace, FACE_OUTPUT_PICKLE, FACE_REF_TO_CURR_TFM_OUTPUT)

    back_face_tfm = parse_kabsch_transform_dump(
        BACK_FACE_REF_TFM_OUTPUT)
    face_face_tfm = parse_kabsch_transform_dump(
        FACE_REF_TO_CURR_TFM_OUTPUT)

    apply_kabsch_tfm((1, 2, 3), parse_kabsch_transform_dump(
        BACK_FACE_REF_TFM_OUTPUT))

    angles = pd.read_csv(anglesId, sep="\t")

    for _, row in angles.iterrows():
        (target_tfmd, com_tfmd) = calib_row(row, back_face_tfm, face_face_tfm)
        print(row["labels"])
        row["Xcom"] = com_tfmd[0]
        row["Ycom"] = com_tfmd[1]
        row["Zcom"] = com_tfmd[2]
        row["Xtarget"] = target_tfmd[0]
        row["Ytarget"] = target_tfmd[1]
        row["Ztarget"] = target_tfmd[2]

    angles.to_csv(r'./output/AprilTags_Calib.csv', sep='\t', index=False)

    print("Finished orchestration")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "apriltag", help="File path to AprilTag face video output.", type=str)
    parser.add_argument(
        "anglesId", help="File path to the original AnglesIdFile.csv", type=str)

    parser.add_argument(
        "refBack", help="File path to pickle describing the back reference", type=str)

    parser.add_argument(
        "refFace", help="File path to pickle describing the face reference", type=str)

    args = parser.parse_args()

    orchestrate(args.apriltag, args.anglesId, args.refBack, args.refFace)
