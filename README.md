# 23020770-Tung
ROS GIUA KI
# my_robot

Package ROS 2 Humble cho robot omni 3 banh co tay may tinh tien 2 bac tu do, mo phong tren Gazebo va hien thi tren RViz.

## Cau truc package

- `urdf/`: mo ta robot, lien ket, sensor va plugin Gazebo.
- `meshes/`: file STL cua than xe, banh xe, lidar va tay may.
- `launch/gazebo_rviz.launch.py`: launch chinh de bat Gazebo, RViz, bridge va node dieu khien omni.
- `worlds/lidar_test.sdf`: world mac dinh co tuong va hop de kiem tra lidar trong Gazebo/RViz.
- `scripts/base_teleop.py`: node nhan phim va publish `geometry_msgs/msg/Twist` len `/cmd_vel`.
- `scripts/arm_teleop.py`: node nhan phim va publish len `/arm_dung_cmd`, `/arm_ngang_cmd`.
- `scripts/omni_controller.py`: node dong hoc thuan cho de omni 3 banh, doi `Twist` thanh toc do tung banh.
- `scripts/imu_visualizer.py`: node doi topic `/imu` thanh `/imu_pose` de RViz hien thi huong IMU bang Pose.
- `config/sensors.rviz`: cau hinh RViz da them RobotModel, TF, LaserScan va Pose cho IMU.
- `report/Bao_cao_giua_ky.pdf`: bao cao giua ky.

## Moi truong

- Ubuntu 22.04
- ROS 2 Humble
- `ros_gz_sim` / `ros_gz_bridge`

## Phu thuoc can cai

```bash
sudo apt update
sudo apt install \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-rviz2 \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-xacro
```

Khong can thu vien Python ben ngoai `rclpy`, vi cac node teleop da nam trong package.

## Cach build

```bash
cd ~/robot_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select my_robot
source install/setup.bash
```

## Cach chay

Terminal 1:

```bash
cd ~/robot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch my_robot gazebo_rviz.launch.py
```

Terminal 2, dieu khien de bang ban phim va gui `Twist`:

```bash
cd ~/robot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run my_robot base_teleop.py
```

Phim dieu khien de:

- `w`: tien
- `x`: lui
- `a`: dich trai
- `d`: dich phai
- `q`: quay trai
- `e`: quay phai
- `s`: dung

Luu y de omni:

- Teleop de publish lien tuc `/cmd_vel`. Bam 1 lan de robot giu huong chay hien tai, bam `s` de dung.

Terminal 3, dieu khien tay may:

```bash
cd ~/robot_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run my_robot arm_teleop.py
```

Phim dieu khien tay may:

- `w/s`: nang ha khop dung
- `a/d`: tien lui khop ngang
- `space`: giu nguyen vi tri

Luu y:

- World mac dinh da co vat can phia truoc robot de `/scan` hien diem tren RViz. Neu chay world rong thi lidar van publish nhung co the khong thay diem nao.
- Tay may hien khoi tao o vi tri giua hanh trinh de de quan sat chuyen dong hon.

## Topic chinh

- `/cmd_vel`: lenh `geometry_msgs/msg/Twist` cho de robot.
- `/wheel_1_cmd`, `/wheel_2_cmd`, `/wheel_3_cmd`: lenh toc do banh sau khi doi dong hoc.
- `/arm_dung_cmd`, `/arm_ngang_cmd`: lenh vi tri 2 khop tay may.
- `/scan`: du lieu lidar.
- `/imu`: du lieu IMU.
- `/imu_pose`: huong IMU da doi sang `geometry_msgs/msg/PoseStamped` de RViz hien thi.
- `/joint_states`: trang thai khop.
- `/odom`: odometry tu Gazebo.
