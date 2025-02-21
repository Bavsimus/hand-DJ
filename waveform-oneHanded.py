import pyaudio
import numpy as np
import wave
import struct
from pydub import AudioSegment
import cv2
import threading
import mediapipe as mp

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

# OpenCV camera
cap = cv2.VideoCapture(0)

# amplitude scaling factor
amplitude_scale = 200

# Mediapipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# function to play audio
def play_audio():
    global sound_data
    while sound_data:
        stream.write(sound_data)
        sound_data = wf.readframes(frames_per_buffer)

# start audio playback in a separate thread
audio_thread = threading.Thread(target=play_audio)
audio_thread.start()

# main loop
running = True
while running:
    # analyze the sound data
    if sound_data:
        audio_data = np.array(struct.unpack(str(2 * frames_per_buffer) + 'h', sound_data))

    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with Mediapipe
    results = hands.process(frame)

    # Draw hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Determine the color based on the hand (left or right)
            if handedness.classification[0].label == 'Right':
                color = (255, 0, 0)  # Red for right hand
            else:
                color = (255, 100, 100)  # Light red for left hand

            # Draw only the landmarks for the index finger (8) and thumb (4)
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            # Convert normalized coordinates to pixel coordinates
            h, w, _ = frame.shape
            index_finger_tip_coords = (int(index_finger_tip.x * w), int(index_finger_tip.y * h))
            thumb_tip_coords = (int(thumb_tip.x * w), int(thumb_tip.y * h))

            # Draw circles on the index finger tip and thumb tip
            cv2.circle(frame, index_finger_tip_coords, 10, color, 2)  # thickness = 2
            cv2.circle(frame, thumb_tip_coords, 10, color, 2)  # thickness = 2

            # Draw a line between the index finger tip and thumb tip
            cv2.line(frame, index_finger_tip_coords, thumb_tip_coords, color, 2)  # thickness = 2

            # Calculate the midpoint between the index finger tip and thumb tip
            midpoint_x = (index_finger_tip_coords[0] + thumb_tip_coords[0]) // 2
            midpoint_y = (index_finger_tip_coords[1] + thumb_tip_coords[1]) // 2
            midpoint_coords = (midpoint_x, midpoint_y)

            # Draw the waveform between the index finger tip and thumb tip
            if sound_data:
                for i in range(1, len(audio_data)):
                    x1 = int(index_finger_tip_coords[0] + (thumb_tip_coords[0] - index_finger_tip_coords[0]) * (i - 1) / len(audio_data))
                    y1 = int(midpoint_y - audio_data[i - 1] / amplitude_scale)
                    x2 = int(index_finger_tip_coords[0] + (thumb_tip_coords[0] - index_finger_tip_coords[0]) * i / len(audio_data))
                    y2 = int(midpoint_y - audio_data[i] / amplitude_scale)
                    cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)

    # Display the frame
    cv2.imshow('Hand Detection', frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False

# Release the camera
cap.release()

# pyaudio close
stream.stop_stream()
stream.close()
wf.close()
p.terminate()

# Close OpenCV window
cv2.destroyAllWindows()