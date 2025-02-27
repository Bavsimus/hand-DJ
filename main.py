import cv2
from handMenu import handMenu  # Import the handMenu function
from handDjNoCam import process_frame, start_audio_playback, stop_audio_playback  # Import functions from handDjNoCam

def open_camera_and_run_script():
    # Open the camera
    cap = cv2.VideoCapture(0)
    audio_thread = start_audio_playback() # KENDİME NOT BU SATIR MÜZİĞİ BAŞLATIYOR, FRAME 2 AKTİF OLDUĞUNDA ÇALIŞSIN İSTİYORUM AMA 44. SATIRA KOYUNCA ÇALIŞMIOR
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    frame_2_active = False  # Initialize the boolean variable

    
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
        
        # Call the hand detection function
        if not frame_2_active:
            frame, pinch_detected = handMenu(frame)
            if pinch_detected:
                frame_2_active = True
        
        # If frame_2_active is True, use handDjNoCam to process the frame
        if frame_2_active:
            frame = process_frame(frame)
            #BURASI

        
        # Process the frame with handDjNoCam
        
        
        cv2.imshow('Camera', frame)
        
        # Press 'q' to quit the camera view
        if key == ord('q'):
            break
    
    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    
    # Stop audio playback
    stop_audio_playback(audio_thread)

# Open the camera and run the script
open_camera_and_run_script()