#!/bin/bash

if [ $# -lt 9 ]; then
    echo "Usage: $0 <angles id file> <face video path> <face calib start frame> <face calib end frame> <back video path> <back calib start frame> <back calib end frame> <back calibration pickle> <face calibration pickle>" >&2
    exit 1
fi

APRIL_TAG=./apriltags/build/bin/apriltags_demo

CURR_FACE="output/CURR_FACE_AP_TAG_OUTPUT.csv"
CURR_BACK="output/CURR_BACK_AP_TAG_OUTPUT.csv"

CALIB_SCRIPT="apriltags/scripts/calibrateFromContGaze.py"

ANGLES_ID_FILE=$1

FACE_VIDEO_PATH=$2
FACE_CALIB_FRAME_START=$3
FACE_CALIB_FRAME_END=$4

BACK_VIDEO_PATH=$5
BACK_CALIB_FRAME_START=$6
BACK_CALIB_FRAME_END=$7

BACK_CALIB_PICKLE=$8
FACE_CALIB_PICKLE=$9

echo "Storing AprilTag Face Calib data in $CURR_FACE"

# checks if APRIL_TAG 
if [ ! -f "$APRIL_TAG" ]; then
    echo "Couldn't find AprilTag at $APRIL_TAG, building source."
    cd apriltags
    make
    cd ..
else
    echo "Using AprilTag at $APRIL_TAG."
fi


$APRIL_TAG -F 1000 -W 1920 -H 1080 -S 0.04 -I $FACE_VIDEO_PATH -O $CURR_FACE -d -f -b $FACE_CALIB_FRAME_START -e $FACE_CALIB_FRAME_END &
$APRIL_TAG -F 1000 -W 1920 -H 1080 -S 0.04 -I $BACK_VIDEO_PATH -O $CURR_BACK -d -f -b $BACK_CALIB_FRAME_START -e $BACK_CALIB_FRAME_END

wait

python3 $CALIB_SCRIPT $CURR_BACK $CURR_FACE $ANGLES_ID_FILE $BACK_CALIB_PICKLE $FACE_CALIB_PICKLE

# TEST COMMAND: python3 apriltags/scripts/calibrateFromFixedGaze.py ./output/CURR_FACE_AP_TAG_OUTPUT.csv ~/Desktop/shared/calib_files/AnglesIDfile.csv ./apriltags/scripts/calibration/calib_files/BackCalibAll2019-6-20.pickle ./apriltags/scripts/calibration/calib_files/FaceCalib2019-6-20.pickle 