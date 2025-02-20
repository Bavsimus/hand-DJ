import cv2
import mediapipe as mp
import math

# MediaPipe el algılama modülü
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# VideoCapture ile kamerayı başlat
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

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
                index_finger_tip = hand_landmarks.landmark[8]
                thumb_tip = hand_landmarks.landmark[4]
            else:
                color = (0, 0, 255)  # Sol el için kırmızı
                index_finger_tip = hand_landmarks.landmark[8]
                thumb_tip = hand_landmarks.landmark[4]

            h, w, _ = frame.shape
            cv2.circle(frame, (int(index_finger_tip.x * w), int(index_finger_tip.y * h)), 10, color, 2)
            cv2.circle(frame, (int(thumb_tip.x * w), int(thumb_tip.y * h)), 10, color, 2)
            cv2.line(frame, (int(thumb_tip.x * w), int(thumb_tip.y * h)), (int(index_finger_tip.x * w), int(index_finger_tip.y * h)), color, 2)

            # Çizginin uzunluğunu hesapla
            length = math.sqrt((thumb_tip.x - index_finger_tip.x) ** 2 + (thumb_tip.y - index_finger_tip.y) ** 2) * w
            length = int(length / 10)  # Değeri 10'a böl ve tam sayıya çevir

            # Çizginin ortasına metin ekle
            mid_x = int((thumb_tip.x + index_finger_tip.x) / 2 * w)
            mid_y = int((thumb_tip.y + index_finger_tip.y) / 2 * h)
            if label == 'Right':
                cv2.putText(frame, 'RIGHT', (mid_x + 20, mid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(frame, f'{length}', (mid_x + 20, mid_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            else:
                cv2.putText(frame, 'LEFT', (mid_x - 50, mid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(frame, f'{length}', (mid_x - 50, mid_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Görüntüyü göster
    cv2.imshow("Hand Detection", frame)

    # 'q' tuşuna basıldığında çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kaynakları serbest bırak
cap.release()
cv2.destroyAllWindows()