# XRoboToolkit-PC-Service-Pybind

This project provides a python interface to extract XR state using XRoboToolkit-PC-Service sdk.

currently the PXREAsdk from pico is not supporting the linux arch64 platform, because the libs need to recompile locally and need more building configurations

## Requirements

- [`pybind11`](https://github.com/pybind/pybind11)
- [`XRoboRoolkit PC Service`](https://github.com/XR-Robotics/XRoboToolkit-PC-Service#)

## Building the Project
### Ubuntu 22.04

```
conda remove --name xr --all
conda create -n xr python=3.10
conda activate xr

mkdir -p tmp
cd tmp
git clone https://github.com/XR-Robotics/XRoboToolkit-PC-Service.git
cd XRoboToolkit-PC-Service/RoboticsService/PXREARobotSDK 
bash build.sh
cd ../../../..

mkdir -p lib
mkdir -p include
cp tmp/XRoboToolkit-PC-Service/RoboticsService/PXREARobotSDK/PXREARobotSDK.h include/
cp -r tmp/XRoboToolkit-PC-Service/RoboticsService/PXREARobotSDK/nlohmann include/nlohmann/
cp tmp/XRoboToolkit-PC-Service/RoboticsService/PXREARobotSDK/build/libPXREARobotSDK.so lib/
# rm -rf tmp

# Build the project
conda install -c conda-forge pybind11

pip uninstall -y xrobotoolkit_sdk
python setup.py install
```
### Linux Ubuntu 22.04 arm64 version (Nvidia orin supported)
```
bash setup_orin.sh
```
### Windows

**Ensure pybind11 is installed before running the following command.**

```
setup_windows.bat
```

```

**Body Joint Indices (similar to SMPL, 24 joints total):**
- 0: Pelvis, 1: Left Hip, 2: Right Hip, 3: Spine1, 4: Left Knee, 5: Right Knee
- 6: Spine2, 7: Left Ankle, 8: Right Ankle, 9: Spine3, 10: Left Foot, 11: Right Foot
- 12: Neck, 13: Left Collar, 14: Right Collar, 15: Head, 16: Left Shoulder, 17: Right Shoulder
- 18: Left Elbow, 19: Right Elbow, 20: Left Wrist, 21: Right Wrist, 22: Left Hand, 23: Right Hand
