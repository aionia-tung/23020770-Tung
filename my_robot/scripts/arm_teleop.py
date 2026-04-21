#!/usr/bin/env python3

import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float64


HELP = """
Dieu khien tay may my_robot
---------------------------
W / S : Nang / Ha tay dung
A / D : Thu / Dua tay ngang
Space : Dung tay may
Ctrl-C: Thoat
"""


class ArmTeleop(Node):
    def __init__(self):
        super().__init__('arm_teleop')

        self.pub_dung = self.create_publisher(Float64, '/arm_dung_cmd', 10)
        self.pub_ngang = self.create_publisher(Float64, '/arm_ngang_cmd', 10)
        self.pub_cmd_vel = self.create_publisher(Twist, '/arm_cmd_vel', 10)

        self.pos_dung = -0.08
        self.pos_ngang = 0.0
        self.limit_dung = (-0.125, 0.02)
        self.limit_ngang = (-0.035, 0.045)

        self.linear_speed_dung_up = 0.008
        self.linear_speed_dung_down = 0.004
        self.linear_speed_ngang = 0.008
        self.current_cmd = Twist()
        self.last_update_time = self.get_clock().now()

        self.create_timer(0.05, self.update)

    def clamp(self, value, limits):
        return max(limits[0], min(limits[1], value))

    def publish_positions(self):
        self.pub_dung.publish(Float64(data=self.pos_dung))
        self.pub_ngang.publish(Float64(data=self.pos_ngang))

    def publish_cmd(self):
        self.pub_cmd_vel.publish(self.current_cmd)

    def set_cmd(self, vz=0.0, vx=0.0):
        self.current_cmd = Twist()
        self.current_cmd.linear.z = vz
        self.current_cmd.linear.x = vx
        self.publish_cmd()
        self.get_logger().info(
            f'arm_cmd_vel -> vx={vx:.3f} m/s, vz={vz:.3f} m/s'
        )

    def handle_key(self, key):
        if key == 'w':
            self.set_cmd(vz=self.linear_speed_dung_up)
        elif key == 's':
            self.set_cmd(vz=-self.linear_speed_dung_down)
        elif key == 'd':
            self.set_cmd(vx=self.linear_speed_ngang)
        elif key == 'a':
            self.set_cmd(vx=-self.linear_speed_ngang)
        elif key == ' ':
            self.set_cmd()

    def update(self):
        now = self.get_clock().now()
        dt = (now - self.last_update_time).nanoseconds / 1e9
        self.last_update_time = now

        next_dung = self.pos_dung + (self.current_cmd.linear.z * dt)
        next_ngang = self.pos_ngang + (self.current_cmd.linear.x * dt)

        clamped_dung = self.clamp(next_dung, self.limit_dung)
        clamped_ngang = self.clamp(next_ngang, self.limit_ngang)

        hit_limit = (
            clamped_dung != next_dung or
            clamped_ngang != next_ngang
        )

        self.pos_dung = clamped_dung
        self.pos_ngang = clamped_ngang
        self.publish_positions()

        if hit_limit and (
            self.current_cmd.linear.z != 0.0 or
            self.current_cmd.linear.x != 0.0
        ):
            self.set_cmd()


def main():
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init()
    node = ArmTeleop()

    print(HELP)
    node.publish_positions()
    node.get_logger().info(
        f'arm_start -> joint_arm_dung={node.pos_dung:.3f} m, '
        f'joint_arm_ngang={node.pos_ngang:.3f} m'
    )

    try:
        while True:
            tty.setraw(sys.stdin.fileno())
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if ready:
                key = sys.stdin.read(1)
                if key == '\x03':
                    break
                node.handle_key(key.lower())
            rclpy.spin_once(node, timeout_sec=0.0)
    finally:
        node.set_cmd()
        node.publish_positions()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
