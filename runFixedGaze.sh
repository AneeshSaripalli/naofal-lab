#!/bin/bash
if [ $# -lt 1 ]; then
    echo "Usage: $0 <back video path>" >&2
    exit 1
fi
####N.B.: Manually set the start and end frane of the calibration in this script
START=15
END=7200


HAT_BACK="output/AprilTag_Hat1.csv"
OP_VIS="visualize_2/meshsave_back_2.mat"
AprilTag_Calib_Back="output/AprilTag_CalibBack1.csv"
Ref_Calib_Back="config/MarkersAppended2019-6-20.pickle"
KabaschRotTrans="output/KabaschRotTrans.pickle"

APRIL_TAG=./apriltags/build/bin/apriltags_demo

OUTPUT_FOLDER="./output"

# checks if output folder exists

if [ ! -d "$OUTPUT_FOLDER" ]; then
    echo "Creating output folder."
    mkdir $OUTPUT_FOLDER
fi

# checks if APRIL_TAG 
if [ ! -f "$APRIL_TAG" ]; then
    echo "Couldn't find AprilTag at $APRIL_TAG, building source."
    cd apriltags
    make
    cd ..
else
    echo "Could AprilTag at $APRIL_TAG."
fi

echo "Back video file is:   $1"


#### Runs AprilTag with Back behind the scenes for cap
$APRIL_TAG -F 1000 -W 1920 -H 1080 -S 0.032 -I $1 -O "$HAT_BACK" -d -f &

#### Runs AprilTag with Back behind the scenes for calibration
#### Uses $START AND $END defined above to decide the start and end of calibration frames
$APRIL_TAG -F 1000 -W 1920 -H 1080 -S 0.04 -I $1 -O "$AprilTag_Calib_Back" -b $START -e $END -d -f &

wait

##### Calibrate the back camera to obtain the transformation rotation and trasnlation mastrices 
echo "Calculating transformation matrices w.r.t the reference saved back coordinates and outputting to $KabaschRotTrans"
cd apriltags/scripts/
python3 Calibration.py "../../$AprilTag_Calib_Back" "../../$Ref_Calib_Back" "../../$KabaschRotTrans"  & 

wait
cd ../../visualize_2/ #we have to enter visualize_2 directory because files are saved there
echo "Calculating center of mass. Output to $OP_VIS"
python3 Visualize_2.py "../$HAT_BACK" &


wait
cd ..
echo "Standardizing visualize_2 output by writing pose_all matrix from meshsave to a csv file & adding a frame column"
python3 apriltags/scripts/standardize_visualize.py    $HAT_BACK $OP_VIS
