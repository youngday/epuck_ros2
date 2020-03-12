
import time
import rclpy
import launch
import launch_ros.actions
import unittest
import launch_testing.actions
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Range


SENSORS_SIZE = 47
DISTANCE_FROM_CENTER = 0.035


def arr2int16(bytearr):
    """
    Little-endian formulation
    """
    val = (bytearr[0] & 0x00FF) | ((bytearr[1] << 8) & 0xFF00)
    if val > 2**15:
        val -= 2**16
    return val


def int162arr(val):
    """
    Little-endian formulation
    """
    arr = [
        val & 0xFF,
        (val >> 8) & 0xFF
    ]
    return arr


def get_params(buffer):
    params = {}
    params['left_speed'] = arr2int16(buffer[0:2])
    params['right_speed'] = arr2int16(buffer[2:4])
    return params


def read_params_from_i2c(idx=4):
    for _ in range(3):
        with open(f'/tmp/dev/i2c-{idx}_write', 'rb') as f:
            data = list(f.read())
            if len(data) > 0:
                return get_params(data)
        time.sleep(0.01)
    return {}


def write_params_to_i2c(params, idx=4):
    buffer = [0] * SENSORS_SIZE

    # Fill the buffer
    for key in params.keys():
        # Distance sensors
        if key[:2] == 'ps':
            sid = int(key[2])
            buffer[sid:sid+2] = int162arr(params[key])

    # Write the buffer
    for _ in range(3):
        with open(f'/tmp/dev/i2c-{idx}_read', 'wb') as f:
            n_bytes = f.write(bytearray(buffer))
            if n_bytes == SENSORS_SIZE:
                return
        time.sleep(0.01)


def publish_twist(node, linear_x=0.0, linear_y=0.0, angular_z=0.0):
    # Publish a message
    pub = node.create_publisher(
        Twist,
        'cmd_vel',
        1
    )
    for _ in range(3):
        msg = Twist()
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = angular_z
        msg.linear.x = linear_x
        msg.linear.y = linear_y
        msg.linear.z = 0.0
        pub.publish(msg)
        time.sleep(0.1)

    # Wait a bit
    time.sleep(0.1)
    node.destroy_publisher(pub)


def generate_test_description():
    """
    To run the tests you can use either `launch_test` directly as:
    $ launch_test src/epuck_ros2/epuck_ros2_cpp/test/test_controller.py
    or `colcon`:
    $ colcon test --packages-select epuck_ros2_cpp

    The testing procedure is based on `launch_test`:
    https://github.com/ros2/launch/tree/master/launch_testing
    and the following example:
    https://github.com/ros2/launch_ros/blob/master/launch_testing_ros/test/examples/talker_listener_launch_test.py 
    """

    controller = launch_ros.actions.Node(
        package='epuck_ros2_cpp',
        node_executable='controller',
        output='screen'
    )

    return launch.LaunchDescription([
        controller,
        launch_testing.actions.ReadyToTest(),
    ])


class TestController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_controller')

    def tearDown(self):
        self.node.destroy_node()

    def test_forward_velocity(self, launch_service, proc_output):
        publish_twist(self.node, linear_x=0.02)

        # Check what has been written to I2C
        params = read_params_from_i2c()
        self.assertEqual(params['left_speed'], 147, 'Left wheel speed of 0.02 should correspond to 147 over I2C')
        self.assertEqual(params['right_speed'], 147, 'Right wheel speed of 0.02 should correspond to 147 over I2C')

    def test_limits(self, launch_service, proc_output):
        publish_twist(self.node, linear_x=1.0)

        # Check what has been written to I2C
        params = read_params_from_i2c()
        self.assertEqual(params['left_speed'], 1108, 'The speed should be in range of [-1108, 1108]')
        self.assertEqual(params['right_speed'], 1108, 'The speed should be in range of [-1108, 1108]')

    def test_distance_sensors(self, launch_service, proc_output):
        msgs_rx = []

        write_params_to_i2c({'ps0': 120})

        sub = self.node.create_subscription(
            Range,
            '/ps0',
            lambda msg: msgs_rx.append(msg),
            1
        )

        measurement_found = False
        end_time = time.time() + 2
        while time.time() < end_time:
            rclpy.spin_once(self.node, timeout_sec=0.1)
            for msg in msgs_rx:
                if abs(msg.range - 0.05 - DISTANCE_FROM_CENTER) < 1E-3:
                    measurement_found = True
                    break
            if measurement_found:
                break

        self.assertTrue(measurement_found, 'The node hasn\'t published any distance measurement')
            
        