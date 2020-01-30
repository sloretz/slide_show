# Copyright 2019 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import cv2
import cv_bridge
from rcl_interfaces.msg import ParameterDescriptor
from rcl_interfaces.msg import ParameterType
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy
from rclpy.qos import QoSHistoryPolicy
from rclpy.qos import QoSProfile
from rclpy.qos import QoSReliabilityPolicy
from sensor_msgs.msg import Image


class SlideShowNode(Node):

    def __init__(self):
        super().__init__('slide_show')

        self._bridge = cv_bridge.CvBridge()

        dir_desc = ParameterDescriptor()
        # TODO(sloretz) Allow changing directory
        dir_desc.read_only = True
        dir_desc.description = 'Directory from which images will be published'
        dir_desc.type = ParameterType.PARAMETER_STRING
        dir_desc.name = 'directory'
        self.declare_parameter(
            dir_desc.name,
            os.path.abspath(os.curdir),
            dir_desc)
        self._dirpath = self.get_parameter(dir_desc.name).value

        self._current_file = None

        image_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
            reliability=QoSReliabilityPolicy.RELIABLE,
            depth=1)

        self._image_pub = self.create_publisher(Image, 'images', image_qos)

        period_desc = ParameterDescriptor()
        # TODO(sloretz) allow changing period
        period_desc.read_only = True
        period_desc.description = 'Time between publishing images (seconds)'
        period_desc.type = ParameterType.PARAMETER_DOUBLE
        period_desc.name = 'period'
        self.declare_parameter(
            period_desc.name,
            5.0,
            period_desc)
        period = self.get_parameter(period_desc.name).value

        self._next_slide_timer = self.create_timer(
            period, self.on_timer)

        self.publish_next()

    def _refresh(self):
        # os.listdir is arbitrary order, so sort alphabetically
        self._dir_content = os.listdir(self._dirpath)
        self._dir_content.sort()

    def _next_image(self):
        if not self._dir_content:
            # No files to display :(
            self._current_file = None
            return
        if self._current_file is None:
            # Start with the first file in the list
            index = 0
        else:
            try:
                index = self._dir_content.index(self._current_file)
                index += 1
            except ValueError:
                # Current file was deleted :(
                index = 0
                for filename in self._dir_content:
                    if self._current_file < filename:
                        # This is where the current file would have been
                        break
                    index += 1
        if index >= len(self._dir_content):
            # Loop back to beginning
            index = 0

        self._current_file = self._dir_content[index]
        path = os.path.join(self._dirpath, self._current_file)
        cv_image = None
        if os.path.isfile(path):
            cv_image = cv2.imread(path, cv2.IMREAD_COLOR)
        if cv_image is None:
            self.get_logger().warn('Failed to read: ' + path)
            # ignore this one and try the next image
            self._dir_content.remove(self._current_file)
            return self._next_image()

        self.get_logger().info('Next image: ' + self._current_file)
        return self._bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")

    def publish_next(self):
        self._refresh()
        image_msg = self._next_image()
        if image_msg:
            image_msg.header.stamp = self.get_clock().now().to_msg()
            self._image_pub.publish(image_msg)
        else:
            self.get_logger().error('No images found in ' + self._dirpath)

    def on_timer(self):
        self.publish_next()


def main():
    rclpy.init()
    rclpy.spin(SlideShowNode())
    rclpy.shutdown()
