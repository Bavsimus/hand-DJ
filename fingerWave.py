import cv2
import mediapipe as mp
import numpy as np
import pyaudio
import wave
import struct
from pydub import AudioSegment
import pygame
import threading
import math

# MediaPipe el algılama modülü
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Pyaudio ayarları
p = pyaudio.PyAudio()

# mp3 to wav
mp3_filename = r'C:\Users\USER\Documents\GitHub\hand-DJ\limp-bizkit_boiler.mp3'  # song path
wav_filename = 'temp.wav'
audio_segment = AudioSegment.from_file(mp3_filename)
audio_segment.export(wav_filename, format='wav')

# wav file
wf = wave.open(wav_filename, 'rb')

# pyaudio stream
stream = p.open(format=pyaudio.paInt16,
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# reading the first frame
frames_per_buffer = 1024
sound_data = wf.readframes(frames_per_buffer)

# start pygame
pygame.init()

# pygame screen
screen = pygame.display.set_mode((1400, 600))
pygame.display.set_caption('Audio Visualizer')

# colors
white = (255, 255, 255)
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)

# Slider settings
scale_factor = 1
slider_pos = 700
slider_min = 1
slider_max = 20
slider_width = 200
slider_height = 20
slider_color = blue
slider_handle_color = green
slider_handle_radius = 10

