import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (0, 0, 255)

# Şarkı adları ve pathleri
TEXTS = ["sickomode", "dans et", "boiler", "check my brain", "lazy song"]
SONG_PATHS = {
    "sickomode": r"C:\Users\USER\Music\cropped\sickomode.wav",
    "dans et": r"C:\Users\USER\Music\cropped\danset.wav",
    "boiler": r"C:\Users\USER\Music\cropped\boiler.wav",
    "check my brain": r"C:\Users\USER\Music\cropped\checkmybrain.wav",
    "lazy song": r"C:\Users\USER\Music\cropped\lazysong.wav"
}

def is_hand_open(hand_landmarks):
    """Elin açık olup olmadığını belirler."""
    fingers_open = 0
    finger_tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    for tip in finger_tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:  # Parmak ucu alt eklemden yukarıdaysa açıktır
            fingers_open += 1

    return fingers_open >= 3  # En az 3 parmak açıksa eli açık kabul et

def draw_right_hand_menu(frame, hand_landmarks, w, h):
    """Sağ el açıksa interaktif menüyü çizer ve seçili şarkıyı döndürür."""
    if not is_hand_open(hand_landmarks):  
        return None  # Eğer el kapalıysa menüyü çizme

    middle_finger_base = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    center = (int(middle_finger_base.x * w), int(middle_finger_base.y * h))

    # Yarım daire çiz
    axes = (100, 100)
    cv2.ellipse(frame, center, axes, 0, 180, 360, GREEN, 2)

    # İşaret parmağının ucunu işaretle
    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_finger_tip_point = (int(index_finger_tip.x * w), int(index_finger_tip.y * h))
    cv2.circle(frame, index_finger_tip_point, 10, GREEN, 2)

    # Seçeneklerin pozisyonlarını belirle
    circle_positions = []
    for i in range(5):
        angle = 180 + (180 / 4 * i)
        x = int(center[0] + axes[0] * math.cos(math.radians(angle)))
        y = int(center[1] + axes[1] * math.sin(math.radians(angle)))
        circle_positions.append((x, y, TEXTS[i]))
        cv2.circle(frame, (x, y), 5, GREEN, -1)

    # En yakın seçeneği bul
    closest_circle = min(circle_positions, key=lambda pos: math.dist(index_finger_tip_point, pos[:2]))

    # Seçili olanı büyüt ve metni ekle
    cv2.circle(frame, (closest_circle[0], closest_circle[1]), 10, WHITE, -1)
    cv2.putText(frame, closest_circle[2], (closest_circle[0], closest_circle[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 2, cv2.LINE_AA)

    return SONG_PATHS[closest_circle[2]]

def check_left_hand_gesture(frame, hand_landmarks, w, h):
    """Sol elin işaret ve baş parmağı arasındaki mesafeyi kontrol eder."""
    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

    index_point = (int(index_finger_tip.x * w), int(index_finger_tip.y * h))
    thumb_point = (int(thumb_tip.x * w), int(thumb_tip.y * h))

    cv2.circle(frame, index_point, 10, RED, 2)
    cv2.circle(frame, thumb_point, 10, RED, 2)

    # Mesafe hesapla
    distance = math.dist(index_point, thumb_point)
    pinch_detected = False
    if distance < 20:  # 20 piksel altında ise
        cv2.putText(frame, 'Pinch Detected', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2, cv2.LINE_AA)
        pinch_detected = True
    
    return pinch_detected

def handMenu(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    pinch_detected = False
    selected_song_path = None

    if result.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            label = handedness.classification[0].label
            h, w, _ = frame.shape

            if label == 'Right':
                selected_song_path = draw_right_hand_menu(frame, hand_landmarks, w, h)
            else:
                pinch_detected = check_left_hand_gesture(frame, hand_landmarks, w, h)

    return frame, pinch_detected, selected_song_path
