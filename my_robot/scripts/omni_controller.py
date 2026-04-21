#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float64


class OmniController(Node):
    def __init__(self):
        super().__init__('omni_controller')

        self.declare_parameter('wheel_radius', 0.038)
        self.declare_parameter('wheel_base', 0.1315)
        self.declare_parameter('command_timeout', 1.0)
        self.declare_parameter('wheel_angles_deg', [90.0, 210.0, 330.0])
        self.declare_parameter('wheel_signs', [1.0, 1.0, 1.0])
        self.declare_parameter('max_wheel_speed', 8.0)
        self.declare_parameter('max_wheel_accel', 12.0)

        self.wheel_radius = float(self.get_parameter('wheel_radius').value)
        self.wheel_base = float(self.get_parameter('wheel_base').value)
        self.command_timeout = float(self.get_parameter('command_timeout').value)
        self.max_wheel_speed = float(self.get_parameter('max_wheel_speed').value)
        self.max_wheel_accel = float(self.get_parameter('max_wheel_accel').value)
        self.wheel_angles = [
            math.radians(float(angle))
            for angle in self.get_parameter('wheel_angles_deg').value
        ]
        self.wheel_signs = [
            float(sign) for sign in self.get_parameter('wheel_signs').value
        ]

        self.wheel_publishers = [
            self.create_publisher(Float64, '/wheel_1_cmd', 10),
            self.create_publisher(Float64, '/wheel_2_cmd', 10),
            self.create_publisher(Float64, '/wheel_3_cmd', 10),
        ]
        self.last_command_time = self.get_clock().now()
        self.last_update_time = self.get_clock().now()
        self.current_cmd = Twist()
        self.current_wheel_speeds = [0.0, 0.0, 0.0]

        self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10)
        self.create_timer(0.02, self.update)

        self.get_logger().info(
            'Omni controller ready: /cmd_vel -> /wheel_[1..3]_cmd'
        )

    def cmd_callback(self, msg):
        self.current_cmd = msg
        self.last_command_time = self.get_clock().now()

    def compute_wheel_speeds(self, vx, vy, wz):
        speeds = []
        for angle, sign in zip(self.wheel_angles, self.wheel_signs):
            speed = (
                (-math.sin(angle) * vx)
                + (math.cos(angle) * vy)
                + (self.wheel_base * wz)
            ) / self.wheel_radius
            clamped = max(-self.max_wheel_speed, min(self.max_wheel_speed, sign * speed))
            speeds.append(clamped)
        return speeds

    def update(self):
        now = self.get_clock().now()
        dt = (now - self.last_command_time).nanoseconds / 1e9
        step_dt = max((now - self.last_update_time).nanoseconds / 1e9, 1e-3)
        self.last_update_time = now

        if dt > self.command_timeout:
            vx = 0.0
            vy = 0.0
            wz = 0.0
        else:
            vx = self.current_cmd.linear.x
            vy = self.current_cmd.linear.y
            wz = self.current_cmd.angular.z

        target_speeds = self.compute_wheel_speeds(vx, vy, wz)
        max_delta = self.max_wheel_accel * step_dt

        next_speeds = []
        for current, target in zip(self.current_wheel_speeds, target_speeds):
            delta = target - current
            if delta > max_delta:
                current += max_delta
            elif delta < -max_delta:
                current -= max_delta
            else:
                current = target
            next_speeds.append(current)

        self.current_wheel_speeds = next_speeds

        for publisher, speed in zip(
            self.wheel_publishers, self.current_wheel_speeds
        ):
            publisher.publish(Float64(data=speed))


def main():
    rclpy.init()
    node = OmniController()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