def draw_slider(screen, pos, min_val, max_val, width, height, color, handle_color, handle_radius):
    pygame.draw.rect(screen, color, (pos - width // 2, 550, width, height))
    handle_x = pos - width // 2 + int((scale_factor - min_val) / (max_val - min_val) * width)
    pygame.draw.circle(screen, handle_color, (handle_x, 550 + height // 2), handle_radius)

def play_audio():
    global sound_data
    while sound_data:
        stream.write(sound_data)
        sound_data = wf.readframes(frames_per_buffer)

# ...existing code...
# Amplitude değeri
amplitude = 800

def visualize_audio():
    global sound_data
    cap = cv2.VideoCapture(0)
    
    # Kamera boyutunu ayarla
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    running = True
    while running and sound_data:
        ret, frame = cap.read()
        if not ret:
            break

        # BGR görüntüyü RGB'ye dönüştür
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # El algılama
        result = hands.process(rgb_frame)

        # Algılanan elleri çiz
        if result.multi_hand_landmarks:
            right_thumb_tip = None
            right_index_tip = None
            left_thumb_tip = None
            left_index_tip = None

            for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                # Elin sağ mı sol mu olduğunu belirle
                label = handedness.classification[0].label
                if label == 'Right':
                    color = (0, 255, 0)  # Sağ el için yeşil
                    right_thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    right_index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                else:
                    color = (0, 0, 255)  # Sol el için kırmızı
                    left_thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    left_index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Sadece işaret ve baş parmak uçlarını çember şeklinde çiz
                for landmark in [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.INDEX_FINGER_TIP]:
                    x = int(hand_landmarks.landmark[landmark].x * frame.shape[1])
                    y = int(hand_landmarks.landmark[landmark].y * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, color, -1)  # İç dolu nokta
                    cv2.circle(frame, (x, y), 10, color, 2)  # İç boş çember

            if right_thumb_tip and right_index_tip:
                # Sağ el işaret ve baş parmak uçları arasına çizgi çek
                right_thumb_x, right_thumb_y = int(right_thumb_tip.x * frame.shape[1]), int(right_thumb_tip.y * frame.shape[0])
                right_index_x, right_index_y = int(right_index_tip.x * frame.shape[1]), int(right_index_tip.y * frame.shape[0])
                cv2.line(frame, (right_thumb_x, right_thumb_y), (right_index_x, right_index_y), (255, 255, 255), 2)

                # Sağ el işaret ve baş parmak uçları arasındaki orta noktayı hesapla
                right_mid_x = (right_thumb_x + right_index_x) // 2
                right_mid_y = (right_thumb_y + right_index_y) // 2

            if left_thumb_tip and left_index_tip:
                # Sol el işaret ve baş parmak uçları arasına çizgi çek
                left_thumb_x, left_thumb_y = int(left_thumb_tip.x * frame.shape[1]), int(left_thumb_tip.y * frame.shape[0])
                left_index_x, left_index_y = int(left_index_tip.x * frame.shape[1]), int(left_index_tip.y * frame.shape[0])
                cv2.line(frame, (left_thumb_x, left_thumb_y), (left_index_x, left_index_y), (255, 255, 255), 2)

                # Sol el işaret ve baş parmak uçları arasındaki orta noktayı hesapla
                left_mid_x = (left_thumb_x + left_index_x) // 2
                left_mid_y = (left_thumb_y + left_index_y) // 2

            if right_thumb_tip and right_index_tip and left_thumb_tip and left_index_tip:
                # Dalga formunu sağ ve sol el işaret ve baş parmak uçları arasındaki orta noktalar arasına yerleştir
                audio_data = np.array(struct.unpack(str(2 * frames_per_buffer) + 'h', sound_data))
                
                # İki orta nokta arasındaki açıyı hesapla
                angle = math.atan2(right_mid_y - left_mid_y, right_mid_x - left_mid_x)
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)

                for i in range(1, len(audio_data), scale_factor):
                    x1 = left_mid_x + (right_mid_x - left_mid_x) * (i - 1) // len(audio_data)
                    y1 = left_mid_y - audio_data[i - 1] // amplitude  # Amplitude değerini kullan
                    x2 = left_mid_x + (right_mid_x - left_mid_x) * i // len(audio_data)
                    y2 = left_mid_y - audio_data[i] // amplitude  # Amplitude değerini kullan

                    # Döndürme işlemi
                    x1_rot = int(cos_angle * (x1 - left_mid_x) - sin_angle * (y1 - left_mid_y) + left_mid_x)
                    y1_rot = int(sin_angle * (x1 - left_mid_x) + cos_angle * (y1 - left_mid_y) + left_mid_y)
                    x2_rot = int(cos_angle * (x2 - left_mid_x) - sin_angle * (y2 - left_mid_y) + left_mid_x)
                    y2_rot = int(sin_angle * (x2 - left_mid_x) + cos_angle * (y2 - left_mid_y) + left_mid_y)

                    cv2.line(frame, (x1_rot, y1_rot), (x2_rot, y2_rot), (255, 255, 255), 1)

        # Görüntüyü göster
        cv2.imshow("Hand Detection", frame)

        # 'q' tuşuna basıldığında çık
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False

        # analyze the sound data
        # byte to integer
        audio_data = np.array(struct.unpack(str(2 * frames_per_buffer) + 'h', sound_data))

        # screen clear
        screen.fill((0, 0, 0))

        # Ses dalgasını çiz
        for i in range(1, len(audio_data), scale_factor):
            pygame.draw.line(screen, blue, 
                             (i - 1, 300 - audio_data[i - 1] // amplitude),  # Amplitude değerini kullan
                             (i, 300 - audio_data[i] // amplitude),  # Amplitude değerini kullan
                             1)

        # Slider'ı çiz
        draw_slider(screen, slider_pos, slider_min, slider_max, slider_width, slider_height, slider_color, slider_handle_color, slider_handle_radius)

        pygame.display.flip()

    # Kaynakları serbest bırak
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()  # Pygame penceresini kapat

# Ses çalma iş parçacığını başlat
audio_thread = threading.Thread(target=play_audio)
audio_thread.start()

# Görselleştirme iş parçacığını başlat
visualize_thread = threading.Thread(target=visualize_audio)
visualize_thread.start()

# İş parçacıklarının tamamlanmasını bekle
audio_thread.join()
visualize_thread.join()

# pyaudio close
stream.stop_stream()
stream.close()
wf.close()
p.terminate()