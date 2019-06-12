#!/bin/bash
if [ $# -lt 1 ]; then
    echo "Usage: $0 <back video path>" >&2
    exit 1
fi

HAT_BACK="output/AprilTag_Hat.csv"
OP_VIS="visualize_2/meshsave_back_2.mat"
Calib_Back="output/CalibBack.csv"

echo "Back video file is:   $1"


# Runs AprilTag with Back behind the scenes for cap
#./apriltags/build/bin/apriltags_demo -F 1000 -W 1920 -H 1080 -S 0.032 -I $1 -O "$HAT_BACK" -d -f 

# Runs AprilTag with Back behind the scenes for calibration
#./apriltags/build/bin/apriltags_demo -F 1000 -W 1920 -H 1080 -S 0.04 -I $1 -O "$Calib_Back" -d -f 

#wait

python3 apriltags/scripts/Calibration.py $Calib_Back &

cd visualize_2/ #we have to enter visualize_2 directory because files are saved there
echo "Calculating center of mass. Output to $OP_VIS"
python3 Visualize_2.py "../$HAT_BACK" &
cd ..

wait

echo "Standardizing visualize_2 output by writing pose_all matrix from meshsave to a csv file & adding a frame column"
python3 apriltags/scripts/standardize_visualize.py    $HAT_BACK $OP_VIS
