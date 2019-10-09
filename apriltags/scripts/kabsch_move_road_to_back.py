import argparse
import csv

import numpy as np

import rot_matrix_solve as d_basis
import rmsd

# Translation Basis Definitions
# All sync positions are defined row wise (x, y, z)
# Back points 
MAT_B = np.array([
    [3.01962, -1.62632, -0.0588382], 
    [3.01049, -1.32811, -0.0523163],
    [4.73079, 0.513522, 0.348696],
    [6.7341, -0.0642532, -0.255916],
    [3.29329, -1.66661, -0.0864262]
])

#corresponding road points
MAT_R = np.array([
    [1.83623, -1.38257, -0.198698], 
    [1.82529, -1.08902, -0.177534],
    [3.59977, 0.669499, 0.14374],
    [5.07927, 0.160885, -0.598324],
    [1.91183, -1.3677, -0.206757]
])

# End Basis Definitions


X_POS = 4
Y_POS = X_POS + 1
Z_POS = X_POS + 2

NULL_MARKER = 2222

R2B_OUTPUT_FILE = '/home/marzban/calibrateCameras/naofal-lab/output/road_proj_to_back.csv'
#road_csv_path = '/home/marzban/calibrateCameras/naofal-lab/output/D2019-5-30/ContGaze/AprilRoadOutdoor.csv'  # Extracts the path to the road_csv data file

'''
    Usage:
        python3 move_road_to_back.py <road_csv_file>
'''

#
#   Defines all arguments taken in by command line
#       Road and Back are the calibration positions used
#       road_csv_path: str  |   CSV data file containing AprilTag output for the road camera
#
def define_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('road_csv_path', help="road data file", type=str)
    return parser


"""
    road_csv_row: array |   A single non-header row from the AprilTag road camera output   
        Extracts and returns the (x: float, y: float, z: float) tuple from the row of csv data
    Structure:
        frameId | detectionId | Hamming Distance | Distance | X | Y | Z | Yaw | Pitch | Roll
"""
def extract_pos_from_csv(road_csv_row):
    return (float(road_csv_row[X_POS]), float(road_csv_row[Y_POS]), float(road_csv_row[Z_POS]))


'''
    r2b_csv_file: file handle |     File handle on the output data file to pipe the projected road vector positions to
    r2b_vec:    3-tuple |   (back ^x, back ^y, back ^z) projection calculated by <back ^vec> = <road csv vec> + <proj vec>  
'''
def write_to_r2b_file(r2b_csv_file, frameId, detectionId, total_dist, r2b_vec, hammingDistance=-1):
    r2b_csv_file.write(str(frameId) + '\t' + str(detectionId) + '\t' + str(total_dist) +
                       '\t' + str(r2b_vec[0]) + '\t' + str(r2b_vec[1]) + '\t' + str(r2b_vec[2]) + '\n')


def magnitude(vector):
    return pow(pow(vector[0], 2) + pow(vector[1], 2) + pow(vector[2], 2), .5)


def write_header(r2b_proj_csv_file):
    r2b_proj_csv_file.write('frameId' + '\t' + 'detectionId' + '\t' +
                            'distance' + '\t' + 'projX' + '\t' 'projY' + '\t' + 'projZ' + '\n')

'''
Given a matrix of back points (MAT_B) and the corresponding matrix of road points (MAT_R),
This function calculates the rotation (R) and the centeroid (translation vectors) required to transform road points to back
'''
def KabschTransform (MAT_B, MAT_R):
    C_road = rmsd.centroid (MAT_R) # centreroid of the road points
    C_back = rmsd.centroid (MAT_B) # centreroid of the back points
    XYZroad_centered = MAT_R - C_road  #XYZ of road after centering 
    XYZback_centered = MAT_B - C_back  #XYZ of back after centering
    R = rmsd.kabsch(XYZroad_centered, XYZback_centered) # the optimal rotation matrix to rotate road points to back coordinates
    return C_road, C_back, R

def get_r2b_proj_pos(road_csv_row, R, C_road, C_back):
    road_pos = np.asarray(extract_pos_from_csv(road_csv_row))
    
    back_pos = np.matmul(road_pos - C_road, R) + C_back 

    return back_pos


def main():
    # Gets the parser object after initializing the required parameters
    parser = define_arguments()
    args = parser.parse_args()  # Gets the parsed arguments
    
    road_csv_path = args.road_csv_path  # Extracts the path to the road_csv data file
    print("============================road CSV path is ", road_csv_path,'/n')

    r2b_proj_csv_file = None
    try:
        r2b_proj_csv_file = open(R2B_OUTPUT_FILE, 'w+')
    except:
        print('Unable to open output R2B data file @ %s' % R2B_OUTPUT_FILE)

    write_header(r2b_proj_csv_file)
    
    C_road, C_back, R = KabschTransform (MAT_B, MAT_R)
    
    #(R, T, _) = d_basis.calc_basis_change(MAT_R, MAT_B, MAT_R, MAT_B)
    #trans_vec = d_basis.calc_trans_vec_from_mat(T)

    print("Yielded Rotation")
    print(R)

    print("Yielded Road centeroid")
    print(C_road)
    
    print("Yielded Back centeroid")
    print(C_back)

    with open(road_csv_path, 'r') as road_csv:
        csv_reader = csv.reader(road_csv, delimiter='\t')
        next(csv_reader, None)  # Skips the header row of the CSV file
        for row in csv_reader:
            # Casts the frameId value in the first column to an int
            frameId = int(row[0])
            detectionId = row[1]
            if int(detectionId) == NULL_MARKER:  # Checks if the row is a frame terminator row
                write_to_r2b_file(r2b_proj_csv_file, frameId, detectionId,
                                  2222, (NULL_MARKER, NULL_MARKER, NULL_MARKER))
            else:
                r2b_proj_vec = get_r2b_proj_pos(row, R, C_road, C_back)
                write_to_r2b_file(r2b_proj_csv_file, frameId, detectionId, magnitude(
                    r2b_proj_vec), r2b_proj_vec)


if __name__ == '__main__':
    main()
