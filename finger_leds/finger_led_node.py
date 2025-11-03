#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import mediapipe as mp
import serial
import time

class FingerLedNode(Node):
    def __init__(self):
        super().__init__('finger_led_node')
        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('camera_index', 0)

        serial_port = self.get_parameter('serial_port').get_parameter_value().string_value
        baudrate = self.get_parameter('baudrate').get_parameter_value().integer_value
        cam_idx = self.get_parameter('camera_index').get_parameter_value().integer_value

        self.get_logger().info(f"Serial port: {serial_port}, baud: {baudrate}, camera: {cam_idx}")

        # Try to open serial
        try:
            self.ser = serial.Serial(serial_port, baudrate, timeout=1)
            time.sleep(2)  # wait for Arduino reset if any
            self.get_logger().info("Opened serial to Arduino.")
        except Exception as e:
            self.get_logger().error(f"Cannot open serial {serial_port}: {e}")
            self.ser = None

        # Mediapipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Video capture
        self.cap = cv2.VideoCapture(cam_idx)
        if not self.cap.isOpened():
            self.get_logger().error("Cannot open camera index {}".format(cam_idx))
            raise RuntimeError("Camera not available")

        self.prev_count = -1

        # Start main loop via timer
        self.timer = self.create_timer(0.05, self.timer_cb)  # 20 Hz

    def timer_cb(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn("Frame capture failed")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        count = 0
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            landmarks = hand.landmark
            h, w, _ = frame.shape

            # Convert landmarks to pixel coords for easier logic
            lm = [(int(l.x * w), int(l.y * h)) for l in landmarks]

            # Finger tip ids in MediaPipe: 4 thumb, 8 index, 12 middle, 16 ring, 20 pinky
            tip_ids = [4, 8, 12, 16, 20]

            # For fingers except thumb: compare tip y with pip y (lower y value means finger up because origin top-left)
            fingers = []

            # Thumb: compare tip x with ip x depending on handness
            wrist_x = lm[0][0]
            # Determine handness via x of index vs thumb: rough heuristic
            # We'll use tip vs mcp for thumb direction
            # Simpler: check if tip (4) is to the right of ip(3) for right hand
            # For robust approach we trust MediaPipe handedness would be better; this avoids complexity.

            # For non-thumb fingers:
            for i in range(1,5):
                tip_y = lm[tip_ids[i]][1]
                pip_y = lm[tip_ids[i] - 2][1]  # pip is tip_id-2 for these fingers
                fingers.append(1 if tip_y < pip_y else 0)

            # Thumb:
            # If thumb tip x is to the right of IP x and wrist x, consider it open for one hand orientation.
            # We'll check both directions to be robust:
            thumb_tip_x = lm[4][0]
            thumb_ip_x = lm[3][0]
            # If thumb_tip_x is farther from wrist than ip, count as open
            thumb_open = 1 if abs(thumb_tip_x - wrist_x) > abs(thumb_ip_x - wrist_x) and abs(thumb_tip_x - wrist_x) > 20 else 0
            # Insert thumb at start
            fingers.insert(0, thumb_open)

            count = sum(fingers)

            # draw landmarks for feedback
            self.mp_draw.draw_landmarks(frame, hand, self.mp_hands.HAND_CONNECTIONS)

        # Show the count on frame
        cv2.putText(frame, f"Fingers: {count}", (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 2)
        cv2.imshow('Finger Count', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC closes
            self.get_logger().info("ESC pressed, shutting down")
            rclpy.shutdown()
            return

        # Send to Arduino only on change
        if self.ser and count != self.prev_count:
            try:
                s = f"{count}\n"
                self.ser.write(s.encode('utf-8'))
                self.prev_count = count
                self.get_logger().info(f"Sent to Arduino: {count}")
            except Exception as e:
                self.get_logger().error(f"Serial write failed: {e}")

    def destroy_node(self):
        # clean up
        if self.cap and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        if self.ser:
            self.ser.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = FingerLedNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

