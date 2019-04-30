import csv
import argparse

NULL_MARKER = 2222

def define_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("road", help="road csv", type=str)
    parser.add_argument("back", help="back csv", type=str)
    parser.add_argument("offset", help="road minus back offset", type=int)
    return parser


def move_csv_ptr(csv_reader, search_frame):
    frames = 1
    next(csv_reader, None)  # Skips the header row of the CSV file
    while frames < search_frame:
        row = next(csv_reader, None)
        detectionId = row[0]
        if detectionId == str(NULL_MARKER):  # Checks if the row is a frame terminator row 
            frames = frames + 1


def find_matching(dId, road_csv, back_csv):
    print("Searching for dID", dId)
    sat = False
    frame = 0

    while sat is False:

        back_row = next(back_csv, None)
        road_row = next(road_csv, None)

        print(back_row)
        print(road_row)

        if back_row == None and road_row is None:
            break

        move_csv_ptr(road_csv, 1)
        move_csv_ptr(back_csv, 1)
        
        frame = frame + 1


def main():
    parser = define_arguments() # Gets the parser object after initializing the required parameters
    args = parser.parse_args()  # Gets the parsed arguments

    road_path = args.road  # Extracts the path to the road_csv data file
    back_path = args.back  
    offset = args.offset

    road_csv = csv.reader(open(road_path, 'r'), delimiter='\t')
    back_csv = csv.reader(open(back_path, 'r'), delimiter='\t')
    print("ROAD",next(road_csv, None))
    print("BACK",next(back_csv, None))

    if offset > 0:
        move_csv_ptr(road_csv, offset)
    elif offset < 0:
        move_csv_ptr(back_csv, -offset)
    
    find_matching("100", road_csv, back_csv)

if __name__ == '__main__':
    main()
