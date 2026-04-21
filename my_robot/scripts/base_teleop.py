#!/usr/bin/env python3

import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


HELP = """
Dieu khien de omni 3 banh
-------------------------
W / X : Tien / Lui
A / D : Dich trai / phai
Q / E : Quay trai / phai
S     : Dung
Ctrl-C: Thoat
"""


class BaseTeleop(Node):
    def __init__(self):
        super().__init__('base_teleop')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.linear_step = 0.08
        self.angular_step = 0.25
        self.current_cmd = Twist()
        self.last_logged = (None, None, None)

        self.create_timer(0.05, self.publish_current_cmd)

    def set_cmd(self, vx=0.0, vy=0.0, wz=0.0):
        self.current_cmd = Twist()
        self.current_cmd.linear.x = vx
        self.current_cmd.linear.y = vy
        self.current_cmd.angular.z = wz

        current = (vx, vy, wz)
        if current != self.last_logged:
            self.get_logger().info(
                f'cmd_vel -> vx={vx:.2f} m/s, vy={vy:.2f} m/s, wz={wz:.2f} rad/s'
            )
            self.last_logged = current

    def publish_current_cmd(self):
        self.publisher.publish(self.current_cmd)

    def handle_key(self, key):
        if key == 'w':
            self.set_cmd(vx=self.linear_step)
        elif key == 'x':
            self.set_cmd(vx=-self.linear_step)
        elif key == 'a':
            self.set_cmd(vy=self.linear_step)
        elif key == 'd':
            self.set_cmd(vy=-self.linear_step)
        elif key == 'q':
            self.set_cmd(wz=-self.angular_step)
        elif key == 'e':
            self.set_cmd(wz=self.angular_step)
        elif key == 's':
            self.set_cmd()


def main():
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init()
    node = BaseTeleop()
    print(HELP)
    node.set_cmd()

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
        node.publish_current_cmd()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
