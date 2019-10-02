#!/bin/bash

# ./runCalibFolder <calib folder> <back calib picle> <face calib pickle>


CALIB_FOLDER=$1
BACK_CALIB=$2
FACE_CALIB=$3

echo "Calibration folder is $CALIB_FOLDER"

FG_FACE_START=(0 2 3 4)
FG_FACE_END=(300 3 4 5)

CG_FACE_START=(0 2 3 4)
CG_FACE_END=(300 2 3 4)

CG_BACK_START=(11100 2 3 4)
CG_BACK_END=(11400 2 3 4)


index=0
for f in $1/; do
    echo "Folder $index: $f"
    CG_HOME=$f/cg

    CG_AP=$CG_HOME/cg_ap.csv
    CG_BACK=$CG_HOME/cg_back.mp4
    CG_FACE=$CG_HOME/cg_face.mp4

    
    mkdir $f"output"

    echo $f"output"

    rm -f output/*

    mkdir $f"output/fg"
    
    ./runContGazeCalibration.sh $CG_AP $CG_FACE ${CG_FACE_START[index]} ${CG_FACE_END[index]} $CG_BACK ${CG_BACK_START[index]} ${CG_BACK_END[index]} $BACK_CALIB $FACE_CALIB

    cp -r output $f"output/fg"

    ### END OF CONT GAZE

    FG_HOME=$f/fg

    FG_AP=$FG_HOME/fg_ap.csv
    FG_FACE=$FG_HOME/fg_face.mp4

    rm -f output/*

    mkdir $f"output/cg"

    ./runFixedGazeCalibration.sh $FG_FACE $FG_AP ${FG_FACE_START[index]} ${FG_FACE_END[index]} $BACK_CALIB $FACE_CALIB

    cp -r output $f"output/cg"

    ((index=index+1))

done
