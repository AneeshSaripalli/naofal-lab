import csv
import argparse

X_POS = 3
Y_POS = 4
Z_POS = 5

NULL_MARKER = 2222

def define_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to csv file", type=str)
    parser.add_argument("n", help="nth frame", type=int)
    return parser
  
def move_csv_ptr(csv_reader, search_frame):
    frames = 1
    next(csv_reader, None)  # Skips the header row of the CSV file
    while frames < search_frame:
        row = next(csv_reader, None)
        detectionId = row[1]
        print(frames,row)
        if detectionId == str(NULL_MARKER):  # Checks if the row is a frame terminator row 
            frames = frames + 1
         
def main():
    parser = define_arguments() # Gets the parser object after initializing the required parameters
    args = parser.parse_args()  # Gets the parsed arguments

    path = args.path  # Extracts the path to the road_csv data file
    search_frame = args.n

    print(search_frame)

    file = csv.reader(open(path, 'r'), delimiter='\t')

    move_csv_ptr(file, search_frame)

    row = next(file, None)
    while row[0] != str(NULL_MARKER):
        print (row)
        row = next(file, None)

if __name__ == '__main__':
    main()
