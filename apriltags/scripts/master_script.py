import argparse

### importing modules to finish subtasks

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("apriltag_back", help="AprilTag from back of driver head", type=str)
    parser.add_argument("apriltag_road", help="AprilTag from front of dashboard viewing road", type=str)
    parser.add_argument("road_offset", help="Number of frames to add to road video to synchronize with back video", type=int)
    parser.add_argument("go_pro_face_vid", help="Camera stream from camera attached to visor in front of driver", type=str)
    parser.add_argument("face_offset", help="Number of frames to add to face video to synchronize with back video", type=int)

    return parser.parse_args()

def main():
    
    print("MAIN")


if __name__ == '__main__':
    main()