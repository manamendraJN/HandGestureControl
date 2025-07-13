import cv2
import mediapipe as mp
import pyautogui
import math
import time

# Set PyAutoGUI to fail-safe mode
pyautogui.FAILSAFE = True

def count_fingers(hand_landmarks, frame_width, frame_height):
    """Count raised fingers based on landmark positions for right hand."""
    # Landmarks: thumb (4), index (8), middle (12), ring (16), pinky (20)
    # MCP joints: thumb (2), index (5), middle (9), ring (13), pinky (17)
    finger_tips = [4, 8, 12, 16, 20]
    finger_mcp = [2, 5, 9, 13, 17]
    raised_fingers = 0
    for tip, mcp in zip(finger_tips, finger_mcp):
        tip_y = hand_landmarks.landmark[tip].y * frame_height
        mcp_y = hand_landmarks.landmark[mcp].y * frame_height
        tip_x = hand_landmarks.landmark[tip].x * frame_width
        mcp_x = hand_landmarks.landmark[mcp].x * frame_width

        # Non-thumb fingers: raised if tip is above MCP
        if tip != 4:
            if tip_y < mcp_y:
                raised_fingers += 1
        # Thumb: check if it extends right for right hand
        else:
            if tip_x > mcp_x + 50:  # Adjust threshold for thumb extension
                raised_fingers += 1

    return raised_fingers

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Initialize MediaPipe Hands (restrict to one hand)
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

    # State variables
    last_click_time = 0
    click_cooldown = 0.5  # Seconds between clicks (single or double)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Flip the frame horizontally for natural movement
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame for hand detection
        results = hands.process(frame_rgb)

        # Process detected hand
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # Only process right hand
                if handedness.classification[0].label != "Right":
                    continue

                # Draw landmarks
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get index finger tip (8)
                index_tip = hand_landmarks.landmark[8]

                # Convert to pixel coordinates
                x_index = int(index_tip.x * frame_width)
                y_index = int(index_tip.y * frame_height)

                # Count raised fingers
                finger_count = count_fingers(hand_landmarks, frame_width, frame_height)

                # Map index finger to screen coordinates
                screen_x = int(index_tip.x * screen_width)
                screen_y = int(index_tip.y * screen_height)

                current_time = time.time()

                # No action if fist
                if finger_count == 0:
                    continue

                # Actions based on finger count
                if finger_count == 1:  # Move mouse
                    pyautogui.moveTo(screen_x, screen_y)

                elif finger_count == 2:  # Single click
                    if (current_time - last_click_time) > click_cooldown:
                        pyautogui.click()
                        last_click_time = current_time
                        cv2.circle(frame, (x_index, y_index), 10, (0, 255, 0), -1)  # Visual feedback

                elif finger_count == 3:  # Double click
                    if (current_time - last_click_time) > click_cooldown:
                        pyautogui.doubleClick()
                        last_click_time = current_time
                        cv2.circle(frame, (x_index, y_index), 10, (0, 255, 0), -1)  # Visual feedback

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