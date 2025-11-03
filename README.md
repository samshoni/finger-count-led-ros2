# 🤖 Finger Count LED Controller (ROS 2 + OpenCV + Arduino Mega)

This project detects how many fingers you show to the camera using **OpenCV** and controls that many LEDs on an **Arduino Mega** through **ROS 2 Humble**.

---

## 🧩 Features
- Detects 0–5 fingers using OpenCV hand tracking.
- Turns ON the same number of LEDs (connected to pins 22–26 on Arduino Mega).
- Fully integrated with ROS 2 (custom node using `rclpy`).
- Real-time camera feed and LED feedback.

---

## 🛠️ Hardware Used
| Component | Description |
|------------|-------------|
| Arduino Mega | Controls 5 LEDs |
| 5 LEDs + 250 Ω resistors | Visual output |
| USB Camera | For finger detection |
| Ubuntu 22.04 + ROS 2 Humble | Main system |

---

## ⚙️ Connections
| Arduino Pin | LED | Resistor | GND |
|--------------|-----|-----------|------|
| 22 | LED 1 | 250 Ω | GND |
| 23 | LED 2 | 250 Ω | GND |
| 24 | LED 3 | 250 Ω | GND |
| 25 | LED 4 | 250 Ω | GND |
| 26 | LED 5 | 250 Ω | GND |

---

## 🧠 Software Setup

### 1️⃣ Clone and build
```bash
cd ~/ros2_finger_ws/src
git clone https://github.com/samshoni/finger-count-led-ros2.git
cd ~/ros2_finger_ws
colcon build --symlink-install

2️⃣ Run the node

source install/setup.bash
ros2 run finger_leds finger_led_node --ros-args -p serial_port:=/dev/ttyUSB0


	
##🧾 License

This project is open-sourced under the MIT License

.
##👤 Author

Sam Shoni Zacharia
🔗 LinkedIn : samshoni

📧 samshoni10@gmail.com

