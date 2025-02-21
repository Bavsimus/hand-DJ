import pygame
import pyaudio
import numpy as np
import wave
import struct
from pydub import AudioSegment

# start pygame
pygame.init()

# pygame screen
screen = pygame.display.set_mode((1400, 600))
pygame.display.set_caption('Audio Visualizer')

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

# main loop
running = True
while running and sound_data:
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if 550 <= mouse_y <= 550 + slider_height and slider_pos - slider_width // 2 <= mouse_x <= slider_pos + slider_width // 2:
                scale_factor = int((mouse_x - (slider_pos - slider_width // 2)) / slider_width * (slider_max - slider_min) + slider_min)

    # sound data to stream
    stream.write(sound_data)

    # analyze the sound data
    # byte to integer
    audio_data = np.array(struct.unpack(str(2 * frames_per_buffer) + 'h', sound_data))

    # screen clear
    screen.fill((0, 0, 0))

    # Ses dalgasını çiz
    for i in range(1, len(audio_data), scale_factor):
        pygame.draw.line(screen, blue, 
                         (i - 1, 300 - audio_data[i - 1] // 200), 
                         (i, 300 - audio_data[i] // 200), 1)

    # Slider'ı çiz
    draw_slider(screen, slider_pos, slider_min, slider_max, slider_width, slider_height, slider_color, slider_handle_color, slider_handle_radius)

    pygame.display.flip()

    # carry on with the next frame
    sound_data = wf.readframes(frames_per_buffer)

# pyaudio close
stream.stop_stream()
stream.close()
wf.close()
p.terminate()

# pygame close
pygame.quit()