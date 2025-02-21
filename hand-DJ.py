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

# mp3 to wav
mp3_filename = r'C:\Users\USER\Documents\GitHub\hand-DJ\SICKOMODE.wav'  # song path
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

# OpenCV video capture
cap = cv2.VideoCapture(0)

# MediaPipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Flag to stop threads
stop_flag = threading.Event()

# Volume control variable
volume = 1.0  # Default volume (1.0 is original volume)

# Function to play audio in a separate thread
def play_audio():
    global sound_data
    while not stop_flag.is_set():
        # Adjust volume
        adjusted_data = np.frombuffer(sound_data, dtype=np.int16) * volume
        adjusted_data = adjusted_data.astype(np.int16).tobytes()
        stream.write(adjusted_data)
        sound_data = wf.readframes(frames_per_buffer)
        if len(sound_data) == 0:  # If end of file is reached, rewind
            wf.rewind()
            sound_data = wf.readframes(frames_per_buffer)

# Function to draw the equator line
def draw_equator(frame, left_mid_x, left_mid_y, right_mid_x, right_mid_y):
    cv2.line(frame, (left_mid_x, left_mid_y), (right_mid_x, right_mid_y), (255, 255, 0), 2)

# Start audio playback thread
audio_thread = threading.Thread(target=play_audio)
audio_thread.start()

# main loop
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Mirror the frame
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe
    results = hands.process(rgb_frame)

    # Initialize midpoints
    right_mid_x = right_mid_y = left_mid_x = left_mid_y = None

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
                    cv2.circle(frame, (x, y), 5, green, -1)

                # Draw line between right index finger and right thumb
                right_index_finger_x = int(right_index_finger.x * frame.shape[1])
                right_index_finger_y = int(right_index_finger.y * frame.shape[0])
                right_thumb_x = int(right_thumb.x * frame.shape[1])
                right_thumb_y = int(right_thumb.y * frame.shape[0])
                cv2.line(frame, (right_index_finger_x, right_index_finger_y), (right_thumb_x, right_thumb_y), red, 2)

                # Calculate and draw midpoint
                right_mid_x = (right_index_finger_x + right_thumb_x) // 2
                right_mid_y = (right_index_finger_y + right_thumb_y) // 2
                #cv2.circle(frame, (right_mid_x, right_mid_y), 5, red, -1)

            elif hand_label == 'Left':
                # Left hand landmarks (index finger and thumb)
                left_index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                left_thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                # Draw the landmarks
                for landmark in [left_index_finger, left_thumb]:
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 10, green, 2)

                # Draw line between left index finger and left thumb
                left_index_finger_x = int(left_index_finger.x * frame.shape[1])
                left_index_finger_y = int(left_index_finger.y * frame.shape[0])
                left_thumb_x = int(left_thumb.x * frame.shape[1])
                left_thumb_y = int(left_thumb.y * frame.shape[0])
                cv2.line(frame, (left_index_finger_x, left_index_finger_y), (left_thumb_x, left_thumb_y), green, 2)

                # Calculate and draw midpoint
                left_mid_x = (left_index_finger_x + left_thumb_x) // 2
                left_mid_y = (left_index_finger_y + left_thumb_y) // 2
                #cv2.circle(frame, (left_mid_x, left_mid_y), 5, green, -1)

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

            # Draw the equator line
            # draw_equator(frame, left_mid_x, left_mid_y, right_mid_x, right_mid_y)

            # Calculate the midpoint of the equator line
            equator_mid_x = (left_mid_x + right_mid_x) // 2
            equator_mid_y = (left_mid_y + right_mid_y) // 2

            # Display the distance at the midpoint of the equator line
            cv2.putText(frame, distance_text, (equator_mid_x - 50, equator_mid_y - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, distance_text_var, (equator_mid_x - 30, equator_mid_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Display the frame
    cv2.imshow('Audio Visualizer', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        stop_flag.set()
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

# Wait for audio thread to finish
audio_thread.join()

# pyaudio close
stream.stop_stream()
stream.close()
wf.close()
p.terminate()