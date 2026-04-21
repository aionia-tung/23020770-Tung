#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import LaserScan


class ScanVisualizer(Node):
    def __init__(self):
        super().__init__('scan_visualizer')

        scan_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
        )
        pub_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self.pub = self.create_publisher(LaserScan, '/scan_visual', pub_qos)
        self.sub = self.create_subscription(LaserScan, '/scan', self.handle_scan, scan_qos)

    def handle_scan(self, msg: LaserScan):
        out = LaserScan()
        out.header = msg.header
        out.header.frame_id = 'link_lidar'
        out.angle_min = msg.angle_min
        out.angle_max = msg.angle_max
        out.angle_increment = msg.angle_increment
        out.time_increment = msg.time_increment
        out.scan_time = msg.scan_time
        out.range_min = msg.range_min
        out.range_max = msg.range_max
        out.ranges = list(msg.ranges)
        out.intensities = list(msg.intensities)
        self.pub.publish(out)


def main():
    rclpy.init()
    node = ScanVisualizer()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
