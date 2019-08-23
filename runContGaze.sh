
cd apriltags

# Run AprilTags on back-outdoor, back-cap and road-outdoor cameras
./build/bin/apriltags_demo -F 1000 -W 1920 -H 1080 -S 0.176 -I "/home/marzban/Downloads/ContGaze2019-7-11/BContGaze.mp4" -O /home/marzban/calibrateCameras/naofal-lab/output/D2019-7-11/ContGaze/AprilBackOutdoor.csv -f -d &
./build/bin/apriltags_demo -F 1000 -W 1920 -H 1080 -S 0.032 -I "/home/marzban/Downloads/ContGaze2019-7-11/BContGaze.mp4" -O /home/marzban/calibrateCameras/naofal-lab/output/D2019-7-11/ContGaze/AprilHatContGaze.csv -f -d &
./build/bin/apriltags_demo -F 1000 -W 1920 -H 1080 -S 0.176 -I "/home/marzban/Downloads/ContGaze2019-7-11/RContGaze.mp4" -O /home/marzban/calibrateCameras/naofal-lab/output/D2019-7-11/ContGaze/AprilRoadOutdoor.csv -f -d 

wait

echo "Finished running all 3 files"



