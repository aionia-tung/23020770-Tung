import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo, SetEnvironmentVariable, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_name = 'my_robot'
    pkg_share = get_package_share_directory(package_name)
    ros_gz_share = get_package_share_directory('ros_gz_sim')

    urdf_file = os.path.join(pkg_share, 'urdf', 'my_robot.urdf')
    rviz_config = os.path.join(pkg_share, 'config', 'sensors.rviz')
    controller_config = os.path.join(pkg_share, 'config', 'omni_controller.yaml')
    meshes_dir = os.path.join(pkg_share, 'meshes')
    default_world = os.path.join(pkg_share, 'worlds', 'corridor_test.sdf')

    with open(urdf_file, 'r', encoding='utf-8') as infp:
        robot_description = infp.read()

    # Replace model:// URIs with file:// URIs for mesh loading in Gazebo
    robot_description = robot_description.replace(
        'package://my_robot/meshes/',
        f'file://{meshes_dir}/'
    )

    use_rviz = LaunchConfiguration('use_rviz')
    world = LaunchConfiguration('world')

    # Set Gazebo resource paths to find mesh files and models
    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=f'{os.path.dirname(pkg_share)}:' + os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    )

    return LaunchDescription([
        gz_resource_path,
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Open RViz together with Gazebo.',
        ),
        DeclareLaunchArgument(
            'world',
            default_value=default_world,
            description='Gazebo world passed to ros_gz_sim.',
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            remappings=[
                ('/robot_description', '/my_robot/robot_description'),
            ],
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': True,
            }],
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(ros_gz_share, 'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={'gz_args': ['-r ', world]}.items(),
        ),
        TimerAction(
            period=2.0,
            actions=[
                Node(
                    package='ros_gz_sim',
                    executable='create',
                    remappings=[
                        ('/robot_description', '/my_robot/robot_description'),
                    ],
                    arguments=[
                        '-topic', '/my_robot/robot_description',
                        '-name', 'my_robot',
                        '-x', '0.4',
                        '-y', '0.0',
                        '-z', '0.06',
                    ],
                    output='screen',
                ),
            ],
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
                '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
                '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
                '/wheel_1_cmd@std_msgs/msg/Float64]gz.msgs.Double',
                '/wheel_2_cmd@std_msgs/msg/Float64]gz.msgs.Double',
                '/wheel_3_cmd@std_msgs/msg/Float64]gz.msgs.Double',
                '/arm_dung_cmd@std_msgs/msg/Float64]gz.msgs.Double',
                '/arm_ngang_cmd@std_msgs/msg/Float64]gz.msgs.Double',
            ],
            output='screen',
        ),
        Node(
            package=package_name,
            executable='omni_controller.py',
            name='omni_controller',
            output='screen',
            parameters=[controller_config],
        ),
        Node(
            package=package_name,
            executable='imu_visualizer.py',
            name='imu_visualizer',
            output='screen',
        ),
        Node(
            package=package_name,
            executable='scan_visualizer.py',
            name='scan_visualizer',
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            remappings=[
                ('/robot_description', '/my_robot/robot_description'),
            ],
            parameters=[{
                'use_sim_time': True,
            }],
            condition=IfCondition(use_rviz),
            output='screen',
        ),
        LogInfo(
            msg=(
                'Launch xong. Mo them terminal khac va chay: '
                '`ros2 run my_robot base_teleop.py` de gui Twist, '
                '`ros2 run my_robot arm_teleop.py` de dieu khien tay may.'
            )
        ),
    ])
