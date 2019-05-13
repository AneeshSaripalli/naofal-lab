import argparse

import pandas as pd

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('road_to_back_path', help="path to road_to_back projected csv data", type = str)
    parser.add_argument('markerId', help="AprilTag marker id", type=int)
    return parser.parse_args()

def normalize_road(r2b_file_path, apriltag_id):
    df_r2b = pd.read_csv(r2b_file_path, sep='\t')
    csv_output = open('output/road_normalized.csv', 'w+')

    rows = len(df_r2b)

    df_r2b = df_r2b.T

    last_frame = -1
    row_counter = 0

    header = "frameId\tdetectionId\tdistance\tprojX\tprojY\tprojZ\n"
    csv_output.write(header)

    null_row = "nan	0.0	0.0	0.0	0.0"

    while row_counter < rows:
        row = df_r2b[row_counter]
        frameId = int(row['frameId'])
        detectId = int(row['detectionId'])
        
        if detectId == apriltag_id:
            for i in range(last_frame+1, frameId):
                csv_output.write(str(i) + '\t' + null_row + '\n')
            last_frame = frameId
            csv_output.write(str(frameId) + '\t' + str(detectId) + '\t' + str(row['distance']) + '\t' + str(row['projX']) + '\t' + str(row['projY']) + '\t' + str(row['projZ']) + '\n')

        row_counter = row_counter + 1




def main():
    args = get_args()
    r2b_path = args.road_to_back_path
    markerId = args.markerId

    print("Normalizing", r2b_path)
    normalize_road(r2b_path, markerId)

if __name__ == '__main__':
    main()