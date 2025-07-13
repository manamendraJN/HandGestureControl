import cv2
import mediapipe as mp
import pyautogui
import math
import time

# Set PyAutoGUI to fail-safe mode
pyautogui.FAILSAFE = True

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    # Get screen size for mapping
    screen_width, screen_height = pyautogui.size()

    # Get frame size
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        return
    frame_height, frame_width, _ = frame.shape

    # Click and key press state
    last_click_time = 0
    last_key_time = 0
    click_cooldown = 0.5  # Seconds between clicks
    key_cooldown = 0.2    # Seconds between key presses

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame for hand detection
        results = hands.process(frame_rgb)

        # Draw hand landmarks and control mouse/keyboard
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get landmarks for index finger tip (8), thumb tip (4), and wrist (0)
                index_tip = hand_landmarks.landmark[8]
                thumb_tip = hand_landmarks.landmark[4]
                wrist = hand_landmarks.landmark[0]

                # Convert to pixel coordinates
                x_index = int(index_tip.x * frame_width)
                y_index = int(index_tip.y * frame_height)
                x_thumb = int(thumb_tip.x * frame_width)
                y_thumb = int(thumb_tip.y * frame_height)
                x_wrist = int(wrist.x * frame_width)
                y_wrist = int(wrist.y * frame_height)

                # Map index finger to screen coordinates for mouse movement
                screen_x = int(index_tip.x * screen_width)
                screen_y = int(index_tip.y * screen_height)
                pyautogui.moveTo(screen_x, screen_y)

                # Calculate distance for click
                distance = math.hypot(x_index - x_thumb, y_index - y_thumb)
                current_time = time.time()

                # Perform click if fingers are close
                if distance < 30 and (current_time - last_click_time) > click_cooldown:
                    pyautogui.click()
                    last_click_time = current_time

                # Calculate hand tilt for arrow keys
                delta_x = x_index - x_wrist
                delta_y = y_index - y_wrist
                angle = math.degrees(math.atan2(delta_y, delta_x))

                # Press arrow keys based on hand tilt
                if (current_time - last_key_time) > key_cooldown:
                    if 45 <= angle < 135:
                        pyautogui.press('up')
                        last_key_time = current_time
                    elif -135 <= angle < -45:
                        pyautogui.press('down')
                        last_key_time = current_time
                    elif -45 <= angle < 45:
                        pyautogui.press('right')
                        last_key_time = current_time
                    elif 135 <= angle or angle < -135:
                        pyautogui.press('left')
                        last_key_time = current_time

        # Display the frame
        cv2.imshow('Hand Tracking', frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    main()