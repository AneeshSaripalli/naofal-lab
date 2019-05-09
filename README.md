# Overview
## File Structure
```
.
+-  _AprilTag
+-- _apriltags                      # home directory for all of the AprilTag software
|   +-- _example
|   +-- _scripts                    # home directory for the python script pipeline
|       +-- move_road_to_back.py
|       +-- standardize_road.py
|       +-- standardize_visualize.py    # adds a frame count to the matlab output from visualize
|       +-- rot_matrix.solve.py     # attempts to solve for calibration between road & back cams
        +-- unify_road_and_face.py  # uses data from both road & face to get COM to AprilTag & spherical coords
        +-- extract_faces_frames.py # uses output from unify... & face video to extract labelled frames
|   +-- Makefile                    # run make in apriltags/ to build the AprilTag library
|   +-- CMakeLists.txt              # CMake is called in the make process to build the C++ exe
+-- _output                         # write & defacto read folder for data in the python scripts
|   +-- _MOHAMMED DRIVING
|       +-- BACK_DATA_FRAMES.csv
|       +-- ... more unused files
|   +--_TIANJING DRIVING
|       +-- ROAD_CLEAR_2.csv
|       +-- BACK_CLEAR_2.csv
|   +-- AprilTag_Back.csv           # AprilTag (back cam) will create [ AprilTag]
|   +-- AprilTag_Road.csv           # AprilTag (road cam) will create [AprilTag]
|   +-- road_proj_to_back.csv       # Road cam data => back cam [move_road_to_back.py]
|   +-- road_normalized.csv         # road_proj data to look like visualize_2 data [std_road.py]
|   +-- visualize_frames.csv        # Visualize_2 output with frame count added [std_vis.py] 
+-- _visualize_2
|   +-- Visualize_2.py              # script to calculate center of mass from back data
|   +-- mesh_calib.npy              # calibration file required for Visualize_2.py to work properly
|   +-- rotation_functions.py       # library module for rotation calculations in Visualize_2
++- run.sh                          # master pipeline, will output labelled face images 
```
## Script Pipeline
Running `AprilTags/run.sh` will do the following things.
  1) Run the `AprilTag` software (`./apriltags/build/bin/apriltags_demo`) on the road facing video and back facing video in parallel -> `output/road.csv`, `output/back.csv` - expect this to take a very long time (10+ hour)
  2) NOTE: Please change the sync vectors in `scripts/move_road_to_back.py` before running this. Run `scripts/move_road_to_back.py` using `output/road.csv` -> `output/road_proj_to_back.csv`
  3) Run `visualize_2/Visualize_2.py` on `back.csv` -> `visualize_2/meshsave_back_2.mat`
  4) Run `scripts/standardize_visualize.py` on `meshsave_back_2.mat` -> `output/visualize_frames.csv` 
  5) Run `scripts/standarize_road.py` on `road.csv` -> `road_normalized.csv`
  6) Run `scripts/road_to_face.py` on `visualize_frames.csv` & `road_normalized.csv` and the frame offset -> `face_data.csv`
  7) Run `scripts/extract_face_frames.py` -> labelled face images in `imgs/*`

## AprilTags library

Detect April tags (2D bar codes) in images; reports unique ID of each
detection, and optionally its position and orientation relative to a
calibrated camera.

See examples/apriltags_demo.cpp for a simple example that detects
April tags (see tags/pdf/tag36h11.pdf) in laptop or webcam images and
marks any tags in the live image.

Ubuntu dependencies:
sudo apt-get install subversion cmake libopencv-dev libeigen3-dev libv4l-dev

Mac dependencies:
sudo port install pkgconfig opencv eigen3

Uses the pods build system in connection with cmake, see:
http://sourceforge.net/p/pods/

Michael Kaess
October 2012

----------------------------

AprilTags were developed by Professor Edwin Olson of the University of
Michigan.  His Java implementation is available on this web site:
  http://april.eecs.umich.edu.

Olson's Java code was ported to C++ and integrated into the Tekkotsu
framework by Jeffrey Boyland and David Touretzky.

See this Tekkotsu wiki article for additional links and references:
  http://wiki.tekkotsu.org/index.php/AprilTags

----------------------------

This C++ code was further modified by
Michael Kaess (kaess@mit.edu) and Hordur Johannson (hordurj@mit.edu)
and the code has been released under the LGPL 2.1 license.

- converted to standalone library
- added stable homography recovery using OpenCV
- robust tag code table that does not require a terminating 0
  (omission results in false positives by illegal codes being accepted)
- changed example tags to agree with Ed Olson's Java version and added
  all his other tag families
- added principal point as parameter as in original code - essential
  for homography
- added some debugging code (visualization using OpenCV to show
  intermediate detection steps)
- added fast approximation of arctan2 from Ed's original Java code
- using interpolation instead of homography in Quad: requires less
  homography computations and provides a small improvement in correct
  detections

todo:
- significant speedup could be achieved by performing image operations
  using OpenCV (Gaussian filter, but also operations in
  TagDetector.cc)
- replacing arctan2 by precomputed lookup table
- converting matrix operations to Eigen (mostly for simplifying code,
  maybe some speedup)