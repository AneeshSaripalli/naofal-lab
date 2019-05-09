# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 16:09:13 2018

@author: txh160830
"""

import argparse
import csv
import os

import matplotlib.pyplot as plt
import numpy as np
import rmsd
import scipy.io as sio
from mpl_toolkits.mplot3d import Axes3D
from pyquaternion import Quaternion

import rotation_functions as rf

"""
    This script accepts a back camera data output from AprilTag
        and attempts to calculate the center of mass for each frame
        in the AprilTag output. 
    There's no frame count attached to the output because I'm afraid
        of the rest of the weird phantom math going on in this script.
    Run this code through append_frame_to_visualize.py to append
        a frame count in the first column.
    This code outputs multiple tables/matrices in a .mat matlab file -
        the most pertinent is pose_all, which outputs the (x,y,z) displacement 
        of the center of mass along with the rotation of the center of mass
        relative to the back camera as a quarternion. 
"""



NULL_MARKER = 2222


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "csv_file", help='CSV Data File to get Center of Mass', type=str)
    return parser.parse_args()


def main():
    args = get_args()
    back_csv_path = args.csv_file
    process_back_data(back_csv_path)


def process_back_data(file):    
    f_cam = 1000
    n_tags = 23
    no_subj = 1
    pose_all = np.empty((no_subj), dtype=object)
    mesh_all = np.empty((no_subj), dtype=object)
    suct = 0
    
    print('Calculating center of mass on file', file)
    for i in np.array([1]):  # files in os.listdir(path_loc):
        file_path = file
        f = open(file_path)
        csv_f = csv.reader(f, delimiter='\t')

        new_frame = np.empty((23, 7, 1))
        new_frame[:] = np.NAN
        full_array = new_frame.copy()
        count = -1
        for row in csv_f:
            row = row[1:]
            if (count == -1):
                count = count+1
            elif (row[1] == str(NULL_MARKER)):
                full_array = np.append(full_array, new_frame, axis=2)
                count = count+1
            else:
                if (int(row[0]) < 23):
                    read_array = np.asarray(row[2:]).astype(np.float)
                    quart = Quaternion(matrix=rf.eul2mat(read_array[4:]))
                    full_array[int(row[0]), :, count] = np.concatenate(
                        (np.array([-read_array[2], read_array[3], -read_array[1]]), quart.elements), axis=0)
        full_array = full_array[:, :, :-1]
        f.close()

        pose_all[suct] = full_array
        suct += 1
        final_ori = np.zeros((full_array.shape[2], full_array.shape[1]))
        cur_fullmesh = np.empty((n_tags*4, 3, full_array.shape[2]))
        cur_fullmesh[:] = np.NaN
        mesh_visible = np.empty((n_tags*4, 3, full_array.shape[2]))
        mesh_visible[:] = np.NaN

        vismesh_px = np.empty((n_tags*4, 2, full_array.shape[2]))
        vismesh_px[:] = np.NaN

        fullmesh_px = np.empty((n_tags*4, 2, full_array.shape[2]))
        fullmesh_px[:] = np.NaN
        err_dist = np.zeros((full_array.shape[2], 1))

        avg_mesh = np.load("mesh_calib.npy")

        for f_ct in range(0, full_array.shape[2]):
            cur_mesh = np.empty((n_tags*4, 3))
            cur_mesh[:] = np.NaN
            for tag_ct in range(0, n_tags):
                cur_mesh[tag_ct*4:(tag_ct+1)*4, :] = rf.orient_square(
                    full_array[tag_ct, 0:3, f_ct], Quaternion(full_array[tag_ct, 3:, f_ct]))
            while True:
                mesh1 = avg_mesh[(~np.isnan(cur_mesh[:, 1])), :]
                mesh2 = cur_mesh[(~np.isnan(cur_mesh[:, 1])), :]
                m1c = rmsd.centroid(mesh1)
                m2c = rmsd.centroid(mesh2)
                mesh1 -= m1c
                mesh2 -= m2c
                rot2_1 = rmsd.kabsch(mesh1, mesh2)
                cur_fullmesh[:, :, f_ct] = np.dot(avg_mesh - m1c, rot2_1) + m2c
        #        if f_ct >= 2:
        #            cur_fullmesh[:,:,f_ct] = np.nansum((0.5*cur_fullmesh[:,:,f_ct],0.3*cur_fullmesh[:,:,f_ct-1],0.2*cur_fullmesh[:,:,f_ct-2]),axis = 0)
                err = np.linalg.norm(
                    cur_fullmesh[:, :, f_ct] - cur_mesh, axis=1)
                if mesh1.shape[0] == 0:
                    break
                if np.partition(err, 3)[3] > 0.005:
                    break
                elif (np.nanmean(err) < 0.005):
                    break
                cur_mesh[np.nanargmax(err), :] = np.array(
                    [np.nan, np.nan, np.nan])
            final_ori[f_ct, 0:3] = rmsd.centroid(cur_fullmesh[:, :, f_ct])
            final_ori[f_ct, 3:] = Quaternion(matrix=rot2_1).elements

    #        mesh_visible[(~np.isnan(cur_mesh[:,1])),:] = cur_fullmesh[(~np.isnan(cur_mesh[:,1])),:]
            vismesh_px[:, 0, f_ct] = 960 - \
                (cur_mesh[:, 0]/cur_mesh[:, 2]*f_cam)
            vismesh_px[:, 1, f_ct] = 540 + \
                (cur_mesh[:, 1]/cur_mesh[:, 2]*f_cam)
            fullmesh_px[:, 0, f_ct] = 960 - \
                (cur_fullmesh[:, 0, f_ct]/cur_fullmesh[:, 2, f_ct]*f_cam)
            fullmesh_px[:, 1, f_ct] = 540 + \
                (cur_fullmesh[:, 1, f_ct]/cur_fullmesh[:, 2, f_ct]*f_cam)
            err_dist[f_ct] = np.nanmean(np.linalg.norm(
                cur_fullmesh[:, :, f_ct] - cur_mesh, axis=1))
            if np.size(mesh2, axis=0) <= 12:
                err_dist[f_ct] = 1
            loc = rmsd.centroid(cur_fullmesh)
        #pose_all[suct] = final_ori
        #mesh_all[suct] = fullmesh_px
        suct = suct+1
        print(suct)

    axis_px = np.empty((4, 2, full_array.shape[2]))
    axis_px[:] = np.NaN
    for ct in range(0, full_array.shape[2]):
        rot_mat = Quaternion(np.array(
            [final_ori[ct, 3], final_ori[ct, 4], final_ori[ct, 5], final_ori[ct, 6]])).rotation_matrix/25
        ax = np.c_[rot_mat, final_ori[ct, 0:3]]
        ax_ad = ax.copy()
        for row in range(3):
            ax_ad[:, row] = ax[:, row] + final_ori[ct, 0:3]
            axis_px[:, 0, ct] = 960 - (ax_ad[0, :]/ax_ad[2, :]*f_cam)
            axis_px[:, 1, ct] = 540 + (ax_ad[1, :]/ax_ad[2, :]*f_cam)

    axis_px1 = np.empty((4, 2, full_array.shape[2]))
    axis_px1[:] = np.NaN
    for ct in range(0, full_array.shape[2]):
        rot_mat = Quaternion(np.array(
            [final_ori[ct, 6], final_ori[ct, 5], final_ori[ct, 4], final_ori[ct, 3]])).rotation_matrix/25
        ax = np.c_[rot_mat, final_ori[ct, 0:3]]
        ax_ad = ax.copy()
        for row in range(3):
            ax_ad[:, row] = ax[:, row] + final_ori[ct, 0:3]
            axis_px1[:, 0, ct] = 960 - (ax_ad[0, :]/ax_ad[2, :]*f_cam)
            axis_px1[:, 1, ct] = 540 + (ax_ad[1, :]/ax_ad[2, :]*f_cam)

    # sio.savemat('meshsave_back_2.mat',{'vismesh_px':vismesh_px,'mesh_all':fullmesh_px,'pose_all':pose_all[1],'axis_px':axis_px,'axis_px1':axis_px1})
    sio.savemat('meshsave_back_2.mat', {'vismesh_px': vismesh_px, 'mesh_all': fullmesh_px,
                                        'pose_all': final_ori, 'axis_px': axis_px, 'axis_px1': axis_px1})


if __name__ == "__main__":
    main()
