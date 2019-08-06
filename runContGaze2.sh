

STD_ROAD="output/road_normalized.csv"
STD_VIS="output/visualize_frames.csv"

AP_BACK="output/D2019-7-9/ContGaze/AprilBackOutdoor.csv"
AP_ROAD="output/D2019-7-9/ContGaze/AprilRoadOutdoor.csv"
HAT_BACK="output/D2019-7-9/ContGaze/AprilHatContGaze.csv"

OP_R2B="output/road_proj_to_back.csv"
OP_FACE="output/ContGazeIntialLabelsAllFrames.csv"
OP_VIS="visualize_2/meshsave_back_2.mat"
OutDoorTagID="300"
B_R_offset="0" # sync Offset in frame number between the back and the road videos
F_offset="0"



cd visualize_2/
echo "Calculating center of mass. Output to $OP_VIS"
python3 Visualize_2.py "../$HAT_BACK" &
cd ..

wait

echo "Projecting road distance vectors to the back camera using the sync frames defined in move_back_to_road.py. Output to $OP_R2B"
python3 apriltags/scripts/kabsch_move_road_to_back.py $AP_ROAD

wait

echo "Standardizing visualize_2 output by writing pose_all matrix from meshsave to a csv file & adding a frame column"
python3 apriltags/scripts/standardize_visualize.py    $HAT_BACK $OP_VIS &

echo "Standardizing $OP_R2B by considering only AprilTag marker frames and changing file schema"
python3 apriltags/scripts/standardize_road.py $OP_R2B $OutDoorTagID &

wait

echo "Extracting viable face frames by combining visualize_frames.csv & road_normalized.csv"
python3 apriltags/scripts/unify_road_and_head.py      $STD_VIS     $STD_ROAD  $B_R_offset

