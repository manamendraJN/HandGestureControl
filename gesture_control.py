import cv2
import mediapipe as mp
import pyautogui
import time
import pygetwindow as gw
import win32gui
import win32con

pyautogui.FAILSAFE = False

def count_fingers(hand_landmarks, frame_width, frame_height):
    finger_tips = [4, 8, 12, 16, 20]
    finger_mcp = [2, 5, 9, 13, 17]
    raised_fingers = 0

    for tip, mcp in zip(finger_tips, finger_mcp):
        tip_y = hand_landmarks.landmark[tip].y * frame_height
        mcp_y = hand_landmarks.landmark[mcp].y * frame_height
        tip_x = hand_landmarks.landmark[tip].x * frame_width
        mcp_x = hand_landmarks.landmark[mcp].x * frame_width

        if tip != 4:
            if tip_y < mcp_y:
                raised_fingers += 1
        else:
            if tip_x > mcp_x + 50:
                raised_fingers += 1

    return raised_fingers

def make_window_always_on_top(title):
    try:
        hwnd = win32gui.FindWindow(None, title)
        win32gui.SetWindowPos(
            hwnd, win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
    except Exception as e:
        print("Could not set always on top:", e)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    screen_width, screen_height = pyautogui.size()

    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        return
    frame_height, frame_width, _ = frame.shape

    last_click_time = 0
    click_cooldown = 0.5
    smooth_factor = 0.3
    prev_screen_x, prev_screen_y = None, None

    x_norm_min, x_norm_max = 1.0, 0.0
    y_norm_min, y_norm_max = 1.0, 0.0
    calibration_samples = 0
    calibration_duration = 5
    calibration_start = time.time()
    calibrated = False
    padding = 0.1
    x_center_norm, y_center_norm = 0.5, 0.5

    window_title = "Hand Tracking - Mouse Control"
    window_shown_once = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                if handedness.classification[0].label != "Right":
                    continue

                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                index_tip = hand_landmarks.landmark[8]
                x_index = int(index_tip.x * frame_width)
                y_index = int(index_tip.y * frame_height)
                finger_count = count_fingers(hand_landmarks, frame_width, frame_height)

                x_norm = index_tip.x
                y_norm = index_tip.y

                calibrating = (time.time() - calibration_start < calibration_duration)

                if calibrating and finger_count == 1:
                    x_norm_min = min(x_norm_min, x_norm)
                    x_norm_max = max(x_norm_max, x_norm)
                    y_norm_min = min(y_norm_min, y_norm)
                    y_norm_max = max(y_norm_max, y_norm)
                    calibration_samples += 1

                    cv2.putText(frame, "Calibrating... Move finger to all corners", (30, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    continue

                if not calibrated:
                    x_range = x_norm_max - x_norm_min
                    y_range = y_norm_max - y_norm_min
                    x_pad = padding * x_range
                    y_pad = padding * y_range

                    x_norm_min = max(0.0, x_norm_min - x_pad)
                    x_norm_max = min(1.0, x_norm_max + x_pad)
                    y_norm_min = max(0.0, y_norm_min - y_pad)
                    y_norm_max = min(1.0, y_norm_max + y_pad)

                    x_center_norm = (x_norm_min + x_norm_max) / 2
                    y_center_norm = (y_norm_min + y_norm_max) / 2

                    calibrated = True

                x_range = max(0.3, x_norm_max - x_norm_min)
                y_range = max(0.3, y_norm_max - y_norm_min)

                x_scaled = (x_norm - x_center_norm) / (x_range + 1e-6)
                y_scaled = (y_norm - y_center_norm) / (y_range + 1e-6)

                screen_x = int(x_scaled * screen_width / 2 + screen_width / 2)
                screen_y = int(y_scaled * screen_height / 2 + screen_height / 2)

                if prev_screen_x is None:
                    prev_screen_x, prev_screen_y = screen_x, screen_y
                else:
                    screen_x = int(prev_screen_x * smooth_factor + screen_x * (1 - smooth_factor))
                    screen_y = int(prev_screen_y * smooth_factor + screen_y * (1 - smooth_factor))
                    prev_screen_x, prev_screen_y = screen_x, screen_y

                current_time = time.time()

                if finger_count == 0:
                    continue
                elif finger_count == 1:
                    pyautogui.moveTo(screen_x, screen_y)
                elif finger_count == 2:
                    if current_time - last_click_time > click_cooldown:
                        pyautogui.click()
                        last_click_time = current_time
                        cv2.circle(frame, (x_index, y_index), 10, (0, 255, 0), -1)
                elif finger_count == 3:
                    if current_time - last_click_time > click_cooldown:
                        pyautogui.doubleClick()
                        last_click_time = current_time
                        cv2.circle(frame, (x_index, y_index), 10, (0, 255, 0), -1)

        # 📌 Show small preview camera window in top-left corner
        cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_title, 300, 220)
        cv2.moveWindow(window_title, 0, 0)
        cv2.imshow(window_title, frame)

        # 📌 Only apply always-on-top once
        if not window_shown_once:
            make_window_always_on_top(window_title)
            window_shown_once = True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    main()
