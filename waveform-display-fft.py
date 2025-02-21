import pygame
import pyaudio
import numpy as np
import wave
import struct
from pydub import AudioSegment

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 1400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Audio Visualizer with FFT')

# PyAudio settings
p = pyaudio.PyAudio()

# Convert mp3 to wav
mp3_filename = r'C:\Users\USER\Documents\GitHub\hand-DJ\SICKOMODE.wav'  # song path
wav_filename = 'temp1.wav'
audio_segment = AudioSegment.from_file(mp3_filename)
audio_segment.export(wav_filename, format='wav')

# Open wav file
wf = wave.open(wav_filename, 'rb')

# Open PyAudio stream
stream = p.open(format=pyaudio.paInt16,
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# Read the first frame
frames_per_buffer = 1024
sound_data = wf.readframes(frames_per_buffer)

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Slider settings (for scaling FFT visualization)
scale_factor = 10
slider_pos = WIDTH // 2
slider_min = 1
slider_max = 50
slider_width = 200
slider_height = 20
slider_color = RED
slider_handle_color = GREEN
slider_handle_radius = 10

def draw_slider(screen, pos, min_val, max_val, width, height, color, handle_color, handle_radius):
    """Draws a slider for adjusting the FFT visualization scale."""
    pygame.draw.rect(screen, color, (pos - width // 2, HEIGHT - 50, width, height))
    handle_x = pos - width // 2 + int((scale_factor - min_val) / (max_val - min_val) * width)
    pygame.draw.circle(screen, handle_color, (handle_x, HEIGHT - 50 + height // 2), handle_radius)

# Main loop
running = True
while running and sound_data:
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if (HEIGHT - 50) <= mouse_y <= (HEIGHT - 50 + slider_height) and (slider_pos - slider_width // 2) <= mouse_x <= (slider_pos + slider_width // 2):
                scale_factor = int((mouse_x - (slider_pos - slider_width // 2)) / slider_width * (slider_max - slider_min) + slider_min)

    # Write sound data to the stream (for audio playback)
    stream.write(sound_data)

    # Convert sound data to an array
    audio_data = np.array(struct.unpack(str(2 * frames_per_buffer) + 'h', sound_data))

    # Compute FFT
    fft_data = np.fft.fft(audio_data)
    fft_magnitude = np.abs(fft_data[:len(fft_data) // 2])  # Use first half
    fft_magnitude = np.log1p(fft_magnitude)  # Logarithmic scaling

    # Normalize to fit screen height
    fft_magnitude = fft_magnitude / np.max(fft_magnitude) * (HEIGHT // 2)

    # Clear the screen
    screen.fill(BLACK)

    # Draw FFT bars
    num_bins = len(fft_magnitude) // scale_factor
    bar_width = max(1, WIDTH // num_bins)  # Adjust width dynamically

    for i in range(num_bins):
        x = i * bar_width
        y = HEIGHT - int(fft_magnitude[i * scale_factor])  # Flip since Pygame's origin is top-left
        pygame.draw.rect(screen, BLUE, (x, y, bar_width - 1, int(fft_magnitude[i * scale_factor])))

    # Draw slider
    draw_slider(screen, slider_pos, slider_min, slider_max, slider_width, slider_height, slider_color, slider_handle_color, slider_handle_radius)

    # Update display
    pygame.display.flip()

    # Read next frame of sound data
    sound_data = wf.readframes(frames_per_buffer)

# Close PyAudio
stream.stop_stream()
stream.close()
wf.close()
p.terminate()

# Quit pygame
pygame.quit()
