import cv2

def display_text_on_frame(frame, text):
    # Write the text on the frame
    cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    return frame

def display_text_on_camera(text):
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Write the text on the frame
        frame = display_text_on_frame(frame, text)
        
        # Display the frame
        cv2.imshow('Camera', frame)
        
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()