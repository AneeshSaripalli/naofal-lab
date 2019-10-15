#!/bin/bash
if [ $# -lt 6 ]; then
    echo "Usage: $0 <face video path> <angles id file> <calib start frame> <calib end frame> <back calibration pickle> <face calibration pickle>" >&2
    exit 1
fi

APRIL_TAG=./apriltags/build/bin/apriltags_demo

CURR_FACE="output/CURR_FACE_AP_TAG_OUTPUT.csv"

CALIB_SCRIPT="apriltags/scripts/calibrateFromFixedGaze.py"

FACE_VIDEO_PATH=$1
ANGLES_ID_FILE=$2
CALIB_FRAME_START=$3
CALIB_FRAME_END=$4
BACK_CALIB_PICKLE=$5
FACE_CALIB_PICKLE=$6

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


#$APRIL_TAG -F 1000 -W 1920 -H 1080 -S 0.04 -I $FACE_VIDEO_PATH -O $CURR_FACE -d -f -b $CALIB_FRAME_START -e $CALIB_FRAME_END

python3 $CALIB_SCRIPT $CURR_FACE $ANGLES_ID_FILE $BACK_CALIB_PICKLE $FACE_CALIB_PICKLE

# TEST COMMAND: python3 apriltags/scripts/calibrateFromFixedGaze.py /home/marzban/Downloads/ReCalibrate/2019-5-22/fg/output/CURR_FACE_AP_TAG_OUTPUT.csv /home/marzban/Downloads/ReCalibrate/2019-5-22/fg/AnglesIDfile.csv ./apriltags/scripts/calibration/calib_files/BackCalibAll2019-6-20.pickle ./apriltags/scripts/calibration/calib_files/FaceCalib2019-6-20.pickle 
