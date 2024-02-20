from pygame import mixer
from time import sleep
mixer.init()
sound = mixer.Sound('250Hz.wav')
sound.play()
sleep(2)
# sound.stop()
sound = mixer.Sound('1kHz.wav')
sound.play()				#plays at the same time.
sleep(2)
sound.stop()

