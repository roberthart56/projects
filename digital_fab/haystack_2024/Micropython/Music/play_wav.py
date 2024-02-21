from pygame import mixer
from time import sleep
mixer.init()
sound = mixer.Sound('sine_wave.wav')
sound.play()
sleep(1.5)
sound.fadeout(100)


