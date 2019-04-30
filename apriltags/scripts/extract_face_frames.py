import argparse
import cv2
import csv

def define_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("face_video_path",      help="Face Video Path", type=str)
    parser.add_argument("face_video_offset",    help="Data CSV frame offset. This will be the same as the start frame of the back camera data stream.", type=int)
    parser.add_argument("face_csv_data",        help="Data CSV File", type=str)
    return parser

def open_csv(face_csv_path):
    face_csv = open(face_csv_path, 'r')
    return csv.reader(face_csv, delimiter='\t')

def main():
    parser = define_arguments()
    args = parser.parse_args()

    print_imgs(args.face_video_path, args.face_video_offset, args.face_csv_data)
    print(args)

def print_imgs(video_path, csv_offset, csv_data):
    video = cv2.VideoCapture(video_path)

    face = open_csv(csv_data)

    csv_length = int((len(list(face)) - 1) / 2)

    print(csv_length)

    success,image = video.read()
    count = 0
    while success and count < csv_offset:
        success,image = video.read()
        count += 1
    
    print("Finally got to proper offset.")
    while success:   
        index = count - csv_offset
        if index >= csv_length:
            break
        cv2.imwrite("../face_imgs/frame%d.png" % index, image)
        print("Wrote frame %d" % index)
        success,image = video.read()
        count += 1


if __name__ == '__main__':
    main()