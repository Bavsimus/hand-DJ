import cv2
import mediapipe as mp

# MediaPipe el algılama modülü
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

def detect_hand(frame):
    # BGR görüntüyü RGB'ye dönüştür
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # El algılama
    result = hands.process(rgb_frame)

    # Algılanan elleri çiz
    if result.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            # Elin sağ mı sol mu olduğunu belirle
            label = handedness.classification[0].label
            if label == 'Right':
                color = (0, 255, 0)  # Sağ el için yeşil
            else:
                color = (0, 0, 255)  # Sol el için kırmızı

            # Elin etrafına dikdörtgen çiz
            x_min = min([lm.x for lm in hand_landmarks.landmark])
            y_min = min([lm.y for lm in hand_landmarks.landmark])
            x_max = max([lm.x for lm in hand_landmarks.landmark])
            y_max = max([lm.y for lm in hand_landmarks.landmark])
            h, w, _ = frame.shape
            cv2.rectangle(frame, (int(x_min * w), int(y_min * h)), (int(x_max * w), int(y_max * h)), color, 2)

            # Elin bağlantı noktalarını çiz
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    return frame