import cv2
import pyaudio
import numpy as np
import wave
import struct
from pydub import AudioSegment
import threading
import mediapipe as mp
import math

# Pyaudio settings
p = pyaudio.PyAudio()
RED = (0, 0, 255)
pinch_detectedDJ = False
# mp3 to wav
mp3_filename = r'C:\Users\USER\Music\cropped\sickomode.wav'  # song path
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

# colors
blue = (255, 0, 0)
green = (0, 255, 0)
red = (0, 0, 255)
white = (255, 255, 255)

# MediaPipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Flag to stop threads
stop_flag = threading.Event()

# Volume control variable
volume = 1.0  # Default volume (1.0 is original volume)

# Function to play audio in a separate thread
def play_audio(wf, stream):
    global sound_data
    while not stop_flag.is_set():
        # Adjust volume
        sound_data = wf.readframes(1024)
        if len(sound_data) == 0:  # If end of file is reached, rewind
            wf.rewind()
            sound_data = wf.readframes(1024)
        
        adjusted_data = np.frombuffer(sound_data, dtype=np.int16) * volume
        adjusted_data = adjusted_data.astype(np.int16).tobytes()
        stream.write(adjusted_data)

# Function to calculate the distance between two points
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt(((x2 - x1) ** 2 + (y2 - y1) ** 2 ) / 10)

# Function to draw the equator line
def draw_equator(frame, left_mid_x, left_mid_y, right_mid_x, right_mid_y):
    cv2.line(frame, (left_mid_x, left_mid_y), (right_mid_x, right_mid_y), (255, 255, 0), 2)

def check_left_pinch(frame, hand_landmarks, w, h):
    """Sol elin işaret ve baş parmağı arasındaki mesafeyi kontrol eder."""
    global pinch_detectedDJ  # Burada farklı isim kullanıyoruz

    index_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
    thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]

    index_point = (int(index_finger_tip.x * w), int(index_finger_tip.y * h))
    thumb_point = (int(thumb_tip.x * w), int(thumb_tip.y * h))

    distance = math.dist(index_point, thumb_point)
    
    pinch_detectedDJ = distance < 20  # Eğer mesafe küçükse True yap

    return pinch_detectedDJ


# Function to process the frame
def process_frame(frame):
    global volume, sound_data

    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe
    results = hands.process(rgb_frame)

    # Initialize midpoints
    right_mid_x = right_mid_y = left_mid_x = left_mid_y = None
    right_thumb_index_distance = left_thumb_index_distance = None  # Initialize the distance variables

    # Draw specific hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            hand_label = handedness.classification[0].label

            if hand_label == 'Right':
                # Right hand landmarks (index finger and thumb)
                right_index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                right_thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                # Draw the landmarks
                for landmark in [right_index_finger, right_thumb]:
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 10, red, 2)

                # Draw line between right index finger and right thumb
                right_index_finger_x = int(right_index_finger.x * frame.shape[1])
                right_index_finger_y = int(right_index_finger.y * frame.shape[0])
                right_thumb_x = int(right_thumb.x * frame.shape[1])
                right_thumb_y = int(right_thumb.y * frame.shape[0])
                cv2.line(frame, (right_index_finger_x, right_index_finger_y), (right_thumb_x, right_thumb_y), red, 2)

                # Calculate and draw midpoint
                right_mid_x = (right_index_finger_x + right_thumb_x) // 2
                right_mid_y = (right_index_finger_y + right_thumb_y) // 2

                check_left_pinch(frame, hand_landmarks, frame.shape[1], frame.shape[0])

            elif hand_label == 'Left':
                # Left hand landmarks (index finger and thumb)
                left_index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                left_thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                # Draw the landmarks
                for landmark in [left_index_finger, left_thumb]:
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 10, white, 2)

                # Draw line between left index finger and left thumb
                left_index_finger_x = int(left_index_finger.x * frame.shape[1])
                left_index_finger_y = int(left_index_finger.y * frame.shape[0])
                left_thumb_x = int(left_thumb.x * frame.shape[1])
                left_thumb_y = int(left_thumb.y * frame.shape[0])
                cv2.line(frame, (left_index_finger_x, left_index_finger_y), (left_thumb_x, left_thumb_y), green, 2)

                # Calculate and draw midpoint
                left_mid_x = (left_index_finger_x + left_thumb_x) // 2
                left_mid_y = (left_index_finger_y + left_thumb_y) // 2

                # Calculate the distance between left thumb and index finger
                left_thumb_index_distance = calculate_distance(left_index_finger_x, left_index_finger_y, left_thumb_x, left_thumb_y)

   
    # analyze the sound data
    if sound_data:
        audio_data = np.array(struct.unpack(str(2 * frames_per_buffer) + 'h', sound_data))

        # Draw the waveform between the midpoints
        if right_mid_x is not None and left_mid_x is not None:
            # Calculate the distance between the midpoints
            distance = math.sqrt((right_mid_x - left_mid_x) ** 2 + (right_mid_y - left_mid_y) ** 2) // 10
            distance_text = f"volume"
            distance_text_var = f"{int(distance)}"

            # Adjust volume based on distance
            volume = distance / 100  # Adjust this factor as needed

            angle = math.atan2(right_mid_y - left_mid_y, right_mid_x - left_mid_x)
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)
            for i in range(1, len(audio_data)):
                x1 = left_mid_x + (right_mid_x - left_mid_x) * (i - 1) // len(audio_data)
                y1 = left_mid_y - audio_data[i - 1] // 800  # Adjusted amplitude
                x2 = left_mid_x + (right_mid_x - left_mid_x) * i // len(audio_data)
                y2 = left_mid_y - audio_data[i] // 800  # Adjusted amplitude

                # Rotate the points around the left midpoint
                x1_rot = left_mid_x + (x1 - left_mid_x) * cos_angle - (y1 - left_mid_y) * sin_angle
                y1_rot = left_mid_y + (x1 - left_mid_x) * sin_angle + (y1 - left_mid_y) * cos_angle
                x2_rot = left_mid_x + (x2 - left_mid_x) * cos_angle - (y2 - left_mid_y) * sin_angle
                y2_rot = left_mid_y + (x2 - left_mid_x) * sin_angle + (y2 - left_mid_y) * cos_angle

                cv2.line(frame, (int(x1_rot), int(y1_rot)), (int(x2_rot), int(y2_rot)), blue, 1)

            # Calculate the midpoint of the equator line
            equator_mid_x = (left_mid_x + right_mid_x) // 2
            equator_mid_y = (left_mid_y + right_mid_y) // 2

            # Display the distance at the midpoint of the equator line
            cv2.putText(frame, distance_text, (equator_mid_x - 50, equator_mid_y - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, distance_text_var, (equator_mid_x - 30, equator_mid_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

    return frame

# Function to start audio playback
def start_audio_playback(song_path):
    # Convert MP3 to WAV
    stop_flag.clear()  # stop_audio_playback çağırıldıktan sonra tekrar çalıştırılabilir

    wav_filename = 'temp.wav'
    audio_segment = AudioSegment.from_file(song_path)
    audio_segment.export(wav_filename, format='wav')

    # Open WAV file
    wf = wave.open(wav_filename, 'rb')

    # Pyaudio stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    audio_thread = threading.Thread(target=play_audio, args=(wf, stream))
    audio_thread.start()
    return audio_thread, wf, stream

# Function to stop audio playback
def stop_audio_playback(audio_thread, wf, stream):
    stop_flag.set()
    audio_thread.join()
    stream.stop_stream()
    stream.close()
    wf.close()
    audio_thread = None
    #p.terminate()
