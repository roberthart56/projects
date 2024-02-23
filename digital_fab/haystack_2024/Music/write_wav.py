import numpy as np
from scipy.io.wavfile import write

# Parameters
sample_rate = 44100  # Sample rate in Hz
duration = 2  # Duration in seconds
frequency = 440  # Frequency of the sine wave in Hz

# Generate time array
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# Generate audio waveform
audio = np.sin(2 * np.pi * frequency * t)\
+ 0.2 * np.sin(2 * np.pi * 3*frequency * t)\
+ 0.1 * np.sin(2 * np.pi * 5*frequency * t)

# Normalize to 16-bit range
audio_normalized = np.int16(audio * 32767)

# Save as WAV file
write('complex_wave.wav', sample_rate, audio_normalized)
