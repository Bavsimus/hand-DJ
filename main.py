import cv2
from handMenu import handMenu  # Import the handMenu function

def open_camera_and_run_script():
    # Open the camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        
        # Flip the frame
        frame = cv2.flip(frame, 1)
        
        # Call the hand detection function
        frame = handMenu(frame)
        
        cv2.imshow('Camera', frame)
        
        # Press 'q' to quit the camera view
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

# Open the camera and run the script
open_camera_and_run_script()
