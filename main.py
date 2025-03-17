import cv2
import handDjNoCam  # Pinch değişkenini buradan alıyoruz
from handMenu import handMenu
from handDjNoCam import process_frame, start_audio_playback, stop_audio_playback

def open_camera_and_run_script(song_path):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    frame_2_active = False
    audio_thread = None
    wf = None
    stream = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv2.flip(frame, 1)
        key = cv2.waitKey(1) & 0xFF

        # Eğer handDjNoCam içindeki pinch_detectedDJ True olursa geçiş yap
        if handDjNoCam.pinch_detectedDJ:
            frame_2_active = not frame_2_active  # Aktifliği değiştir
            handDjNoCam.pinch_detectedDJ = False  # Bir kere geçiş yaptıktan sonra sıfırla

            if frame_2_active:  # Açıldıysa müziği başlat
                if audio_thread is None:
                    audio_thread, wf, stream = start_audio_playback(song_path)
            else:  # Kapandıysa müziği durdur
                stop_audio_playback(audio_thread, wf, stream)
                audio_thread, wf, stream = None, None, None  

        # Eğer Frame_2 aktif değilse ve handMenu'da pinch varsa, aç
        if not frame_2_active:
            frame, pinch_detected, song_path = handMenu(frame)  
            if pinch_detected:
                frame_2_active = True
                if audio_thread is None:  
                    audio_thread, wf, stream = start_audio_playback(song_path)

        if frame_2_active:
            frame = process_frame(frame)

        cv2.imshow('Camera', frame)

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if audio_thread is not None:
        stop_audio_playback(audio_thread, wf, stream)

# Başlat
song_path = r"C:\Users\USER\Music\cropped\sickomode.wav"
open_camera_and_run_script(song_path)
