#chris alpuerto
from pythonosc import udp_client
import cv2
import mediapipe as mp
import numpy as np

# OSC client
client = udp_client.SimpleUDPClient("127.0.0.1",12345)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

frameWidth = 640
frameHeight = 500 

# distance range
min_distance = 20
max_distance = 370

# initialize left and right hand distances
left_distance = 0
right_distance = 0
normalized_distance = 0
normailzed_distance_left = 0
normalized_distance_right = 0

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

            # distance between thumb and index finger (pixel vals)
            distance = np.linalg.norm(np.array([thumb_x, thumb_y]) - np.array([index_x, index_y]))
            
            if label == "Left":
                left_distance = int(distance)
                normalized_distance_left = (left_distance - min_distance) / (max_distance - min_distance)
                normalized_distance_left = max(0, min(1, normalized_distance_left))
                text_position = (50, 50)
                color = (0,255,0)
            else:
                right_distance = int(distance)
                normalized_distance_right = (right_distance - min_distance) / (max_distance - min_distance)
                normalized_distance_right = max(0, min(1, normalized_distance_right))
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
            client.send_message("/live/track/volume", normalized_distance_left)
            client.send_message("/live/track/reverb", normalized_distance_right)
            

    cv2.imshow("HandAutoMation", frame)

    print(f"normalized left : {normalized_distance_left}, normalized right: {normalized_distance_right}")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
