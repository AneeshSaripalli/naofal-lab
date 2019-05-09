import argparse
import cv2
import csv
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("face_video_path",      help="Face Video Path", type=str)
    parser.add_argument("face_csv_data",        help="Data CSV File", type=str)
    parser.add_argument("face_video_offset",    help="Video sync offset back - face. This will be the same as the start frame of the back camera data stream.", type=int)
    parser.add_argument("road_video_offset",    help="Video sync offset back - road", type=int)

    return parser.parse_args()

def open_csv(face_csv_path):
    face_csv = open(face_csv_path, 'r')
    return csv.reader(face_csv, delimiter='\t')

def main():
    args = get_args()
    
    print_imgs(args.face_video_path, args.face_video_offset, args.road_video_offset, args.face_csv_data)

def print_imgs(video_path, face_offset, road_offset, csv_data):
    video = cv2.VideoCapture(video_path)

    face = pd.read_csv(csv_data, sep='\t')

    csv_length = len(face)

    print("Face length is",csv_length)

    face = face.T

    success,image = video.read()
    face_index = 0 # face_index = back frame at this point

    OFFSET = face[0]['frame id']

    while True:   
        back_index = face_index + face_offset
        road_index = back_index - road_offset

        face_data_index = back_index - OFFSET

        if road_index >= csv_length:
            print("Hit last frame in CSV")
            break
        if face_data_index >= 0 and str(face[face_data_index]['faceX']) != 'nan':
            cv2.imwrite("imgs/face_b%d_f%d.png" % (back_index, face_index), image)
            print("Printing frame %d (road) | %d (back) | %d (face)" % (road_index, back_index, face_index))
            print('Combined data line:', face[face_data_index])
        else:
            print("frame id %d (road) | %d (back) | %d (face)" % (road_index, back_index, face_index))
        success,image = video.read()
        face_index += 1


if __name__ == '__main__':
    main()