#!/usr/bin/env python3

import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from sensor_msgs.msg import Imu


class ImuVisualizer(Node):
    def __init__(self):
        super().__init__('imu_visualizer')
        self.publisher = self.create_publisher(PoseStamped, '/imu_pose', 10)
        self.create_subscription(Imu, '/imu', self.imu_callback, 10)

    def imu_callback(self, msg):
        pose = PoseStamped()
        pose.header = msg.header
        pose.header.frame_id = 'base_link'
        pose.pose.orientation = msg.orientation
        pose.pose.position.x = 0.0
        pose.pose.position.y = 0.0
        pose.pose.position.z = 0.12
        self.publisher.publish(pose)


def main():
    rclpy.init()
    node = ImuVisualizer()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
