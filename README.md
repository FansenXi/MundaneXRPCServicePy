# Mundane-XR-PCService-Pybind

This project provides a python interface to extract XR state using XRoboToolkit-PC-Service sdk.

Currently supported environments: Linux aarch64 and amd64.

## Requirements

- Python 3.10
- [`pybind11`](https://github.com/pybind/pybind11)
- [`XRoboToolkit PC Service`](https://github.com/XR-Robotics/XRoboToolkit-PC-Service#)

## Building the Project
download the apk and corresponding deb file in the release page.
```
apt install corresponding.deb
cd /opt/app/RoboticsService
./runService.sh
```
run the [runService.sh](/opt/app/RoboticsService/runService.sh) every time the computer starts up to start a pico service process

Run the corresponding script based on your operating platform:
### Ubuntu 22.04

```
conda create -n PCService python=3.10
conda activate PCService
bash setup_ubuntu.sh #or setup_orin.sh accroding to your platform
```
### Pico headset operation to connect to PCService
1. Power on the Pico headset.
2. Connect the Pico headset to the PC using a USB cable.
3. adb install MundaneRoboToolkit.apk
4. Start the newly installed xrobotoolkit application on the Pico headset.
5. If the PC service is running, a dialog will automatically rise up to confirm the connection with the PC after a few seconds.
6. After confirming the connection, the USB share network toggle need to be turned on.
7. press the button StartSendToPC to start sending video in hevc to the PC port 12345 via the usb shared network.
