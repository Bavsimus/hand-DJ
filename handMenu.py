import cv2
import mediapipe as mp
import math

# MediaPipe el algılama modülü
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

def handMenu(frame):
    # BGR görüntüyü RGB'ye dönüştür
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # El algılama
    result = hands.process(rgb_frame)

    # Algılanan elleri işaretle
    if result.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            # Elin sağ mı sol mu olduğunu belirle
            label = handedness.classification[0].label
            h, w, _ = frame.shape

            if label == 'Right':
                color = (0, 255, 0)  # Sağ el için yeşil
                # Orta parmağın avuçtaki başlangıç noktasını işaretle
                middle_finger_base = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
                center = (int(middle_finger_base.x * w), int(middle_finger_base.y * h))
                axes = (100, 100)  # Yarıçapı belirleyen eksenler
                angle = 0  # Elipsin açısı
                startAngle = 180  # Başlangıç açısı
                endAngle = 360  # Bitiş açısı (üst yarım daire için 180 derece)
                cv2.ellipse(frame, center, axes, angle, startAngle, endAngle, color, 2)
                
                # İşaret parmağının ucunu işaretle
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_finger_tip_point = (int(index_finger_tip.x * w), int(index_finger_tip.y * h))
                cv2.circle(frame, index_finger_tip_point, 10, color, 2)
                
                # Yarım dairenin üzerine dört küçük daire çiz
                circle_positions = []
                for i in range(5):
                    offset_angle = startAngle + (endAngle - startAngle) / 4 * i
                    offset_x = int(center[0] + axes[0] * math.cos(math.radians(offset_angle)))
                    offset_y = int(center[1] + axes[1] * math.sin(math.radians(offset_angle)))  # Yukarıda olması için + kullanıyoruz
                    circle_positions.append((offset_x, offset_y))
                    cv2.circle(frame, (offset_x, offset_y), 5, color, -1)
                
                # En yakın circle'ı bul ve çapını iki katına çıkar
                min_distance = float('inf')
                closest_circle = None
                for pos in circle_positions:
                    distance = math.sqrt((index_finger_tip_point[0] - pos[0]) ** 2 + (index_finger_tip_point[1] - pos[1]) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_circle = pos
                
                if closest_circle:
                    cv2.circle(frame, closest_circle, 10, color, -1)
            else:
                color = (0, 0, 255)  # Sol el için kırmızı
                # İşaret parmağının ucunu işaretle
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_finger_tip_point = (int(index_finger_tip.x * w), int(index_finger_tip.y * h))
                cv2.circle(frame, index_finger_tip_point, 10, color, 2)
                # Baş parmağın ucunu işaretle
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                thumb_tip_point = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                cv2.circle(frame, thumb_tip_point, 10, color, 2)

                # İşaret parmağı ve baş parmak arasındaki mesafeyi kontrol et
                distance = math.sqrt((index_finger_tip_point[0] - thumb_tip_point[0]) ** 2 + (index_finger_tip_point[1] - thumb_tip_point[1]) ** 2)
                if distance / 10 <= 2:
                    # Mesafe 1 ve altında ise yapılacak işlem
                    cv2.putText(frame, 'Distance <= 2', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

    return frame