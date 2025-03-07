import cv2
from handMenu import handMenu
from handDjNoCam import process_frame, start_audio_playback, stop_audio_playback

def open_camera_and_run_script(song_path):
    # Open the camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    frame_2_active = False  # Initialize the boolean variable
    audio_thread = None
    wf = None
    stream = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Flip the frame
        frame = cv2.flip(frame, 1)

        key = cv2.waitKey(1) & 0xFF

        # Press 'd' to toggle frame_2_active
        if key == ord('d'):
            frame_2_active = not frame_2_active
            if frame_2_active and audio_thread is None:  
                audio_thread, wf, stream = start_audio_playback(song_path)  # Müziği başlat

        # Call the hand detection function
        if not frame_2_active:
            frame, pinch_detected, song_path = handMenu(frame)
            if pinch_detected:
                frame_2_active = True
                if audio_thread is None:  
                    audio_thread, wf, stream = start_audio_playback(song_path)  # Müziği başlat

        # If frame_2_active is True, use handDjNoCam to process the frame
        if frame_2_active:
            frame = process_frame(frame)

        cv2.imshow('Camera', frame)

        # Press 'q' to quit the camera view and stop music
        if key == ord('q'):
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

    # Stop audio playback
    if audio_thread is not None:
        stop_audio_playback(audio_thread, wf, stream)

# Open the camera and run the script
song_path = r"C:\Users\USER\Music\cropped\sickomode.wav"  # Şarkı yolunu buraya gir
open_camera_and_run_script(song_path)
