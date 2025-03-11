#chris alpuerto

import cv2
import mediapipe as mp
import numpy as np


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

frameWidth = 720
frameHeight = 600

# initialize left and right hand distances
left_distance = 0
right_distance = 0

cap = cv2.VideoCapture(1)
cap.set(3, frameWidth)
cap.set(4, frameHeight)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # determine if left or right hand
            label = handedness.classification[0].label
            
            # drawing hand landmarks
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # landmark positions
            h, w, _ = frame.shape
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            #converting to pixel values
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)

            distance = np.linalg.norm(np.array([thumb_x, thumb_y]) - np.array([index_x, index_y]))
            if label == "Left":
                left_distance = int(distance)
                text_position = (50, 50)
                color = (0,255,0)
            else:
                right_distance = int(distance)
                text_position = (w - 200, 50)
                color = (255,0,0)

            color = (255, 0, 0) if label == "Left" else (0, 0, 255)

            # circles at thumbs and index finger
            cv2.circle(frame, (thumb_x, thumb_y), 10, (0,0,255), -1)
            cv2.circle(frame, (index_x, index_y), 10, (255,0,0), -1)

            # line between thumb and index finger
            cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (0,255,0), 3)
            
            # distance text
            cv2.putText(frame, f"{int(distance)} px", text_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow("HandAutoMation", frame)

    print(f"left: {left_distance}, right: {right_distance}")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
