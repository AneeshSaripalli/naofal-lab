import csv
import argparse

X_POS = 4
Y_POS = X_POS + 1
Z_POS = X_POS + 2

NULL_MARKER = 2222

R2B_OUTPUT_FILE = '../output/road_proj_to_back.csv'

'''
    Usage:
        python move_road_to_back.py <backX - roadX> <backY - roadY> <backZ - roadZ> <road_csv_file>
'''

#
#   Defines all arguments taken in by command line
#       Road and Back are the calibration positions used
#       dX: float   |   backX - roadX;
#       dY: float   |   backY - roadY;
#       dZ: float   |   backZ - roadZ;
#       road_csv_path: str  |   CSV data file containing AprilTag output for the road camera
#
def define_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("dx", help="x transform", type=float)
    parser.add_argument("dy", help="y transform", type=float)
    parser.add_argument("dz", help="z transform", type=float)
    parser.add_argument('road_csv_path', help="road data file", type=str)
    return parser

'''
    road_csv_row: array |   A single non-header row from the AprilTag road camera output   
        Extracts and returns the (x: float, y: float, z: float) tuple from the row of csv data
    Structure:
        frameId | detectionId | Hamming Distance | Distance | X | Y | Z | Yaw | Pitch | Roll
'''
def extract_pos_from_csv(road_csv_row):
    return (float(road_csv_row[X_POS]), float(road_csv_row[Y_POS]), float(road_csv_row[Z_POS]))

'''
    road_csv_row: array |   Single non-header row from AprilTag road camera output
        Interest specifically in (x, y, z) data contained in said row
    proj_vec: 3-tuple   | Calibration vector (projX, projY, projZ) defined s.t. 
        <Calibration road vec> + <Proj vec> = <Calibration back vec>   
'''
def get_r2b_proj_pos(road_csv_row, proj_vec):
    road_pos = extract_pos_from_csv(road_csv_row)
    return (road_pos[0] + proj_vec[0], road_pos[1] + proj_vec[1], road_pos[2] + proj_vec[2])

'''
    r2b_csv_file: file handle |     File handle on the output data file to pipe the projected road vector positions to
    r2b_vec:    3-tuple |   (back ^x, back ^y, back ^z) projection calculated by <back ^vec> = <road csv vec> + <proj vec>  
'''
def write_to_r2b_file(r2b_csv_file, frameId, detectionId, total_dist, r2b_vec, hammingDistance = -1):
    r2b_csv_file.write(str(frameId) + '\t' + str(detectionId) + '\t' + str(total_dist) + '\t' + str(r2b_vec[0]) + '\t' + str(r2b_vec[1]) + '\t' + str(r2b_vec[2]) + '\n')

def magnitude(vector):
    return pow(pow(vector[0], 2) + pow(vector[1], 2) + pow(vector[2], 2), .5)

def write_header(r2b_proj_csv_file):
    r2b_proj_csv_file.write('frameId' + '\t' + 'detectionId' + '\t' + 'distance' + '\t' + 'projX' + '\t' 'projY' + '\t' + 'projZ' + '\n')

def main():
    parser = define_arguments() # Gets the parser object after initializing the required parameters
    args = parser.parse_args()  # Gets the parsed arguments

    proj_vec = (args.dx, args.dy, args.dz)  # Extracts the calibration-based projection vector
    road_csv_path = args.road_csv_path  # Extracts the path to the road_csv data file

    r2b_proj_csv_file = None
    try:
        r2b_proj_csv_file = open(R2B_OUTPUT_FILE, 'w+')
    except:
        print('Unable to open output R2B data file @ %s' % R2B_OUTPUT_FILE)

    write_header(r2b_proj_csv_file)

    with open('../output/%s' % road_csv_path, 'r') as road_csv:
        csv_reader = csv.reader(road_csv, delimiter='\t')
        next(csv_reader, None)  # Skips the header row of the CSV file
        for row in csv_reader:
            frameId = int(row[0])   # Casts the frameId value in the first column to an int
            detectionId = row[1]
            if frameId == NULL_MARKER:  # Checks if the row is a frame terminator row 
                write_to_r2b_file(r2b_proj_csv_file, frameId, detectionId, 2222, (NULL_MARKER, NULL_MARKER, NULL_MARKER))
            else:
                r2b_proj_vec = get_r2b_proj_pos(row, proj_vec)
                write_to_r2b_file(r2b_proj_csv_file, frameId, detectionId, magnitude(r2b_proj_vec), r2b_proj_vec)

if __name__ == '__main__':
    main()
