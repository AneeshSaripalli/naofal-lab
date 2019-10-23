#!/bin/bash

# HEADS UP PLEASE READ THIS
# FG stands for Fixed Gaze
# CG stands for Continous Gaze


# When running this, you may need to adjust the [FG/CG]_[BACK/FACE]_[START/END] frame starting
# and ending values. These values specify the frames to use in AprilTag for calibration.
# no synchronization is required for these frames - we just need at least 3 commonly detected tags 
# between the current reference frame and the base reference frame (stored in the pickles)
# these base reference frames are stored twice in this directory (for no good reason),
# once in ./config
# once in ./apriltags/scripts/calibration/calib-files

# ./runCalibFolder <calib folder> <back calib picle> <face calib pickle>

# sample usage is as follows.
# calib specifies the root directory to look for all drives
# ./runCalibFolder.sh ~/Desktop/shared/calib ./apriltags/scripts/calibration/calib_files/BackCalibAll2019-6-20Rmv300.pickle ./apriltags/scripts/calibration/calib_files/FaceCalib2019-6-20.pickle 


# expected folder struct

# root
    # <drive folder 1>
        # cg
            # cg_ap.csv         Processed apriltag for continuous gaze
            # cg_face.mp4       Raw continuous gaze face video for calibration
            # cg_back.mp4       Raw continuous gaze back video for calibration
        # fg
            # fg_ap.csv         Processed apriltag for fixed gaze
            # fg_face.mp4       Raw fixed gaze face video for calibration



CALIB_FOLDER=$1
BACK_CALIB=$2
FACE_CALIB=$3

echo "Calibration folder is $CALIB_FOLDER"

### DEFINE FRAMES FOR CALIBRATION

FG_FACE_START=(32400 36000 28800 0 0 7200) #(36000 36000 10800 10800 14400 0 7200 36000 7200) #(14400 0 3600) #(0 0 0 0 0 0 0 0 0 0 0)
FG_FACE_END=(36000 39600 32400 1 1 10800) #(43200 43200 18000 14400 18000 3600 10800 39600 10800) #(18000 3605 7210) #(11400 11400 11400 300 300 300 300 300 300 300 300)

CG_FACE_START=(0 0 0 0 0 0) #(0 0 0 0 0 0 0 0 0) #(0 0 0) #(0 0 0 0 0 0 0 0 0 0 0)
CG_FACE_END=(3600 3600 3600 3600 3600 3600) #(3600 3600 3600 3600 3600 3600 3600 3600 3600) #(3600 3600 3600) #(11400 11400 11400 300 300 300 300 300 300 300 300)

CG_BACK_START=(0 0 0 0 0 0) #(0 0 0 0 0 0 0 0 0) #(0 0 0) #(0 0 0 0 0 0 0 0 0 0 0)
CG_BACK_END=(3600 3600 3600 3600 3600 3600) #(3600 3600 10800 10800 3600 3600 3600 3600 3600) #(3600 3600 3600) #(11400 11400 11400 300 300 300 300 300 300 300)

### END CALIB FRAMES DEFINITION ###

if [ ! -d "./output" ]; then
    mkdir output
fi

index=0
# iterates through all files in root dir
for f in $1/*; do 
    echo "Folder $index: $f"
    CG_HOME=$f/cg

    CG_AP=$CG_HOME/AnglesIDfile.csv
    CG_BACK=$CG_HOME/BContGaze.mp4
    CG_FACE=$CG_HOME/FContGaze.mp4

    echo "$f/output"

    rm -f output/*
    

    echo "===================ContinuousGaze $f====================================="
    ./runContGazeCalibration.sh $CG_AP $CG_FACE ${CG_FACE_START[index]} ${CG_FACE_END[index]} $CG_BACK ${CG_BACK_START[index]} ${CG_BACK_END[index]} $BACK_CALIB $FACE_CALIB

    cp -r output "$f/cg"

    ### END OF CONT GAZE

    FG_HOME=$f/fg

    FG_AP=$FG_HOME/AnglesIDfile.csv
    FG_FACE=$FG_HOME/FfixedGaze.mp4

    rm -f output/*

    echo "===================FixedGaze $f====================================="
    ./runFixedGazeCalibration.sh $FG_FACE $FG_AP ${FG_FACE_START[index]} ${FG_FACE_END[index]} $BACK_CALIB $FACE_CALIB

    cp -r output "$f/fg"

    ((index=index+1))

done

rm -f output/*

