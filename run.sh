if [ $# -lt 6 ]; then
    echo "Usage: $0 <back video path> <road video path> <road video offset> <face video path> <face video offset> <apriltag marker>" >&2
    exit 1
fi

STD_ROAD="output/road_normalized.csv"
STD_VIS="output/visualize_frames.csv"

AP_BACK="output/AprilTag_Back.csv"
AP_ROAD="output/AprilTag_Road.csv"

OP_R2B="output/road_proj_to_back.csv"
OP_FACE="output/face_data.csv"
OP_VIS="visualize_2/meshsave_back_2.mat"

FACE_IMGS="imgs"

echo "Back video file is:   $1"
echo "Road video file is:   $2"
echo "Road back offset is:  $3"
echo "Face video file is:   $4"
echo "Face video offset is: $5"
echo "AprilTag marker is:   $6"

cd apriltags

# Runs AprilTag with Back & Road behind the scenes
#./build/bin/apriltags_demo -F 1080 -W 1920 -H 1080 -S 0.176 -I "$1" -O "$AP_BACK" -d -f & ./build/bin/apriltags_demo -F 1080 -W 1920 -H 1080 -S 0.176 -I $2 -O "$AP_ROAD" -d -f

# Waits for AprilTag to the parallel processes to finish  
wait

cd .. 

cd visualize_2/
echo "Calculating center of mass. Output to $OP_VIS"
#python3 Visualize_2.py ../output/AprilTag_Back.csv &
cd ..

echo "Projecting road distance vectors to the back camera using the sync frames defined in move_back_to_road.py. Output to $OP_R2B"
#python3 apriltags/scripts/move_road_to_back.py $AP_ROAD &

wait

echo "Standardizing visualize_2 output by writing pose_all matrix from meshsave to a csv file & adding a frame column"
#python3 apriltags/scripts/standardize_visualize.py    $AP_BACK $OP_VIS &

echo "Standardizing $OP_R2B by considering only AprilTag marker frames and changing file schema"
#python3 apriltags/scripts/standardize_road.py         $OP_R2B      $6 &

wait

echo "Extracting viable face frames by combining visualize_frames.csv & road_normalized.csv"
#python3 apriltags/scripts/unify_road_and_face.py      $STD_VIS     $STD_ROAD  $3

if [ ! -d $FACE_IMGS ]; then
    mkdir $FACE_IMGS
fi

python3 apriltags/scripts/extract_face_frames.py $4 $OP_FACE $5 $3

