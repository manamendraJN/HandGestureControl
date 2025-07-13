🖐️ HandGestureControl: Control Your Mouse with Gestures! 🚀

Welcome to HandGestureControl, a cutting-edge Python project that lets you control your mouse using intuitive right-hand gestures captured via webcam! Built with OpenCV, MediaPipe, and PyAutoGUI, this project transforms your hand movements into seamless mouse actions, complete with a sleek, always-on-top preview window. Perfect for tech enthusiasts, developers, or anyone looking to add a touch of magic to their desktop navigation! ✨

🎯 Features
Intuitive Gestures (Right Hand Only):
     Fist (0 fingers): No action, keeping things idle.
     1 finger (index): Move the mouse cursor smoothly across your entire 1920x1080 screen with adjustable speed.
     2 fingers (index + middle): Trigger a single left-click with a vibrant green circle as visual feedback.
     3 fingers (index + middle + ring): Perform a double left-click with the same cool visual cue.


🛠️ Automatic Calibration: Maps your hand movements to the full screen in just 5 seconds for pixel-perfect control.
📸 Mini Preview Window: A compact 300x220 webcam feed in the top-left corner, always on top for easy monitoring.
⚙️ Smooth & Customizable: Fine-tune mouse speed and smoothness for a tailored experience.

🛠️ Requirements
To get started, you’ll need:

🐍 Python 3.7+
📷 A webcam
💻 Windows (for the always-on-top preview window)
📦 Python Libraries:
opencv-python
mediapipe
pyautogui
pygetwindow
pywin32

🚀 Installation
Get up and running in just a few steps!

1.Clone the Repository:

Open GitHub Desktop and clone the project to D:\Github-Projects\HandGestureControl:git clone https://github.com/<your-username>/HandGestureControl.git
cd HandGestureControl

2.Set Up Virtual Environment:
python -m venv venv

3.Activate it on Windows:venv\Scripts\activate

4.Install Dependencies:
pip install opencv-python mediapipe pyautogui pygetwindow pywin32
pip freeze > requirements.txt

🎮 Usage

Launch the Script:

1.Open the project in VS Code

2.Run the magic:python gesture_control.py

🛠️ Customization & Troubleshooting

1.Adjust Mouse Speed:

Tweak sensitivity (default: 0.5) in gesture_control.py for faster (0.7) or slower (0.3) cursor movement.
Increase smooth_factor (default: 0.7) to 0.8 for smoother motion.

2.Calibration Tips:

Move your hand to the extreme edges of the webcam frame during calibration to cover the full screen.
Check console output for calibration values (x_min, x_max, y_min, y_max). A narrow range (e.g., <0.5) means you need to move further.
Extend calibration_duration to 7 seconds if needed.

3.Common Issues:

Mouse Not Reaching Corners? Ensure calibration captures a wide range. Try a different webcam index (cv2.VideoCapture(1)).
Jittery Movement? Increase smooth_factor to 0.8 or lower sensitivity to 0.3.
Hand/Finger Detection Issues? Improve lighting, adjust min_detection_confidence (default: 0.7), or tweak the thumb threshold (default: 50) in count_fingers.
