import cv2
import mediapipe as mp
import pyautogui

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

        # Draw hand landmarks and control mouse
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get index finger tip coordinates (landmark 8)
                index_tip = hand_landmarks.landmark[8]
                x = int(index_tip.x * frame_width)
                y = int(index_tip.y * frame_height)

                # Map to screen coordinates
                screen_x = int(index_tip.x * screen_width)
                screen_y = int(index_tip.y * screen_height)

                # Move mouse
                pyautogui.moveTo(screen_x, screen_y)

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