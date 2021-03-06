# E-Puck Driver for ROS2
[![Build Status](https://travis-ci.com/cyberbotics/epuck_ros2.svg?branch=master)](https://travis-ci.com/cyberbotics/epuck_ros2)
[![license - apache 2.0](https://img.shields.io/:license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Version](https://img.shields.io/github/v/tag/cyberbotics/epuck_ros2?label=version)](http://wiki.ros.org/epuck_ros2)

<img src="./assets/pi-puck.jpg" width="400px" />

This package adds ROS2 support for the [e-puck](https://www.gctronic.com/doc/index.php/e-puck2) physical robot with [Pi-puck extension](https://www.gctronic.com/doc/index.php?title=Pi-puck).
Please use the following links for the instructions:
- [Installation](./installation/README.md)
- [Getting Started](#getting-started)
- [Examples](https://github.com/cyberbotics/webots_ros2/blob/master/webots_ros2_epuck/EPUCK_ROS2.md)
- [Simulation](https://github.com/cyberbotics/webots_ros2/tree/master/webots_ros2_epuck)

## Getting Started
Make sure you followed the [installation tutorial](./installation/README.md), so you have ROS2 and `epuck_ros2` installed on your robot.
If everything properly installed you should be able to source your ROS2 workspace:
```
source $HOME/ros2_ws/install/local_setup.bash
```

Then, launch the driver:
```
ros2 launch webots_ros2_epuck2 robot_launch.py
```
This command will activate a ROS2 node with support for all sensors and actuators available on the e-puck except the camera.
We consider the camera node be heavy for device such as Raspberry Pi Zero W and therefore it is not included by default.
You can activate the camera node as:
```
ros2 launch webots_ros2_epuck2 robot_launch.py camera:=true
```

Your robot should be ready now and you can check examples [here](https://github.com/cyberbotics/webots_ros2/blob/master/webots_ros2_epuck/EPUCK_ROS2.md).

## Development
If you prefer to compile `epuck_ros2` from the source you can clone the repository to your workspace:
```
git clone --recurse-submodules https://github.com/cyberbotics/epuck_ros2.git src/epuck_ros2
```

Install dependencies with [`rosdep`](http://wiki.ros.org/rosdep):
```
rosdep install --from-paths src --ignore-src -r -y
```

Then simply build it with [`colcon`](https://colcon.readthedocs.io/en/released/user/installation.html):
```
colcon build
```
Or, if you wish to build it on your PC (that doesn't have MMAL library):
```
colcon build --cmake-args -DAVOID_EPUCK_CAMERA_BUILD=true
```

## Acknowledgement

<a href="http://rosin-project.eu">
  <img src="http://rosin-project.eu/wp-content/uploads/rosin_ack_logo_wide.png" 
       alt="rosin_logo" height="60" >
</a></br>

Supported by ROSIN - ROS-Industrial Quality-Assured Robot Software Components.  
More information: <a href="http://rosin-project.eu">rosin-project.eu</a>

<img src="http://rosin-project.eu/wp-content/uploads/rosin_eu_flag.jpg" 
     alt="eu_flag" height="45" align="left" >  

This project has received funding from the European Union’s Horizon 2020  
research and innovation programme under grant agreement no. 732287. 
